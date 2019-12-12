import os

# https://stackoverflow.com/questions/431684/how-do-i-change-directory-cd-in-python
class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()

        try:
            os.chdir(self.newPath)
        except OSError:
            # make the directory and then chdir
            os.makedirs(self.newPath)
            os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)