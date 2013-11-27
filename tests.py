
from hacker_public_radio import ShowNotes


class TestSuite():
    # def test_basic(self): #Function stores all the modules to be tested
    #     publish_show(
    #         input_file="test.flac"
    #     )

    def test_html(self):  # Function stores all the modules to be tested

        x = ShowNotes()
        x.set_input_file("example_show/test.flac")
        h = x.get_html()
        o = open("test.html", "w")
        o.write(h)
        o.close()

    def test_dict(self):  # Function stores all the modules to be tested

        x = ShowNotes()
        x.set_input_file("example_show/test.flac")
        h = x.get_dict()
        o = open("dict.txt", "w")
        o.write(str(h))
        o.write(str(x.__dict__))
        o.close()
