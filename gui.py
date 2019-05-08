#! python3
# -*- coding: utf-8 -*-
import sys
import os
import bootstrapping_module
try:
	import cv2
except ImportError:
	os.system("pip install opencv-python")
try:
	import numpy
except ImportError:
	os.system("pip install numpy")
import pyautogui
from commands import *


__version__ = "1.6.0"

class State:
	move_duration = 0.5
	sleep_before_click = 0.1
	sleep_before_locate = 0.1
	
	buttons_pics_folder = Path.combine(".", "buttonpics")  # картиночки
	
	# speed
	grayscale = True  # if grayscale mode is on, convert screen and button images to
	                  # grayscale in runtime to the locate functions to give a slight
					  # speedup (about 30%-ish)
	step = 2  # step == 2 skips every other row and column = ~3x faster but prone to miss
	hotkey_interval = 0.0  # interval between pressing keys
	
	confidence = 0.999
	
	quiet = False
	get_img_name_quiet = True
	log_object_debug = False
	debug_step = False
	debug_grayscale = False
	debug_confidence = True


class Click:
	@staticmethod
	def click(button, position):
		Time.sleep(State.sleep_before_click, quiet_small=True)
		if position:
			pyautogui.click(x=position[0],y=position[1],button=button)
		else:
			pyautogui.click(button=button)
		if not State.quiet:
			print("click mouse " + button)

	@classmethod
	def right(cls,position=None):
		cls.click(button='right',position=position)

	@classmethod
	def left(cls,position=None):
		cls.click(button='left',position=position)


def get_img_name(*name_shards):
	if len(name_shards[0]) == 0:
		raise IndexError("first name shard is empty")
	#Print.debug("name_shards",name_shards,"len(name_shards)",len(name_shards),"len(name_shards[0])",len(name_shards[0]))
	imgs = []
	for file in Dir.list_of_files(State.buttons_pics_folder):
		file_is_good = True
		for name_shard in name_shards:
			#print("name_shard",name_shard,"not in","file",file,name_shard not in file)
			if name_shard not in file:
				file_is_good = False
		if file_is_good:
			imgs += [file]
	if len(imgs) == 1:
		if not State.quiet and not State.get_img_name_quiet:
			print("found image", imgs[0], "with shards", name_shards)
		return Path.combine(State.buttons_pics_folder, imgs[0])
	else:
		raise IndexError("found " + str(len(imgs)) + " buttons pics by " + str(name_shards) + " shards: " + str(imgs))


def move(x, y=None, x2=None, y2=None, duration=State.move_duration, tween=pyautogui.easeInOutQuad, rel=False):
	if isinstance(x, tuple):
		if len(x) == 2:
			y = x[1]
			x = x[0]
		elif len(x) == 4:
			y = x[1]
			x2 = x[2]
			y2 = x[3]
			x = x[0]
	if x2 and y2:
		x,y = pyautogui.center((x,y,x2,y2))
	if not State.quiet:
		if rel:
			how = "relative"
		else:
			how = "to"
		print("moved mouse", how, x, y)

	if rel:
		pyautogui.moveRel(x, y, duration=duration, tween=tween)
	else:
		pyautogui.moveTo(x, y, duration=duration, tween=tween)


def locate_by_shards(*name_shards, safe=False, timer=False,
					grayscale=None, step=None, confidence=None):
	if grayscale is None:
		grayscale = State.grayscale
	if step is None:
		step = State.step
	if confidence is None:
		confidence = State.confidence
	assert isinstance(grayscale, bool)
	assert step in (1,2)
	assert isinstance(confidence, float)
	Time.sleep(State.sleep_before_locate, quiet_small=True)
	name = get_img_name(*name_shards)
	filename = os.path.split(name)[1]
	Print.rewrite(f"Locating {filename} {CLI.wait_update(quiet=True)}")
	retry_cnt = 0
	position = None
	if State.debug_step:
		Print.rewrite()
		print("step", step, "State.step", State.step)
	if State.debug_grayscale:
		Print.rewrite()
		print("grayscale", grayscale, "State.grayscale", State.grayscale)
	if State.debug_confidence:
		Print.rewrite()
		print("confidence", confidence, "State.confidence", State.confidence)
	try:
		position = pyautogui.locateOnScreen(name, 
											grayscale=grayscale, 
											step=step,
											confidence=confidence)
	except OSError:
		pass
	if (position is None) and not safe:
		raise IndexError("not located " + filename + " ")
	if not State.quiet:
		message = "not located " + filename
		if position:
			message = Str.substring(message, before="not ") + " on " + str(position)
		elif timer:
			message += " timer " + str(Timer_wait_locate.get())
		Print.rewrite()
		print(message)
	return position


def locate(*names, safe=False, timer=False, 
			grayscale=None, step=None, confidence=None):
	output_position = None
	for name in names:
		output_position = locate_by_shards(name, safe=True, timer=timer,
											grayscale=grayscale, step=step, confidence=confidence)
		if output_position:
			return output_position
	if not safe:
		raise IndexError("nothing found from " + str(names) + " names")


Timer_wait_locate = Bench(quiet=True)


def wait_locate(*names, every=1, timeout=60, safe=False, 
				grayscale=None, step=None, confidence=None):
	if State.log_object_debug:
		Print.debug("wait_locate started")
	timeout_reached = False
	position = None
	Timer_wait_locate.start()
	while not timeout_reached and not position:
		position = locate(*names, safe=True, timer=True, 
							grayscale=grayscale, step=step, confidence=confidence)
		timeout_reached = Timer_wait_locate.get() > timeout
		Time.sleep(every, quiet_small=True)
	if timeout_reached and not position and not safe:
		raise RuntimeError("timeout " + str(timeout) + " reached while searching for " + str(names))
	return position


def hotkey(*args, quiet=False):
	pyautogui.hotkey(*args, interval=State.hotkey_interval)
	if not quiet:
		print("pressed", str(args))


def multiple_hotkey(cnt, *keys, quiet=False):
	if not quiet:
		print(f"pressed '{keys}' {cnt} times")
	for i in range(cnt):
		hotkey(*keys, quiet=True)


def message(text, title='some window', button='oh no'):
	pyautogui.alert(text=text, title=title, button=button)


class Scroll:  # doesnt work good at new windows

	def scroll(value, up):
		value = int(value)
		if not up:
			value = 0-value
		pyautogui.vscroll(clicks=value)
		print("scrolled", value)

	@classmethod
	def up(cls, value=100):
		cls.scroll(value, up=True)

	@classmethod
	def down(cls, value=100):
		cls.scroll(value, up=False)
