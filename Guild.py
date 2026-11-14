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
__version__ = (1, 0, 0)

import logging
from herokutl.tl.types import Message
from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class GuildMod(loader.Module):
    """Автоматизация действий в гильдиях"""
    
    strings = {
        "name": "Guild"
        },
    
    strings_ru = {
        }
    
    