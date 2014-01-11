import time
import os
import socket
import json
import random
import hashlib
NOSE = os.environ.get('NOSE', None)
if not NOSE:
  import xbmc
  import xbmcaddon

  __addon__      = xbmcaddon.Addon()
  __cwd__        = __addon__.getAddonInfo('path')
  __icon__       = os.path.join(__cwd__,"icon.png")
  __settings__   = os.path.join(__cwd__,"resources","settings.xml")
  __xml__        = os.path.join( __cwd__, 'addon.xml' )

def notify(title, msg=""):
  if not NOSE:
    global __icon__
    xbmc.executebuiltin("XBMC.Notification(%s, %s, 3, %s)" % (title, msg, __icon__))

try:
  import requests
except ImportError:
  notify("XBMC Hue", "ERROR: Could not import Python requests")

def get_version():
  # prob not the best way...
  global __xml__
  try:
    for line in open(__xml__):
      if line.find("ambilight") != -1 and line.find("version") != -1:
        return line[line.find("version=")+9:line.find(" provider")-1]
  except:
    return "unkown"

def start_autodisover():
  port = 1900
  ip = "239.255.255.250"

  address = (ip, port)
  data = """M-SEARCH * HTTP/1.1
  HOST: %s:%s
  MAN: ssdp:discover
  MX: 3
  ST: upnp:rootdevice""" % (ip, port)
  client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  hue_ip = None
  num_retransmits = 0
  while(num_retransmits < 10) and hue_ip == None:
      num_retransmits += 1
      client_socket.sendto(data, address)
      recv_data, addr = client_socket.recvfrom(2048)
      if "IpBridge" in recv_data and "description.xml" in recv_data:
        hue_ip = recv_data.split("LOCATION: http://")[1].split(":")[0]
      time.sleep(1)
      
  return hue_ip

def register_user(hue_ip):
  username = hashlib.md5(str(random.random())).hexdigest()
  device = "xbmc-player"
  data = '{"username": "%s", "devicetype": "%s"}' % (username, device)

  r = requests.post('http://%s/api' % hue_ip, data=data)
  response = r.text
  while "link button not pressed" in response:
    notify("Bridge discovery", "press link button on bridge")
    r = requests.post('http://%s/api' % hue_ip, data=data)
    response = r.text 
    time.sleep(3)

  return username

class Light:
  start_setting = None
  group = False
  livingwhite = False
  fullSpectrum = False

  def __init__(self, light_id, settings):
    self.logger = Logger()
    if settings.debug:
      self.logger.debug()

    self.bridge_ip    = settings.bridge_ip
    self.bridge_user  = settings.bridge_user
    self.light        = light_id
    self.dim_time     = settings.dim_time
    self.override_hue = settings.override_hue
    self.dimmed_bri   = settings.dimmed_bri
    self.dimmed_hue   = settings.dimmed_hue
    self.undim_bri    = settings.undim_bri
    self.undim_hue    = settings.undim_hue
    self.override_undim_bri = settings.override_undim_bri
    self.hueLast = 0
    self.satLast = 0
    self.valLast = 255

    self.get_current_setting()
    self.s = requests.Session()

  def request_url_put(self, url, data):
    if self.start_setting['on']:
      try:
        self.s.put(url, data=data)
      except:
        self.logger.debuglog("exception in request_url_put")
        pass # probably a timeout

  def get_current_setting(self):
    r = requests.get("http://%s/api/%s/lights/%s" % \
      (self.bridge_ip, self.bridge_user, self.light))
    j = r.json()
    self.start_setting = {}
    state = j['state']
    self.start_setting['on'] = state['on']
    self.start_setting['bri'] = state['bri']
    self.valLast = state['bri']
    
    modelid = j['modelid']
    self.fullSpectrum = ((modelid == 'LST001') or (modelid == 'LLC007'))

    if state.has_key('hue'):
      self.start_setting['hue'] = state['hue']
      self.start_setting['sat'] = state['sat']
      self.hueLast = state['hue']
      self.satLast = state['sat']
    
    else:
      self.livingwhite = True

  def set_light(self, data):
    self.logger.debuglog("set_light: %s: %s" % (self.light, data))
    self.request_url_put("http://%s/api/%s/lights/%s/state" % \
      (self.bridge_ip, self.bridge_user, self.light), data=data)

  def set_light2(self, hue, sat, bri, dur=20):
    if not self.livingwhite:
      data = json.dumps({
          "on": True,
          "hue": hue,
          "sat": sat,
          "bri": bri,
          "transitiontime": dur
      })
    else:
      data = json.dumps({
          "on": True,
          "bri": bri,
      })

    # self.logger.debuglog("set_light2: %s: %s" % (self.light, data))
    self.request_url_put("http://%s/api/%s/lights/%s/state" % \
      (self.bridge_ip, self.bridge_user, self.light), data=data)

    self.hueLast = hue
    self.satLast = sat
    self.valLast = bri

  def flash_light(self):
    self.dim_light()
    time.sleep(self.dim_time/10)
    self.brighter_light()

  def dim_light(self):
    if not self.livingwhite and self.override_hue:
      dimmed = '{"on":true,"bri":%s,"hue":%s,"transitiontime":%d}' % \
        (self.dimmed_bri, self.dimmed_hue, self.dim_time)
      self.hueLast = self.dimmed_hue
    else:
      dimmed = '{"on":true,"bri":%s,"transitiontime":%d}' % \
        (self.dimmed_bri, self.dim_time)
    self.valLast = self.dimmed_bri
    self.set_light(dimmed)
    if self.dimmed_bri == 0:
      off = '{"on":false}'
      self.set_light(off)
      self.valLast = 0

  def brighter_light(self):
    data = '{"on":true,"transitiontime":%d' % (self.dim_time)
    if self.override_undim_bri:
      data += ',"bri":%s' % self.undim_bri
      self.valLast = self.undim_bri
    else:
      data += ',"bri":%s' % self.start_setting['bri']
      self.valLast = self.start_setting['bri']
    if not self.livingwhite:
      data += ',"sat":%s' % self.start_setting['sat']
      self.satLast = self.start_setting['sat']

      if self.override_hue:
        data += ',"hue":%s' % self.undim_hue
        self.hueLast = self.undim_hue
      else:
        data += ',"hue":%s' % self.start_setting['hue']
        self.hueLast = self.start_setting['hue']
    data += "}"
    self.set_light(data)

class Group(Light):
  group = True
  lights = {}

  def __init__(self, settings):
    self.group_id = settings.group_id

    self.logger = Logger()
    if settings.debug:
      self.logger.debug()

    Light.__init__(self, settings.light1_id, settings)
    
    for light in self.get_lights():
      tmp = Light(light, settings)
      tmp.get_current_setting()
      if tmp.start_setting['on']:
        self.lights[light] = tmp

  def __len__(self):
    return 0

  def get_lights(self):
    try:
      r = requests.get("http://%s/api/%s/groups/%s" % \
        (self.bridge_ip, self.bridge_user, self.group_id))
      j = r.json()
    except:
      self.logger.debuglog("WARNING: Request fo bridge failed")
      #notify("Communication Failed", "Error while talking to the bridge")

    try:
      return j['lights']
    except:
      # user probably selected a non-existing group
      self.logger.debuglog("Exception: no lights in this group")
      return []

  def set_light(self, data):
    self.logger.debuglog("set_light: %s" % data)
    Light.request_url_put(self, "http://%s/api/%s/groups/%s/action" % \
      (self.bridge_ip, self.bridge_user, self.group_id), data=data)

  def set_light2(self, hue, sat, bri, dur=20):
    data = json.dumps({
        "on": True,
        "hue": hue,
        "sat": sat,
        "bri": bri,
        "transitiontime": dur
    })
    
    self.logger.debuglog("set_light2: %s" % data)

    try:
      self.request_url_put("http://%s/api/%s/groups/%s/action" % \
        (self.bridge_ip, self.bridge_user, self.group_id), data=data)
    except:
      self.logger.debuglog("WARNING: Request fo bridge failed")
      pass

  def dim_light(self):
    for light in self.lights:
        self.lights[light].dim_light()

  def brighter_light(self):
      for light in self.lights:
        self.lights[light].brighter_light()

  def request_url_put(self, url, data):
    try:
      self.s.put(url, data=data)
    except Exception as e:
      # probably a timeout
      self.logger.debuglog("WARNING: Request fo bridge failed")
      pass

class Logger:
  scriptname = "XBMC Hue"
  enabled = True
  debug_enabled = False

  def log(self, msg):
    if self.enabled:
      xbmc.log("%s: %s" % (self.scriptname, msg))

  def debuglog(self, msg):
    if self.debug_enabled:
      self.log("DEBUG %s" % msg)

  def debug(self):
    self.debug_enabled = True

  def disable(self):
    self.enabled = False
