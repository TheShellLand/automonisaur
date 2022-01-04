import unittest
import types

from swiftclient.service import ClientException

from automon.integrations.swift import SwiftClient, SwiftError_, SwiftItem, SwiftPage, SwiftList
from automon.integrations.swift.config import SwiftConfig


class SwiftConfigTest(unittest.TestCase):

    def test_config(self):
        self.assertTrue(SwiftConfig())


class SwiftTest(unittest.TestCase):
    s = SwiftClient()

    def test_Swift(self):
        self.assertTrue(SwiftClient)
        self.assertTrue(self.s)

    def test_list(self):
        # self.assertEqual(self.s.list('test'), [])
        self.assertRaises(
            TypeError, self.s.list_container(container='0000000xxx'))
        self.assertRaises(
            TypeError, self.s.list_container(container='0000000xxx'))


class SwiftPageTest(unittest.TestCase):
    page = {
        'action': None,
        'container': None,
        'prefix': None,
        'success': True,
        'marker': None,
        'error': None,
        'traceback': None,
        'error_timestamp': None,
        'listing': []
    }
    error = {
        'action': None,
        'container': None,
        'prefix': None,
        'success': None,
        'marker': None,
        'error': ClientException,
        'traceback': None,
        'error_timestamp': None,
    }

    s = SwiftPage(page)
    e = SwiftPage(error)

    def test_SwiftPage(self):
        self.assertTrue(SwiftPage)
        self.assertTrue(self.s)
        self.assertTrue(self.s._dict())
        self.assertIsInstance(self.s._dict(), dict)
        self.assertEqual(self.s._dict(), self.page)
        self.assertEqual(self.e.error, ClientException)
        self.assertNotEqual(self.s.error, ClientException)
        self.assertTrue(self.s)
        self.assertIsInstance(self.s.list_gen(), types.GeneratorType)
        self.assertTrue(self.e.list_gen())
        self.assertTrue(f'{self.e}')
        self.assertTrue(f'{self.s}')


class SwiftErrorTest(unittest.TestCase):
    error = {
        'action': '',
        'container': '',
        'headers': '',
        'success': '',
        'error': '',
        'traceback': '',
        'error_timestamp': '',
        'response_dict': '',
    }

    def test_SwiftError(self):
        self.assertTrue(SwiftError_)
        self.assertTrue(SwiftError_(self.error))
        self.assertIsInstance(f'{SwiftError_(self.error)}', str)


class SwiftItemTest(unittest.TestCase):
    item = {
        'size': 0,
        'name': None,
        'hash': None,
        'etag': None,
        'content_type': None,
        'last_modified': None
    }
    item2 = {
        'size': 0,
        'name': 'test',
        'hash': None,
        'etag': None,
        'content_type': 'application/directory',
        'last_modified': None
    }

    def test_SwiftItem(self):
        self.assertTrue(SwiftItem)
        self.assertTrue(SwiftItem({}))
        self.assertFalse(SwiftItem(self.item).is_directory())
        self.assertEqual(SwiftItem(self.item).data(), self.item)
        self.assertFalse(SwiftItem(self.item).has_dir_marker())
        self.assertTrue(SwiftItem(self.item2).is_directory())
        self.assertEqual(SwiftItem(self.item2).data(), self.item2)
        self.assertTrue(SwiftItem(self.item2).filter('test'))
        self.assertFalse(SwiftItem(self.item2).filter('nottest'))
        self.assertTrue(f'{SwiftItem(self.item2)}')


if __name__ == '__main__':
    unittest.main()
