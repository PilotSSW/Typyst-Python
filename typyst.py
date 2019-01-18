#!/usr/bin/env python3

import sys
import pyaudio
import wave
import os
import glob
import signal
import enum
from threading import Thread
from random import randrange, seed
from pynput.keyboard import Key, Listener

CHUNK = 1024 #! Stream CHUNK size
NUM_KEYS = 86 #! Number of keys on my keyboard
listener = None

#! Instantiate pyaudio
p = pyaudio.PyAudio()

#! A dictionary of tuples of the form (wavfile, stream, lock).
#  length is 26 since there are 26 key sounds.
sounds = {}
filelist = []

#! Keys that require a numerical mapping for association with a file and stream
#  in sounds
other_keys = {
	Key.alt : 0,
	Key.alt_l : 1,
	Key.alt_r : 2,
	Key.alt_gr : 3,
	Key.backspace : 4,
	Key.caps_lock : 5,
	Key.cmd : 6,
	Key.cmd_l : 7,
	Key.cmd_r : 8,
	Key.ctrl : 9,
	Key.ctrl_l : 10,
	Key.ctrl_r : 11,
	Key.delete : 12,
	Key.down : 13,
	Key.end : 14,
	Key.enter : 15,
	Key.esc : 16,
	Key.f1 : 17,
	Key.f2 : 18,
	Key.f3 : 19,
	Key.f4 : 20,
	Key.f5 : 21,
	Key.f6 : 22,
	Key.f7 : 23,
	Key.f8 : 24,
	Key.f9 : 25,
	Key.f10 : 0,
	Key.f11 : 1,
	Key.f12 : 2,
	Key.f13 : 3,
	Key.f14 : 4,
	Key.f15 : 5,
	Key.f16 : 6,
	Key.f17 : 7,
	Key.f18 : 8,
	Key.f19 : 9,
	Key.f20 : 10,
	Key.home : 11,
	Key.left : 12,
	Key.page_down : 13,
	Key.page_up : 14,
	Key.right : 15,
	Key.shift : 16,
	Key.shift_l : 17,
	Key.shift_r : 18,
	Key.space : 19,
	Key.tab : 20,
	Key.up : 21,
	
	# Key.insert : 22,
	# Key.menu : 23,
	# Key.num_lock : 24,
	# Key.pause : 25,
	# Key.print_screen : 0,
	# Key.scroll_lock : 1
	}


class State(enum.Enum):
	default = 0
	hold = 1
	released = 2


def play_sound(n):
	global CHUNK

	(wavfile, stream, state) = sounds[n]

	if state is State.hold:
		return

	stream.start_stream()
	data = wavfile.readframes(CHUNK)
#	data = bytearray(wavfile.readframes(CHUNK))
	
	#! Play stream
	while len(data) > 0:
		stream.write(data, exception_on_underflow=False)
		data = wavfile.readframes(CHUNK)

#		if CHUNK > len(data):
#			SILENCE = chr(0) * CHUNK * wavfile.getnchannels() * 2
#			fill = CHUNK - len(data)
#			data.extend(bytes(str(fill * SILENCE).encode()))
#			stream.write(bytes(data))
#			break
#		stream.write(bytes(data))
#		data = bytearray(wavfile.readframes(CHUNK))

	wavfile.rewind()
	state = State.hold
	stream.stop_stream()
	sounds[n] = (wavfile, stream, state)

	return


def get_key_mapping(key):
	global other_keys, filelist

	if hasattr(key, "char"):
		return ord(key.char) % len(filelist)
	else:
		return other_keys[key]
		
		
#! The action to be performed when a key is pressed
def on_press(key):
	n = get_key_mapping(key)
	t = Thread(target=play_sound, args=(n,))
	t.start()
	t.join()
	print(str(key) + " pressed")
	return


def on_release(key):
	n = get_key_mapping(key)
	(wavfile,stream,state) = sounds[n]

	if key == Key.esc:
		listener.stop()

	state = State.released
	sounds[n] = (wavfile,stream,state)
	print(str(key) + " released")
	return


#! Script entrance point (main loop of the program)
def main():
	global listener

	listener = Listener(on_press=on_press, on_release=on_release)
	listener.start()
	listener.join()

	return


#! Initializes all the files needed for the program
def initialize():
	global p, CHUNK, sounds, filelist
	seed(os.urandom(4))

	try:
		#! Initialize filelists
		filelist = glob.glob("/Users/seanwolford/Developer/Projects/Typyst/res/tw/*.wav")


		#! Initialize streams
		for i, f in enumerate(filelist):
			state = State.default
			macos = pyaudio.PaMacCoreStreamInfo()
			wavfile = wave.open(f,"rb")
			stream = p.open(format=p.get_format_from_width(wavfile.getsampwidth()),
					channels=wavfile.getnchannels(), rate=wavfile.getframerate(),
					input=False, output=True, frames_per_buffer=CHUNK, output_host_api_specific_stream_info=macos)
			sounds[i] = (wavfile, stream, state)

	except IOError as ioe:
		print("IOError: {0}".format(ioe))
	except EOFError as eof:
		print("EOFError: {0}".format(eof))
	
	#! Register the signal handlers
	signal.signal(signal.SIGINT, signal_handler)
	signal.signal(signal.SIGTERM, signal_handler)
	return


#! Terminates all resources that were initalized at the beginning of the
#  program
def terminate():
	global p, listener

	#! Terminate resources in the reverse order in which they were intialized
	for (wavfile, stream, state) in sounds.values():
		wavfile.close()
		stream.stop_stream()
		stream.close()

	#! Terminate pyaudio
	p.terminate()

	listener.stop()
	listener.join()

	return


#! Signal handler for graceful exits
def signal_handler(signal, frame):
	terminate()
	sys.exit(0)
	return


#! If script is being run as main
if __name__ == "__main__":
	initialize()
	main()
	terminate()

