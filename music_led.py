import pyaudio
import struct
import math
import os
import time
import random
import zmq
import sys

# use pavucontrol to finetune (once running..)

hosts = ["kast1", "totem1", "touch1", "slaap0"]


def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

 
INITIAL_TAP_THRESHOLD = 0.010
FORMAT = pyaudio.paInt16 
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 2
RATE = 44100  
INPUT_BLOCK_TIME = 0.006
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)

OVERSENSITIVE = 15.0/INPUT_BLOCK_TIME                    

UNDERSENSITIVE = 120.0/INPUT_BLOCK_TIME # if we get this many quiet blocks in a row, decrease the threshold

MAX_TAP_BLOCKS = 0.15/INPUT_BLOCK_TIME # if the noise was longer than this many blocks, it's not a 'tap'

def get_rms(block):

    # RMS amplitude is defined as the square root of the 
    # mean over time of the square of the amplitude.
    # so we need to convert this string of bytes into 
    # a string of 16-bit samples...

    # we will get one short out for each 
    # two chars in the string.
    count = len(block)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, block )

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
    # sample is a signed short in +/- 32768. 
    # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n

    return math.sqrt( sum_squares / count ) * 200

pa = pyaudio.PyAudio()                                 #]
                                                       #|
stream = pa.open(format = FORMAT,                      #|
         channels = CHANNELS,                          #|---- You always use this in pyaudio...
         rate = RATE,                                  #|
         input = True,                                 #|
         frames_per_buffer = INPUT_FRAMES_PER_BLOCK)   #]

tap_threshold = INITIAL_TAP_THRESHOLD                  #]
noisycount = MAX_TAP_BLOCKS+1                          #|---- Variables for noise detector...
quietcount = 0                                         #|
errorcount = 0                                         #]         


def sr():
    try:                                                    #]
        block = stream.read(INPUT_FRAMES_PER_BLOCK)         #|
        return block
    except IOError, e:                                      #|---- just in case there is an error!
        errorcount += 1                                     #|
        print( "(%d) Error recording: %s"%(errorcount,e) )  #|
        noisycount = 1                                      #]

a = []
b = []
for i in range(64):
    rgb=[]
    block = sr()
    amplitude1 = int(round(get_rms(block)*100))
    b.append(amplitude1)
    if i > 0:
        if b[i-1] > amplitude1 + 3 or b[i-1] < amplitude1 - 3:
            amplitude1 = b[i-1]
    block = sr()
    amplitude2 = int(round(get_rms(block)*100))
    if amplitude2 > amplitude1 + 3 or amplitude2 < amplitude1 -3:
        amplitude2 = amplitude1
    block = sr()
    amplitude3 = int(round(get_rms(block)*100))
    if amplitude3 > amplitude1 + 3 or amplitude3 < amplitude1 -3:
        amplitude3 = amplitude1
    a.append(rgb_to_hex((amplitude1, amplitude2, amplitude3)))
print(amplitude1, amplitude2, amplitude3)


sok = {}
for h in hosts:
    sok[h] = {}
    sok[h]["c"] = zmq.Context()
    zmq_socket = sok[h]["c"].socket(zmq.PUSH)
    zmq_socket.connect("tcp://%s:4455" % h)
    sok[h]["e"] = zmq_socket

while True:
    for h in hosts:
       try:
           state = {}
           for i in range(0, 64):
                state[i] = [a[i], b[i], 'green', '1', 'normal', '0.1']
           sok[h]["e"].send_json(state, zmq.NOBLOCK)
       except:
           pass

    if random.random() > 0.5:
        d = False
    else:
        d = True
    for i in range(5):
        block = sr()
        amplitude1 = int(round(get_rms(block)*5)) * 2
        block = sr()
        amplitude2 = int(round(get_rms(block)*5)) * 1.3
        if b[i] > amplitude1:
            amplitude1 *= 1.2
        else:
            amplitude2 *= 1.2
        block = sr()
        amplitude3 = int(round(get_rms(block)*2)) * amplitude2
        print(amplitude1, amplitude2*2, amplitude3, a, b[0])
        if d:
            a = [rgb_to_hex((amplitude1, amplitude2, amplitude3*2))] + a
        else:
            if random.random() > 0.5:
                a = [rgb_to_hex((amplitude1, amplitude2*1.6, amplitude3))] + a
            else:
                a = [rgb_to_hex((amplitude1*1.6, amplitude2, amplitude3))] + a
            
        a.pop()

        b = [amplitude1*amplitude2] + b
        b.pop()
