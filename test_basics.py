"""Test suite."""

import unittest
from pathlib import Path

import numpy as np

import sispo.sim.utils as utils


class TestUtils(unittest.TestCase):

    def test_check_dir(self):
        dir_name = "dir_test"

        file_dir = Path(__file__).parent.resolve()
        test_dir = file_dir / dir_name

        dir = utils.check_dir(test_dir)
        self.assertTrue(test_dir == dir)
        self.assertTrue(test_dir.exists())

        test_dir_relative = test_dir / ".." / dir_name
        self.assertTrue(test_dir == utils.check_dir(test_dir_relative))
        self.assertTrue(test_dir.exists())

        Path.rmdir(test_dir)

    def test_write_vec_string(self):
        vec = (1.234, 2.345, 3.456)

        self.assertEqual(utils.write_vec_string(vec, 0), "[1,2,3]")
        self.assertEqual(utils.write_vec_string(vec, 1), "[1.2,2.3,3.5]")
        self.assertEqual(utils.write_vec_string(vec, 2), "[1.23,2.35,3.46]")
        self.assertEqual(utils.write_vec_string(vec, 3), "[1.234,2.345,3.456]")
        self.assertEqual(utils.write_vec_string(vec, 4),
                         "[1.2340,2.3450,3.4560]")

    def test_read_vec_string(self):
        vec1 = np.array([1.2, 2.3, 3.5])
        vec2 = np.array([1.23, 2.35, 3.46])
        vec3 = np.array([1.234, 2.345, 3.456])
        vec_str1 = "[1.2, 2.3, 3.5]"
        vec_str2 = "[1.23, 2.35, 3.46]"
        vec_str3 = "[1.234, 2.345, 3.456]"

        np.testing.assert_equal(utils.read_vec_string(vec_str1), vec1)
        np.testing.assert_equal(utils.read_vec_string(vec_str2), vec2)
        np.testing.assert_equal(utils.read_vec_string(vec_str3), vec3)

    def test_write_mat_string(self):
        mat = ((1.234, 2.345, 3.456),
               (4.567, 5.678, 6.789), (7.891, 8.912, 9.123))

        self.assertEqual(utils.write_mat_string(mat, 0),
                         "[[1,2,3],[5,6,7],[8,9,9]]")
        self.assertEqual(utils.write_mat_string(mat, 1),
                         "[[1.2,2.3,3.5],[4.6,5.7,6.8],[7.9,8.9,9.1]]")
        self.assertEqual(utils.write_mat_string(mat, 3),
                         "[[1.234,2.345,3.456],[4.567,5.678,6.789],[7.891,8.912,9.123]]")
        self.assertEqual(utils.write_mat_string(mat, 4),
                         "[[1.2340,2.3450,3.4560],[4.5670,5.6780,6.7890],[7.8910,8.9120,9.1230]]")

    def test_read_mat_string(self):
        mat1 = ((1.2, 2.3, 3.5),
                (4.6, 5.7, 6.8), (7.9, 8.9, 9.1))
        mat2 = ((1.23, 2.35, 3.46),
                (4.57, 5.68, 6.79), (7.89, 8.91, 9.12))
        mat3 = ((1.234, 2.345, 3.456),
                (4.567, 5.678, 6.789), (7.891, 8.912, 9.123))
        mat_str1 = "[[1.2, 2.3, 3.5],[4.6, 5.7, 6.8],[7.9, 8.9, 9.1]]"
        mat_str2 = "[[1.23, 2.35, 3.46],[4.57, 5.68, 6.79],[7.89, 8.91, 9.12]]"
        mat_str3 = "[[1.234, 2.345, 3.456],[4.567, 5.678, 6.789],[7.891, 8.912, 9.123]]"

        np.testing.assert_equal(utils.read_mat_string(mat_str1), mat1)
        np.testing.assert_equal(utils.read_mat_string(mat_str2), mat2)
        np.testing.assert_equal(utils.read_mat_string(mat_str3), mat3)

    def test_serialise(self):
        test_array = np.array([0, 1, 2, 3, 4, 5, 6])
        test_float = "1.234567"

        self.assertEqual(utils.serialise(test_array), [0, 1, 2, 3, 4, 5, 6])
        self.assertEqual(utils.serialise(test_float), float(test_float))

    def test_check_file_ext(self):
        filename_1 = "test"
        filename_2 = "test.txt"

        filepath_1 = Path(filename_1)
        filepath_2 = Path(filename_2)

        self.assertEqual(utils.check_file_ext(filename_1, ".txt"), filename_2)
        self.assertEqual(utils.check_file_ext(filename_1, "txt"), filename_2)
        self.assertEqual(utils.check_file_ext(filename_2, ".txt"), filename_2)
        self.assertEqual(utils.check_file_ext(filename_2, "txt"), filename_2)
        self.assertEqual(utils.check_file_ext(filepath_1, ".txt"), filepath_2)
        self.assertEqual(utils.check_file_ext(filepath_1, "txt"), filepath_2)
        self.assertEqual(utils.check_file_ext(filepath_2, ".txt"), filepath_2)
        self.assertEqual(utils.check_file_ext(filepath_2, "txt"), filepath_2)


if __name__ == "__main__":
    unittest.main()
