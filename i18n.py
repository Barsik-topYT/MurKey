"""Общий язык интерфейса для MurTools и MurBlocker."""

current_language = "ru"

LANG_OPTIONS = {
    "ru": "Русский",
    "en": "English",
    "zh": "中文",
    "de": "Deutsch",
}

LABEL_TO_CODE = {v: k for k, v in LANG_OPTIONS.items()}
CODE_TO_LABEL = LANG_OPTIONS


def get_language():
    return current_language


def set_language(lang):
    """Устанавливает язык (ru, en, zh, de)."""
    global current_language
    if lang in LANG_OPTIONS:
        current_language = lang


def set_language_from_label(label):
    """Устанавливает язык по подписи в меню («Русский», «English», …)."""
    code = LABEL_TO_CODE.get(label)
    if code:
        set_language(code)
