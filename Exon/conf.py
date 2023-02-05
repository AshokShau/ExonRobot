from envparse import env

from Exon import LOGGER

DEFAULTS = {
    "LOAD_MODULES": True,
}


def get_str_key(name, required=False):
    default = DEFAULTS.get(name)
    if not (data := env.str(name, default=default)) and not required:
        LOGGER.warn("No str key: " + name)
        return None
    if not data:
        LOGGER.critical("No str key: " + name)
        sys.exit(2)
    else:
        return data


def get_int_key(name, required=False):
    default = DEFAULTS.get(name)
    if not (data := env.int(name, default=default)) and not required:
        LOGGER.warn("No int key: " + name)
        return None
    if not data:
        LOGGER.critical("No int key: " + name)
        sys.exit(2)
    else:
        return data
