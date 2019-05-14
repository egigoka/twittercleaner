import mss
import mss.tools
from commands import *

b = Bench(quiet=False)

with mss.mss() as sct:
    # Get information of monitor 1
    monitor_number = 1
    mon = sct.monitors[monitor_number]

    # The screen part to capture
    #monitor = {
    #    "top": mon["top"] + 100,  # 100px from the top
    #    "left": mon["left"] + 100,  # 100px from the left
    #    "width": 160,
    #    "height": 135,
    #    "mon": monitor_number,
    #}
    # output = "sct-mon{mon}_{top}x{left}_{width}x{height}.png".format(**monitor)

    # Grab the data
    # sct_img = sct.grab(monitor)
    sct_img = sct.grab(mon)

    #print(type(sct_img))
    #print(sct_img)
    #input()
    print(dir(sct_img))
    #input()
    #print(sct_img.pixels[0])
    #print(sct_img.pixels[0][0])
    #print(sct_img.pixels[0][0][0])

    # Save to the picture file
    #mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
    #print(output)

b.end()