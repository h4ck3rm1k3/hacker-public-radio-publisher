test_publish:
	python hacker_public_radio.py --load test2  --publish

test_three:
	python hacker_public_radio.py --load test2  --add-intro-outro

test_two :
	python ./hacker_public_radio.py --create test2  --use-flac=./projects/hpt_pub/recording.flac  --series="Testing" --tag=Funky --tag=Soul --title="My test show from the command line with a very long title that will be truncated for twitter to 144 chars...... 1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890" --shownotes-load --save --print-config --emit-html --print-config --add-intro-outro


test_append notes :
	python ./hacker_public_radio.py --load test123 --shownotes-load --save --print-config

test_load :
	python ./hacker_public_radio.py --load test123 --use-flac=./projects/hpt_pub/recording.flac --save --print-config

test_new2 :
	python ./hacker_public_radio.py --create test123 --series="Testing" --tag=Funky --tag=Soul --title="My test show from the command line with a very long title that will be truncated for twitter to 144 chars...... 1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890" --shownotes-load --save --print-config

test_editor :
	python ./hacker_public_radio.py  --load test123 --shownotes-editor --save --print-config

test_new :
	python ./hacker_public_radio.py --create test123
	cat projects/test123/config.py




test_html :
	python ./hacker_public_radio.py --load test123  --emit-html --print-config


test_enhance :
	python ./hacker_public_radio.py --load test123 --series="Testing" --tag=Funky --tag=Soul --title="My test show from the command line with a very long title that will be truncated for twitter to 144 chars...... 1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890" --shownotes-load --save --print-config


test_print :
	python ./hacker_public_radio.py --load test123  --print-config


test_append notes :
	python ./hacker_public_radio.py --load test123 --shownotes-load --save --print-config

test_load :
	python ./hacker_public_radio.py --load test123 --use-flac=./projects/hpt_pub/recording.flac --save --print-config

test_new2 :
	python ./hacker_public_radio.py --create test123 --series="Testing" --tag=Funky --tag=Soul --title="My test show from the command line with a very long title that will be truncated for twitter to 144 chars...... 1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890" --shownotes-load --save --print-config

test_editor :
	python ./hacker_public_radio.py  --load test123 --shownotes-editor --save --print-config

test_new :
	python ./hacker_public_radio.py --create test123
	cat projects/test123/config.py


test2:
	PYTHONPATH=. python tests/__init__.py

test:
	python ./setup.py test

check : lint flake
	echo 
lint :
	~/.local/bin/pylint  --output-format=parseable *.py

linte :
	~/.local/bin/pylint -E --output-format=parseable *.py

flake :
	~/.local/bin/pyflakes  *.py

#merge :
#	python ./merge_files.py

autopep8:
	~/.local/bin/autopep8 -v -a -a -a -a  -i *.py

autopep8_ :
	pep8ify -v -w *.py

fixlines:
	~/.local/bin/autopep8 -v --select=E501 --max-line-length=78 -i -a -a -a -a *.py

pep8 :
	~/.local/bin/pep8 *.py
