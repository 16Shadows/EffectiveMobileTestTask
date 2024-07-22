from __future__ import annotations

import traceback

from modules.menu.hosts import SimpleConsoleMenuHost
from modules.books import BookStorage
from menus.RootMenu import LibraryManagerRootMenu

host = SimpleConsoleMenuHost()

db_path = './database.json'

try:
    storage = BookStorage.load_from_disk(db_path)
except Exception:
    traceback.print_exc()
    print()
    print('Не удалось загрузить БД с диска, создаём новую БД.')
    storage = BookStorage(db_path)

def on_exit(*args: object)-> None:
    storage.save_to_disk()

import signal
signal.signal(signal.SIGTERM, on_exit)
signal.signal(signal.SIGABRT, on_exit)

try:
    host.run(LibraryManagerRootMenu(storage))
finally:
    on_exit()