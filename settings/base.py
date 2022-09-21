import os


def get_parent(path, levels=1):
    start = path
    for i in range(levels):
        start = os.path.dirname(start)
    return start


_basedir = get_parent(os.path.abspath(os.path.dirname(__file__)))

DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'currencies.db')

PAGE_SIZE = 24

STATIC_PATH = os.path.join(_basedir, 'static')

del os

