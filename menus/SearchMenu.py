from __future__ import annotations

from typing import Self

from modules.menu.static import StaticMenuEntry, MenuEntryBack
from modules.menu.core import MenuBase, MenuEntryBase, MenuHostBase

from modules.books import BookStorage, DefaultBookSearchCondition

from modules.menu.input import converter_string, converter_int, validator_string_not_empty, validator_always

import re

from menus.BooksListMenu import LibraryManagerBooksListMenu

class LibraryManagerSearchMenu(MenuBase):
    '''Меню для поиска по книгами'''
    def __init__(self, storage: BookStorage) -> None:
        self._storage = storage
        self._author = None
        self._title = None
        self._year = None

    @MenuBase.text.getter
    def text(self: Self) -> str:
        res : str = 'Поиск по книгам\n'
        
        #Отобразить текущее условие поиска по автору, если указано
        if self._author is not None:
            res += f'По автору: {self._author}\n'

        #Отобразить текущее условие поиска по названию, если указано
        if self._title is not None:
            res += f'По названию: {self._title}\n'

        #Отобразить текущее условие поиска по году публикации, если указано
        if self._year is not None:
            res += f'По году: {self._year}\n'

        return res.strip()
    
    @MenuBase.entries.getter
    def entries(self: Self) -> list[MenuEntryBase]:
        entries : list[MenuEntryBase] = []

        #Добавить опцию задать поиск по автору и очистить, если уже задан
        entries.append(StaticMenuEntry('Задать поиск по автору', self._set_by_author))
        if self._author is not None:
            entries.append(StaticMenuEntry('Очистить поиск по автору', self._clear_by_author))

        #Добавить опцию задать поиск по названию и очистить, если уже задан
        entries.append(StaticMenuEntry('Задать поиск по названию', self._set_by_author))
        if self._title is not None:
            entries.append(StaticMenuEntry('Очистить поиск по названию', self._clear_by_author))

        #Добавить опцию задать поиск по году публикации и очистить, если уже задан
        entries.append(StaticMenuEntry('Задать поиск по году публикации', self._set_by_year))
        if self._year is not None:
            entries.append(StaticMenuEntry('Очистить поиск по году публикации', self._clear_by_year))

        #Добавить опцию выполнить и вернуться
        entries.append(StaticMenuEntry('Выполнть поиск', self._do_search))
        entries.append(MenuEntryBack())

        return entries

    def _set_by_author(self: Self, host: MenuHostBase) -> None:
        '''выставить условие поиска по автору'''
        self._author = host.input('Введите частичное имя автора (или нажмите Ctrl + C для отмены): ', converter_string, validator_string_not_empty, 'Имя автора должно быть не пустой строкой!')

    def _clear_by_author(self: Self, _: MenuHostBase) -> None:
        '''удалить условие поиска по автору'''
        self._author = None

    def _set_by_title(self: Self, host: MenuHostBase) -> None:
        '''выставить условие поиска по заголовку'''
        self._title = host.input('Введите частичное название книги (или нажмите Ctrl + C для отмены): ', converter_string, validator_string_not_empty, 'Название книги должно быть не пустой строкой!')

    def _clear_by_title(self: Self, _: MenuHostBase) -> None:
        '''удалить условие поиска по заголовку'''
        self._title = None

    def _set_by_year(self: Self, host: MenuHostBase) -> None:
        '''выставить условие поиска по году публикации'''
        self._year = host.input('Введите год публикации (или нажмите Ctrl + C для отмены): ', converter_int, validator_always, 'Год публикации должен быть целым числом!')

    def _clear_by_year(self: Self, _: MenuHostBase) -> None:
        '''удалить условие поиска по году публикации'''
        self._year = None

    def _do_search(self: Self, host: MenuHostBase) -> None:
        '''выполнить поиск'''

        #создаём условие и выставляем на нём параметры, генерируем регулярные выражения для поиска подстроки 
        cond = DefaultBookSearchCondition()

        if self._author is not None:
            cond.by_author(re.compile(f'.*{re.escape(self._author)}.*'))

        if self._title is not None:
            cond.by_title(re.compile(f'.*{re.escape(self._title)}.*'))

        if self._year is not None:
            cond.by_year(self._year)

        #Создаём меню списка книг на основе результата поиска
        host.push(LibraryManagerBooksListMenu(self._storage, self._storage.find_books(cond)))