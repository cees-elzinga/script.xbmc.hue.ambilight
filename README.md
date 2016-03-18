script.xbmc.hue.ambilight
=========================

[![Screenshot](http://meethue.files.wordpress.com/2013/07/youtube.png?w=400)](http://youtu.be/eU5ZvXzXmrU)

An XBMC add-on that controls Philips Hue lights. In "Theatre mode" the add-on dims the the Philips Hue lights as soon as a movie starts playing, and turns the lights back on once the movie is done. "Ambilight mode" turns your Philips Hue lights in a room-sized ambilight

No longer maintained
--------------------

This project is no longer maintained. Feel free to fork away and have fun!

You might be interested in these forks that are still being developed:

 - https://github.com/fritsch/script.kodi.hue.ambilight
 - https://github.com/michaelrcarroll/script.kodi.hue.ambilight
 - https://github.com/ErlendSB/script.kodi.hue.ambilight
 - https://github.com/robwalch/script.xbmc.hue.ambilight
 
Want your project added here? You can contact me on my Github profile page.

Installation
------------

The add-on depends on the XBMC add-on "requests" for the ambilight mode.

**XBMC add-on script.module.requests**

 - Download the add-on as a ZIP file from https://github.com/beenje/script.module.requests
  - (Right click on the "ZIP" icon and select "Download Linked File").
 - Open XBMC
 - Go to `System -> Settings -> Add-ons -> Install from zip file`
 - Select the zip file.

**XBMC add-on script.xbmc.hue.ambilight**

 - Download the add-on as a ZIP file from the top of this page
   - (Right click on the "ZIP" icon and select "Download Linked File")
 - Open XBMC
 - Go to `System -> Settings -> Add-ons -> Install from zip file`
 -  Restart XBMC and configure the add-on:
   - `System -> Settings -> Add-ons -> Enabled add-ons -> Services -> XBMC Philips Hue`
   - Run `Start auto discovery of bridge IP and User`.

Note for Raspberry Pi users:

 - Save the add-on configuration by exiting XBMC before shutting down the Pi completely
 - Ambilight mode doesn't work on a Raspberry Pi due to the way it renders video

Release history
---------------
  * 2014-01-12 v 0.6.2 Minor improvements
  * 2013-07-13 v 0.6.0 General improvements all around (by robwalch)
  * 2013-05-25 v 0.5.0 Debug logging, livingwhite lights
  * 2013-05-04 v 0.4.0 Advanced settings
  * 2013-04-25 v 0.3.6 Custom dimmed brightness in theatre mode
  * 2013-04-02 v 0.3.4 Ambilight is more responsive
  * 2013-04-01 v 0.3.3 Rename to script.xbmc.hue.ambilight
  * 2013-02-25 v 0.3.1 Improved handling for grouped lights
  * 2013-01-27 v 0.1.0 Initial release
