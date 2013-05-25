from nose.tools import *
import os
import time
os.sys.path.append("./resources/lib/")

NOSE = os.environ.get('NOSE', None)
BRIDGE_IP = os.environ.get('BRIDGE_IP', None)
BRIDGE_USER = os.environ.get('BRIDGE_USER', None)
ok_(NOSE != None, "NOSE not set")
ok_(BRIDGE_IP != None, "BRIDGE_IP not set")
ok_(BRIDGE_USER != None, "BRIDGE_USER not set")

from tools import *

class settings():
	mode		= 1 # theatre
	light 		= 1 # single bulb
	light_id	= 2
	group_id	= 0
	misc_initialflash = True
	override_hue = True
	override_undim_bri = True
	dimmed_bri	= 0
	undim_bri	= 228
	dimmed_hue	= 10000
	undim_hue	= 30000
	ambilight_dim = False
	ambilight_dim_group = 1
	debug		= False

s = settings()
s.bridge_ip = BRIDGE_IP
s.bridge_user = BRIDGE_USER
l = Light(s)
l.logger.disable()

def test_not_group():
	ok_(l.group == False)

def test_current_setting():
	l.get_current_setting()
	ok_(l.start_setting['bri'] >= 0)
	eq_(l.start_setting['on'], True, msg="Light is not turned on, failing")

def test_set_light():
	data = '{"on":true,"hue":10000}'
	l.set_light(data)
	l.get_current_setting()
	eq_(l.start_setting['on'], True)
	eq_(l.start_setting['hue'], 10000)

def test_dim_light():
	l.dim_light()
	time.sleep(1)
	l.get_current_setting()
	eq_(l.start_setting['bri'], s.dimmed_bri)
	eq_(l.start_setting['hue'], s.dimmed_hue)

	# reset light to on, get_current_setting just set it to off
	l.start_setting['on'] = True

def test_brighter_light():
	l.start_setting['bri'] = 255
	l.brighter_light()
	time.sleep(1)
	l.get_current_setting()
	ok_(l.start_setting['bri'] == s.undim_bri)
	ok_(l.start_setting['hue'] == s.undim_hue)

def test_flash_light():
	start_bri = l.start_setting['bri']
	l.flash_light()
	time.sleep(2)
	l.get_current_setting()
	eq_(l.start_setting['bri'], start_bri)

def test_turned_off_light():
	# if a light is turned off, it should do nothing
	l.start_setting['on'] = False

	start_bri = l.start_setting['bri']
	start_hue = l.start_setting['hue']
	data = '{"on":true,"bri":123,"hue":40000}'
	l.set_light(data)
	l.get_current_setting()
	eq_(l.start_setting['bri'], start_bri)
	eq_(l.start_setting['hue'], start_hue)

	# Reset again
	l.start_setting['on'] = True

# Without overriding hue settings
class settings2:
	mode		= 1 # theatre
	light 		= 1 # single bulb
	light_id	= 2
	group_id	= 0
	misc_initialflash = True
	override_hue = False
	override_undim_bri = True
	dimmed_bri	= 0
	undim_bri	= 228
	dimmed_hue	= 10000
	undim_hue	= 30000
	ambilight_dim = False
	ambilight_dim_group = 1
	debug		= False

s2 = settings2
s2.bridge_ip = BRIDGE_IP
s2.bridge_user = BRIDGE_USER
l2 = Light(s2)
l2.logger.disable()

def test_dim_light_override():
	l2.get_current_setting()
	start_hue = l2.start_setting['hue']
	l2.dim_light()
	time.sleep(1)
	l2.get_current_setting()
	eq_(l2.start_setting['bri'], s2.dimmed_bri)
	eq_(l2.start_setting['hue'], start_hue)

	# reset light to on, get_current_setting just set it to off
	l2.start_setting['on'] = "true"

def test_brighter_light_override():
	l2.get_current_setting()
	start_hue = l2.start_setting['hue']
	l2.start_setting['on'] = "true"
	l2.start_setting['bri'] = 255
	l2.brighter_light()
	time.sleep(1)
	l2.get_current_setting()
	ok_(l2.start_setting['bri'] == s2.undim_bri)
	ok_(l2.start_setting['hue'] == start_hue)

# living white
s = settings()
s.bridge_ip = BRIDGE_IP
s.bridge_user = BRIDGE_USER
l3 = Light(s)
l3.logger.disable()
l3.livingwhite = True

def test_living_light_set_light():
	l3.get_current_setting()
	start_hue = l3.start_setting['hue']
	l3.set_light2(200, 1, 1)
	# Although we're setting a hue and sat, it should be ignored
	l3.get_current_setting()
	eq_(l3.start_setting['hue'], start_hue)

# not overriding undim brightness
class settings4:
	mode		= 1 # theatre
	light 		= 1 # single bulb
	light_id	= 2
	group_id	= 0
	misc_initialflash = True
	override_hue = False
	override_undim_bri = False
	dimmed_bri	= 5
	undim_bri	= 228
	dimmed_hue	= 10000
	undim_hue	= 30000
	ambilight_dim = False
	ambilight_dim_group = 1
	debug		= False

s4 = settings4
s4.bridge_ip = BRIDGE_IP
s4.bridge_user = BRIDGE_USER
l4 = Light(s4)
l4.logger.disable()

def test_not_overriding_undim_bri():
	data = '{"on":true,"bri":123}'
	l4.set_light(data)
	time.sleep(1)
	l4.get_current_setting()
	start_bri = l4.start_setting['bri']
	ok_(start_bri == 123)

	l4.dim_light()
	time.sleep(1)
	l4.brighter_light()
	time.sleep(1)

	l4.get_current_setting()
	# should be at 123, not 228
	ok_(l4.start_setting['bri'] == 123)