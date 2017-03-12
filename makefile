test:
	#/usr/bin/virtualenv env --no-site-packages
	. env/bin/activate; \
	/usr/bin/pep8 bollocks.py; \
	python setup.py install; \
	python bollocks.py --test
travis-test:
	sudo python setup.py install
	/usr/local/bin/pep8 bollocks.py
	python bollocks.py --test
clean:
	rm -rf env
