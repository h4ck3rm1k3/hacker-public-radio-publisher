import os
#, unittest
from hacker_public_radio import publish_show, ShowNotes

def test_dict(): #Function stores all the modules to be tested
    
    x = ShowNotes()
    #x.ls_main_ftp()
    x.set_input_file( "test.flac" )
    print x.get_filename()
    x.add_intro_outtro()
    print " going to emit html"
    x.emit_html()
    print " upload ftp"
    x.ls_main_ftp()
    x.put_main_ftp()
    x.ls_main_ftp()


test_dict()
