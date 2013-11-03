import os, unittest
from hacker_public_radio import publish_show

suite = unittest.TestSuite()

class SomeTestSuite(unittest.TestSuite):

    def test_basic(self): #Function stores all the modules to be tested
        
        publish_show(
            input_file="test.flac"
        )


if __name__ == '__main__':
    unittest.main()
