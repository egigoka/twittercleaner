#! python3
# -*- coding: utf-8 -*-
import sys
import os
import bootstrapping_module
import pyscreeze

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

__version__ = "2.0.0"


class State:
    move_duration = 0.5
    sleep_before_click = 0.1
    sleep_before_locate = 0.1

    buttons_pics_folder = Path.combine(".", "buttonpics")  # картиночки

    # speed
    step = 2  # step == 2 skips every other row and column = ~3x faster but prone to miss
    hotkey_interval = 0.0  # interval between pressing keys

    confidence = 1

    quiet = False
    get_img_name_quiet = True
    log_object_debug = False
    debug_step = False
    debug_confidence = False


class Click:
    @staticmethod
    def click(button, position):
        Time.sleep(State.sleep_before_click, quiet_small=True)
        if position:
            pyautogui.click(x=position[0], y=position[1], button=button)
        else:
            pyautogui.click(button=button)
        if not State.quiet:
            print("click mouse " + button)

    @classmethod
    def right(cls, position=None):
        cls.click(button='right', position=position)

    @classmethod
    def left(cls, position=None):
        cls.click(button='left', position=position)


def get_img_names(*name_shards):
    if len(name_shards[0]) == 0:
        raise IndexError("first name shard is empty")
    # Print.debug("name_shards",name_shards,"len(name_shards)",len(name_shards),"len(name_shards[0])",len(name_shards[0]))
    imgs = []
    for file in Dir.list_of_files(State.buttons_pics_folder):
        file_is_good = True
        for name_shard in name_shards:
            # print("name_shard",name_shard,"not in","file",file,name_shard not in file)
            if name_shard not in file:
                file_is_good = False

        if file_is_good:
            imgs += [Path.combine(State.buttons_pics_folder, file)]
    if not State.quiet and not State.get_img_name_quiet:
        print("found image", imgs[0], "with shards", name_shards)

    return imgs[::-1]

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
        x, y = pyautogui.center((x, y, x2, y2))
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


def screen_size():
    return pyautogui.size()


def locate_by_filename(file_name, safe=False, timer=False,
                       step=None, confidence=None, region=None,
                       cnt=1):
    if step is None:
        step = State.step
    if confidence is None:
        confidence = State.confidence
    assert step in (1, 2)
    Time.sleep(State.sleep_before_locate, quiet_small=True)

    filename = os.path.split(file_name)[1]
    Print.rewrite(f"Locating {filename} {CLI.wait_update(quiet=True)}")
    positions = None
    if State.debug_step:
        Print.rewrite()
        print("step", step, "State.step", State.step)
    if State.debug_confidence:
        Print.rewrite()
        print("confidence", confidence, "State.confidence", State.confidence)
    try:
        added_kwargs = {}
        if confidence:
            added_kwargs["confidence"] = confidence
        positions = pyscreeze.locateAllOnScreen(file_name,
                                                step=step,
                                                **added_kwargs,
                                                region=region,
                                                limit=cnt)
    except OSError:
        pass
    # except someerror if confidence is unexpected (numpy or cv2 not installed)
    if positions is None:
        return
    positions = list(positions)
    if ((positions is None) or (len(positions) == 0)) and not safe:
        raise IndexError("not located " + filename + " ")
    if not State.quiet:
        message = "not located " + filename
        if positions:
            if len(positions) == 1:
                message = Str.substring(message, before="not ") + " on " + str(positions[0])
            elif len(positions) <= 3:
                message = Str.substring(message, before="not ") + " on " + str(positions[:3])
            else:
                message = Str.substring(message, before="not ") + " on " + str(positions[:3]) + "[...]"
        elif timer:
            message += " timer " + str(Timer_wait_locate.get())
        Print.rewrite()
        color = "green"
        if "not" in message:
            color = "red"
        Print.colored(message, color)

    if cnt == 1:
        if positions:
            return positions[0]
    return positions


def locate_by_shards(*name_shards, safe=False, timer=False,
                     step=None, confidence=None, region=None,
                     cnt=1):

    names = get_img_names(*name_shards)

    for name in names:
        output = locate_by_filename(name, safe=safe, timer=timer/len(names),
                                  step=step, confidence=confidence, region=region,
                                  cnt=cnt)
        if len(output) != 0:
            return output




def locate(*names, safe=False, timer=False,
           step=None, confidence=None, cnt=1):
    for name in names:
        output_position = locate_by_shards(name, safe=True, timer=timer,
                                           step=step,
                                           confidence=confidence, cnt=cnt)
        if output_position:
            return output_position
    if not safe:
        raise IndexError("nothing found from " + str(names) + " names")


Timer_wait_locate = Bench(quiet=True)


def wait_locate(*names, every=0.2, timeout=60, safe=False,
                step=None, confidence=None, cnt=1):
    if State.log_object_debug:
        Print.debug("wait_locate started")
    timeout_reached = False
    position = None
    Timer_wait_locate.start()
    while not timeout_reached and not position:
        position = locate(*names, safe=True, timer=True,
                          step=step, confidence=confidence, cnt=cnt)
        timeout_reached = Timer_wait_locate.get() > timeout
        if not position and not timeout_reached:
            Time.sleep(every, quiet_small=True)
    if timeout_reached and not position and not safe:
        raise RuntimeError("timeout " + str(timeout) + " reached while searching for " + str(names))
    return position


def show_region(region, outlineColor=None):
    import pyscreeze

    if outlineColor is None:
        outlineColor = 'red'

    pyscreeze.showRegionOnScreen(region, outlineColor, filename='_showRegionOnScreen.png')


def hotkey(*args, quiet=False):
    pyautogui.hotkey(*args, interval=State.hotkey_interval)
    if not quiet:
        Print.colored("pressed", str(args), "yellow")


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
            value = 0 - value
        pyautogui.vscroll(clicks=value)
        print("scrolled", value)

    @classmethod
    def up(cls, value=100):
        cls.scroll(value, up=True)

    @classmethod
    def down(cls, value=100):
        cls.scroll(value, up=False)


def subimg_location(haystack, needle):
    import re
    haystack = haystack.convert('RGB')
    needle   = needle.convert('RGB')

    haystack_str = haystack.tostring()
    needle_str   = needle.tostring()

    gap_size = (haystack.size[0] - needle.size[0]) * 3
    gap_regex = '.{' + str(gap_size) + '}'

    # Split b into needle.size[0] chunks
    chunk_size = needle.size[0] * 3
    split = [needle_str[i:i+chunk_size] for i in range(0, len(needle_str), chunk_size)]

    # Build regex
    regex = re.escape(split[0])
    for i in range(1, len(split)):
        regex += gap_regex + re.escape(split[i])

    p = re.compile(regex)
    m = p.search(haystack_str)

    if not m:
        return None

    x, _ = m.span()

    left = x % (haystack.size[0] * 3) / 3
    top  = x / haystack.size[0] / 3

    return left, top


def mine_locateAll_opencv(needleImage, haystackImage, limit=10000, region=None, step=1,
                      confidence=0.999):
    """ faster but more memory-intensive than pure python
        step 2 skips every other row and column = ~3x faster but prone to miss;
            to compensate, the algorithm automatically reduces the confidence
            threshold by 5% (which helps but will not avoid all misses).
        limitations:
          - OpenCV 3.x & python 3.x not tested
          - RGBA images are treated as RBG (ignores alpha channel)
    """
    grayscale = False

    confidence = float(confidence)

    needleImage = pyscreeze._load_cv2(needleImage, grayscale)
    needleHeight, needleWidth = needleImage.shape[:2]
    haystackImage = pyscreeze._load_cv2(haystackImage, grayscale)

    if region:
        haystackImage = haystackImage[region[1]:region[1] + region[3],
                        region[0]:region[0] + region[2]]
    else:
        region = (0, 0)  # full image; these values used in the yield statement
    if (haystackImage.shape[0] < needleImage.shape[0] or
            haystackImage.shape[1] < needleImage.shape[1]):
        # avoid semi-cryptic OpenCV error below if bad size
        raise ValueError('needle dimension(s) exceed the haystack image or region dimensions')

    if step == 2:
        confidence *= 0.95
        needleImage = needleImage[::step, ::step]
        haystackImage = haystackImage[::step, ::step]
    else:
        step = 1

    # get all matches at once, credit: https://stackoverflow.com/questions/7670112/finding-a-subimage-inside-a-numpy-image/9253805#9253805
    # orig result = cv2.matchTemplate(haystackImage, needleImage, cv2.TM_CCOEFF_NORMED)
    # orig match_indices = numpy.arange(result.size)[(result > confidence).flatten()]
    result = cv2.matchTemplate(haystackImage, needleImage, cv2.TM_SQDIFF_NORMED)  # calculating diff
    match_indices = numpy.arange(result.size)[(result < 0.0005).flatten()]  # picking where diff < failure rate
    matches = numpy.unravel_index(match_indices[:limit], result.shape)

    #if result.min() != 0:
    Print.colored("result min", result.min(), "magenta")

    if len(matches[0]) == 0 and pyscreeze.RAISE_IF_NOT_FOUND:
        raise pyscreeze.ImageNotFoundException('Could not locate the image (highest confidence = %.3f)' % (1-result.min()))

    # use a generator for API consistency:
    matchx = matches[1] * step + region[0]  # vectorized
    matchy = matches[0] * step + region[1]
    for x, y in zip(matchx, matchy):
        yield (x, y, needleWidth, needleHeight)

pyscreeze.locateAll = mine_locateAll_opencv
