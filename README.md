script.xbmc.hue
===============

This is an XBMC add-on that controls Philips Hue lights. It supports two modes of operations: "Theatre mode" and "Ambilight mode:.

### Theatre mode

Dims the the Philips Hue lights as soon as a movie starts playing, and turns the lights back on once the movie is done

### Ambilight mode

Turn your Philips Hue lights in a room-sized ambilight. No external libraries are required. Just install the add-on, and use the built-in "bridge discovery" to discover your bridge and register an account.

Installation
------------

Copy the `script.xbmc.hue` folder to your XBMC add-ons. For Mac OSX users: `/Users/username/Library/Application Support/XBMC/addons/`.

Restart XBMC and configure the add-on:

System -> Settings -> Add-ons -> Enabled add-ons -> Services

Future work
-----------

Some more work needs to be done, especially on the ambilight mode. The biggest issue is that is takes approx 1 second for the bridge to adjust the lights, per light. The ambilight is therefore at least 1 second behind on the video traks, ruining the effect.

Some other, smaller issues:
 - Better support to detect if a movie is playing / paused or stopped (the callback function didn't seem to work for me)
 - Monitor changes in the add-on's settings. Changes are now effective after restarting XBMC
 - Support a variable number of lights

Contributing
------------

Want to contribute? Great! I don't plan on actvily maintaining this code, but will accept push requests. You can contact me on my Github profile page.

Feel free to fork away and have fun!
