import os
import sys
#, unittest
from hacker_public_radio import ShowNotes
import sys, getopt
import yaml

def create_show(force): #create a show
    
    x = ShowNotes()
    #x.ls_main_ftp()
    x.set_input_file( "example_show/test.flac" )

    x.load_shownotes_from_file("example_show/html_notes.html")
    x.add_directory_as_tgz('example_show/datafiles/')
    print x.get_filename()

    x.add_intro_outtro()

    print " going to emit html"
    print yaml.dump(x.get_dict())

    x.emit_html()
    print " upload ftp"
    x.ls_main_ftp()
    x.put_main_ftp(force)
    x.ls_main_ftp()



def printhelp():
      print 'example.py -f|--force'

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hf",["force"])
    except getopt.GetoptError:
        printhelp()
        sys.exit(2)
    force=False
    for opt, arg in opts:
        if opt == '-h':
            help()
            sys.exit()
        elif opt in ("-f", "--force"):
            force = True
    create_show(force)

if __name__ == "__main__":
   main(sys.argv[1:])

    

