
import json

with open("lang/en.json", encoding="utf-8") as f:
    _translations = json.load(f)

def t(key: str, **kwargs):
    parts = key.split(".")
    value = _translations
    try:
        for part in parts:
            value = value[part]
        if isinstance(value, str) and kwargs:
            return value.format(**kwargs)
        return value
    except (KeyError, TypeError):
        return key
