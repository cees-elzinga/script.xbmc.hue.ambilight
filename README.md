script.xbmc.hue
===============

This is an XBMC add-on that controls Philips Hue lights. It supports two modes of operations: "Theatre mode" and "Ambilight mode:

### Theatre mode

Dims the the Philips Hue lights as soon as a movie starts playing, and turns the lights back on once the movie is done

### Ambilight mode

Turn your Philips Hue lights in a room-sized ambilight. Just install the add-on, and use the built-in "bridge discovery" to discover your bridge and register the XBMC player.

Future work
-----------

 - Ambilight mode doesn't work on a Raspberry Pi due to the way it renders video.
 - Support a variable number of lights

Installation
------------

The add-on requires two external Python libraries for the ambilight mode. If you don't care about the ambilight mode, there's also a stripped version of this add-on that works out of the box (https://github.com/cees-elzinga/script.xbmc.hue.stripped).

 - Python PIL

Follow the instructions at: http://www.pythonware.com/products/pil/.

 - Python requests

Download the XBMC add-on from https://github.com/beenje/script.module.requests, and put the `scripts.module.requests` in your add-ons folder. For Mac OSX users: `/Users/username/Library/Application Support/XBMC/addons/`.

 - Install the add-on

Copy the `script.xbmc.hue` folder to your XBMC add-ons. Restart XBMC and configure the add-on:
System -> Settings -> Add-ons -> Enabled add-ons -> Services -> XBMC Philips Hue

Donations
---------
Donations are always welcome :)

![Pledgie](http://www.pledgie.com/campaigns/19430.png)

Release history
---------------
  * 2013-03-05 v 0.3.2 Small improvements
  * 2013-02-25 v 0.3.1 Improved handling for grouped lights
  * 2013-01-27 v 0.1.0 Initial release

Contributing
------------

Want to contribute? Great! I don't plan on actvily extending this code, but will accept push requests and help with bug reports. You can contact me on my Github profile page.

Feel free to fork away and have fun!
