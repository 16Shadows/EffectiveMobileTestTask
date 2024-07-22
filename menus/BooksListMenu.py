from __future__ import annotations

from typing import Self

from modules.menu.static import StaticMenuEntry, MenuEntryBack
from modules.menu.core import MenuBase, MenuEntryBase, MenuHostBase

from modules.books import Book, BookStorage

from modules.input import input_validated, converter_int, validator_int_range

import math

from menus.BookMenu import book_status_to_string, BookMenu

class LibraryManagerBooksListMenu(MenuBase):
    def __init__(self, storage: BookStorage, books : list[Book]) -> None:
        self._books = books
        self._storage = storage
        self.__currentPage = 0
        self._pageSize = 10

    @MenuBase.text.getter
    def text(self: Self) -> str:
        if len(self._books) < 1:
            return 'Нет книг.'
        return f'Страница {self._current_page + 1}/{ self._page_count }'

    @MenuBase.entries.getter
    def entries(self: Self) -> list[MenuEntryBase]:
        entries : list[MenuEntryBase] = []

        if len (self._books) > 0:
            entries.append(StaticMenuEntry('Изменить размер страницы', self.__change_page_size))

        if (self._current_page + 1) * self._pageSize < len(self._books):
            entries.append(StaticMenuEntry('Следующая страница', self.__next_page))

        if self._current_page > 0:
            entries.append(StaticMenuEntry('Предыдущая страница', self.__previous_page))

        for i in range(self._current_page * self._pageSize, min((self._current_page + 1) * self._pageSize, len(self._books))):
            book = self._books[i]
            entries.append(StaticMenuEntry(f'{book.title} ({book.author}) [{book.year} г.] - {book_status_to_string(book.status)} (ID: {book.id})', lambda host: host.push(BookMenu(self._storage, book))))

        entries.append(MenuEntryBack())

        return entries

    def __previous_page(self: Self, _: MenuHostBase) -> None:
        if (self.__currentPage > 0):
            self.__currentPage -= 1

    def __next_page(self: Self, _: MenuHostBase) -> None:
        if self.__currentPage * self._pageSize < len(self._books):
            self.__currentPage += 1
    
    @property
    def _page_count(self: Self) -> int:
        return int(math.ceil(len(self._books) / self._pageSize))

    @property
    def _current_page(self: Self) -> int:
        self.__currentPage = min(self.__currentPage, self._page_count - 1)
        return self.__currentPage

    def __change_page_size(self: Self, _:MenuHostBase) -> None:
        size = input_validated('Введите желаемое число книг на странице:', converter_int, lambda x: validator_int_range(x, 1), 'Количество книг на странице должно быть целым числом не меньше 1!')
        if size is None:
            return
        self._pageSize = size