import unittest

from passnorm import normalize


class TestLineEndings(unittest.TestCase):
    def test_crlf(self):
        self.assertEqual(normalize("hunter2\r\n"), "hunter2")

    def test_lf(self):
        self.assertEqual(normalize("hunter2\n"), "hunter2")

    def test_bare_cr(self):
        self.assertEqual(normalize("hunter2\r"), "hunter2")

    def test_repeated_trailing_newlines(self):
        # a line that survived two rounds of concatenation, e.g. cat'ing
        # files that each ended without a final newline
        self.assertEqual(normalize("hunter2\r\n\r\n"), "hunter2")

    def test_no_trailing_newline(self):
        self.assertEqual(normalize("hunter2"), "hunter2")


class TestBOM(unittest.TestCase):
    def test_leading_bom_stripped(self):
        self.assertEqual(normalize("﻿hunter2"), "hunter2")

    def test_leading_bom_with_crlf(self):
        self.assertEqual(normalize("﻿hunter2\r\n"), "hunter2")

    def test_embedded_bom_also_stripped(self):
        # a BOM that ended up mid-string (e.g. two files concatenated
        # without stripping the second one's BOM) is category Cf like any
        # other, so it falls out in the format-character pass even though
        # it isn't at the front.
        self.assertEqual(normalize("hun﻿ter2"), "hunter2")

    def test_only_bom_normalizes_to_empty(self):
        self.assertEqual(normalize("﻿"), "")


class TestNFKCCollisions(unittest.TestCase):
    def test_fullwidth_digits_collapse_to_ascii(self):
        # U+FF11 etc. - a phone keyboard or IME can emit these instead of
        # ASCII digits without the user noticing.
        self.assertEqual(normalize("１２３"), "123")

    def test_fullwidth_letters_collapse_to_ascii(self):
        self.assertEqual(normalize("ＡＢＣ"), "ABC")

    def test_ligature_expands(self):
        # U+FB01 LATIN SMALL LIGATURE FI -> "fi"
        self.assertEqual(normalize("ﬁsh"), "fish")

    def test_distinct_looking_passwords_collide(self):
        # this is the documented tradeoff: two strings that are not
        # byte-identical before normalization become identical after it.
        self.assertEqual(normalize("password1"), normalize("password１"))


class TestControlAndFormatStripping(unittest.TestCase):
    def test_control_character_stripped(self):
        self.assertEqual(normalize("hunter\x072"), "hunter2")

    def test_null_byte_stripped(self):
        self.assertEqual(normalize("hunter\x002"), "hunter2")

    def test_zero_width_space_stripped(self):
        self.assertEqual(normalize("hunter​2"), "hunter2")

    def test_zero_width_joiner_stripped(self):
        self.assertEqual(normalize("hunter‍2"), "hunter2")

    def test_rtl_mark_stripped(self):
        self.assertEqual(normalize("hunter‏2"), "hunter2")


class TestInputValidation(unittest.TestCase):
    def test_non_str_raises_type_error(self):
        with self.assertRaises(TypeError):
            normalize(12345678)

    def test_bytes_raises_type_error(self):
        with self.assertRaises(TypeError):
            normalize(b"hunter2")


class TestEmptyAndWhitespace(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(normalize(""), "")

    def test_only_line_ending(self):
        self.assertEqual(normalize("\r\n"), "")

    def test_preserves_internal_whitespace(self):
        self.assertEqual(normalize("hunter 2\n"), "hunter 2")


if __name__ == "__main__":
    unittest.main()
