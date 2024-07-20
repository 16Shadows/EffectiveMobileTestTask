from __future__ import annotations

from typing import Self

from modules.menu.static import StaticMenuEntry, MenuEntryBack
from modules.menu.core import MenuBase, MenuEntryBase, MenuHostBase
from modules.menu.hosts import SimpleConsoleMenuHost

from modules.books import BookStorage, Book, BookStatus

from modules.input import input_validated, converter_string, converter_int, validator_string_not_empty, validator_always, validator_int_range

import math

def book_status_to_string(status : BookStatus) -> str:
    if status == BookStatus.in_storage:
        return 'В наличии'
    else:
        return 'Выдана'

class LibraryManagerRootMenu(MenuBase):
    def __init__(self) -> None:
        self.storage = BookStorage()
        self._entries : list[MenuEntryBase] = [
            StaticMenuEntry('Добавить книгу', self.__add_book),
            StaticMenuEntry('Удалить книгу по ID', self.__remove_book_by_id),
            StaticMenuEntry('Вывести все книги', lambda host: host.push(LibraryManagerBooksList(self.storage.all_books()))),
            StaticMenuEntry('Выход', lambda host: host.pop())
        ]

    @MenuBase.text.getter
    def text(self: Self) -> str:
        return 'Выберите действие:'
    
    @MenuBase.entries.getter
    def entries(self: Self) -> list[MenuEntryBase]:
        return self._entries
    
    def __add_book(self: Self, _: MenuHostBase) -> None:
        title = input_validated('Введите название книги: ', converter_string, validator_string_not_empty, 'Название должно быть непустой строкой!')
        if title is None:
            return
        author = input_validated('Введите автора книги: ', converter_string, validator_string_not_empty, 'Автор должен быть непустой строкой!')
        if author is None:
            return
        year = input_validated('Введите год издания книги: ', converter_int, validator_always, 'Год издания должен быть целым числом!')
        if year is None:
            return
        self.storage.new_book(title, author, year)

    def __remove_book_by_id(self: Self, _: MenuHostBase) -> None:
        if self.storage.books_count < 1:
            print('Книг нет')
            return
        id = input_validated('Введите ID книги: ', converter_int, self.storage.has_book_with_id, 'Книги с таким ID не существует!')
        if id is None:
            return
        self.storage.remove_book(self.storage.find_book_by_id(id))

class LibraryManagerBooksList(MenuBase):
    def __init__(self, books : list[Book]) -> None:
        self._books = books
        self.__currentPage = 0
        self._pageSize = 10

    @MenuBase.text.getter
    def text(self: Self) -> str:
        if len(self._books) < 1:
            return 'Нет книг.'
        result : str = 'ID - Название - Автор - Год Издания - Статус\n'
        for i in range(self._current_page * self._pageSize, min((self._current_page + 1) * self._pageSize, len(self._books))):
            book = self._books[i]
            result += f'{book.id} - {book.title} - {book.author} - {book.year} - {book_status_to_string(book.status)}\n'
        result += f'Страница {self._current_page + 1}/{ self._page_count }'
        return result

    @MenuBase.entries.getter
    def entries(self: Self) -> list[MenuEntryBase]:
        entries : list[MenuEntryBase] = []

        if (self._current_page + 1) * self._pageSize < len(self._books):
            entries.append(StaticMenuEntry('Следующая страница', self.__next_page))

        if self._current_page > 0:
            entries.append(StaticMenuEntry('Предыдущая страница', self.__previous_page))

        if len (self._books) > 0:
            entries.append(StaticMenuEntry('Изменить размер страницы', self.__change_page_size))

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
        

host = SimpleConsoleMenuHost()
host.run(LibraryManagerRootMenu())