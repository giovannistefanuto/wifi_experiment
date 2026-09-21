import unittest

from wifi_lab.selection import parse_selection


class SelectionTests(unittest.TestCase):
    def test_single_and_list(self):
        self.assertEqual(parse_selection("1,2,7", 7), [1, 2, 7])

    def test_range_and_duplicates(self):
        self.assertEqual(parse_selection("1-3,2", 5), [1, 2, 3])

    def test_all(self):
        self.assertEqual(parse_selection("all", 3), [1, 2, 3])

    def test_out_of_range(self):
        with self.assertRaises(ValueError):
            parse_selection("4", 3)

    def test_malformed_range_has_clear_error(self):
        with self.assertRaisesRegex(ValueError, "Intervallo non valido"):
            parse_selection("uno-tre", 3)

    def test_empty_tokens_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "alcun indice"):
            parse_selection(",,", 3)


if __name__ == "__main__":
    unittest.main()
