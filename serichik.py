import hashlib
import hmac
import secrets
from datetime import datetime, date
from typing import Dict, Any, Optional

from pyrogram import Client, types, enums

from .. import loader, utils


FIRE_EFFECT_ID = 5104841245755180586
BROKEN_HEART_EFFECT_ID = 5123265598893064880


def today() -> date:
    return datetime.now().date()


def make_sig(secret: str, payload: str) -> str:
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()[:16]


def verify_sig(secret: str, payload: str, sig: str) -> bool:
    expected = make_sig(secret, payload)
    return hmac.compare_digest(expected, sig)


@loader.module(name="serichik", author="SHMods", version=1.4)
class Serichik(loader.Module):
    """Огонёк / серия дней с синхронизацией и эффектами"""

    strings = {
        "only_private": "🚫 <b>Только в личных чатах.</b>",
        "already_paired": "❔ <b>Уже спарены с этим человеком.</b>",
        "pair_created": (
            "🔥 <b>Код для синхронизации создан</b>\n\n"
            "Отправь другу этот код:\n<code>{code}</code>\n\n"
            "Он должен написать:\n<code>.серичик_join {code}</code>"
        ),
        "join_success": "🔥 <b>Успешно спарены!</b>\nТеперь серии будут синхронизироваться автоматически.",
        "join_invalid": "🚫 <b>Неверный или устаревший код.</b>",
        "not_paired": "❔ <b>Сначала нужно спариться (.серичик_pair).</b>",
        "sync_sent": "🔥 <b>Состояние отправлено другу.</b>",
        "status": "🔥 <b>Твои серии:</b>\n\n{list}",
        "series_item": (
            "• <b>{name}</b> — <code>{days}</code> дн. | кредиты: <code>{credits}</code>\n"
            "  Последняя: {last} | paired: {paired}"
        ),
        "left": "✂️ <b>Вышел из серии с {name}.</b>",
        "no_series": "❔ <b>Нет активных серий.</b>",
        "streak_up": (
            "🔥 <b>Серия с {name} продолжается!</b>\n"
            "День <b>{days}</b> • +{points} кредитов • Всего: <code>{credits}</code>"
        ),
        "streak_broken": (
            "💔 <b>Серия с {name} сгорела...</b>\n"
            "Прошло больше одного дня без сообщений."
        ),
        "help": (
            "🔥 <b>Серичик v1.4</b>\n\n"
            "<b>Основные:</b>\n"
            "• <code>.серичик</code> — пригласить (кнопка)\n"
            "• <code>.серии</code> — список серий\n"
            "• <code>.покинуть</code> — выйти из серии\n\n"
            "<b>Синхронизация:</b>\n"
            "• <code>.серичик_pair</code> — создать одноразовый код\n"
            "• <code>.серичик_join КОД</code> — принять код\n"
            "• <code>.серичик_sync</code> — принудительно синхронизировать\n\n"
            "<b>Конфиг:</b>\n"
            "• <code>disable_security</code> — если включить, твои собственные сообщения тоже продлевают серию\n\n"
            "🔥 — огонёк при продлении серии\n"
            "💔 — когда серия сгорает"
        ),
    }

    async def on_load(self, app: Client):
        if not self.db.get("serichik", "series"):
            self.db.set("serichik", "series", {})
        if not self.db.get("serichik", "pairs"):
            self.db.set("serichik", "pairs", {})
        if not self.db.get("serichik", "pending_codes"):
            self.db.set("serichik", "pending_codes", {})

        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "disable_security",
                False,
                "Отключить проверку is_self: твои собственные сообщения тоже продлевают серию",
                validator=loader.validators.Boolean(),
            ),
        )

    def _series(self) -> Dict[str, Any]:
        return self.db.get("serichik", "series", {})

    def _save_series(self, data):
        self.db.set("serichik", "series", data)

    def _pairs(self) -> Dict[str, str]:
        return self.db.get("serichik", "pairs", {})

    def _save_pairs(self, data):
        self.db.set("serichik", "pairs", data)

    def _calc_points(self, days: int) -> int:
        if days <= 3:
            return 10
        if days <= 7:
            return 25
        if days <= 14:
            return 50
        if days <= 30:
            return 100
        return 200

    async def _safe_answer(self, message: types.Message, text: str, **kwargs):
        try:
            return await utils.answer(message, text, **kwargs)
        except Exception:
            try:
                return await message.reply(text)
            except Exception:
                return None

    async def _send_with_effect(self, app: Client, chat_id: int, text: str, effect_id: int = None):
        try:
            kwargs = {"chat_id": chat_id, "text": text}
            if effect_id:
                try:
                    return await app.send_message(**kwargs, message_effect_id=effect_id)
                except TypeError:
                    try:
                        return await app.send_message(**kwargs, effect_id=effect_id)
                    except TypeError:
                        pass
            return await app.send_message(**kwargs)
        except Exception:
            try:
                return await app.send_message(chat_id, text)
            except Exception:
                return None

    @loader.command(alias="serichik_pair")
    async def серичик_pair(self, app: Client, message: types.Message):
        """Создать одноразовый код для синхронизации серий с другом"""
        if message.chat.type != enums.ChatType.PRIVATE:
            return await self._safe_answer(message, self.strings("only_private"))

        peer_id = str(message.chat.id)
        if peer_id in self._pairs():
            return await self._safe_answer(message, self.strings("already_paired"))

        random_part = secrets.token_hex(4)
        code = f"{self.tg_id}:{random_part}"

        pending = self.db.get("serichik", "pending_codes", {})
        pending[code] = {
            "peer_id": peer_id,
            "secret": random_part,
            "created": datetime.now().isoformat(),
            "used": False,
        }
        self.db.set("serichik", "pending_codes", pending)

        await self._safe_answer(message, self.strings("pair_created").format(code=code))

    @loader.command(alias="serichik_join")
    async def серичик_join(self, app: Client, message: types.Message):
        """Принять код синхронизации. Использование: .серичик_join ID:XXXX"""
        args = utils.get_args_raw(message)
        if not args or ":" not in args:
            return await self._safe_answer(message, "Использование: <code>.серичик_join ID:XXXX</code>")

        code = args.strip()
        try:
            creator_id, secret = code.split(":", 1)
            creator_id = int(creator_id)
        except Exception:
            return await self._safe_answer(message, self.strings("join_invalid"))

        peer_id = str(message.chat.id)
        pairs = self._pairs()
        pairs[peer_id] = secret
        self._save_pairs(pairs)

        series = self._series()
        try:
            chat = await app.get_chat(int(peer_id))
            name = utils.get_display_name(chat) or peer_id
        except Exception:
            name = peer_id

        series[peer_id] = {
            "name": name,
            "started": datetime.now().isoformat(),
            "last_active": today().isoformat(),
            "days": 1,
            "credits": 10,
            "active": True,
            "paired": True,
        }
        self._save_series(series)

        await self._send_with_effect(app, message.chat.id, self.strings("join_success"), FIRE_EFFECT_ID)

        try:
            await app.send_message(creator_id, f"🔥SERI:PAIR_OK|{self.tg_id}|{secret}")
        except Exception:
            pass

    def _build_sync_packet(self, peer_id: str) -> Optional[str]:
        series = self._series()
        pairs = self._pairs()
        if peer_id not in series or peer_id not in pairs:
            return None

        data = series[peer_id]
        secret = pairs[peer_id]
        payload = (
            f"days={data.get('days', 1)}|"
            f"credits={data.get('credits', 0)}|"
            f"last={data.get('last_active', today().isoformat())}"
        )
        sig = make_sig(secret, payload)
        return f"🔥SERI:v1|{payload}|sig={sig}"

    async def _send_sync(self, app: Client, peer_id: str):
        packet = self._build_sync_packet(peer_id)
        if not packet:
            return False
        try:
            await app.send_message(int(peer_id), packet, disable_notification=True)
            return True
        except Exception:
            return False

    @loader.command(alias="serichik_sync")
    async def серичик_sync(self, app: Client, message: types.Message):
        """Принудительно отправить текущее состояние серии другу"""
        if message.chat.type != enums.ChatType.PRIVATE:
            return await self._safe_answer(message, self.strings("only_private"))

        peer_id = str(message.chat.id)
        if peer_id not in self._pairs():
            return await self._safe_answer(message, self.strings("not_paired"))

        ok = await self._send_sync(app, peer_id)
        await self._safe_answer(message, self.strings("sync_sent") if ok else "Не удалось отправить.")

    @loader.command(alias="serichik")
    async def серичик(self, app: Client, message: types.Message):
        """Пригласить человека в серию (кнопка доступна всем)"""
        if message.chat.type != enums.ChatType.PRIVATE:
            return await self._safe_answer(message, self.strings("only_private"))

        peer_id = str(message.chat.id)
        series = self._series()

        if peer_id in series and series[peer_id].get("active"):
            return await self._safe_answer(
                message,
                "Серия уже активна. Используй .серичик_pair для синхронизации."
            )

        # Shizu: фиксированный callback_data через поле `data` —
        # пресс доходит до callback_handlers модуля (serichik_accept_callback_handler).
        # Ключ `callback` со строкой нельзя: он регистрируется в _custom_map без
        # _callback и падает с KeyError: '_callback'.
        markup = [
            [{"text": "🔥 Принять серию", "data": f"serichik_accept:{peer_id}"}]
        ]

        await self._safe_answer(
            message,
            "🔥 <b>Приглашение в серию</b>\nНажми кнопку, чтобы начать.",
            reply_markup=markup,
        )

    async def serichik_accept_callback_handler(self, call: types.CallbackQuery):
        """Обработка кнопки «Принять серию» (доступна всем)"""
        if not call.data or not call.data.startswith("serichik_accept:"):
            return

        peer_id = call.data.split(":")[1]
        series = self._series()
        app = self.app

        try:
            chat = await app.get_chat(int(peer_id))
            name = utils.get_display_name(chat) or peer_id
        except Exception:
            name = peer_id

        series[peer_id] = {
            "name": name,
            "started": datetime.now().isoformat(),
            "last_active": today().isoformat(),
            "days": 1,
            "credits": 10,
            "active": True,
            "paired": peer_id in self._pairs(),
        }
        self._save_series(series)

        try:
            await call.answer("Серия начата!", show_alert=True)
        except Exception:
            pass

        try:
            await call.message.edit_text("🔥 <b>Серия начата!</b>")
        except Exception:
            pass

        await self._send_with_effect(
            app,
            int(peer_id),
            "🔥 Серия с тобой начата!",
            FIRE_EFFECT_ID,
        )

    @loader.command(alias="series")
    async def серии(self, app: Client, message: types.Message):
        """Показать список всех активных серий"""
        series = self._series()
        active = {k: v for k, v in series.items() if v.get("active", True)}

        if not active:
            return await self._safe_answer(message, self.strings("no_series"))

        lines = []
        pairs = self._pairs()
        for pid, data in active.items():
            last = data.get("last_active", "?")
            lines.append(
                self.strings("series_item").format(
                    name=data.get("name", pid),
                    days=data.get("days", 1),
                    credits=data.get("credits", 0),
                    last=last,
                    paired="✅" if pid in pairs else "❌",
                )
            )

        await self._safe_answer(message, self.strings("status").format(list="\n".join(lines)))

    @loader.command(alias="leave")
    async def покинуть(self, app: Client, message: types.Message):
        """Выйти из текущей серии с собеседником"""
        if message.chat.type != enums.ChatType.PRIVATE:
            return await self._safe_answer(message, "Только в личке.")

        peer_id = str(message.chat.id)
        series = self._series()

        if peer_id not in series:
            return await self._safe_answer(message, self.strings("no_series"))

        name = series[peer_id].get("name", peer_id)
        series[peer_id]["active"] = False
        self._save_series(series)

        pairs = self._pairs()
        pairs.pop(peer_id, None)
        self._save_pairs(pairs)

        await self._send_with_effect(
            app, message.chat.id, self.strings("left").format(name=name), BROKEN_HEART_EFFECT_ID
        )

    @loader.watcher()
    async def serichik_watcher(self, app: Client, message: types.Message):
        if message.chat.type != enums.ChatType.PRIVATE:
            return

        text = message.text or message.caption or ""
        peer_id = str(message.chat.id)

        if text.startswith("🔥SERI:"):
            pairs = self._pairs()
            if peer_id not in pairs:
                return

            secret = pairs[peer_id]
            try:
                parts = text.split("|")
                if parts[0] == "🔥SERI:v1":
                    data_part = "|".join(parts[1:-1])
                    sig = parts[-1].replace("sig=", "")
                    if verify_sig(secret, data_part, sig):
                        kv = dict(x.split("=") for x in data_part.split("|"))
                        series = self._series()
                        if peer_id not in series:
                            series[peer_id] = {"name": peer_id, "active": True, "paired": True}

                        series[peer_id].update({
                            "days": int(kv.get("days", 1)),
                            "credits": int(kv.get("credits", 0)),
                            "last_active": kv.get("last", today().isoformat()),
                            "active": True,
                            "paired": True,
                        })
                        self._save_series(series)
            except Exception:
                pass
            return

        if message.from_user and message.from_user.is_self:
            if not self.config.get("disable_security", False):
                return

        series = self._series()
        if peer_id not in series or not series[peer_id].get("active"):
            return

        data = series[peer_id]
        try:
            last = date.fromisoformat(data.get("last_active", today().isoformat()))
        except Exception:
            last = today()

        current = today()
        delta = (current - last).days

        if delta == 0:
            return

        name = data.get("name", "другом")

        if delta == 1:
            data["days"] = data.get("days", 1) + 1
            points = self._calc_points(data["days"])
            data["credits"] = data.get("credits", 0) + points
            data["last_active"] = current.isoformat()
            self._save_series(series)

            await self._send_with_effect(
                app,
                message.chat.id,
                self.strings("streak_up").format(
                    name=name,
                    days=data["days"],
                    points=points,
                    credits=data["credits"],
                ),
                FIRE_EFFECT_ID,
            )

            if peer_id in self._pairs():
                await self._send_sync(app, peer_id)

        elif delta > 1:
            data["active"] = False
            data["days"] = 0
            self._save_series(series)

            await self._send_with_effect(
                app,
                message.chat.id,
                self.strings("streak_broken").format(name=name),
                BROKEN_HEART_EFFECT_ID,
            )

    @loader.command()
    async def серичикhelp(self, app: Client, message: types.Message):
        """Показать справку по модулю Серичик"""
        await self._safe_answer(message, self.strings("help"))
        
