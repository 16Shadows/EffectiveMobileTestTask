from __future__ import annotations

from typing import Self

from modules.menu.static import StaticMenuEntry
from modules.menu.core import MenuBase, MenuEntryBase, MenuHostBase

from modules.books import BookStorage

from modules.input import input_validated, converter_string, converter_int, validator_string_not_empty, validator_always

from menus.BooksListMenu import LibraryManagerBooksListMenu
from menus.SearchMenu import LibraryManagerSearchMenu
from menus.BookMenu import BookMenu

class LibraryManagerRootMenu(MenuBase):
    def __init__(self, storage: BookStorage) -> None:
        self._storage = storage
        self._entries : list[MenuEntryBase] = [
            StaticMenuEntry('Добавить книгу', self.__add_book),
            StaticMenuEntry('Найти книгу по ID', self.__find_book_by_id),
            StaticMenuEntry('Список книг', lambda host: host.push(LibraryManagerBooksListMenu(self._storage.all_books()))),
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

    def __find_book_by_id(self: Self, host: MenuHostBase) -> None:
        if self._storage.books_count < 1:
            print('Книг нет')
            return
        id = input_validated('Введите ID книги: ', converter_int, self._storage.has_book_with_id, 'Книги с таким ID не существует!')
        if id is None:
            return
        host.push(BookMenu(self._storage, self._storage.find_book_by_id(id)))