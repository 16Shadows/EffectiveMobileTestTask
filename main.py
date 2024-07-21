from __future__ import annotations

import traceback

from typing import Self

from modules.menu.static import StaticMenuEntry, MenuEntryBack
from modules.menu.core import MenuBase, MenuEntryBase, MenuHostBase
from modules.menu.hosts import SimpleConsoleMenuHost

from modules.books import BookStorage, Book, BookStatus, BookSearchCondition

from modules.input import input_validated, converter_string, converter_int, validator_string_not_empty, validator_always, validator_int_range

import math
import re

def book_status_to_string(status : BookStatus) -> str:
    if status == BookStatus.in_storage:
        return 'В наличии'
    else:
        return 'Выдана'

class LibraryManagerRootMenu(MenuBase):
    def __init__(self, storage: BookStorage) -> None:
        self._storage = storage
        self._entries : list[MenuEntryBase] = [
            StaticMenuEntry('Добавить книгу', self.__add_book),
            StaticMenuEntry('Удалить книгу по ID', self.__remove_book_by_id),
            StaticMenuEntry('Вывести все книги', lambda host: host.push(LibraryManagerBooksList(self._storage.all_books()))),
            StaticMenuEntry('Поиск по книгам', lambda host: host.push(LibraryManagerSearchMenu(self._storage))),
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
        self._storage.new_book(title, author, year)

    def __remove_book_by_id(self: Self, _: MenuHostBase) -> None:
        if self._storage.books_count < 1:
            print('Книг нет')
            return
        id = input_validated('Введите ID книги: ', converter_int, self._storage.has_book_with_id, 'Книги с таким ID не существует!')
        if id is None:
            return
        self._storage.remove_book(self._storage.find_book_by_id(id))

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
        
class LibraryManagerSearchMenu(MenuBase):
    def __init__(self, storage: BookStorage) -> None:
        self._storage = storage
        self._author = None
        self._title = None
        self._year = None

    @MenuBase.text.getter
    def text(self: Self) -> str:
        res : str = 'Поиск по книгам\n'
        
        if self._author is not None:
            res += f'По автору: {self._author}\n'

        if self._title is not None:
            res += f'По названию: {self._title}\n'

        if self._year is not None:
            res += f'По году: {self._year}\n'

        return res.strip()
    
    @MenuBase.entries.getter
    def entries(self: Self) -> list[MenuEntryBase]:
        entries : list[MenuEntryBase] = []

        entries.append(StaticMenuEntry('Задать поиск по автору', self._set_by_author))
        if self._author is not None:
            entries.append(StaticMenuEntry('Очистить поиск по автору', self._clear_by_author))

        entries.append(StaticMenuEntry('Задать поиск по названию', self._set_by_author))
        if self._title is not None:
            entries.append(StaticMenuEntry('Очистить поиск по названию', self._clear_by_author))

        entries.append(StaticMenuEntry('Задать поиск по году публикации', self._set_by_year))
        if self._year is not None:
            entries.append(StaticMenuEntry('Очистить поиск по году публикации', self._clear_by_year))

        entries.append(StaticMenuEntry('Выполнть поиск', self._do_search))
        entries.append(MenuEntryBack())

        return entries

    def _set_by_author(self: Self, _: MenuHostBase) -> None:
        self._author = input_validated('Введите частичное имя автора: ', converter_string, validator_string_not_empty, 'Имя автора должно быть не пустой строкой!')

    def _clear_by_author(self: Self, _: MenuHostBase) -> None:
        self._author = None

    def _set_by_title(self: Self, _: MenuHostBase) -> None:
        self._title = input_validated('Введите частичное название книги: ', converter_string, validator_string_not_empty, 'Название книги должно быть не пустой строкой!')

    def _clear_by_title(self: Self, _: MenuHostBase) -> None:
        self._title = None

    def _set_by_year(self: Self, _: MenuHostBase) -> None:
        self._year = input_validated('Введите год публикации: ', converter_int, validator_always, 'Год публикации должен быть целым числом!')

    def _clear_by_year(self: Self, _: MenuHostBase) -> None:
        self._year = None

    def _do_search(self: Self, host: MenuHostBase) -> None:
        cond = BookSearchCondition()

        if self._author is not None:
            cond.by_author(re.compile(f'.*{re.escape(self._author)}.*'))

        if self._title is not None:
            cond.by_title(re.compile(f'.*{re.escape(self._title)}.*'))

        if self._year is not None:
            cond.by_year(self._year)

        host.push(LibraryManagerBooksList(self._storage.find_books(cond)))

host = SimpleConsoleMenuHost()

db_path = './database.json'

try:
    storage = BookStorage.load_from_disk(db_path)
except Exception:
    traceback.print_exc()
    print()
    print('Не удалось загрузить БД с диска, создаём новую БД.')
    storage = BookStorage(db_path)

try:
    host.run(LibraryManagerRootMenu(storage))
finally:
    storage.save_to_disk()