#  ▄▄▄▄▄▄▄ ▄▄▄   ▄▄▄    ▄▄▄      ▄▄▄   ▄▄▄▄▄   ▄▄▄▄▄▄    ▄▄▄▄▄▄▄
# █████▀▀▀ ███   ███    ████▄  ▄████ ▄███████▄ ███▀▀██▄ █████▀▀▀
#  ▀████▄  █████████    ███▀████▀███ ███   ███ ███  ███  ▀████▄
#    ▀████ ███▀▀▀███    ███  ▀▀  ███ ███▄▄▄███ ███  ███    ▀████
# ███████▀ ███   ███ ██ ███      ███  ▀█████▀  ██████▀  ███████▀

# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html
# 👤 https://t.me/SH_Mods

# banner: https://github.com/Nyashka17/SHMods/blob/master/assets/SH.INFO.jpg?raw=true
# meta developer: @SH_Mods
__version__ = "1.0.0"

import collections
import random
import json

from .. import loader, utils, version
from pyrogram import types


@loader.module("SH_INFO")
class SH_INFOMod(loader.Module):
    """
    Custom info module + Rich HTML
    """

    strings = {
        "name": "SH_INFO",
    }

    async def cinfocmd(self, message):
        """Кастом-инфо в стиле Rich HTML"""
        await self.inline.form(
            (
                "<blockquote>"
                '<img src="https://raw.githubusercontent.com/Nyashka17/SHMods/refs/heads/main/assets/SH.INFO.jpg"/>'
                "</blockquote>"
            ),
            message,
            rich=True,
        )