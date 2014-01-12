import sys
import xbmcaddon

__addon__      = sys.modules[ "__main__" ].__addon__

class settings():
  def __init__( self, *args, **kwargs ):
    self.readxml()
    self.addon = xbmcaddon.Addon()

  def readxml(self):
    self.bridge_ip             = __addon__.getSetting("bridge_ip")
    self.bridge_user           = __addon__.getSetting("bridge_user")

    self.mode                  = int(__addon__.getSetting("mode"))
    self.light                 = int(__addon__.getSetting("light"))
    self.light1_id             = int(__addon__.getSetting("light1_id"))
    self.light2_id             = int(__addon__.getSetting("light2_id"))
    self.light3_id             = int(__addon__.getSetting("light3_id"))
    self.group_id              = int(__addon__.getSetting("group_id"))
    self.misc_initialflash     = __addon__.getSetting("misc_initialflash") == "true"
    self.misc_disableshort     = __addon__.getSetting("misc_disableshort") == "true"

    self.dimmed_bri            = int(int(__addon__.getSetting("dimmed_bri").split(".")[0])*254/100)
    self.override_undim_bri    = __addon__.getSetting("override_undim_bri") == "true"
    self.undim_bri             = int(int(__addon__.getSetting("undim_bri").split(".")[0])*254/100)
    self.dim_time              = int(float(__addon__.getSetting("dim_time"))*10)
    self.override_hue          = __addon__.getSetting("override_hue") == "true"
    self.dimmed_hue            = int(__addon__.getSetting("dimmed_hue").split(".")[0])
    self.undim_hue             = int(__addon__.getSetting("undim_hue").split(".")[0])
    self.ambilight_dim         = __addon__.getSetting("ambilight_dim") == "true"
    self.ambilight_dim_group   = int(__addon__.getSetting("ambilight_dim_group"))
    self.ambilight_min         = int(int(__addon__.getSetting("ambilight_min").split(".")[0])*254/100)
    self.ambilight_max         = int(int(__addon__.getSetting("ambilight_max").split(".")[0])*254/100)
    self.color_bias            = int(int(__addon__.getSetting("color_bias").split(".")[0])/3*3)

    if self.ambilight_min > self.ambilight_max:
        self.ambilight_min = self.ambilight_max
        __addon__.setSetting("ambilight_min", __addon__.getSetting("ambilight_max"))

    self.debug                 = __addon__.getSetting("debug") == "true"

  def update(self, **kwargs):
    self.__dict__.update(**kwargs)
    for k, v in kwargs.iteritems():
      self.addon.setSetting(k, v)

  def __repr__(self):
    return 'bridge_ip: %s\n' % self.bridge_ip + \
    'bridge_user: %s\n' % self.bridge_user + \
    'mode: %s\n' % str(self.mode) + \
    'light: %s\n' % str(self.light) + \
    'light1_id: %s\n' % str(self.light1_id) + \
    'light2_id: %s\n' % str(self.light2_id) + \
    'light3_id: %s\n' % str(self.light3_id) + \
    'group_id: %s\n' % str(self.group_id) + \
    'misc_initialflash: %s\n' % str(self.misc_initialflash) + \
    'misc_disableshort: %s\n' % str(self.misc_disableshort) + \
    'dimmed_bri: %s\n' % str(self.dimmed_bri) + \
    'undim_bri: %s\n' % str(self.undim_bri) + \
    'dimmed_hue: %s\n' % str(self.dimmed_hue) + \
    'override_hue: %s\n' % str(self.override_hue) + \
    'undim_hue: %s\n' % str(self.undim_hue) + \
    'ambilight_dim: %s\n' % str(self.ambilight_dim) + \
    'ambilight_dim_group: %s\n' % str(self.ambilight_dim_group) + \
    'ambilight_min: %s\n' % str(self.ambilight_min) + \
    'ambilight_max: %s\n' % str(self.ambilight_max) + \
    'color_bias: %s\n' % str(self.color_bias) + \
    'debug: %s\n' % self.debug