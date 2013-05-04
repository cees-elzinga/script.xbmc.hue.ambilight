
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

SCRIPTNAME = "XBMC Hue"

def log(msg):
  global SCRIPTNAME
  xbmc.log("%s: %s" % (SCRIPTNAME, msg))

try:
  import requests
except ImportError:
  log("ERROR: Could not locate required library requests")
  notify("XBMC Hue", "ERROR: Could not import Python requests")

log("Service started")
# Assume a ratio of 4/3
capture_width = 100
capture_height = 75

capture = xbmc.RenderCapture()
fmt = capture.getImageFormat()
# probably BGRA
# log("Image format: %s" % fmt)

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

  def __init__(self, settings, args):
    self.settings = settings
    self._parse_argv(args)

    if self.settings.bridge_user not in ["-", "", None]:
      self.update_settings()

    if self.params == {}:
      if self.settings.bridge_ip not in ["-", "", None]:
        self.test_connection()
    elif self.params['action'] == "discover":
      log("Starting discover")
      notify("Bridge discovery", "starting")
      hue_ip = start_autodisover()
      if hue_ip != None:
        notify("Bridge discovery", "Found bridge at: %s" % hue_ip)
        username = register_user(hue_ip)
        log("Updating settings")
        self.settings.update(bridge_ip = hue_ip)
        self.settings.update(bridge_user = username)
        notify("Bridge discovery", "Finished")
        self.test_connection()
      else:
        notify("Bridge discovery", "Failed. Could not find bridge.")
    else:
      # not yet implemented
      log("unimplemented action call: %s" % self.params['action'])

    if self.connected:
      if self.settings.misc_initialflash:
        self.flash_lights()

  def flash_lights(self):
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
    self.light.dim_light()
        
  def brighter_lights(self):
    self.light.brighter_light()

  def update_settings(self):
    if self.settings.light == 0 and \
        (self.light is None or self.light.group is not True):
      self.light = Group(
        self.settings.bridge_ip,
        self.settings.bridge_user,
        self.settings.group_id,
        self.settings.group_primary,
        self.settings.dimmed_bri,
        self.settings.dimmed_hue,
        self.settings.undim_bri,
        self.settings.undim_hue,
      )
    elif self.settings.light > 0 and \
          (self.light is None or \
          self.light.group == True or \
          self.light.light != self.settings.light):
      self.light = Light(
        self.settings.bridge_ip,
        self.settings.bridge_user,
        self.settings.light,
        self.settings.dimmed_bri,
        self.settings.dimmed_hue,
        self.settings.undim_bri,
        self.settings.undim_hue,
      )

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
      last = datetime.datetime.now()
      hue.settings.readxml()
      hue.update_settings()
    
    if hue.settings.mode == 1: # theatre mode
      if player == None:
        player = MyPlayer()
      xbmc.sleep(500)
    if hue.settings.mode == 0: # ambilight mode
      if hue.settings.ambilight_dim:
        if player == None:
          hue.settings.dim_group = Group(
            hue.settings.bridge_ip,
            hue.settings.bridge_user,
            hue.settings.ambilight_dim_group,
            hue.settings.ambilight_dim_primary,
            hue.settings.dimmed_bri,
            hue.settings.dimmed_hue,
            hue.settings.undim_bri,
            hue.settings.undim_hue,
          )
          player = MyPlayer()
        else:
          xbmc.sleep(1)

      capture.waitForCaptureStateChangeEvent(10)
      if capture.getCaptureState() == xbmc.CAPTURE_STATE_DONE:
        screen = Screenshot(capture.getImage(), capture.getWidth(), capture.getHeight())
        h, s, v = screen.get_hsv()
        hue.light.set_light2(h, s, v)

def state_changed(state):
  if state == "started":
    hue.light.get_current_setting()

  if state == "started" or state == "resumed":
    if mixed_mode(hue):
      hue.settings.dim_group.dim_light()
    else:
      hue.dim_lights()
  elif state == "stopped" or state == "paused":
    if mixed_mode(hue):
      # Be persistent in restoring the lights 
      # (prevent from being overwritten by an ambilight update)
      for i in range(0, 3):
        hue.settings.dim_group.brighter_light()
        time.sleep(1)
    else:
      hue.brighter_lights()

if ( __name__ == "__main__" ):
  settings = settings()
  args = None
  if len(sys.argv) == 2:
    args = sys.argv[1]
  hue = Hue(settings, args)
  while not hue.connected:
    time.sleep(1)
  run()
