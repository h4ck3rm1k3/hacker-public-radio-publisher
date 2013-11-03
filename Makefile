check : lint flake
	echo 
lint :
	~/.local/bin/pylint --output-format=parseable *.py

flake :
	~/.local/bin/pyflakes  *.py
