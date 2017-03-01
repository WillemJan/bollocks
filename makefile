test:
	flake8 bollocks.py
	python bollocks.py --test
travis-test:
	sudo python setup.py install
	flake8 bollocks.py
	python bollocks.py --test
