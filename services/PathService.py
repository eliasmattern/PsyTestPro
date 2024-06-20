import sys
import os


def get_resource_path(relative_path: str, outside: bool = False):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        if outside:
            if sys.platform == "darwin":
                path = os.path.join(base_path, relative_path)
                path = path.replace('/./', '/../', 1)
                path = path.replace('Contents/Frameworks/', '', 1)
                return path
            else:
                relative_path = relative_path.replace('.', '..', 1)
                return os.path.join(base_path, relative_path)

    except Exception:
        base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
