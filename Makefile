test2:
	PYTHONPATH=. python tests/__init__.py

test:
	python ./setup.py test

check : lint flake
	echo 
lint :
	~/.local/bin/pylint --output-format=parseable *.py

flake :
	~/.local/bin/pyflakes  *.py
