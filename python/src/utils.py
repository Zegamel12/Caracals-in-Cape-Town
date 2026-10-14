# This code was mainly written by: Jerom den Rooijen. See the commit history for a detailed contribution record.

from python.src.config import base


def clear_outputs():
    """Delete all data within step_dirs"""
    # Source: https://docs.python.org/3/library/pathlib.html#pathlib.Path.rglob
    for folder in [base / "python" / "step_dirs", base / "python" / "output"]:
        for file in folder.rglob("*"):
            if file.is_file() and file.name != ".gitkeep":
                print(f"Deleting {file}")
                file.unlink()


if __name__ == "__main__":
    clear_outputs()