script.xbmc.hue
===============

This is an XBMC add-on that controls Philips Hue lights. It supports two modes of operations: "Theatre mode" and "Ambilight mode:.

### Theatre mode

Dims the the Philips Hue lights as soon as a movie starts playing, and turns the lights back on once the movie is done

### Ambilight mode

Turn your Philips Hue lights in a room-sized ambilight. Just install the add-on, and use the built-in "bridge discovery" to discover your bridge and register the XBMC player.

Installation
------------

Make sure the Python PIL library is installed (http://www.pythonware.com/products/pil/).

Copy the `script.xbmc.hue` folder to your XBMC add-ons. For Mac OSX users: `/Users/username/Library/Application Support/XBMC/addons/`.

Restart XBMC and configure the add-on:

System -> Settings -> Add-ons -> Enabled add-ons -> Services -> XBMC Philips Hue

Future work
-----------

Some more work needs to be done on the "Ambilight mode". The biggest issue is that it takes approximately 1 second to adjust the lights. The time is spent by the bridge, and I don't see any quick way to improve it. For now - "Ambilight mode" works but will be out of sync with the video streams for at least 1 second.

Some other, smaller issues:
 - Support a variable number of lights
 - Ambilight does't work on a Raspberry Pi

Contributing
------------

Want to contribute? Great! I don't plan on actvily maintaining this code, but will accept push requests. You can contact me on my Github profile page.

Feel free to fork away and have fun!
