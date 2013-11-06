import os
#, unittest
from hacker_public_radio import publish_show, ShowNotes

def test_dict(): #Function stores all the modules to be tested
    
    x = ShowNotes()
    h= x.get_dict()
    print(str(h))

        

test_dict()
