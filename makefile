test:
	/usr/bin/virtualenv env --no-site-packages
	. env/bin/activate; \
	/usr/bin/pep8 bollocks.py; \
	python setup.py install; \
	python bollocks.py --test
clean:
	rm -rf env dist build
	rm -rf bollocks.egg-info
