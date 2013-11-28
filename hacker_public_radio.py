u'''
python module for HPR broadcasting
based on :http://hackerpublicradio.org/README.txt
# Version 11: 2013-10-31T19:42:37Z (Thursday)

Templating using jinja
http://jinja.pocoo.org/docs/

code :
copyright 2013 James Michael DuPont
distributed under the AGPL v3

'''
import audiotools
from audiotools.flac import (
    Flac_STREAMINFO,
    Flac_VORBISCOMMENT)
from jinja2 import Environment
from jinja2 import PackageLoader
import ftputil
import getopt
import glob
import os
import os.path
import pprint
import re
import secret as _secret  # passwords
import sys
import tarfile
import logging
import shutil

#logging.basicConfig(filename='HPR.log',level=logging.DEBUG)
logging.basicConfig(stream=sys.stdout,level=logging.DEBUG)

def encoding_progress_update(position, chunk):
    u'''
    called when flac encoding has updated its progress
    '''
    print position, chunk

def ftp_upload_cb(chunk):
    u'''
    callback when a chunk is uploaded
    '''
    print "uploaded chunk ."

class AudioFile(object):
    u'''
    Audio file, encapsulates all the audio files methods
    '''
    def __init__(self):
        '''
        constructor
        '''
        self.input_file = None
        self.audio_file = None
        self.audio_metadata = None
        self._format = "FLAC"
        # the audio metdata
        self.metadata = {}

    @property
    def file_format(self):
        '''
        get property of file format,
        will always be flac for now
        will want to support wav files and conversions,
        so if this is not flac, then we will convert it for the user
        '''
        return self._format

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
        self.metadata['md5sum'] = str(streaminfo.md5sum)
        self.metadata['total_sample'] = streaminfo.total_samples
        self.metadata['bits_per_sample'] = streaminfo.bits_per_sample
        self.metadata['channels'] = streaminfo.channels
        self.metadata['sample_rate'] = streaminfo.sample_rate
        self.metadata['file_size'] = os.path.getsize(self.input_file)

        comments = self.audio_metadata.get_block(Flac_VORBISCOMMENT.BLOCK_ID)
        for comment in comments.comment_strings:
            (tag, value) = comment.split(u"=", 1)
            self.metadata[tag] = value

    def add_intro_outtro(self, output_filename):
        '''
        output_filename = self.get_filename() + ".flac"

        Please add the intro and outro clips.
        http://audiotools.sourceforge.net/install.html
        prepend intro.flac
        append outro.flac
        '''

        if (os.path.exists(output_filename)):
            return

        output_filename = audiotools.Filename(output_filename)

        intro = audiotools.open_files(['intro.flac'])
        content = audiotools.open_files([self.input_file])
        outro = audiotools.open_files(['outro.flac'])

        audiofiles = [
            intro[0],
            content[0],
            outro[0],
        ]

        audio_type = audiotools.filename_to_type("intro.flac")
        metadata = content[0].get_metadata()
        output_class = audio_type
        # print audiofiles
        pcms = ([af.to_pcm() for af in audiofiles])
        # print [r.bits_per_sample for r in pcms]

        encoded = output_class.from_pcm(
            str(output_filename),
            audiotools.PCMReaderProgress(
                audiotools.PCMCat(pcms),
                sum([af.total_frames() for af in audiofiles]),
                encoding_progress_update),
            # output_quality,
            total_pcm_frames=sum([af.total_frames() for af in audiofiles]))
        encoded.set_metadata(metadata)

    def get_input_file(self):
        u'''
        get attribute
        '''
        return self.input_file

    def set_input_file(self, filename):
        u'''
        set attribute 
        '''
        self.input_file = filename

    def read_audio_files():
        self.audio_file.read_file()
        # read metadata
        self.audio_file.read_metadata()


    def get_format(self):
        return self._format

    def get_dict(self):
        u'''
        turn the show into a dictionary
        for the template system
        '''
        mydict =   self.metadata
        mydict["format"] =self.get_format()
        mydict["input_file"] = self.get_input_file()

        return mydict


class HPRFtp (object):
    '''
    wrapper for the hpr ftp site, takes a show and processes it.
    '''

    def __init__(self, show):
        self._show = show
        self._host = None # call login

    @property
    def show(self):
        """
        returns the show
        """        
        return self._show

    @property
    def secret(self):
        """
        returns the secret from the show
        """        
        return self.show.secret

    @property 
    def host (self):
        """
        logs in or returns the last one
        TODO: add a logout function 
        """        
        if self._host :
            return self._host
        else:
            return self.login()

    def login(self):
        '''
        create a host object
        '''
        server = self.secret.get_hpr_ftp_server()
        user = self.secret.get_hpr_ftp_username()
        password = self.secret.get_hpr_ftp_password()

        self._host = ftputil.FTPHost(server,
                             user,
                             password)

    def ls_main_ftp(self):
        '''
        ftputil
        '''
        names = self.host.listdir("/temp_dir_please_ignore/")
        for name in names:
            print "/temp_dir_please_ignore/" + name

    def remove_temp(self, host):
        '''
        remove the temp dir from the ftp server
        '''
        names = self.host.listdir("/temp_dir_please_ignore/")
        for name in names:
            print " to remove /temp_dir_please_ignore/" + name
            host.remove("/temp_dir_please_ignore/" + name)

    def put_main_ftp(self, force=False):
        '''
        ftputil
        '''
        
        path = '/temp_dir_please_ignore'
        try:
            self.host.mkdir(path)
        except Exception, exp:
            pass

        names = self.host.listdir("/temp_dir_please_ignore/")

        files = self.show.get_file_list()
        for filename in files:

            if (filename in names):
                if (not force):
                    print "skip existing %s" % filename
                    continue
            try:
                self.host.upload(filename,
                            path + "/" + filename,
                            mode='',
                            callback=ftp_upload_cb)
            except Exception, exp:
                print (str(exp))
                pass


class ShowNotes(object):

    u'''
    SHOWNOTES:
    All shows must include an associated show note text file. We
    will use this information to fill out the website. The
    headings of the file must be as follows:
    '''

    def __init__(self):
        '''
        constructor
        '''
        self.secret = _secret
        self.metadata = {}
        self.template = None
        self.file_list = []
        self.audio_file = AudioFile()
        self.show_name = None
        self._project_dir = None

    def get_project_name(self):
        logging.info('get project name: %s ' % self._project_name) 
        return self._project_name

    def set_project_name(self, value):
        logging.info('set project name: %s ' % value) 
        self._project_name = value
        self.set_name(value)

    def get_temp_flac_file(self):
        return self.get_project_dir() + "/" + "recording.flac" 

    def use_flac_file(self, source):
        dest = self.get_project_dir() + "/" + "recording.flac" 
        logging.info('copy from %s to %s' % (source, dest)) 
        if (not source == dest):
            shutil.copyfile(source, dest)

    def get_config_file_name(self):
        return self.get_project_dir() + "/config.py"

    def write_config(self):
        filename = self.get_config_file_name()
        fileobj = open(filename, "w")
        data = self.get_dict()
        data['project_dir'] = self.get_project_dir()
        data['project_name'] = self.get_project_name()
        string = pprint.pformat(data)
        fileobj.write(string)
        fileobj.close()

    def read_config(self):
        filename = self.get_config_file_name()

        fileobj = open(filename)
        data = fileobj.read()
        print (data)
        obj = eval(data)
        if 'project_dir' in obj:
            self.set_project_dir( obj['project_dir'])
        if 'project_dir' in obj:
            self.set_project_dir( obj['project_dir'])

        if 'audio_input_file' in obj:
            self.audio_file.set_input_file = obj['audio_input_file']

        if 'format' in obj:
            self.audio_file.set_format = obj['format']
            
        for (    pair) in (
            [
                [ 'explicit'        , "Explicit"            ],
            [ "template_file", "template_file"          ], 
            [ 'twitter_summary' , "Twitter Description" ],
            [ 'host_email_address', 'Artist Email' ],
            [ 'host_handle',  'Artist Handle' ],
            [ 'host_name',  'ARTIST' ],
            [ 'host_number', 'Artist Number'],
            [ 'intro_added', "Contains Intro"],
            [ 'license', "License"],
            [ 'series', "Series"],
            [ 'shownotes_text', "COMMENTS"],
            [ 'slot', "Slot"],
            [ 'tags' , "Tags"],
            [ 'title', "TITLE"]
            ]
        ):
            logging.info('check metadata %s ' % str(pair) )
            (name,    metadata_name) = pair

            if name in obj:
                value = obj[name]
                self.set_metadata(metadata_name, value)



    def create(self, name):
        # create a project dir
        self.set_project_name(name)
        # make dirs
        logging.info('project dir %s ' % self.get_project_dir()) 
        if not os.path.exists(self.get_project_dir()):
            os.makedirs(self.get_project_dir())
        self.write_config()

    def read_project(self, project_name):
        self.set_project_name(project_name)
        self.read_config()

    def record(self, project_name):
        '''
        record a project
        '''
        self.read_project(project_name)
        filename = self.get_temp_flac_file
        command = "sox -b 24 -t alsa default %s" % filename
        print (command)
        os.system(command)

    def playback(self, project_name):
        self.read_project(project_name)
        filename = self.get_temp_flac_file
        command = "mplayer %s" % filename
        print (command)
        os.system(command)
        
    def get_project_dir(self):
        if self._project_dir is None :
            self._project_dir = "./projects/%s" % self.get_project_name()
        return self._project_dir

    def set_project_dir(self, value):
        self._project_dir = value


    def get_metadata(self, name, default=None):
        '''
        get one field from the metadata
        '''
        if name in self.metadata:
            value = self.metadata[name]
            logging.debug("get metadata name(%s)=value(%s)" % (name,value))
            return value
        else:
            self.metadata[name] = default  # store it for later use
            logging.debug("setting metadata name(%s) to default(%s)" % (name,default))
            return default

    def set_metadata(self, name, value):
        '''
        set one field from the metadata cache,
        TODO: update the flac file as well
        '''
        self.metadata[name] = value
        logging.debug("Name %s=value:%s" % (name,value))
    # acccessors for metadata

    def get_html(self):
        u'''
         You may also include very basic validated XHTML.
         See the example file on the ftp server.
         PLEASE USE THE TEMPLATE FILES FROM THE FTP SERVER.
         http://hackerpublicradio.org/sample_shownotes.html
         http://hackerpublicradio.org/sample_shownotes.txt
        '''
        loader = PackageLoader('hpr', 'templates')
        env = Environment(loader=loader)
        template_file = self.get_metadata(
            "template_file",
            default="shownotes.tpl"
        )
        # print template_file
        template = env.get_template(template_file)

        # Finally, process the template to produce our final text.
        html = template.render(self.get_dict())
        return html

    def emit_html(self):
        u'''
        create the the html
        '''
        html_file = self.get_filename() + ".html"
        html = self.get_html()
        output_file = open(html_file, "w")
        output_file.write(html)
        output_file.flush()
        output_file.close()
        self.add_file(html_file)

    def get_dict(self):
        u'''
        turn the show into a dictionary
        for the template system
        '''
        mydict= {
            "host_name": self.get_host_name(),
            "host_handle": self.get_host_handle(),
            "host_number": self.get_host_number(),
            "host_email_address": self.get_host_email_address(),
            "license": self.get_license(),
            "title": self.get_title(),
            "slot": self.get_slot(),
            "series": self.get_series(),
            "tags": self.get_tags(),
            "explicit": self.get_explicit(),
            "twitter_summary": self.get_twitter_summary(),
            "format": self.get_format(),
            "shownotes_text": self.get_shownotes_text(),
            "filename": self.get_filename(),
            "intro_added": self.get_intro_added(),
            "audio_file" : self.audio_file.get_dict(), 
        }

#            "input_file": self.get_input_file(),
        
        return mydict

    def get_host_name(self):
        u'''
        returns the name of the show host
        '''
        return self.get_metadata("ARTIST") or self.secret.get_host_fullname()


    def get_host_handle(self):
        u'''
        returns the handle of the show host
        '''
        return self.get_metadata("Artist Handle") or self.secret.get_host_name()

    def get_host_number(self):
        u'''
        get the artist number
        '''
        return self.get_metadata("Artist Number") or self.secret.get_host_id()

    def get_host_email_address(self):
        u'''
        1. Hostname and email address:
        First Lastname (email.nospam@nospam.gmail.com)
        '''
        return self.get_metadata("Artist Email") or self.secret.get_host_email()

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

    def set_title(self, value):
        u'''
        setter for the TITLE field
        '''
        return self.set_metadata("TITLE", value)

    def get_title(self):
        u'''
        2. Show Title: The title of your show
        '''
        return self.get_metadata("TITLE") or "NONE"

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
        return self.get_metadata("Slot", default="Next Available Slot") or "NONE"

    def get_series(self):
        u'''
         5. Series
        '''
        return self.get_metadata("Series", default= "NONE")

    def set_series(self,value):
        u'''
         5. Series
        '''
        return self.set_metadata("Series", value)

    def get_tags(self):
        u'''
        TODO: where do they come from?
        '''
        return self.get_metadata("Tags") or "NONE"

    def add_tags(self,value):
        u'''
         5. tag
        '''
        tags= self.get_metadata("Tags") or []
        tags.append(value)
        return self.set_metadata("Tags", tags)

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
        return self.get_metadata("Twitter Description") or self.get_title()[0:144]

    def get_format(self):
        u'''
        FORMATS:
        We will encode the MP3, ogg and spx formats.
        We prefer FLAC File format (Best - Level 8), 24 Bit, with
        a Project Rate of 44100 Hz but we will accept anything as
        long as it's audible. Please upload a media file in the
        highest quality you have.
        We mix down to mono by default so if you want stereo then
        make note of it in the show.
        '''
        return self.audio_file.get_format()

    def set_format(self, value):
        return self.audio_file.set_format(value)

    def get_shownotes_text(self):
        '''
        we store the show notes in the comment metadata
        '''
        return self.get_metadata("COMMENTS") or "NONE"

    def set_shownotes_text(self, value):
        '''
        override the shownotes
        '''
        self.set_metadata("COMMENTS", value)

    def load_shownotes_from_file(self, filename):
        '''
        reads the shownotes from a file
        '''
        logging.info('to load shownotes file %s ' % filename) # 
        if (os.path.exists(filename)):
            fileobj = open(filename)
            notes = fileobj.read()
            self.set_shownotes_text(notes)

    def print_config(self):
        '''
        prints the config
        '''
        filename = self.get_config_file_name()        
        fileobj = open(filename)
        notes = fileobj.read()
        print notes

    def edit_shownotes(self):
        '''
        edit the shownotes
        '''
        filename = self.get_filename() + ".txt"
        command = "emacs %s" % filename
        stat = os.system(command)
        if (stat == 0):
            self.load_shownotes_from_file(filename)

    def load_shownotes(self):
        '''
        edit the shownotes
        '''
        filename = self.get_filename() + ".txt"
        self.load_shownotes_from_file(filename)


    @property 
    def input_file(self):
        if self.audio_file:
            return self.audio_file.input_file

    def set_name(self, name):
        self.show_name = name 
        flac_file_name = self.get_temp_flac_file()
        self.audio_file.set_input_file(flac_file_name)

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

        infilename = self.show_name
        filename = "%s-%s-%s" % (
            host_number,
            host_name,
            infilename
        )
        filename = filename.replace(" ", "_")
        filename = re.sub(r'[^A-Za-z0-9_-]', '_', filename)

        return self.get_project_dir() + "/" + filename


    def add_intro_outtro(self, output_filename):
        '''
        coordinates
        '''
        output_filename = self.get_filename() + ".flac"
        self.audio_file.add_intro_outtro(output_filename)
        self.set_intro_added()

    def set_intro_added(self):
        '''
        has the intro been added to the file?
        turned on if you call the add intro method
        '''
        self.set_metadata("Contains Intro", "Y")

    def get_intro_added(self):
        '''
        4. Intro and Outro Added:
        YES or NO
        '''
        value = self.get_metadata("Contains Intro", default="N")
        print "intro added value %s " % value
        if value[0] == "Y":
            return "Yes"
        return "No"


    def announce_mailing(self):
        '''
        MAILINGLIST:
        send mail to mailing list
        If you are not already on our mailing list you can join it
        by going to
        http://hackerpublicradio.org/mailman/listinfo/hpr_hackerpublicradio.org
        '''
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
        '''
        adds a file to the list of files to be uploaded in the show
        '''
        self.file_list.append(filename)


    def add_directory_as_tgz(self, dirname):
        '''
        adds a whole directory as tar gz file to the list
        this is good for packing up source code and things.
        '''
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
        '''
        produce the file list and add the flac file to it.
        '''
        temp_list = self.file_list
        temp_list.append(self.get_filename() + ".flac")
        return temp_list



def usage():
    print (
        "--help \n"
        "--create=project name  : create the project \n"
        "--record=project name  : record this projects audio file \n"
        "--playback=projectname : playback the recorded audio file \n"
        "--publish\n",
        "--load=name\n",
        "--save\n",
        "--series=X\n",
        "--shownotes=\n",
        "--shownotes-file=\n",
        "--shownotes-load\n",
        "--shownotes-editor\n",
        "--summary=\n",
        "--tag=\n",
        "--title=\n",
        "--print-config\n",
        "--use-flac=flacfile copy this file into the working directoy\n"
        "\n"
    )



def main():
    project = ShowNotes()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:r:p:x:", ["help",
                                                               "create=",
                                                               "record=",
                                                               "playback=",
                                                               "publish",
                                                               "load=",
                                                               "save",
                                                               "series=",
                                                               "shownotes=",
                                                               "shownotes-file=",
                                                               "summary=",
                                                               "tag=",
                                                               "title=",
                                                               "shownotes-editor",
                                                               "shownotes-load",
                                                               "print-config",
                                                               "use-flac=",
                                                               "emit-html",
                                                               ])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for o, a in opts:
        if o == "-v":
            project.verbose = True

        elif o in ("-h", "--help"):
            usage()
            sys.exit()

        elif o in ("-c", "--create"):
            logging.info('create project %s ' % a) # 
            project.create(a)

        elif o in ("--load"):
            logging.info('load project %s ' % a) # 
            project.read_project(a)

        elif o in ("--save"):
            logging.info('save project %s ' % a) # 
            project.write_config()

        elif o in ("-r", "--record"):
            project.record(a)

        elif o in ("-x", "--publish"):
            project.record(a)

        elif o in ("-p", "--playback"):
            project.playback(a)

        elif o in ("--series"):
            project.set_series(a)

        elif o in ("--shownotes-file"):
            project.load_shownotes_from_file(a)

        elif o in ("--shownotes-editor"):
            project.edit_shownotes()

        elif o in ("--shownotes-load"):
            project.load_shownotes()

        elif o in ("--shownotes"):
            project.set_shownotes(a)

        elif o in ("--summary"):
            project.set_twitter_summary(a)

        elif o in ("--tag"):
            project.add_tags(a)

        elif o in ("--title"):
            project.set_title(a)

        elif o in ("--use-flac"):
            project.use_flac_file(a)

        elif o in ("--print-config"):
            project.print_config()

        elif o in ("--emit-html"):
            project.emit_html()

        else:
            assert False, "unhandled option %s" % o


if __name__ == "__main__":
    main()

