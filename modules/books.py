from __future__ import annotations

from typing import Self
from enum import Enum
import re
import json

class BookStatus(Enum):
    in_storage = 0
    '''Книга в наличии'''
    loaned = 1
    '''Книга выдана'''

    def serialize(self: Self) -> int:
        return self.value

    @staticmethod
    def deserialize(value: int) -> BookStatus:
        if value == BookStatus.in_storage.value:
            return BookStatus.in_storage
        elif value == BookStatus.loaned.value:
            return BookStatus.loaned
        else:
            raise ValueError

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
    
    def serialize(self: Self) -> dict[object, object]:
        o : dict[object, object] = {}
        o['id'] = self.id
        o['title'] = self.title
        o['author'] = self.author
        o['year'] = self.year
        o['status'] = self.status.serialize()
        return o
    
    @staticmethod
    def deserialize(source: dict[object, object]) -> Book:
        if (not isinstance(source['id'], int) or
            not isinstance(source['title'], str) or
            not isinstance(source['author'], str) or
            not isinstance(source['year'], int) or
            not isinstance(source['status'], int)
        ):
            raise TypeError

        b = Book(source['id'], source['title'], source['author'], source['year'])
        b.status = BookStatus.deserialize(source['status'])
        return b

class BookStorage:
    def __init__(self, storage_file_path: str) -> None:
        self._storage_file_path = storage_file_path
        self._nextId = 0
        self._instances : dict[int, Book] = {}

    def new_book(self: Self, title : str, author : str, year : int) -> Book:
        book = Book(self._nextId, title, author, year)
        self._nextId += 1
        self._instances[book.id] = book
        self.save_to_disk()
        return book
    
    def remove_book(self: Self, book: Book) -> None:
        del self._instances[book.id]
        self.save_to_disk()
    
    @property
    def books_count(self: Self) -> int:
        return len(self._instances)

    def all_books(self: Self) -> list[Book]:
        return list(self._instances.values())

    def find_book_by_id(self: Self, id: int) -> Book:
        return self._instances[id]
    
    def has_book_with_id(self: Self, id: int) -> bool:
        return id in self._instances
    
    def find_books(self: Self, condition: BookSearchCondition) -> list[Book]:
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
    
    def save_to_disk(self: Self) -> None:
        enc = json.JSONEncoder()
        with open(self._storage_file_path, "w") as f:
            f.write(enc.encode(self._serialize()))

    def _serialize(self: Self) -> dict[object, object]:
        o : dict[object, object] = {}
        o['books'] = []
        for book in self._instances.values():
            o['books'].append(book.serialize())
        return o
    
    @staticmethod
    def load_from_disk(path: str) -> BookStorage:
        dec = json.JSONDecoder()

        with open(path, "r") as f:
            source = dec.decode(f.read())

        if not isinstance(source, dict) or not isinstance(source['books'], list):
            raise TypeError
        
        storage = BookStorage(path)
        books : list[dict[object, object]] = source['books']
        for book in books:
            b = Book.deserialize(book)
            storage._nextId = max(storage._nextId, b.id)
            storage._instances[b.id] = b

        storage._nextId += 1

        return storage
    
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