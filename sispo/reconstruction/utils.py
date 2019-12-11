"""Utils module contains functions possibly used by all modules."""

from pathlib import Path

def check_dir(directory, create=True):
    """
    Resolves directory and creates it, if it doesn't existing.
    
    :type directory: Path or str
    :param directory: Directory to be created if not existing

    :type create: bool
    :param create: Set to false if directory should not be created and instead
                   an exception shall be raise
    """
    print(f"Checking if directory {directory} exists...")
    if isinstance(directory, str):
        directory = Path(directory)

    dir_resolved = directory.resolve()

    if not dir_resolved.exists():
        if create:
            print(f"{directory} does not exist. Creating it...")
            Path.mkdir(dir_resolved)
            print("Done!")
        else:
            raise RuntimeError(f"Directory {directory} does not exist!")
    else:
        print("Exists!")

    return dir_resolved