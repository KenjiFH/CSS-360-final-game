from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pygame'],
    'includes': ['math', 'os', 'heapq', 'random'],
    'resources': ['resources'],
}

setup(
    app=APP,
    name='LionArena',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)