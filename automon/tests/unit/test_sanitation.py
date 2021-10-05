import unittest

from automon.helpers.sanitation import Sanitation


class SanitationTest(unittest.TestCase):
    def test_Sanitation(self):
        self.assertTrue(Sanitation)
        self.assertTrue(Sanitation.strip_quotes)
        self.assertTrue(Sanitation.strip_spaces)
        self.assertTrue(Sanitation.strip_spaces_from_list)
        self.assertTrue(Sanitation.safe_string)
        self.assertTrue(Sanitation.dedup)
        self.assertTrue(Sanitation.list_from_string)

        self.assertRaises(TypeError, Sanitation.strip_quotes)
        self.assertRaises(TypeError, Sanitation.strip_spaces)
        self.assertRaises(TypeError, Sanitation.strip_spaces_from_list)
        self.assertRaises(TypeError, Sanitation.safe_string)
        self.assertRaises(TypeError, Sanitation.dedup)
        self.assertRaises(TypeError, Sanitation.list_from_string)

        self.assertEqual(Sanitation.strip_quotes('test'), 'test')
        self.assertEqual(Sanitation.strip_spaces(' t e s t '), 't e s t')
        self.assertEqual(Sanitation.strip_spaces(' t e s t '), 't e s t')
        self.assertEqual(Sanitation.strip_spaces_from_list(
            [' t e s t ']), ['t e s t'])
        self.assertEqual(Sanitation.safe_string(
            'a;skdfjAS*&D)(&!H!:@JEN'), 'a_skdfjAS__D____H___JEN')
        self.assertEqual(Sanitation.dedup(
            [1, 1, 'AAAAA', 'AAAAA', 'AA', 555, 555, 5555, 6666, 7, 8, 33, 1, 1232, 499124, 'a']),
            [1, 'AAAAA', 'AA', 555, 5555, 6666, 7, 8, 33, 1232, 499124, 'a'])

        self.assertEqual(Sanitation.list_from_string(
            'a,d,a,3,1,5,g,2,,a,4,1,,h,4,1,k,z'),
            ['a', 'd', 'a', '3', '1', '5', 'g', '2', '', 'a', '4', '1', '', 'h', '4', '1', 'k', 'z']
        )
        self.assertEqual(Sanitation.list_from_string(
            'a d a 3 1 5 g 2  a 4 1  h 4 1 k z'),
            ['a', 'd', 'a', '3', '1', '5', 'g', '2', '', 'a', '4', '1', '', 'h', '4', '1', 'k', 'z']
        )
        self.assertEqual(Sanitation.list_from_string(
            ' ada315g2a41h41kz '),
            ['ada315g2a41h41kz']
        )


if __name__ == '__main__':
    unittest.main()
