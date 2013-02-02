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
  from pil import Image
except ImportError:
  try:
    from PIL import Image
  except ImportError:
    log("ERROR: Could not locate required library PIL")
    notify("XBMC Hue", "ERROR: Could not import Python PIL")

log("Service started")
# Assume a ratio of 4/3
capture_width = 100
capture_height = 75

capture = xbmc.RenderCapture()
fmt = capture.getImageFormat()
# probably BGRA
# log("Image format: %s" % fmt)

capture.capture(capture_width, capture_height, xbmc.CAPTURE_FLAG_CONTINUOUS)

class Hue:
  params = None
  connected = None
  last_state = None
  settings = None

  def __init__(self, settings):
    self._parse_argv()
    self.settings = settings

    if self.params == {}:
      log("Normal operations")
      if self.settings.bridge_ip != "-":
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
      self.run()

  def flash_lights(self):
    for light in self.used_lights():
        flash_light(self.settings.bridge_ip, self.settings.bridge_user, light)
    
  def _parse_argv( self ):
    try:
        self.params = dict(arg.split("=") for arg in sys.argv[1].split("&"))
    except:
        self.params = {}

  def test_connection(self):
    if not test_connection(self.settings.bridge_ip, self.settings.bridge_user):
      notify("Failed", "Could not connect to bridge")
      self.connected = False
    else:
      notify("XBMC Hue", "Connected")
      self.connected = True

  def check_state(self): 
    if xbmc.Player().isPlaying():
      if self.last_state != 'start':
        self.dim_lights()
      self.last_state = 'start'
    else:
      if self.last_state != 'stop' and self.last_state != None:
        self.brighter_lights()
      self.last_state = 'stop'  

  def dim_lights(self):
    for light in self.used_lights():
        dim_light(self.settings.bridge_ip, self.settings.bridge_user, light)

  def brighter_lights(self):
    for light in self.used_lights():
        brighter_light(self.settings.bridge_ip, self.settings.bridge_user, light)

  def used_lights(self):
    lights = []
    if self.settings.light_1:
      lights.append(1)
    if self.settings.light_2:
      lights.append(2)
    if self.settings.light_3:
      lights.append(3)
    return lights

  def run(self):
    last = datetime.datetime.now()
    while not xbmc.abortRequested:
      if datetime.datetime.now() - last > datetime.timedelta(seconds=1):
        # check for updates every 1s (fixme: use callback function)
        last = datetime.datetime.now()
        self.settings.readxml()
      
      if self.settings.mode == 1: # theatre mode
        self.check_state()
        time.sleep(1)
      if self.settings.mode == 0: # ambilight mode
        capture.waitForCaptureStateChangeEvent(1000)
        if capture.getCaptureState() == xbmc.CAPTURE_STATE_DONE:
          screen = Screenshot(capture.getImage(), capture.getWidth(), capture.getHeight())
          h, s, v = screen.get_hsv()
          for light in self.used_lights():
            set_light2(self.settings.bridge_ip, self.settings.bridge_user, light, h, s, v)

class Screenshot:
  pixels = None
  capture_width = None
  capture_height = None

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
      for x in range(width):
        b = pixels[row + x * 4]
        g = pixels[row + x * 4 + 1]
        r = pixels[row + x * 4 + 2]
        a = pixels[row + x * 4 + 3]
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

if ( __name__ == "__main__" ):
  settings = settings()
  Hue(settings)