from pathlib import Path


def all_modules():
    """
    Returns a sorted list of all modules in this directory.

    This function iterates over all the files in the current directory,
    and returns a sorted list of all the filenames without the .py extension
    and excluding the __init__.py file.
    """
    module_dir = Path(__file__).parent
    return [
        f.stem
        for f in module_dir.glob("*.py")
        if f.is_file() and f.name != "__init__.py"
    ]


ALL_MODULES = sorted(all_modules())
