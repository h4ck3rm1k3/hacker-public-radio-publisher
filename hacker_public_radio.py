u'''
python module for HPR broadcasting
based on :http://hackerpublicradio.org/README.txt
# Version 11: 2013-10-31T19:42:37Z (Thursday)
# Hi Host,
# Thank you for producing a show for the HPR network.

Templating using jinja
http://jinja.pocoo.org/docs/

'''
import audiotools
from audiotools.flac import Flac_STREAMINFO,Flac_VORBISCOMMENT
from jinja2 import Environment
from jinja2 import  PackageLoader
import os 
import ftputil
import secret # passwords
import sys
import os.path

def progress_update(a, chunk):
    print a, chunk

def ftp_upload_cb(chunk):
    print "uploaded chunk ."


class ShowNotes(object):
    u'''
    SHOWNOTES:
    All shows must include an associated show note text file. We
    will use this information to fill out the website. The
    headings of the file must be as follows:
    '''

    def __init__(self ):
        '''
        constructor
        '''
        self.input_file = None
        self.metadata   = {}
        self.audio_file = None
        self.template   = None
        self.audio_metadata = None

    def get_input_file(self):
        u'''
        get attribute
        '''
        return self.input_file

    def set_input_file(self, filename):
        u'''
        set attribute and read it
        '''
        self.input_file = filename
        self.read_file()
        #read metadata
        self.read_metadata()


    def read_file(self):
        u'''
        read the file
        '''
        files = audiotools.open_files(
            [
                self.input_file
            ]
        )
        self.audio_file = files[0]

    def read_metadata(self):
        '''
        read metadata from the file
        '''
        self.audio_metadata = self.audio_file.get_metadata()
        streaminfo = self.audio_metadata.get_block(Flac_STREAMINFO.BLOCK_ID)
        self.metadata['md5sum']          = str(streaminfo.md5sum)
        self.metadata['total_sample']    = streaminfo.total_samples
        self.metadata['bits_per_sample'] = streaminfo.bits_per_sample
        self.metadata['channels']        = streaminfo.channels
        self.metadata['sample_rate']     = streaminfo.sample_rate
        self.metadata['file_size']       = os.path.getsize(self.input_file)

        comments = self.audio_metadata.get_block(Flac_VORBISCOMMENT.BLOCK_ID)
#        print comments.__dict__
#        print comments
#        print comments.comment_strings
        for comment in comments.comment_strings:
            (tag, value) = comment.split(u"=", 1)
            self.metadata[tag]=value

        # for field in (
        #         u'Artist Email', 
        #         u'DATE', 
        #         u'Contains Intro', 
        #         u'TITLE', 
        #         u'TRACKNUMBER', 
        #         u'Twitter Description', 
        #         u'License', 
        #         u'Artist Number', 
        #         u'COMMENTS', 
        #         u'Tags', 
        #         u'ALBUM', 
        #         u'Series', 
        #         u'Artist Handle', 
        #         u'Slot', 
        #         u'GENRE', 
        #         u'ARTIST' ):            
        #     v= getattr(comments,field)
        #     print field, v 
            
            #u'reference libFLAC 1.3.0 20130526'
            #print(self.audio_metadata)

    def get_metadata(self, name, default=None):
        '''
        get one field from the metadata
        '''
        if name in self.metadata :
            return self.metadata[name]
        else:
            return default

    ## acccessors for metadata

    def get_html(self):
        u'''
         You may also include very basic validated XHTML.
         See the example file on the ftp server.
         PLEASE USE THE TEMPLATE FILES FROM THE FTP SERVER.
         http://hackerpublicradio.org/sample_shownotes.html
         http://hackerpublicradio.org/sample_shownotes.txt
        '''
        loader=PackageLoader('hpr', 'templates')
        env = Environment(loader=loader)
        template_file = self.get_metadata(
            "template_file",
            default="shownotes.tpl"
        )    
        #print template_file
        template = env.get_template( template_file )

        # Finally, process the template to produce our final text.
        html = template.render( self.get_dict() )
        return html

    def emit_html(self):
        h= self.get_html()
        o = open (self.get_filename() + ".html","w")
        o.write(h)
        o.flush()
        o.close()

    def get_input_file(self):
        return self.input_file

    def get_dict(self):
        return {
            "host_name" :self.get_host_name(),
            "host_handle" :self.get_host_handle(),
            "host_number" :self.get_host_number(),
            "input_file" :self.get_input_file(),
            "host_email_address" :self.get_host_email_address(),
            "license" :self.get_license(),
            "title" :self.get_title(),
            "slot" :self.get_slot(),
            "series" :self.get_series(),
            "tags" :self.get_tags(),
            "explicit" :self.get_explicit(),
            "twitter_summary" :self.get_twitter_summary(),
            "format" :self.get_format(),
            "shownotes_text" :self.get_shownotes_text(),
            "filename" :self.get_filename(),
            "intro_added" :self.get_intro_added(),
        }

    def get_host_name(self):
        u'''
        returns the name of the show host
        '''
        return self.get_metadata("ARTIST")

    def get_host_handle(self):
        u'''
        returns the handle of the show host
        '''
        return self.get_metadata("Artist Handle")

    def get_host_number(self):
        u'''
        get the artist number
        '''
        return self.get_metadata("Artist Number" )

    def get_host_email_address(self):
        u'''
        1. Hostname and email address:
        Ken Fallon (ken.fallon.nospam@nospam.gmail.com)
        '''
        self.get_metadata("Artist Email")

    def get_license(self):
        u'''
        By uploading your show you are agreeing that your work
        will be released under a Creative Commons Attribution
        ShareAlike 3.0 License.
        If any part of your work is not covered by this License
        make sure to state that clearly in the audio as well as
        in the show notes. You must have written permission for
        all works you include.
        '''
        return self.get_metadata(
            "License",
            default="http://creativecommons.org/licenses/by-sa/3.0/"
        )

    def set_title(self,value):
        return self.set_metadata("TITLE",value)

    def get_title(self):
        u'''
        2. Show Title: The title of your show
        '''
        return self.get_metadata("TITLE")

    def get_slot(self):
        u'''
         SCHEDULING:
         After you upload your show we will process it and post it
         ready for release on the date you requested or the first
         available slot depending on which you selected. Shows will
         not be removed from the FTP server until they are posted.
        3. Desired Slot:
        "Next Available Slot" or
        "Date YYYY-MM-DD" or
        "Episode Number %d" or
        "Backup Shows/Don't Care"
        '''
        return self.get_metadata("Slot", default = "Next Available Slot")

    def get_series(self):
        u'''
         5. Series/Tags:
        '''
        self.get_metadata("Series")

    def get_tags(self):
        u'''
        TODO:
        '''
        self.get_metadata("Tags")

    def get_explicit(self):
        u'''
        6. Explicit:
        "Yes", or "Clean" (See iTunes for more information.)
        '''
        self.get_metadata("Explicit", default="Clean")

    def get_twitter_summary(self):
        u'''
        7. Twitter/Identi.CA Summary:
        '''
        self.get_metadata("Twitter Description")

    def get_format(self):
        u'''
        FORMATS:
        We will encode the MP3, ogg and spx formats.
        We prefer FLAC File format (Best - Level 8), 24 Bit, with
        a Project Rate of 44100 Hz but we will accept anything as
        long as it's audible. Please upload a media file in the
        highest quality you have.
        We mix down to mono by default so if you want stereo then
        make note of it in the shownotes.
        '''
        return "FLAC"


    def get_shownotes_text(self):
        '''
        we store the show notes in the comment metadata
        '''
        self.get_metadata("COMMENTS")

## derived
    def get_filename(self):
        u'''
        FILENAME:
        The file name should be "A-Za-z0-9" "-" or "_" nothing else.
        No spaces, braces "(){}[]", punctuation "' etc.
        Prefix the files with your hostid, then name or handle
        followed by the show title and then extension. New hosts
        should use "0" for their first post.
        The filename must be the same for all files, change the
        extension of the audio, shownotes and optionally one image.
        Eg:
          198_Ahuka-04-LibreOffice-Writer-Style-Properties-1.flac
          198_Ahuka-04-LibreOffice-Writer-Style-Properties-1.html
          198_Ahuka-05-LibreOffice-Writer-Style-Properties-2.flac
          198_Ahuka-05-LibreOffice-Writer-Style-Properties-2.html
          198_Ahuka-05-LibreOffice-Writer-Style-Properties-2.zip
        If you have more files that you wish to include, then include
        the audio, and shownotes file as normal, and put the rest in a
        zip, or tgz file. This should expand to a directory with a
        index.html file that refers to the other files. This will be
        hosted in http://hackerpublicradio/eps/hpr${show number}
        Adding additional files will delay processing as they need to
        be verified manually.
        '''
        host_number = self.get_host_number()
        host_name = self.get_host_name()
        infilename = self.input_file.replace(".flac", "")
        filename =  "%s_%s_%s" % (
            host_number,
            host_name,
            infilename
        )
        filename = filename.replace(" ","_")
        return filename 

## Processing

    def get_intro_added(self):
        '''
        4. Intro and Outro Added:
        YES or NO
        '''
        value = self.get_metadata("Contains Intro", default="N")
        if value[0] == "Y" :
            return True
        return False

    def add_intro_outtro(self):
        '''
        Please add the intro and outro clips.
        http://audiotools.sourceforge.net/install.html
        prepend intro.flac
        append outro.flac
        '''
        
        output_filename = self.get_filename() + ".flac" 
        if (os.path.exists(output_filename)):
            return

        output_filename =audiotools.Filename(output_filename)

        intro = audiotools.open_files(    [        'intro.flac',    ])
        content = audiotools.open_files(    [        'test.flac',    ])
        outro = audiotools.open_files(    [        'outro.flac',    ])

        audiofiles = [
            intro[0],
            content[0],
            outro[0],
        ]
        
        AudioType = audiotools.filename_to_type("info.flac")
        metadata = content[0].get_metadata() 
        output_class = AudioType
        #print audiofiles
        pcms = ([af.to_pcm() for af in audiofiles])
        #print [r.bits_per_sample for r in pcms]

        encoded = output_class.from_pcm(
            str(output_filename),
            audiotools.PCMReaderProgress(
                audiotools.PCMCat(pcms),
                sum([af.total_frames() for af in audiofiles]),
                progress_update),
            #output_quality,
            total_pcm_frames=sum([af.total_frames() for af in audiofiles]))
        encoded.set_metadata(metadata)

    def announce_mailing(self):
        '''
        MAILINGLIST:
        send mail to mailing list
        If you are not already on our mailing list you can join it
        by going to
        http://hackerpublicradio.org/mailman/listinfo/hpr_hackerpublicradio.org
        '''
        pass

    def ls_main_ftp(self):
        '''
        ftputil
        '''
        s=secret.get_hpr_ftp_server()
        u=secret.get_hpr_ftp_username()
        p=secret.get_hpr_ftp_password()

        with ftputil.FTPHost(s, u, p) as host:
            names = host.listdir("/")
            for name in names:
                print name
                #if host.path.isfile(name):
                    # remote name, local name, binary mode
                    #host.download(name, name, 'b')

            names = host.listdir("/temp_dir_please_ignore/")
            for name in names:
                print "/temp_dir_please_ignore/" + name

    def remove_temp(self, host):
        names = host.listdir("/temp_dir_please_ignore/")
        for name in names:
            print " to remove /temp_dir_please_ignore/" + name
            host.remove("/temp_dir_please_ignore/" + name)

    def put_main_ftp(self):
        '''
        ftputil
        '''
        s=secret.get_hpr_ftp_server()
        u=secret.get_hpr_ftp_username()
        p=secret.get_hpr_ftp_password()

        with ftputil.FTPHost(s, u, p) as host:
            path = '/temp_dir_please_ignore'

            self.remove_temp(host)

            try :
                host.rmdir(path)
            except:
                pass

            try :
                host.mkdir(path)
            except:
                pass

          
            flac = self.get_filename() + ".flac"
            html = self.get_filename() + ".html"

            try :
                host.upload(flac, path + "/" + flac, mode='', callback=ftp_upload_cb)
            except:
                pass

            try :
                host.upload(html, path + "/" + html, mode='', callback=ftp_upload_cb)
            except:
                pass

    def put_archive_org(self):
        '''
        post to archive.org
        http://archive.org/~vmb/abouts3.html
        http://archive.org/help/abouts3.txt
        http://www.elastician.com/2011/02/
        accessing-internet-archive-with-boto.html
        http://www.archive.org/stream/jon-s3-test/archiveS3Man_djvu.txt
        '''
        pass

    def put_youtube_com(self):
        '''
        post to youtube
        '''
        pass

    def put_commons_org(self):
        '''
        post to commons
        '''
        pass

    def get_progress(self):
        '''
        You can check the progress here:
        http://hackerpublicradio.org/calendar.php.
        Shows are scheduled on a first come first served basis.
        Once a show has been posted, no further changes can be made.
        '''
        pass


def publish_show(
        input_file 
):
    """
    simple accessor
    """
    show = ShowNotes()
    show.set_input_file( input_file )
    #TODO: not finished yet

    
