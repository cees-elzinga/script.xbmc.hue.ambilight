script.xbmc.hue.ambilight
=========================

![ScreenShot](http://meethue.files.wordpress.com/2013/01/plugin2.png?w=400)

This is an XBMC add-on that controls Philips Hue lights. It supports two modes of operation: "Theatre mode" and "Ambilight mode:

### Theatre mode

Dims the the Philips Hue lights as soon as a movie starts playing, and turns the lights back on once the movie is done

### Ambilight mode

Turn your Philips Hue lights in a room-sized ambilight. Just install the add-on, and use the built-in "bridge discovery" to discover your bridge and register the XBMC player.

Future work
-----------

 - Ambilight mode doesn't work on a Raspberry Pi due to the way it renders video.
 - Support a variable number of lights and groups

Installation
------------

The add-on requires two external Python libraries for the ambilight mode. If you don't care about the ambilight mode, the default version of this add-on works out of the box (https://github.com/cees-elzinga/script.xbmc.hue).

 - Python PIL

Follow the instructions at: http://www.pythonware.com/products/pil/.

 - Python requests

Download the XBMC add-on from https://github.com/beenje/script.module.requests, and put the `scripts.module.requests` in your add-ons folder. For Mac OSX users: `/Users/username/Library/Application Support/XBMC/addons/`.

 - Install the add-on

Download the add-on as a ZIP file. Open XBMC and go to System -> Settings -> Add-ons -> Install from zip file. Restart XBMC and configure the add-on:
System -> Settings -> Add-ons -> Enabled add-ons -> Services -> XBMC Philips Hue

Note for Raspberry Pi users: To save the add-on configuration, exit XBMC first before shutting down the Pi.

Donations
---------
If you like the add-on, donations are always welcome :)

[![PayPal]( https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=48ZKAZK6QHNGJ&lc=NL&item_name=script%2exbmc%2ehue&currency_code=EUR)

Release history
---------------
  * 2013-04-01 v 0.3.3 Rename to script.xbmc.hue.ambilight
  * 2013-03-05 v 0.3.2 Small improvements
  * 2013-02-25 v 0.3.1 Improved handling for grouped lights
  * 2013-01-27 v 0.1.0 Initial release

Contributing
------------

Want to contribute? Great! I don't plan on actvily extending this code, but will accept push requests and help with bug reports. You can contact me on my Github profile page.

Feel free to fork away and have fun!
