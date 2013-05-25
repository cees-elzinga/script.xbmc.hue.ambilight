import xbmc
import xbmcgui
import xbmcaddon
import time
import sys
import colorsys
import os
import datetime

__addon__      = xbmcaddon.Addon()
__cwd__        = __addon__.getAddonInfo('path')
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )

sys.path.append (__resource__)

from settings import *
from tools import *

try:
  import requests
except ImportError:
  xbmc.log("ERROR: Could not locate required library requests")
  notify("XBMC Hue", "ERROR: Could not import Python requests")

xbmc.log("XBMC Hue service started, version: %s" % get_version())
# Assume a ratio of 4/3
capture_width = 100
capture_height = 75

capture = xbmc.RenderCapture()
fmt = capture.getImageFormat()
# probably BGRA
# xbmc.log("Image format: %s" % fmt)

capture.capture(capture_width, capture_height, xbmc.CAPTURE_FLAG_CONTINUOUS)

class MyPlayer(xbmc.Player):
  playingvideo = None

  def __init__(self):
    xbmc.Player.__init__(self)
  
  def onPlayBackStarted(self):
    if self.isPlayingVideo():
      self.playingvideo = True
      state_changed("started")

  def onPlayBackPaused(self):
    if self.isPlayingVideo():
      self.playingvideo = False
      state_changed("paused")

  def onPlayBackResumed(self):
    if self.isPlayingVideo():
      self.playingvideo = True
      state_changed("resumed")

  def onPlayBackStopped(self):
    if self.playingvideo:
      self.playingvideo = False
      state_changed("stopped")

  def onPlayBackEnded(self):
    if self.playingvideo:
      self.playingvideo = False
      state_changed("stopped")

class Hue:
  params = None
  connected = None
  last_state = None
  light = None
  dim_group = None

  def __init__(self, settings, args):
    self.logger = Logger()
    if settings.debug:
      self.logger.debug()

    self.settings = settings
    self._parse_argv(args)

    if self.settings.bridge_user not in ["-", "", None]:
      self.update_settings()

    if self.params == {}:
      if self.settings.bridge_ip not in ["-", "", None]:
        self.test_connection()
    elif self.params['action'] == "discover":
      self.logger.debuglog("Starting discover")
      notify("Bridge discovery", "starting")
      hue_ip = start_autodisover()
      if hue_ip != None:
        notify("Bridge discovery", "Found bridge at: %s" % hue_ip)
        username = register_user(hue_ip)
        self.logger.debuglog("Updating settings")
        self.settings.update(bridge_ip = hue_ip)
        self.settings.update(bridge_user = username)
        notify("Bridge discovery", "Finished")
        self.test_connection()
      else:
        notify("Bridge discovery", "Failed. Could not find bridge.")
    else:
      # not yet implemented
      self.logger.debuglog("unimplemented action call: %s" % self.params['action'])

    if self.connected:
      if self.settings.misc_initialflash:
        self.flash_lights()

  def flash_lights(self):
    self.logger.debuglog("class Hue: flashing lights")
    self.light.flash_light()
    
  def _parse_argv(self, args):
    try:
        self.params = dict(arg.split("=") for arg in args.split("&"))
    except:
        self.params = {}

  def test_connection(self):
    r = requests.get('http://%s/api/%s/config' % \
      (self.settings.bridge_ip, self.settings.bridge_user))
    test_connection = r.text.find("name")
    if not test_connection:
      notify("Failed", "Could not connect to bridge")
      self.connected = False
    else:
      notify("XBMC Hue", "Connected")
      self.connected = True

  def dim_lights(self):
    self.logger.debuglog("class Hue: dim lights")
    self.light.dim_light()
        
  def brighter_lights(self):
    self.logger.debuglog("class Hue: brighter lights")
    self.light.brighter_light()

  def update_settings(self):
    self.logger.debuglog("class Hue: update settings")
    self.logger.debuglog(settings)
    if self.settings.light == 0 and \
        (self.light is None or self.light.group is not True):
      self.logger.debuglog("creating Group instance")
      self.light = Group(self.settings)
    elif self.settings.light > 0 and \
          (self.light is None or \
          self.light.group == True or \
          self.light.light != self.settings.light_id):
      self.logger.debuglog("creating Light instance")
      self.light = Light(self.settings)

class Screenshot:
  def __init__(self, pixels, capture_width, capture_height):
    self.pixels = pixels
    self.capture_width = capture_width
    self.capture_height = capture_height

  def get_hsv(self):
    h, s, v = self.spectrum_hsv(self.pixels, self.capture_width, self.capture_height)
    h, s, v = self.hsv_to_hue(h, s, v)

    return h, s, v

  def most_used_spectrum(self, spectrum):
    ranges = range(36)

    for i in range(360):
      if spectrum.has_key(i):
        ranges[int(i/10)] += spectrum[i]

    return ranges.index(max(ranges))*10 + 5

  def spectrum_hsv(self, pixels, width, height):
    spectrum = {}

    i = 0
    s, v = 0, 0

    g_b, g_g, g_r, g_a = 0, 0, 0, 0
    for y in range(height):
      row = width * y * 4
      for x in range(width/5 - 5):
        b = pixels[row + x * 4 * 5 + y%5]
        g = pixels[row + x * 4 * 5 + y%5 + 1]
        r = pixels[row + x * 4 * 5 + y%5 + 2]
        a = pixels[row + x * 4 * 5 + y%5 + 3]
        g_b += b
        g_g += g
        g_r += r
        g_a += a

        tmph, tmps, tmpv = colorsys.rgb_to_hsv(float(r/255.0), float(g/255.0), float(b/255.0))
        s += tmps
        v += tmpv
        i += 1

        h = int(tmph * 360)
        if spectrum.has_key(h):
          spectrum[h] += 1
        else:
          spectrum[h] = 1

    s = int(s/i * 100)
    v = int(v/i * 100)
    h = self.most_used_spectrum(spectrum)
    return h, s, v

  def hsv_to_hue(self, h, s, v):
    h = int(float(h/360.0)*65535) # on a scale from 0 <-> 65535
    s = int(float(s/100.0)*254)
    v = int(float(v/100.0)*254)

    if v == 0:
      v = 75
    return h, s, v

def run():
  player = None
  last = datetime.datetime.now()
  
  while not xbmc.abortRequested:

    if datetime.datetime.now() - last > datetime.timedelta(seconds=1):
      # check for updates every 1s (fixme: use callback function)
      logger.debuglog("running in mode %s" % str(hue.settings.mode))
      last = datetime.datetime.now()
      hue.settings.readxml()
      hue.update_settings()
    
    if hue.settings.mode == 1: # theatre mode
      if player == None:
        logger.debuglog("creating instance of player")
        player = MyPlayer()
      xbmc.sleep(500)
    if hue.settings.mode == 0: # ambilight mode
      if hue.settings.ambilight_dim and hue.dim_group == None:
        logger.debuglog("creating group to dim")
        tmp = hue.settings
        tmp.group_id = tmp.ambilight_dim_group
        hue.dim_group = Group(tmp)
      
      if player == None:
        player = MyPlayer()
      else:
        xbmc.sleep(1)

      capture.waitForCaptureStateChangeEvent(10)
      if capture.getCaptureState() == xbmc.CAPTURE_STATE_DONE:
        if player.playingvideo:
          screen = Screenshot(capture.getImage(), capture.getWidth(), capture.getHeight())
          h, s, v = screen.get_hsv()
          hue.light.set_light2(h, s, v)

def state_changed(state):
  logger.debuglog("state changed to: %s" % state)
  if state == "started":
    logger.debuglog("retrieving current setting before starting")
    hue.light.get_current_setting()

  if state == "started" or state == "resumed":
    if hue.settings.mode == 0 and hue.settings.ambilight_dim: # only if a complete group
      logger.debuglog("dimming group for ambilight")
      hue.dim_group.dim_light()
    else:
      logger.debuglog("dimming lights")
      hue.dim_lights()
  elif state == "stopped" or state == "paused":
    if hue.settings.mode == 0:
      # Be persistent in restoring the lights 
      # (prevent from being overwritten by an ambilight update)
      for i in range(0, 3):
        logger.debuglog("brighter lights")
        hue.dim_group.brighter_light()
        time.sleep(1)
    else:
      hue.brighter_lights()

if ( __name__ == "__main__" ):
  settings = settings()
  logger = Logger()
  if settings.debug == True:
    logger.debug()
  
  args = None
  if len(sys.argv) == 2:
    args = sys.argv[1]
  hue = Hue(settings, args)
  while not hue.connected:
    logger.debuglog("not connected")
    time.sleep(1)
  run()
