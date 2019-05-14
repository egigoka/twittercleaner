print("init...", end="\r")
import sys
import pyautogui
from commands import *
import gui

__version__ = "0.7.17"


class State:
    region = None


pyautogui.FAILSAFE = False
gui.State.move_duration = 0.5
gui.State.sleep_before_click = 0.0
gui.State.sleep_before_locate = 0.0
pyautogui.PAUSE = 0.0
gui.State.step = 1
gui.State.hotkey_interval = 0.0
gui.State.confidence = 1


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


def activate_twitter_page(confidence=1):
    gui.Click.left(gui.move(gui.wait_locate("backgroundcolor",
                                            every=0.2, timeout=5,
                                            step=1,
                                            confidence=confidence)))


def remove_retweet():
    retweet_pos = gui.wait_locate("retweet", every=0.2, timeout=2, safe=True)
    if retweet_pos:
        gui.Click.left(gui.move(retweet_pos))
        Print.colored(f"Un-retweeted {Removed_retweets.add()} tweets!", "green")
        Time.sleep(1)
        return True
    return False


def remove_tweet():
    arrow_pos = gui.wait_locate("arrowdown", every=0.2, timeout=5, safe=True)
    if arrow_pos:
        gui.Click.left(gui.move(arrow_pos))
        deletetweet_white = gui.wait_locate("deletetweet_white",
                                            every=0.2, timeout=5, safe=True)
        if deletetweet_white:
            gui.Click.left(gui.move(deletetweet_white))
            deletetweet_red = gui.wait_locate("deletetweet_red",
                                              every=0.2, timeout=5, safe=True)
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
    gui.wait_locate("pageloaded", every=0.2, timeout=2, safe=True)


hats = ['hat2', 'hat1']


def go_to_hat():

    gui.hotkey("ctrl", "alt", "shift", "pgup")
    gui.multiple_hotkey(6, "pgup")

    Time.sleep(1)

















print(f"twittercleaner v{__version__}")
print(f"gui v{gui.__version__}")

### gui.locate region ###
# todo
### end gui.locate region ###

timer = Bench("Tweet deleted in", quiet=False)

cnt = ID()

if __name__ == "__main__":
    activate_twitter_page()
    while True:
        any_tweet_deleted = False
        if remove_retweet():
            any_tweet_deleted = True
        elif remove_tweet():
            any_tweet_deleted = True
        else:
            activate_twitter_page()
            Time.sleep(1)
            gui.hotkey("pgdn")
            gui.multiple_hotkey(10, "down")
        if any_tweet_deleted:
            # go_to_hat()
            # gui.multiple_hotkey(2, "pgdn")
            timer.end(start_immediately=True)
        if cnt.get() % 50 == 2:
            refresh_page(activate=True)
            go_to_hat()
            gui.multiple_hotkey(Random.integer(1,8), "pgdn")

