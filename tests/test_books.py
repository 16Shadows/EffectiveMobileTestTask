import unittest
from modules.books import Book, DefaultBookSearchCondition, BookStatus, BookStorage
from typing import Self
import os
import re

class BookTestSuite(unittest.TestCase):
    def test_book_create(self: Self):
        b = Book(5, 'title', 'author', 255)

        self.assertEqual(b.id, 5)
        self.assertEqual(b.author, 'author')
        self.assertEqual(b.title, 'title')
        self.assertEqual(b.year, 255)
        self.assertEqual(b.status, BookStatus.in_storage)

    def test_serialize_deserialize(self: Self):
        b = Book(5, 'title', 'author', 255)
        bd = b.deserialize(b.serialize())
        self.assertEqual(b.id, bd.id)
        self.assertEqual(b.author, bd.author)
        self.assertEqual(b.title, bd.title)
        self.assertEqual(b.year, bd.year)
        self.assertEqual(b.status, bd.status)

class BookStorageTestSuite(unittest.TestCase):    
    def test_create_book(self: Self):
        storage = BookStorage('t')
        b = storage.new_book('title', 'author', 255)

        self.assertEqual(b.author, 'author')
        self.assertEqual(b.title, 'title')
        self.assertEqual(b.year, 255)
        self.assertEqual(b.status, BookStatus.in_storage)

    def test_find_book_by_valid_id(self: Self):
        storage = BookStorage('t')
        b = storage.new_book('title', 'author', 255)

        self.assertEqual(b, storage.find_book_by_id(b.id))

    def test_find_book_by_invalid_id(self: Self):
        storage = BookStorage('t')
        b = storage.new_book('title', 'author', 255)

        self.assertRaises(KeyError, lambda: storage.find_book_by_id(b.id+1))

    def test_has_book_with_valid_id(self: Self):
        storage = BookStorage('t')
        b = storage.new_book('title', 'author', 255)

        self.assertTrue(storage.has_book_with_id(b.id))

    def test_has_book_with_invalid_id(self: Self):
        storage = BookStorage('t')
        b = storage.new_book('title', 'author', 255)

        self.assertFalse(storage.has_book_with_id(b.id+1))

    def test_remove_book_valid(self: Self):
        storage = BookStorage('t')
        b = storage.new_book('title', 'author', 255)
        storage.remove_book(b)
        self.assertEqual(storage.books_count, 0)
        self.assertCountEqual(storage.all_books(), [])

    def test_remove_book_invalid(self: Self):
        storage = BookStorage('t')
        b = Book(5, 'title', 'author', 255)
        self.assertRaises(KeyError, lambda: storage.remove_book(b))

    def test_books_count(self: Self):
        storage = BookStorage('t')
        b = storage.new_book('title', 'author', 255)

        self.assertEqual(storage.books_count, 1)

        storage.remove_book(b)

        self.assertEqual(storage.books_count, 0)

    def test_all_books(self: Self):
        storage = BookStorage('t')
        b = [
            storage.new_book('title', 'author', 255),
            storage.new_book('title', 'author', 256)
        ]

        self.assertCountEqual(storage.all_books(), b)

    def test_find_books(self: Self):
        storage = BookStorage('t')
        b = [
            storage.new_book('title', 'author', 255),
            storage.new_book('title', 'author', 256)
        ]

        self.assertCountEqual(storage.find_books(DefaultBookSearchCondition().by_year(256)), [b[1]])

    def test_save_load(self: Self):
        storage = BookStorage('t')
        bl = [
            storage.new_book('title', 'author', 255),
            storage.new_book('title', 'author', 256)
        ]

        storage.save_to_disk()

        storage = BookStorage.load_from_disk('t')

        for bd in bl:
            b = storage.find_book_by_id(bd.id)
            self.assertEqual(b.id, bd.id)
            self.assertEqual(b.author, bd.author)
            self.assertEqual(b.title, bd.title)
            self.assertEqual(b.year, bd.year)
            self.assertEqual(b.status, bd.status)

        os.remove('t')

class DefaultBookSearchConditionTestSuite(unittest.TestCase):
    def test_by_author(self: Self):
        storage = BookStorage('t')
        b = [
            storage.new_book('title', 'author', 15)
        ]

        f = storage.find_books(DefaultBookSearchCondition().by_author(re.compile('author')))
        self.assertCountEqual(b, f)
        f = storage.find_books(DefaultBookSearchCondition().by_author(re.compile('.*hor')))
        self.assertCountEqual(b, f)
        f = storage.find_books(DefaultBookSearchCondition().by_author(re.compile('.*else.*')))
        self.assertEqual(0, len(f))

    def test_by_title(self: Self):
        storage = BookStorage('t')
        b = [
            storage.new_book('title', 'author', 15)
        ]

        f = storage.find_books(DefaultBookSearchCondition().by_title(re.compile('title')))
        self.assertCountEqual(b, f)
        f = storage.find_books(DefaultBookSearchCondition().by_title(re.compile('.*le')))
        self.assertCountEqual(b, f)
        f = storage.find_books(DefaultBookSearchCondition().by_title(re.compile('.*else.*')))
        self.assertEqual(0, len(f))

    def test_by_year(self: Self):
        storage = BookStorage('t')
        b = [
            storage.new_book('title', 'author', 15)
        ]

        f = storage.find_books(DefaultBookSearchCondition().by_year(15))
        self.assertCountEqual(b, f)
        f = storage.find_books(DefaultBookSearchCondition().by_year(16))
        self.assertEqual(0, len(f))

    def test_mixed(self: Self):
        storage = BookStorage('t')
        b = [
            storage.new_book('title', 'author', 15)
        ]

        f = storage.find_books(DefaultBookSearchCondition().by_author(re.compile('author')).by_title(re.compile('title')).by_year(15))
        self.assertCountEqual(b, f)
        f = storage.find_books(DefaultBookSearchCondition().by_author(re.compile('author')).by_title(re.compile('title')).by_year(16))
        self.assertEqual(0, len(f))

if __name__ == '__main__':
    unittest.main()