
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
