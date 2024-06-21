import sys
import os


def get_resource_path(relative_path: str, outside: bool = False) -> str:
    """ Returns absolute path. Needed to locate files after packaging PsyTestPro to executeable.
    :param relative_path: str
    :param outside: boolean -> If the file should be located next to the executable and not in the internal dir
    :return:
        absolute_path: str
    """
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
        else:
            return os.path.join(base_path, relative_path)

    except Exception:
        base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
