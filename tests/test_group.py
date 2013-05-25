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
	light 		= 0 # single bulb
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
g = Group(s)
g.logger.disable()

def test_group():
	ok_(g.group == True)

def test_current_setting():
	ok_(g.lights['1'].start_setting['bri'] >= 0, "Light 1 should be turned on")
	ok_(g.lights['2'].start_setting['bri'] >= 0, "Light 2 should be turned on")
	ok_(g.lights['3'].start_setting['bri'] >= 0, "Light 3 should be turned on")

	g.lights['1'].logger.disable()
	g.lights['2'].logger.disable()
	g.lights['3'].logger.disable()

def test_set_light():
	g.set_light('{"on":true,"hue":100,"transitiontime":4}')
	time.sleep(1)

	g.lights['1'].get_current_setting()
	g.lights['2'].get_current_setting()
	g.lights['3'].get_current_setting()

	eq_(g.lights['1'].start_setting['hue'], 100)
	eq_(g.lights['2'].start_setting['hue'], 100)
	eq_(g.lights['3'].start_setting['hue'], 100)

def test_set_light2():
	g.set_light2(20000, 100, 100)
	time.sleep(2)
	g.lights['1'].get_current_setting()
	g.lights['2'].get_current_setting()
	g.lights['3'].get_current_setting()

	eq_(g.lights['1'].start_setting['hue'], 20000)
	eq_(g.lights['2'].start_setting['hue'], 20000)
	eq_(g.lights['3'].start_setting['hue'], 20000)
	eq_(g.lights['1'].start_setting['sat'], 100)
	eq_(g.lights['2'].start_setting['sat'], 100)
	eq_(g.lights['3'].start_setting['sat'], 100)
	eq_(g.lights['1'].start_setting['bri'], 100)
	eq_(g.lights['2'].start_setting['bri'], 100)
	eq_(g.lights['3'].start_setting['bri'], 100)

def test_dim_light():
	g.dim_light()
	time.sleep(2)
	g.lights['1'].get_current_setting()
	g.lights['2'].get_current_setting()
	g.lights['3'].get_current_setting()
	eq_(g.lights['1'].start_setting['bri'], 0)
	eq_(g.lights['2'].start_setting['bri'], 0)
	eq_(g.lights['3'].start_setting['bri'], 0)

	# set the lights to on again, get_current_setting just set them to off
	g.lights['1'].start_setting['on'] = "true"
	g.lights['2'].start_setting['on'] = "true"
	g.lights['3'].start_setting['on'] = "true"

def test_brighter_light():
	g.brighter_light()
	time.sleep(2)
	g.lights['1'].get_current_setting()
	g.lights['2'].get_current_setting()
	g.lights['3'].get_current_setting()
	eq_(g.lights['1'].start_setting['bri'], 228)
	eq_(g.lights['2'].start_setting['bri'], 228)
	eq_(g.lights['3'].start_setting['bri'], 228)
