import unittest
from mGRFXLib import *

class TestStringMethods(unittest.TestCase):
    def testSeconds(self):
        self.assertEqual(readTag("s22.936"), {"s": 22.936, "t": 22.936})
        self.assertEqual(readTag("s1.27"), {"s": 1.27, "t": 1.27})
        self.assertEqual(readTag("s1032"), {"s": 1032, "t": 1032})
        self.assertEqual(readTag("s1;"), {"s": 1, "t": 1})
        self.assertEqual(readTag("s17.8;"), {"s": 17.8, "t": 17.8})
        self.assertEqual(readTag("s193;"), {"s": 193, "t": 193})
        self.assertEqual(readTag("s0.102;"), {"s": 0.102, "t": 0.102})
        self.assertEqual(readTag("s0.003"), {"s": 0.003, "t": 0.003})
        self.assertEqual(readTag("s;"), {"s": 0, "t": 0})
        self.assertEqual(readTag(""), {"t": 0})

    def testMinutes(self):
        self.assertEqual(readTag("m0"), {"m": 0, "t": 0})
        self.assertEqual(readTag("m1"), {"m": 1, "t": 60})
        self.assertEqual(readTag("m1;"), {"m": 1, "t": 60})

    def testSecondsMinutes(self):
        self.assertEqual(readTag("m1;s20"), {"m": 1, "s": 20, "t": 80})

    def testPath(self):
        self.assertEqual(readTag("pPATH.flac"), {"p": "PATH.flac", "t": 0})
        self.assertEqual(readTag("pFOLDER\\PATH.flac"), {"p": "FOLDER\\PATH.flac", "t": 0})
        self.assertEqual(readTag("pC:\\FOLDER\\PATH.flac"), {"p": "C:\\FOLDER\\PATH.flac", "t": 0})

if __name__ == "__main__":
    __unittest = True
    unittest.main()