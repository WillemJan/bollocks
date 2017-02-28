test:
	sudo python setup.py install
	sudo mkdir -p /led
	sudo mount -o remount,size=10M /dev/shm
	sudo mount /run/shm /led -o bind
	. example/blink.sh
	. example/fade.sh
	sudo python bollocks.py
