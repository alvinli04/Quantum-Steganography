import unittest

class TestStringMethods(unittest.TestCase):

    def test_classical_preprocessing(self, actualPxlVal, pixelBitValue):
        bitVal = "{0:b}".format(int(actualPxlVal))
        self.assertEqual(pixelBitValue, bitVal, 'message = "First and second values are NOT equal!"')

if __name__ == '__main__':
    unittest.main()



