# ---------------------------------------------------------------------------------
#  ▄▄▄▄▄▄▄ ▄▄▄   ▄▄▄    ▄▄▄      ▄▄▄   ▄▄▄▄▄   ▄▄▄▄▄▄    ▄▄▄▄▄▄▄
# █████▀▀▀ ███   ███    ████▄  ▄████ ▄███████▄ ███▀▀██▄ █████▀▀▀
#  ▀████▄  █████████    ███▀████▀███ ███   ███ ███  ███  ▀████▄
#    ▀████ ███▀▀▀███    ███  ▀▀  ███ ███▄▄▄███ ███  ███    ▀████
# ███████▀ ███   ███ ██ ███      ███  ▀█████▀  ██████▀  ███████▀
# ---------------------------------------------------------------------------------
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html
# 👤 https://t.me/SH_Mods
# ---------------------------------------------------------------------------------
# banner: https://github.com/Nyashka17/SHMods/blob/master/assets/SH.MODS.jpg?raw=true
# meta developer: @SH_Mods
# scope: heroku_only
# Commands: giauto, gitime
# ---------------------------------------------------------------------------------
__version__ = (1, 0, 2)

import logging
from html import escape
from herokutl.tl.types import Message
from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class GuildMod(loader.Module):
    """Автоматизация действий в гильдии"""

    strings = {
        "name": "Guild",
        "start": "Automation of actions in guild started.",
        "stop": "Automation of actions in guild stopped.",
    }

    strings_ru = {
        "start": "Автоматизация действий в гильдии запущена.",
        "stop": "Автоматизация действий в гильдии остановлена.",
    }

    def __init__(self):
        self._giauto_running = False

    async def giautocmd(self, message: Message):
        """Переключить авто-режим: 1-й запуск — старт, 2-й — стоп"""
        self._giauto_running = not self._giauto_running

        if self._giauto_running:
            status = self.strings("start")
            icon = "▶️"
            title = "Started"
        else:
            status = self.strings("stop")
            icon = "⏹"
            title = "Stopped"

        html = (
            f"<h2>{icon} Guild</h2>"
            f"<p><b>{escape(title)}:</b> {escape(status)}</p>"
            "<footer>Auto mode toggled</footer>"
        )
        await utils.answer(message, rich_message=html)

    async def on_unload(self):
        self._giauto_running = False
