import unittest
from utils.base_62_encoding import encode, decode


class EncodingTests(unittest.TestCase):
    tests = [
        (0, '000000'),
        (1, '000001'),
        (62, '000010'),
        (63, '000011'),
        (34441886726, 'base62')
    ]

    def test_encode(self):
        for num, expected_encoded in EncodingTests.tests:
            actual_encoded = encode(num, 6)
            self.assertEqual(expected_encoded, actual_encoded)

    def test_decode(self):
        for expected_num, encoded in EncodingTests.tests:
            actual_num = decode(encoded)
            self.assertIsInstance(actual_num, int)
            self.assertEqual(expected_num, actual_num)

    def test_inverse(self):
        for i in range(1000):
            self.assertEqual(
                i,
                decode(encode(i, 6))
            )