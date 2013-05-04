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
    self.light                 = int(__addon__.getSetting("light"))
    self.mode                  = int(__addon__.getSetting("mode"))
    self.misc_initialflash     = __addon__.getSetting("misc_initialflash") == "true"
    self.ambilight_dim         = __addon__.getSetting("ambilight_dim") == "true"
    self.ambilight_dim_group   = int(__addon__.getSetting("ambilight_dim_group"))
    self.group_id              = int(__addon__.getSetting("group_id"))
    self.group_primary         = int(__addon__.getSetting("group_primary"))
    self.ambilight_dim_primary = int(__addon__.getSetting("ambilight_dim_primary"))
    self.undim_hue             = int(__addon__.getSetting("undim_hue").split(".")[0])
    self.undim_bri             = int(int(__addon__.getSetting("undim_bri").split(".")[0])*254/100)
    self.dimmed_hue            = int(__addon__.getSetting("dimmed_hue").split(".")[0])
    self.dimmed_bri            = int(int(__addon__.getSetting("dimmed_bri").split(".")[0])*254/100)

  def update(self, **kwargs):
    self.__dict__.update(**kwargs)
    for k, v in kwargs.iteritems():
      self.addon.setSetting(k, v)
