from __future__ import annotations

from typing import Self, Iterable
from enum import Enum
import re

class BookStatus(Enum):
    in_storage = 0
    '''Книга в наличии'''
    loaned = 1
    '''Книга выдана'''

class Book:
    def __init__(self, id : int, title : str, author : str, year : int) -> None:
        self._id = id
        self.title = title
        '''Название книги'''
        self.author = author
        '''Автор книги'''
        self.year = year
        '''Год публикации книги'''
        self.status = BookStatus.in_storage
        '''Статус книги'''

    @property
    def id(self: Self) -> int:
        '''ID этой книги в БД. Неизменяемое значение.'''
        return self._id

class BookStorage:
    def __init__(self) -> None:
        self._nextId = 0
        self._instances : dict[int, Book] = {}

    def new_book(self: Self, title : str, author : str, year : int) -> Book:
        book = Book(self._nextId, title, author, year)
        self._nextId += 1
        self._instances[book.id] = book
        return book
    
    def remove_book(self: Self, book: Book) -> None:
        del self._instances[book.id]
    
    @property
    def books_count(self: Self) -> int:
        return len(self._instances)

    def all_books(self: Self) -> list[Book]:
        return list(self._instances.values())

    def find_book_by_id(self: Self, id: int) -> Book:
        return self._instances[id]
    
    def has_book_with_id(self: Self, id: int) -> bool:
        return id in self._instances
    
    def find_book(self: Self, condition: BookSearchCondition) -> Iterable[Book]:
        books : list[Book] = []
        for value in self._instances.values():
            if (
                (condition.by_author_pattern is None or condition.by_author_pattern.match(value.author))
                and
                (condition.by_title_pattern is None or condition.by_title_pattern.match(value.title))
                and
                (condition.by_year_pattern is None or condition.by_year_pattern == value.year)
            ):
                books.append(value)
        return books
    
class BookSearchCondition:
    def __init__(self) -> None:
        self.by_title_pattern : re.Pattern[str] | None = None
        self.by_author_pattern : re.Pattern[str] | None = None
        self.by_year_pattern : int | None = None

    def by_title(self: Self, pattern: re.Pattern[str]) -> Self:
        self.by_title_pattern = pattern
        return self
    
    def by_author(self: Self, pattern: re.Pattern[str]) -> Self:
        self.by_author_pattern = pattern
        return self
    
    def by_year(self: Self, year: int) -> Self:
        self.by_year_pattern = year
        return self