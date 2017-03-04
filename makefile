test:
	/usr/local/bin/pep8 bollocks.py
	python bollocks.py --test
travis-test:
	sudo python setup.py install
	/usr/local/bin/pep8 bollocks.py
	python bollocks.py --test
