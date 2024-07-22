from __future__ import annotations

from typing import Self

from modules.menu.static import StaticMenuEntry, MenuEntryBack
from modules.menu.core import MenuBase, MenuEntryBase, MenuHostBase

from modules.books import BookStorage, BookSearchCondition

from modules.input import input_validated, converter_string, converter_int, validator_string_not_empty, validator_always

import re

from menus.BooksListMenu import LibraryManagerBooksListMenu

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

        host.push(LibraryManagerBooksListMenu(self._storage, self._storage.find_books(cond)))