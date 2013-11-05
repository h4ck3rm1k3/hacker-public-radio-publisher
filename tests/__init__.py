import os, unittest
from hacker_public_radio import publish_show

suite = unittest.TestSuite()

class SomeTestSuite(unittest.TestSuite):

    def test_basic(self): #Function stores all the modules to be tested
        
        publish_show(
            input_file="test.flac"
        )

    def test_html(self): #Function stores all the modules to be tested
        
        x = ShowNotes()
        print x.get_html()


if __name__ == '__main__':
    unittest.main()
