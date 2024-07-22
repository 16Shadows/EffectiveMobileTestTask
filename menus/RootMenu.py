from __future__ import annotations

from typing import Self

from modules.menu.static import StaticMenuEntry
from modules.menu.core import MenuBase, MenuEntryBase, MenuHostBase

from modules.books import BookStorage

from modules.menu.input import converter_string, converter_int, validator_string_not_empty, validator_always

from menus.BooksListMenu import LibraryManagerBooksListMenu
from menus.SearchMenu import LibraryManagerSearchMenu
from menus.BookMenu import BookMenu

class LibraryManagerRootMenu(MenuBase):
    '''корневое меню приложения'''
    def __init__(self, storage: BookStorage) -> None:
        self._storage = storage
        self._entries : list[MenuEntryBase] = [
            StaticMenuEntry('Добавить книгу', self.__add_book),
            StaticMenuEntry('Найти книгу по ID', self.__find_book_by_id),
            StaticMenuEntry('Список книг', lambda host: host.push(LibraryManagerBooksListMenu(self._storage, self._storage.all_books()))),
            StaticMenuEntry('Поиск по книгам', lambda host: host.push(LibraryManagerSearchMenu(self._storage))),
            StaticMenuEntry('Выход', lambda host: host.pop())
        ]

    @MenuBase.text.getter
    def text(self: Self) -> str:
        return 'Выберите действие:'
    
    @MenuBase.entries.getter
    def entries(self: Self) -> list[MenuEntryBase]:
        return self._entries
    
    def __add_book(self: Self, host: MenuHostBase) -> None:
        '''Добавить книгу'''
        #считать параметры книги, досрочно прерывая добавление, если был получен None
        title = host.input('Введите название книги (или нажмите Ctrl + C для отмены): ', converter_string, validator_string_not_empty, 'Название должно быть непустой строкой!')
        if title is None:
            return
        author = host.input('Введите автора книги (или нажмите Ctrl + C для отмены): ', converter_string, validator_string_not_empty, 'Автор должен быть непустой строкой!')
        if author is None:
            return
        year = host.input('Введите год издания книги (или нажмите Ctrl + C для отмены): ', converter_int, validator_always, 'Год издания должен быть целым числом!')
        if year is None:
            return
        self._storage.new_book(title, author, year)

    def __find_book_by_id(self: Self, host: MenuHostBase) -> None:
        '''Открыть меню управления книгой по ID'''
        #считать ID книги (если книги есть), а затем открыть меню книги с этим ID
        if self._storage.books_count < 1:
            host.message('Книг нет')
            return
        id = host.input('Введите ID книги (или нажмите Ctrl + C для отмены): ', converter_int, self._storage.has_book_with_id, 'Книги с таким ID не существует!')
        if id is None:
            return
        host.push(BookMenu(self._storage, self._storage.find_book_by_id(id)))