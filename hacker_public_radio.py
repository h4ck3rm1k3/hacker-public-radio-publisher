u'''
python module for HPR broadcasting
based on :http://hackerpublicradio.org/README.txt
# Version 11: 2013-10-31T19:42:37Z (Thursday)

Templating using jinja
http://jinja.pocoo.org/docs/

'''
import audiotools
from audiotools.flac import (
    Flac_STREAMINFO, 
    Flac_VORBISCOMMENT)
from jinja2 import Environment
from jinja2 import  PackageLoader
import os
import ftputil
import secret # passwords
import os.path
import re
import tarfile
import glob

def progress_update(position, chunk):
    print position, chunk

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
        self.file_list = []

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
        for comment in comments.comment_strings:
            (tag, value) = comment.split(u"=", 1)
            self.metadata[tag] = value


    def get_metadata(self, name, default=None):
        '''
        get one field from the metadata
        '''
        if name in self.metadata :
            return self.metadata[name]
        else:
            self.metadata[name]=default # store it for later use
            return default

    def set_metadata(self, name, value):
        '''
        set one field from the metadata cache,
        TODO: update the flac file as well
        '''
        self.metadata[name]=value

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
        html_file=self.get_filename() + ".html"
        h= self.get_html()
        o = open (html_file,"w")
        o.write(h)
        o.flush()
        o.close()
        self.add_file(html_file)

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
        First Lastname (email.nospam@nospam.gmail.com)
        '''
        return self.get_metadata("Artist Email")

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
        return self.get_metadata("Series")

    def get_tags(self):
        u'''
        TODO: where do they come from?
        '''
        return self.get_metadata("Tags")

    def get_explicit(self):
        u'''
        6. Explicit:
        "Yes", or "Clean" (See iTunes for more information.)
        '''
        return self.get_metadata("Explicit", default="Clean")

    def get_twitter_summary(self):
        u'''
        7. Twitter/Identi.CA Summary:
        '''
        return self.get_metadata("Twitter Description")

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
        return self.get_metadata("COMMENTS")

    def set_shownotes_text(self,value):
        '''
        override the shownotes
        '''
        self.set_metadata("COMMENTS",value)

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
        filename =  "%s-%s-%s" % (
            host_number,
            host_name,
            infilename
        )
        filename = filename.replace(" ","_")
        filename = re.sub(r'[^A-Za-z0-9_-]', '_', filename)
        return filename

## Processing

    def set_intro_added(self):
        self.set_metadata("Contains Intro", "Y")
        
    def get_intro_added(self):
        '''
        4. Intro and Outro Added:
        YES or NO
        '''
        value = self.get_metadata("Contains Intro", default="N")
        print "intro added value %s " % value
        if value[0] == "Y" :
            return "Yes"
        return "No"

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

        intro = audiotools.open_files(    [      'intro.flac'    ])
        content = audiotools.open_files(  [      self.input_file    ])
        outro = audiotools.open_files(    [      'outro.flac'    ])

        audiofiles = [
            intro[0],
            content[0],
            outro[0],
        ]

        AudioType = audiotools.filename_to_type("intro.flac")
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

        self.set_intro_added()

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
            names = host.listdir("/temp_dir_please_ignore/")
            for name in names:
                print "/temp_dir_please_ignore/" + name

    def remove_temp(self, host):
        names = host.listdir("/temp_dir_please_ignore/")
        for name in names:
            print " to remove /temp_dir_please_ignore/" + name
            host.remove("/temp_dir_please_ignore/" + name)

    def put_main_ftp(self, force=False):
        '''
        ftputil
        '''
        s=secret.get_hpr_ftp_server()
        u=secret.get_hpr_ftp_username()
        p=secret.get_hpr_ftp_password()

        with ftputil.FTPHost(s, u, p) as host:
            path = '/temp_dir_please_ignore'
            try :
                host.mkdir(path)
            except:
                pass

            names = host.listdir("/temp_dir_please_ignore/")

            files = self.get_file_list()
            for filename in files :

                if (filename in  names):
                    if (not force) :
                        print "skip existing %s" % filename
                        continue
                try :
                    host.upload(filename, 
                                path + "/" + filename, 
                                mode='', 
                                callback=ftp_upload_cb)
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

    def add_file(self, filename):
        self.file_list.append(filename)

    def load_shownotes_from_file(self, filename):
        f=open(filename)
        notes=f.read()
        self.set_shownotes_text(notes)
        print notes

    def add_directory_as_tgz(self, dirname):
        tarfilename = "%s.tar.gz" % self.get_filename()

        if (not os.path.exists(tarfilename)):
            print("open %s" % tarfilename)
            tar = tarfile.open(tarfilename, "w:gz")
            for filename in glob.glob(dirname + '/*'):
                print("adding %s" % filename)
                tar.add(filename)
            tar.close()
        self.add_file(tarfilename)

    def get_file_list(self):
        temp_list = self.file_list
        temp_list.append(self.get_filename() + ".flac")
        return temp_list


# def publish_show(
#         input_file
# ):
#     """
#     simple accessor
#     """
#     show = ShowNotes()
#     show.set_input_file( input_file )
#     #TODO: not finished yet

import getopt, sys
import os 
def usage():
    print (
        "--help \n"
        "--create=project name  : create the project \n"
        "--record=project name  : record this projects audio file \n"
        "--playback=projectname : playback the recorded audio file \n"
        "\n"
    )

class Project :

    def __init__(self):
        self.project_name =  None
        self.project_dir =  None

    def set_project_name (self, name):
        self.project_name = name
        self.project_dir ="./projects/%s" % self.project_name

    def write_config(self):
        filename = self.project_dir + "/config.py"
        f = open(filename,"w")
        f.write(str(self.__dict__))
        f.close()

    def read_config(self):
        filename = self.project_dir + "/config.py"
        f = open(filename)
        data= f.read()
        print (data)
        obj = eval(data)
        if 'project_dir' in obj:
            self.project_dir = obj['project_dir'] 
        if 'project_dir' in obj:
            self.project_dir = obj['project_dir'] 
                
    def create(self, name):
        # create a project dir    
        self.set_project_name(name)

        # make dirs
        if not os.stat(self.project_dir):
            os.makedirs(self.project_dir)
        self.write_config()

    def get_flac_file(self,project_name):
        self.set_project_name(project_name)
        self.read_config()
        filename = self.project_dir + "/recording.flac"
        return filename

    def record(self, project_name):
        filename =  self.get_flac_file(project_name)
        command = "sox -b 24 -t alsa default %s" % filename
        print (command)
        os.system (command)

    def playback(self, project_name):
        filename =  self.get_flac_file(project_name)
        command = "mplayer %s" % filename
        print (command)
        os.system (command)
    
p = Project()
    
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:r:p:x:", ["help", 
                                                           "create=",
                                                           "record=",
                                                           "playback=",
                                                             "publish="
                                                     ])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    output = None
    verbose = False
    for o, a in opts:
        if o == "-v":
            verbose = True

        elif o in ("-h", "--help"):
            usage()
            sys.exit()

        elif o in ("-c", "--create"):
            p.create(a)

        elif o in ("-r", "--record"):
            p.record(a)

        elif o in ("-x", "--publish"):
            p.record(a)

        elif o in ("-p", "--playback"):
            p.playback(a)

        else:
            assert False, "unhandled option"


if __name__ == "__main__":
    main()
