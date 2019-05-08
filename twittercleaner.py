print("init...", end="\r")
import sys
import pyautogui
from commands import *
import gui

__version__ = "0.6.1"


class State:
	stop_beloved = 4
	pass
	# speed
	# gui.locate_region = True


pyautogui.FAILSAFE = False
gui.State.move_duration = 0.5
gui.State.sleep_before_click = 0.0
gui.State.sleep_before_locate = 0.0
pyautogui.PAUSE = 0.0
gui.State.grayscale = True
gui.State.step = 2
gui.State.hotkey_interval = 0.0

Print.colored("Debug step", "red")


class CounterInFile:
	def __init__(self, file_name):
		self.file_name = file_name
		self.cnt = int(File.read(self.file_name))
	
	def add(self):
		self.cnt += 1
		File.write(self.file_name, str(self.cnt), mode="w")
		return self.cnt


Removed_retweets = CounterInFile("retweets_deleted.txt")
Removed_tweets = CounterInFile("tweets_deleted.txt")


def activate_twitter_page(confidence):
	gui.Click.left(gui.move(gui.wait_locate("backgroundcolor_no_overlay", 
								"backgroundcolor_with_overlay", 
								every=1, timeout=10,
								grayscale=False,
								step=1,
								confidence=confidence)))
	#gui.multiple_hotkey(16, "up")
	#gui.multiple_hotkey(8, "down")

confidence_current = 1.0
confidence_change = 0.5
while True:
	Print.rewrite()
	print(confidence_current)
	result = gui.wait_locate("backgroundcolor_no_overlay", 
								"backgroundcolor_with_overlay", 
								every=1, timeout=0, safe=True,
								grayscale=False,
								step=1,
								confidence=confidence_current)
	confidence_change /= 2
	if result == (0,0,7,4):
		confidence_current += confidence_change
	elif result is None:
		confidence_current -= confidence_change
	else:
		print("fuck", result)
		sys.exit(1)


def remove_retweet():
	retweet_pos = gui.wait_locate("retweet", every=1, timeout=1, safe=True)
	if retweet_pos:
		gui.Click.left(gui.move(retweet_pos))
		Print.colored(f"Un-retweeted {Removed_retweets.add()} tweets!", "green")
		Time.sleep(1)
		return True
	return False


def remove_tweet():
	arrow_pos = gui.wait_locate("arrowdown", every=1, timeout=18, safe=True)
	if arrow_pos:
		gui.Click.left(gui.move(arrow_pos))
		deletetweet_white = gui.wait_locate("deletetweet_white2", 
										"deletetweet_white1", 
										every=1, timeout=18, safe=True)
		if deletetweet_white:
			gui.Click.left(gui.move(deletetweet_white))
			deletetweet_red = gui.wait_locate("deletetweet_red", every=1, timeout=18, safe=True)
			if deletetweet_red:
				gui.Click.left(gui.move(deletetweet_red))
				Print.colored(f"Deleted {Removed_tweets.add()} tweets!", "green")
				return True
	return False


def refresh_page(activate=True):
	if activate:
		activate_twitter_page()
	gui.hotkey('f5')
	Time.sleep(2)
	gui.wait_locate("pageloaded", every=1, timeout=60, safe=True)


print(f"twittercleaner v{__version__}")
print(f"gui v{gui.__version__}")

### save beloved tweets ###
activate_twitter_page()
sys.exit()
while True:
	gui.hotkey("ctrl", "alt", "shift", "pgup")  # try to go to top
	if gui.locate("hat2", "hat1", safe=True, 
					grayscale=False, step=1):
		break
	gui.multiple_hotkey(5, "pgup")
	if gui.locate("hat2", "hat1", safe=True,
					grayscale=False, step=1):
		break
sys.exit(0)
beloved_cnt = 0
while beloved_cnt < State.stop_beloved:
	beloved_cnt += 1
#while True:
	if gui.locate("belovedtweet", safe=True,
					grayscale=False, step=1):
		break
	gui.hotkey("pgdn")
### end save beloved tweets ###

### gui.locate region ###
print(gui.locate("separator",
					grayscale=False, step=1))
gui.State.step = stepbak
print(gui.locate("separator",
					grayscale=False, step=1))
sys.exit(0)
### end gui.locate region ###

timer = Bench("Tweet deleted in", quiet=False)

if __name__ == "__main__":
	while True:
		any_tweet_deleted = False
		activate_twitter_page()
		if remove_retweet():
			refresh_page()
			any_tweet_deleted = True
		elif remove_tweet():
			any_tweet_deleted = True
		else:
			gui.hotkey("down")
			refresh_page()
		if any_tweet_deleted:
			timer.end(start_immediately=True)
