test:
	sudo python setup.py install
	sudo mkdir -p /led
	sudo mknod /dev/spidev0.0 153 0 #major number 153 with a dynamically chosen minor device number
	sudo mount -o remount,size=10M /dev/shm
	sudo mount /run/shm /led -o bind
	sudo python bollocks.py
	. example/blink.sh
	. example/fade.sh
