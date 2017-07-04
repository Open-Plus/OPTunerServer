##############################################################################
#                          <<< Tuner Server >>>
#
#                      2012 meo <lupomeo@hotmail.com>
#
#  This file is open source software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License version 2 as
#               published by the Free Software Foundation.
#
#                    Modified for OE-Allinace by rossi2000
#
##############################################################################

# This plugin implement the Tuner Server feature included.
# Author: meo / rossi2000
# Please Respect credits
# Adapted by Iqas & Villak for openplus

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Network import iNetwork
from Tools.Directories import fileExists
from enigma import eServiceCenter, eServiceReference, eTimer
from boxbranding import getImageDistro
from shutil import rmtree, move, copy
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from enigma import getDesktop
import gettext, os
import os
import sys
import tunerserver

lang = language.getLanguage()
os.environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("optunerserver")
gettext.bindtextdomain("optunerserver", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/OPTunerServer/locale/"))

def _(txt):
	t = gettext.dgettext("optunerserver", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

class OPTunerServer(Screen, ConfigListScreen):
	screenWidth = getDesktop(0).size().width()
	if screenWidth and screenWidth == 1920:
		skin = """<screen position="center,center" size="1000,755" backgroundColor="white" flags="wfNoBorder">
                <widget name="key_red" position="165,580" zPosition="11" size="160,35" font="Regular;18" halign="center" valign="center" backgroundColor="red" transparent="0" foregroundColor="white" />
                <widget name="key_green" position="165,465" zPosition="11" size="160,35" font="Regular;18" halign="center" valign="center" backgroundColor="green" transparent="0" foregroundColor="white" />
                <widget name="key_yellow" position="165,523" zPosition="11" size="160,35" font="Regular;18" halign="center" valign="center" backgroundColor="yellow" transparent="0" foregroundColor="white" />
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/OPTunerServer/images/fondo.png" position="117,101" size="750,533" alphatest="on" zPosition="10" />
</screen>"""
	else:
		skin = """<screen position="center,center" size="800,555" backgroundColor="white" flags="wfNoBorder">
		 <widget name="key_red" position="60,490" zPosition="11" size="160,35" font="Regular;18" halign="center" valign="center" backgroundColor="red" transparent="0" foregroundColor="white" />
		 <widget name="key_green" position="60,394" zPosition="11" size="160,35" font="Regular;18" halign="center" valign="center" backgroundColor="green" transparent="0" foregroundColor="white" />
		 <widget name="key_yellow" position="60,443" zPosition="11" size="160,35" font="Regular;18" halign="center" valign="center" backgroundColor="yellow" transparent="0" foregroundColor="white" />
                 <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/OPTunerServer/images/fondo.png" position="19,12" size="750,533" alphatest="on" zPosition="10" />
                 
</screen>"""	  
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("OPTuner Server setup"))
		self["key_yellow"] = Label(_("Server USB"))
		self["key_green"] = Label(_("Server HDD"))
		self["key_red"] = Label(_("Close"))
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"yellow": self.serverusb,
			"green": self.serverhdd,
			"ok": self.close,
			"back": self.close,
			"red": self.close

		})

	def serverhdd(self):
		self.session.open(tunerserver.TunerServerhdd)

	def serverusb(self):
		self.session.open(tunerserver.TunerServerusb)
			


def settings(menuid, **kwargs):
	if menuid == "network":
		return [(_("OPTuner Server setup"), main, "tuner_server_setup", None)]
	return []

def main(session, **kwargs):
	session.open(OPTunerServer)

def Plugins(**kwargs):
	screenwidth = getDesktop(0).size().width()
	if screenwidth and screenwidth == 1920:
		return [PluginDescriptor(
			name = _('OPTuner Server setup'),
			description = _('Allow Streaming From Box Tuners'),
			where = [
			PluginDescriptor.WHERE_PLUGINMENU,
			PluginDescriptor.WHERE_EXTENSIONSMENU
			],
			icon = "images/pluginhd.png", 
			fnc = main
			)]
	else:
		return [PluginDescriptor(
			name = _('OPTuner Server setup'),
			description = _('Allow Streaming From Box Tuners'),
			where = [
			PluginDescriptor.WHERE_PLUGINMENU,
			PluginDescriptor.WHERE_EXTENSIONSMENU
			],
			icon = "images/plugin.png", 
			fnc = main
			)]