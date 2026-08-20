'''set up settings cache'''
import time
from datetime import datetime

from app.admin.repositories.admin_repositories import SettingRepository

CACHE_TTL = 30

_cache = {
    "settings": {},
    "loaded_at": 0,
    "loaded_datetime": None,
}

def load_settings():
    '''Load all settings in memory'''

    rows = SettingRepository.list_all('active')

    _cache["settings"] = {
        row["name"]: row["value"]
        for row in rows
    }

    _cache["loaded_at"] = time.monotonic()
    _cache["loaded_datetime"] = datetime.now()


def get_setting(name, default=None):
    '''get a specific setting'''
    cache_age = time.monotonic() - _cache["loaded_at"]

    if cache_age > CACHE_TTL:
        load_settings()

    return _cache["settings"].get(name, default)

def get_cache_last_loaded():
    '''Get the time that the settings were last loaded from the db'''
    return _cache["loaded_datetime"]
