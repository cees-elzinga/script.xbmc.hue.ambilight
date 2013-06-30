import xbmc
import xbmcgui
import xbmcaddon
import time
import sys
import colorsys
import os
import datetime
import math

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

capture = xbmc.RenderCapture()
fmt = capture.getImageFormat()
# BGRA or RGBA
# xbmc.log("Hue Capture Image format: %s" % fmt)
fmtRGBA = fmt == 'RGBA'

class MyMonitor( xbmc.Monitor ):
  def __init__( self, *args, **kwargs ):
    xbmc.Monitor.__init__( self )

  def onSettingsChanged( self ):
    logger.debuglog("running in mode %s" % str(hue.settings.mode))
    last = datetime.datetime.now()
    hue.settings.readxml()
    hue.update_settings()

monitor = MyMonitor()

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
        self.update_settings()
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
    if self.settings.light == 0:
      self.light.flash_light()
    else:
      self.light[0].flash_light()
      if self.settings.light > 1:
        xbmc.sleep(1)
        self.light[1].flash_light()
      if self.settings.light > 2:
        xbmc.sleep(1)
        self.light[2].flash_light()
    
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
    if self.settings.light == 0:
      self.light.dim_light()
    else:
      self.light[0].dim_light()
      if self.settings.light > 1:
        xbmc.sleep(1)
        self.light[1].dim_light()
      if self.settings.light > 2:
        xbmc.sleep(1)
        self.light[2].dim_light()

        
  def brighter_lights(self):
    self.logger.debuglog("class Hue: brighter lights")
    if self.settings.light == 0:
      self.light.brighter_light()
    else:
      self.light[0].brighter_light()
      if self.settings.light > 1:
        xbmc.sleep(1)
        self.light[1].brighter_light()
      if self.settings.light > 2:
        xbmc.sleep(1)
        self.light[2].brighter_light()


  def update_settings(self):
    self.logger.debuglog("class Hue: update settings")
    self.logger.debuglog(settings)
    if self.settings.light == 0 and \
        (self.light is None or type(self.light) != Group):
      self.logger.debuglog("creating Group instance")
      self.light = Group(self.settings)
    elif self.settings.light > 0 and \
          (self.light is None or \
          type(self.light) == Group or \
          len(self.light) == 0 or \
          self.light[0].light != self.settings.light1_id or \
          (self.settings.light > 1 and self.light[1].light != self.settings.light2_id) or \
          (self.settings.light > 2 and self.light[2].light != self.settings.light3_id)):
      self.logger.debuglog("creating Light instances")
      self.light = [None] * self.settings.light
      self.light[0] = Light(self.settings.light1_id, self.settings)
      if self.settings.light > 1:
        xbmc.sleep(1)
        self.light[1] = Light(self.settings.light2_id, self.settings)
      if self.settings.light > 2:
        xbmc.sleep(1)
        self.light[2] = Light(self.settings.light3_id, self.settings)

class Screenshot:
  def __init__(self, pixels, capture_width, capture_height):
    self.pixels = pixels
    self.capture_width = capture_width
    self.capture_height = capture_height

  def get_hsv(self):
    h, s, v = self.spectrum_hsv(self.pixels, self.capture_width, self.capture_height)
    h, s, v = self.hsv_to_hue(h, s, v)

    return h, s, v

  def most_used_spectrum(self, spectrum, saturation, value):
    colorGroups = 18
    colorHueRatio = 360 / colorGroups
    ranges = [0] * colorGroups
    hue = {}
    sat = [0] * colorGroups
    val = [0] * colorGroups

    for i in range(360):
      if spectrum.has_key(i):
        colorIndex = int(i/colorHueRatio)
        ranges[colorIndex] += spectrum[i]
        if hue.has_key(colorIndex):
          hue[colorIndex] = (hue[colorIndex] + i)/2
        else:
          hue[colorIndex] = i
        sat[colorIndex] = (sat[colorIndex] + saturation[i])/2
        val[colorIndex] = (val[colorIndex] + value[i])/2

    if len(hue) > 0:
      # logger.debuglog("ranges %s" % ranges)
      # logger.debuglog("hue %s" % hue)
      # logger.debuglog("sat %s" % sat)
      # logger.debuglog("val %s" % val)
      #return ranges.index(max(ranges))*10 + 5
      index = ranges.index(max(ranges))
      return hue[index], sat[index]*100, val[index]*100
    else:
      return 0, 0, 0

  def spectrum_hsv(self, pixels, width, height):
    spectrum = {}
    saturation = {}
    value = {}

    size = int(len(pixels)/4)
    pixel = 0

    i = 0
    s, v = 0, 0
    r, g, b = 0, 0, 0
    tmph, tmps, tmpv = 0, 0, 0
    
    for i in range(size):
      if fmtRGBA:
        r = pixels[pixel]
        g = pixels[pixel + 1]
        b = pixels[pixel + 2]
      else: #probably BGRA
        b = pixels[pixel]
        g = pixels[pixel + 1]
        r = pixels[pixel + 2]
      pixel += 4

      tmph, tmps, tmpv = colorsys.rgb_to_hsv(float(r/255.0), float(g/255.0), float(b/255.0))
      s += tmps
      v += tmpv

      # skip low value and saturation
      if tmpv > 0.25:
        if tmps > 0.33:
          h = int(tmph * 360)

          # logger.debuglog("%s \t set pixel r %s \tg %s \tb %s" % (i, r, g, b))
          # logger.debuglog("%s \t set pixel h %s \ts %s \tv %s" % (i, tmph*100, tmps*100, tmpv*100))

          if spectrum.has_key(h):
            spectrum[h] += 1 # tmps * 2 * tmpv
            saturation[h] = (saturation[h] + tmps)/2
            value[h] = (value[h] + tmpv)/2
          else:
            spectrum[h] = 1 # tmps * 2 * tmpv
            saturation[h] = tmps
            value[h] = tmpv

    v_overlall = int(v * 100 / i)
    # s_overall = int(s * 100 / i)
    h, s, v = self.most_used_spectrum(spectrum, saturation, value)
    v = v + v_overlall/2
    return h, s, v

  def hsv_to_hue(self, h, s, v):
    h = int(h*65535/360.0) # on a scale from 0 <-> 65535
    s = int(s*255/100.0)
    v = int(v*255/100.0)

    if v == 0:
      v = 16
    return h, s, v

def run():
  player = None
  last = datetime.datetime.now()

  while not xbmc.abortRequested:
    
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
        xbmc.sleep(100)

      capture.waitForCaptureStateChangeEvent(1000/60)
      if capture.getCaptureState() == xbmc.CAPTURE_STATE_DONE:
        if player.playingvideo:
          screen = Screenshot(capture.getImage(), capture.getWidth(), capture.getHeight())
          h, s, v = screen.get_hsv()
          if hue.settings.light == 0:
            fade_light_hsv(hue.light, h, s, v)
          else:
            fade_light_hsv(hue.light[0], h, s, v)
            if hue.settings.light > 1:
              xbmc.sleep(4)
              fade_light_hsv(hue.light[1], h, s, v)
            if hue.settings.light > 2:
              xbmc.sleep(4)
              fade_light_hsv(hue.light[2], h, s, v)

def fade_light_hsv(light, h, s, v):
  hvec = abs(h - light.hueLast) % int(65535/2)
  hvec = float(hvec/128.0)
  svec = s - light.satLast
  vvec = v - light.valLast
  distance = math.sqrt(hvec * hvec + svec * svec + vvec * vvec)
  if distance > 0:
    duration = int(3 + 27 * distance/255)
    # logger.debuglog("distance %s duration %s" % (distance, duration))
    light.set_light2(h, s, v, duration)


def state_changed(state):
  logger.debuglog("state changed to: %s" % state)
  if state == "started":
    logger.debuglog("retrieving current setting before starting")
    
    if hue.settings.light == 0:
      hue.light.get_current_setting()
    else:
      hue.light[0].get_current_setting()
      if hue.settings.light > 1:
        xbmc.sleep(1)
        hue.light[1].get_current_setting()
      if hue.settings.light > 2:
        xbmc.sleep(1)
        hue.light[2].get_current_setting()

    #start capture when playback starts
    capture_width = 32 #100
    capture_height = int(capture_width / capture.getAspectRatio())
    logger.debuglog("capture %s x %s" % (capture_width, capture_height))
    capture.capture(capture_width, capture_height, xbmc.CAPTURE_FLAG_CONTINUOUS)

  if state == "started" or state == "resumed":
    if hue.settings.mode == 0 and hue.settings.ambilight_dim: # only if a complete group
      logger.debuglog("dimming group for ambilight")
      hue.dim_group.dim_light()
    else:
      logger.debuglog("dimming lights")
      hue.dim_lights()
  elif state == "stopped" or state == "paused":
    if hue.settings.mode == 0 and hue.settings.ambilight_dim:
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
