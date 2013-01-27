script.xbmc.hue
===============

This is an XBMC add-on that controls Philips Hue lights. It supports two modes of operations:

1) Theatre mode
2) Ambilight mode

### Theatre mode

Dims the the Philips Hue lights as soon as a movie starts playing, and turns the lights back on once the movie is done

### Ambilight mode

Turn your Philips Hue lights in a room-sized ambilight.

No external libraries are required. Just install the add-on, and use the built-in "bridge discovery" to discover your bridge and register an account.

Future work
-----------

Some more work needs to be done, especially on the ambilight mode. The biggest issue is that is takes approx 1 second for the bridge to adjust the lights, per light. Therefore, the color of the lights is at least 1 second behind on the video.

Some other, smaller issues:
 - Better support to detect if a movie is playing / paused or stopped (the callback function didn't seem to work for me)
 - Monitor changes in the add-on's settings. Changes are now effective after restarting XBMC
 - Support a variable number of lights

Fork away
---------

I don't intend to actively maintain this code.

So, fork away and have fun!
