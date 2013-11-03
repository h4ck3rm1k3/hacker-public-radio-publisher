#http://hackerpublicradio.org/README.txt
# Version 11: 2013-10-31T19:42:37Z (Thursday)
# Hi Host,
# Thank you for producing a show for the HPR network.

class ShowNotes():
    # SHOWNOTES:
    # All shows must include an associated show note text file. We 
    # will use this information to fill out the website. The
    # headings of the file must be as follows:

    def __init__(self ):
        self.series = None
        self.tags = None

    def get_host_name(self):
        pass

    def get_email_address(self):
        pass
# 1. Hostname and email address: 
#    Ken Fallon (ken.fallon.nospam@nospam.gmail.com)

    def get_license(self):
        # By uploading your show you are agreeing that your work
        # will be released under a Creative Commons Attribution 
        # ShareAlike 3.0 License. 
        # See: 
        return 'http://creativecommons.org/licenses/by-sa/3.0/'

        # If any part of your work is not covered by this License
        # make sure to state that clearly in the audio as well as
        # in the show notes. You must have written permission for
        # all works you include.

    def get_title(self):
        # 2. Show Title: The title of your show
        pass


    def get_slot(self):
        # 3. Desired Slot: 
        #    "Next Available Slot" or 
        #    "Date YYYY-MM-DD" or 
        #    "Episode Number XXXX" or 
        #    "Backup Shows/Don't Care"

        return "Next Available Slot" 
        # SCHEDULING:
        # After you upload your show we will process it and post it 
        # ready for release on the date you requested or the first
        # available slot depending on which you selected. Shows will 
        # not be removed from the FTP server until they are posted. 

    def get_progress(self):
        # You can check the progress here:
        # http://hackerpublicradio.org/calendar.php. 

        # Shows are scheduled on a first come first served basis. 
        # Once a show has been posted, no further changes can be made.


    def get_intro_added(self):
        # 4. Intro and Outro Added: 
        #    YES or NO
        return "YES"

    def add_intro_outtro(self):
        # Please add the intro and outro clips.

        # 5. Series/Tags:
    def get_series(self):
        return self.series

    def get_tags(self):
        return self.tags

    def get_explicit(self):
        return "Clean"
        # 6. Explicit: 
        #    "Yes", or "Clean" (See iTunes for more information.)

    def get_twitter_summary(self):
        # 7. Twitter/Identi.CA Summary: 
        return ""

    def get_template(self):
        # You may also include very basic validated XHTML. 
        # See the example file on the ftp server. 
        # PLEASE USE THE TEMPLATE FILES FROM THE FTP SERVER.
        # http://hackerpublicradio.org/sample_shownotes.html
        # http://hackerpublicradio.org/sample_shownotes.txt
        return ()

    def get_metdata(self):

        # METADATA TAGS IN AUDIO FILE:
        # The format of the tags should be:
        self.metadata("TITLE",  self.get_title())
        self.metadata("ALBUM",  "Hacker Public Radio"))
        self.metadata("ARTIST",  self.get_host_name())
        self.metadata("GENRE",  "Podcast")
        self.metadata("COMMENT", "http://hackerpublicradio.org\n" + self.get_shownotes_text()

    def get_filename(self):
        # FILENAME:
        # The file name should be "A-Za-z0-9" "-" or "_" nothing else.
        # No spaces, braces "(){}[]", punctuation "' etc.       
        # Prefix the files with your hostid, then name or handle 
        # followed by the show title and then extension. New hosts 
        # should use "0" for their first post.       
        # The filename must be the same for all files, change the 
        # extension of the audio, shownotes and optionally one image.
        # Eg:
        #   198_Ahuka-04-LibreOffice-Writer-Style-Properties-1.flac
        #   198_Ahuka-04-LibreOffice-Writer-Style-Properties-1.html
        #   198_Ahuka-05-LibreOffice-Writer-Style-Properties-2.flac
        #   198_Ahuka-05-LibreOffice-Writer-Style-Properties-2.html
        #   198_Ahuka-05-LibreOffice-Writer-Style-Properties-2.zip        
        # If you have more files that you wish to include, then include
        # the audio, and shownotes file as normal, and put the rest in a 
        # zip, or tgz file. This should expand to a directory with a
        # index.html file that refers to the other files. This will be 
        # hosted in http://hackerpublicradio/eps/hpr${show number}
        # Adding additional files will delay processing as they need to
        # be verified manually.
        pass

    def get_format(self):
        # FORMATS:
        # We will encode the MP3, ogg and spx formats. 
        # We prefer FLAC File format (Best - Level 8), 24 Bit, with 
        # a Project Rate of 44100 Hz but we will accept anything as 
        # long as it's audible. Please upload a media file in the 
        # highest quality you have.        
        # We mix down to mono by default so if you want stereo then 
        # make note of it in the shownotes.
        return "FLAC"

    def get_shownotes_text(self):
        pass

    def announce_mailing(self):
        #MAILINGLIST:
        #send mail to mailing list
        # If you are not already on our mailing list you can join it
        # by going to
        # http://hackerpublicradio.org/mailman/listinfo/hpr_hackerpublicradio.org
        pass

    def archive_org(self):
        #post to archive.org
        pass

    def youtube_com(self):
        #post to youtube
        pass

    def commons_org(self):
        #post to commons
        pass
                
