from __future__ import annotations

from typing import Self

from modules.menu.static import StaticMenuEntry, MenuEntryBack
from modules.menu.core import MenuBase, MenuEntryBase

from modules.books import Book, BookStatus

def book_status_to_string(status : BookStatus) -> str:
    if status == BookStatus.in_storage:
        return 'В наличии'
    else:
        return 'Выдана'

class BookMenuBase(MenuBase):
    def __init__(self, book: Book) -> None:
        self._book = book
    
    @MenuBase.text.getter
    def text(self: Self) -> str:
        return (
            f'ID: {self._book.id}\n' +
            f'Книга: {self._book.title}\n' +
            f'Автор: {self._book.author}\n' +
            f'Год издания: {self._book.year}\n' +
            f'Статус: {book_status_to_string(self._book.status)}'
        )
    
class BookStatusMenu(BookMenuBase):
    @MenuBase.entries.getter
    def entries(self: Self) -> list[MenuEntryBase]:
        ent : list[MenuEntryBase] = []
        
        if (self._book.status == BookStatus.in_storage):
            ent.append(StaticMenuEntry("Изменить статус на 'Выдано'", lambda _: self.__set_book_status(BookStatus.loaned)))
        elif (self._book.status == BookStatus.loaned):
            ent.append(StaticMenuEntry("Изменить статус на 'В наличии'", lambda _: self.__set_book_status(BookStatus.in_storage)))

        ent.append(MenuEntryBack())
        return ent

    def __set_book_status(self: Self, status: BookStatus):
        self._book.status = status