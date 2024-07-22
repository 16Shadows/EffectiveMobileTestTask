from __future__ import annotations

from typing import Self
from enum import Enum
import re
import json
import abc

from modules.events import Event

class BookStatus(Enum):
    in_storage = 0
    '''Книга в наличии'''
    loaned = 1
    '''Книга выдана'''

    def serialize(self: Self) -> int:
        '''
        Преобразует это значение BookStatus в соответствующее целое число.
        '''
        return self.value

    @staticmethod
    def deserialize(value: int) -> BookStatus:
        '''
        Преобразует целое число в соответствующее значение BookStatus.
        Поднимает ValueError, если соответствующего значения BookStatus не существует.
        '''
        if value == BookStatus.in_storage.value:
            return BookStatus.in_storage
        elif value == BookStatus.loaned.value:
            return BookStatus.loaned
        else:
            raise ValueError

class Book:
    '''
    Одна книга
    '''

    def __init__(self, id : int, title : str, author : str, year : int) -> None:
        '''
        Создаёт объект книги с указанными параметрами.
        Не создавайте книги напрямую, используйте метод new_book класса BookStorage.

        Аргументы:
        id : int -- уникальный ID книги в хранилище
        title : str -- название книги
        author : str -- автор книги
        year : int -- год издания книги
        '''
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
        '''
        ID этой книги в БД. Неизменяемое значение.
        '''
        return self._id
    
    def serialize(self: Self) -> dict[str, object]:
        '''
        Создаёт словарь, содержащий все поля этого объекта в json-сериализируемой форме.
        '''
        o : dict[str, object] = {}
        o['id'] = self.id
        o['title'] = self.title
        o['author'] = self.author
        o['year'] = self.year
        o['status'] = self.status.serialize()
        return o
    
    @staticmethod
    def deserialize(source: dict[str, object]) -> Book:
        '''
        Создаёт объект Book из указанного словаря, если все поля в словаре присутствуют и верные.

        Аргументы:
        source : dict[str, object] - словарь json-совместимым представлением полей.

        Исключения:
        KeyError -- если в словаре нет нужного поля.
        TypeError -- если тип данных в словаре не соответствует ожидаемому.
        ValueError -- если значение status не является корректным значением BookStatus.
        '''
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
    '''
    Все книги в библиотеке    
    '''
    def __init__(self, storage_file_path: str) -> None:
        '''
        Создать экземпляр BookStorage с указанным путём для сохранения файла данных.
        Не загружает существующий файл. Для загрузки файла используется load_from_disk.

        Аргументы:
        storage_file_path : str -- путь до файла, в котором будут сохранены данные.
        '''
        self._storage_file_path = storage_file_path
        self._nextId = 0
        self._instances : dict[int, Book] = {}

        self.book_deleted_event = Event[Book]()

    def new_book(self: Self, title : str, author : str, year : int) -> Book:
        '''
        Создать новую книгу с заданными параметрами.

        Аргументы:
        title : str -- название книги
        author : str -- автор книги
        year : int -- год публикации книги
        '''
        book = Book(self._nextId, title, author, year)
        self._nextId += 1
        self._instances[book.id] = book
        return book
    
    def remove_book(self: Self, book: Book) -> None:
        '''
        Удаляет указанную книгу.

        Аргументы:
        book : Book -- книга, которую нужно удалить.

        Исключения:
        KeyError -- если указанной книги не существует в хранилище.
        '''
        del self._instances[book.id]
        #если не было исключения, то книгу удалили, можно поднять событие
        self.book_deleted_event(book)
    
    @property
    def books_count(self: Self) -> int:
        '''
        Возвращает число книг в этом хранилище.
        '''
        return len(self._instances)

    def all_books(self: Self) -> list[Book]:
        '''
        Возвращает список со всеми книгами в хранилище
        '''
        return list(self._instances.values())

    def find_book_by_id(self: Self, id: int) -> Book:
        '''
        Возвращает экземпляр книги с указанным id
        
        Аргументы:
        id : int -- ID книги

        Исключения:
        KeyError - если книги с таким ID не существует
        '''
        return self._instances[id]
    
    def has_book_with_id(self: Self, id: int) -> bool:
        '''
        Проверяет, существует ли книга с указанным id.
        Возвращает True, если существует, False иначе.

        Аргументы:
        id : int -- ID книги
        '''
        return id in self._instances
    
    def find_books(self: Self, condition: BookSearchConditionBase) -> list[Book]:
        '''
        Находит все книги, удовлетворяющие указанному условию.

        Аргументы:
        condition -- условие для поиска книг.
        '''
        books : list[Book] = []
        for value in self._instances.values():
            if condition.matches(value):
                books.append(value)
        return books
    
    def save_to_disk(self: Self) -> None:
        '''
        Сохраняет данные на диск
        '''
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
        '''
        Загружает данные из указанного файла и создаёт BookStorage

        Аргументы:
        path : str -- путь до файла на диске

        Исключения:
        JsonDecodeError - если не содержит валидный JSON
        TypeError, KeyError, ValueError - если структура файла не соответствует ожидаемой структуре
        '''
        dec = json.JSONDecoder()

        with open(path, "r") as f:
            source = dec.decode(f.read())

        if not isinstance(source, dict) or not isinstance(source['books'], list):
            raise TypeError
        
        storage = BookStorage(path)
        books : list[dict[str, object]] = source['books']
        for book in books:
            b = Book.deserialize(book)
            storage._nextId = max(storage._nextId, b.id)
            storage._instances[b.id] = b

        storage._nextId += 1

        return storage
    
class BookSearchConditionBase(abc.ABC):
    '''Базовый класс условия поиска книг'''

    @abc.abstractmethod
    def matches(self: Self, book: Book) -> bool:
        '''Проверить, соответствует ли книга заданному условию'''
        pass

class DefaultBookSearchCondition(BookSearchConditionBase):
    '''
    Условие поиска книг
    '''
    def __init__(self) -> None:
        self.by_title_pattern : re.Pattern[str] | None = None
        self.by_author_pattern : re.Pattern[str] | None = None
        self.by_year_pattern : int | None = None

    def matches(self: Self, book: Book) -> bool:
        return (
            (self.by_author_pattern is None or self.by_author_pattern.fullmatch(book.author) is not None)
            and
            (self.by_title_pattern is None or self.by_title_pattern.fullmatch(book.title) is not None)
            and
            (self.by_year_pattern is None or self.by_year_pattern == book.year)
        )

    def by_title(self: Self, pattern: re.Pattern[str]) -> Self:
        '''
        Задать условие поиска по названию книги

        Аргументы:
        pattern : re.Pattern[str] - регулярное выражение. Если название книги удовлетворяет этому регулярному выражению, то книга входит в результат поиска.
        '''
        self.by_title_pattern = pattern
        return self
    
    def by_author(self: Self, pattern: re.Pattern[str]) -> Self:
        '''
        Задать условие поиска по автору книги

        Аргументы:
        pattern : re.Pattern[str] - регулярное выражение. Если автор книги удовлетворяет этому регулярному выражению, то книга входит в результат поиска.
        '''
        self.by_author_pattern = pattern
        return self
    
    def by_year(self: Self, year: int) -> Self:
        '''
        Задать условие поиска по году публикации книги

        Аргументы:
        year : int - год публикации. Если год публикации книги совпадает с этим, то книга входит в результат поиска
        '''
        self.by_year_pattern = year
        return self