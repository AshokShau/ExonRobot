from envparse import env

from Exon import LOGGER

DEFAULTS = {
    "LOAD_MODULES": True,
}


def get_str_key(name, required=False):
    default = DEFAULTS.get(name)
    if not (data := env.str(name, default=default)) and not required:
        LOGGER.warn(f"No str key: {name}")
        return None
    if data:
        return data
    LOGGER.critical(f"No str key: {name}")
    sys.exit(2)


def get_int_key(name, required=False):
    default = DEFAULTS.get(name)
    if not (data := env.int(name, default=default)) and not required:
        LOGGER.warn(f"No int key: {name}")
        return None
    if data:
        return data
    LOGGER.critical(f"No int key: {name}")
    sys.exit(2)
