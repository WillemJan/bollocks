test:
	sudo python setup.py install
	sudo mkdir -p /led
	sudo mount -o remount,size=10M /dev/shm
	sudo mount /run/shm /led -o bind
	sudo python bollocks.py
	. example/blink.sh
	. example/fade.sh
