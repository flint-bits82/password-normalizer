import os
import tempfile
import unittest

from passnorm import iter_normalize, iter_normalize_file


class TestIterNormalize(unittest.TestCase):
    def test_mixed_line_endings(self):
        lines = ["hunter2\r\n", "correcthorse\n", "trout\r"]
        self.assertEqual(list(iter_normalize(lines)), ["hunter2", "correcthorse", "trout"])

    def test_blank_lines_filtered_out(self):
        lines = ["hunter2\n", "\n", "\r\n", "correcthorse\n"]
        self.assertEqual(list(iter_normalize(lines)), ["hunter2", "correcthorse"])

    def test_bytes_lines_decoded(self):
        lines = [b"hunter2\r\n", b"correcthorse\n"]
        self.assertEqual(list(iter_normalize(lines)), ["hunter2", "correcthorse"])

    def test_mixed_str_and_bytes(self):
        lines = ["hunter2\n", b"correcthorse\n"]
        self.assertEqual(list(iter_normalize(lines)), ["hunter2", "correcthorse"])

    def test_malformed_bytes_do_not_abort_the_run(self):
        lines = [b"hunter2\n", b"\xff\xfebad\n", b"correcthorse\n"]
        results = list(iter_normalize(lines))
        self.assertEqual(results[0], "hunter2")
        self.assertEqual(results[-1], "correcthorse")
        self.assertEqual(len(results), 3)

    def test_leading_bom_on_first_line(self):
        lines = ["﻿hunter2\r\n", "correcthorse\n"]
        self.assertEqual(list(iter_normalize(lines)), ["hunter2", "correcthorse"])


class TestIterNormalizeFile(unittest.TestCase):
    def _write(self, content_bytes):
        fd, path = tempfile.mkstemp()
        with os.fdopen(fd, "wb") as handle:
            handle.write(content_bytes)
        self.addCleanup(os.remove, path)
        return path

    def test_streams_file_with_bom_and_mixed_endings(self):
        path = self._write("﻿hunter2\r\ncorrecthorse\ntrout\r\n".encode("utf-8"))
        self.assertEqual(
            list(iter_normalize_file(path)),
            ["hunter2", "correcthorse", "trout"],
        )

    def test_blank_lines_in_file_are_skipped(self):
        path = self._write("hunter2\n\n\ncorrecthorse\n".encode("utf-8"))
        self.assertEqual(list(iter_normalize_file(path)), ["hunter2", "correcthorse"])

    def test_empty_file_yields_nothing(self):
        path = self._write(b"")
        self.assertEqual(list(iter_normalize_file(path)), [])


if __name__ == "__main__":
    unittest.main()
