import hashlib
import hmac
import secrets
from datetime import datetime, date
from typing import Dict, Any, Optional

from pyrogram import Client, types, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .. import loader, utils


# Эффекты из твоего бота
FIRE_EFFECT_ID = 5104841245755180586      # 🔥
BROKEN_HEART_EFFECT_ID = 5123265598893064880  # 💔


def today() -> date:
    return datetime.now().date()


def make_sig(secret: str, payload: str) -> str:
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()[:16]


def verify_sig(secret: str, payload: str, sig: str) -> bool:
    expected = make_sig(secret, payload)
    return hmac.compare_digest(expected, sig)


@loader.module(name="Серичик", author="SHMods", version=1.0.0)
class Serichik(loader.Module):
    """Огонёк / серия дней с синхронизацией и эффектами"""

    strings = {
        "only_private": "<emoji id=5807626765874499116>🚫</emoji> <b>Только в личных чатах.</b>",
        "already_paired": "<emoji id=6334541265077536138>❔</emoji> <b>Уже спарены с этим человеком.</b>",
        "pair_created": (
            "<emoji id=5104841245755180586>🔥</emoji> <b>Код для синхронизации создан</b>\n\n"
            "Отправь другу этот код:\n<code>{code}</code>\n\n"
            "Он должен написать:\n<code>.серичик_join {code}</code>"
        ),
        "join_success": (
            "<emoji id=5104841245755180586>🔥</emoji> <b>Успешно спарены!</b>\n"
            "Теперь серии будут синхронизироваться автоматически."
        ),
        "join_invalid": "<emoji id=5807626765874499116>🚫</emoji> <b>Неверный или устаревший код.</b>",
        "not_paired": "<emoji id=6334541265077536138>❔</emoji> <b>Сначала нужно спариться (.серичик_pair).</b>",
        "sync_sent": "<emoji id=5104841245755180586>🔥</emoji> <b>Состояние отправлено другу.</b>",
        "status": (
            "<emoji id=5104841245755180586>🔥</emoji> <b>Твои серии:</b>\n\n{list}"
        ),
        "series_item": (
            "• <b>{name}</b> — <code>{days}</code> дн. | кредиты: <code>{credits}</code>\n"
            "  Последняя: {last} | paired: {paired}"
        ),
        "left": "<emoji id=6334551070487873258>✂️</emoji> <b>Вышел из серии с {name}.</b>",
        "no_series": "<emoji id=6334541265077536138>❔</emoji> <b>Нет активных серий.</b>",
        "streak_up": (
            "<emoji id=5104841245755180586>🔥</emoji> <b>Серия с {name} продолжается!</b>\n"
            "День <b>{days}</b> • +{points} кредитов • Всего: <code>{credits}</code>"
        ),
        "streak_broken": (
            "<emoji id=5123265598893064880>💔</emoji> <b>Серия с {name} сгорела...</b>\n"
            "Прошло больше одного дня без сообщений."
        ),
        "help": (
            "<emoji id=5104841245755180586>🔥</emoji> <b>Серичик v1.2</b>\n\n"
            "<b>Основные:</b>\n"
            "• <code>.серичик</code> — пригласить (кнопка)\n"
            "• <code>.серии</code> — список серий\n"
            "• <code>.покинуть</code> — выйти из серии\n\n"
            "<b>Синхронизация:</b>\n"
            "• <code>.серичик_pair</code> — создать одноразовый код\n"
            "• <code>.серичик_join КОД</code> — принять код\n"
            "• <code>.серичик_sync</code> — принудительно синхронизировать\n\n"
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

    async def _send_with_effect(self, app: Client, chat_id: int, text: str, effect_id: int = None):
        """Пытается отправить сообщение с эффектом (если поддерживается)"""
        try:
            # Разные варианты названий параметра в разных форках Pyrogram
            kwargs = {"chat_id": chat_id, "text": text, "disable_notification": False}
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
            # Фоллбек без эффекта
            try:
                return await app.send_message(chat_id, text)
            except Exception:
                return None

    # ====================== ПАРИНГ ======================

    @loader.command(alias="serichik_pair")
    async def серичик_pair(self, app: Client, message: types.Message):
        if message.chat.type != enums.ChatType.PRIVATE:
            return await utils.answer(message, self.strings("only_private"))

        peer_id = str(message.chat.id)
        if peer_id in self._pairs():
            return await utils.answer(message, self.strings("already_paired"))

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

        await utils.answer(message, self.strings("pair_created").format(code=code))

    @loader.command(alias="serichik_join")
    async def серичик_join(self, app: Client, message: types.Message):
        args = utils.get_args_raw(message)
        if not args or ":" not in args:
            return await utils.answer(message, "Использование: <code>.серичик_join ID:XXXX</code>")

        code = args.strip()
        try:
            creator_id, secret = code.split(":", 1)
            creator_id = int(creator_id)
        except Exception:
            return await utils.answer(message, self.strings("join_invalid"))

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

        await self._send_with_effect(
            app, message.chat.id,
            self.strings("join_success"),
            FIRE_EFFECT_ID
        )

        # Уведомляем создателя
        try:
            await app.send_message(creator_id, f"🔥SERI:PAIR_OK|{self.tg_id}|{secret}")
        except Exception:
            pass

    # ====================== СИНХРОНИЗАЦИЯ ======================

    def _build_sync_packet(self, peer_id: str) -> Optional[str]:
        series = self._series()
        pairs = self._pairs()
        if peer_id not in series or peer_id not in pairs:
            return None

        data = series[peer_id]
        secret = pairs[peer_id]
        payload = f"days={data.get('days', 1)}|credits={data.get('credits', 0)}|last={data.get('last_active', today().isoformat())}"
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
        if message.chat.type != enums.ChatType.PRIVATE:
            return await utils.answer(message, self.strings("only_private"))

        peer_id = str(message.chat.id)
        if peer_id not in self._pairs():
            return await utils.answer(message, self.strings("not_paired"))

        ok = await self._send_sync(app, peer_id)
        await utils.answer(message, self.strings("sync_sent") if ok else "Не удалось отправить.")

    # ====================== ОСНОВНЫЕ КОМАНДЫ ======================

    @loader.command(alias="serichik")
    async def серичик(self, app: Client, message: types.Message):
        if message.chat.type != enums.ChatType.PRIVATE:
            return await utils.answer(message, self.strings("only_private"))

        peer_id = str(message.chat.id)
        series = self._series()

        if peer_id in series and series[peer_id].get("active"):
            return await utils.answer(message, "Серия уже активна. Используй .серичик_pair для синхронизации.")

        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔥 Принять серию", callback_data=f"serichik_accept:{peer_id}")
        ]])

        await utils.answer(
            message,
            "<emoji id=5104841245755180586>🔥</emoji> <b>Приглашение в серию</b>\nНажми кнопку, чтобы начать.",
            reply_markup=kb
        )

    async def serichik_accept_callback_handler(self, app: Client, call: types.CallbackQuery):
        if not call.data.startswith("serichik_accept:"):
            return
        peer_id = call.data.split(":")[1]

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
            "paired": peer_id in self._pairs(),
        }
        self._save_series(series)

        await call.answer("Серия начата!", show_alert=True)
        try:
            await call.message.edit_text("<emoji id=5104841245755180586>🔥</emoji> <b>Серия начата!</b>")
        except Exception:
            pass

        # Отправляем эффект огонька
        await self._send_with_effect(
            app, int(peer_id),
            f"<emoji id=5104841245755180586>🔥</emoji> Серия с тобой начата!",
            FIRE_EFFECT_ID
        )

    @loader.command(alias="series")
    async def серии(self, app: Client, message: types.Message):
        series = self._series()
        active = {k: v for k, v in series.items() if v.get("active", True)}
        if not active:
            return await utils.answer(message, self.strings("no_series"))

        lines = []
        pairs = self._pairs()
        for pid, data in active.items():
            last = data.get("last_active", "?")
            lines.append(self.strings("series_item").format(
                name=data.get("name", pid),
                days=data.get("days", 1),
                credits=data.get("credits", 0),
                last=last,
                paired="✅" if pid in pairs else "❌"
            ))
        await utils.answer(message, self.strings("status").format(list="\n".join(lines)))

    @loader.command(alias="leave")
    async def покинуть(self, app: Client, message: types.Message):
        peer_id = str(message.chat.id) if message.chat.type == enums.ChatType.PRIVATE else None
        if not peer_id:
            return await utils.answer(message, "Только в личке.")

        series = self._series()
        if peer_id not in series:
            return await utils.answer(message, self.strings("no_series"))

        name = series[peer_id].get("name", peer_id)
        series[peer_id]["active"] = False
        self._save_series(series)

        pairs = self._pairs()
        pairs.pop(peer_id, None)
        self._save_pairs(pairs)

        await self._send_with_effect(
            app, message.chat.id,
            self.strings("left").format(name=name),
            BROKEN_HEART_EFFECT_ID
        )

    # ====================== WATCHER ======================

    @loader.watcher()
    async def serichik_watcher(self, app: Client, message: types.Message):
        if message.chat.type != enums.ChatType.PRIVATE:
            return

        text = message.text or message.caption or ""
        peer_id = str(message.chat.id)

        # Обработка sync-пакетов
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

        # Обычная активность
        if message.from_user and message.from_user.is_self:
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
            # Серия продолжается
            data["days"] = data.get("days", 1) + 1
            points = self._calc_points(data["days"])
            data["credits"] = data.get("credits", 0) + points
            data["last_active"] = current.isoformat()
            self._save_series(series)

            # Красивое уведомление с огоньком
            await self._send_with_effect(
                app, message.chat.id,
                self.strings("streak_up").format(
                    name=name,
                    days=data["days"],
                    points=points,
                    credits=data["credits"]
                ),
                FIRE_EFFECT_ID
            )

            # Синхронизация
            if peer_id in self._pairs():
                await self._send_sync(app, peer_id)

        elif delta > 1:
            # Серия сгорела
            data["active"] = False
            data["days"] = 0
            self._save_series(series)

            await self._send_with_effect(
                app, message.chat.id,
                self.strings("streak_broken").format(name=name),
                BROKEN_HEART_EFFECT_ID
            )

    @loader.command()
    async def серичикhelp(self, app: Client, message: types.Message):
        await utils.answer(message, self.strings("help"))
