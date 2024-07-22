from __future__ import annotations

from typing import Self

from modules.menu.static import StaticMenuEntry, MenuEntryBack
from modules.menu.core import MenuBase, MenuEntryBase, MenuHostBase

from modules.books import Book, BookStatus, BookStorage

def book_status_to_string(status : BookStatus) -> str:
    if status == BookStatus.in_storage:
        return 'В наличии'
    else:
        return 'Выдана'

class BookMenu(MenuBase):
    def __init__(self, storage: BookStorage, book: Book) -> None:
        self._book = book
        self._storage = storage

    @MenuBase.text.getter
    def text(self: Self) -> str:
        return (
            f'ID: {self._book.id}\n' +
            f'Книга: {self._book.title}\n' +
            f'Автор: {self._book.author}\n' +
            f'Год издания: {self._book.year}\n' +
            f'Статус: {book_status_to_string(self._book.status)}'
        )

    @MenuBase.entries.getter
    def entries(self: Self) -> list[MenuEntryBase]:
        ent : list[MenuEntryBase] = []
        
        if (self._book.status == BookStatus.in_storage):
            ent.append(StaticMenuEntry("Изменить статус на 'Выдана'", lambda _: self.__set_book_status(BookStatus.loaned)))
        elif (self._book.status == BookStatus.loaned):
            ent.append(StaticMenuEntry("Изменить статус на 'В наличии'", lambda _: self.__set_book_status(BookStatus.in_storage)))

        ent.append(StaticMenuEntry('Удалить', self.__delete_book))

        ent.append(MenuEntryBack())
        return ent
    
    def __set_book_status(self: Self, status: BookStatus) -> None:
        self._book.status = status

    def __delete_book(self: Self, host: MenuHostBase) -> None:
        self._storage.remove_book(self._book)
        host.pop()