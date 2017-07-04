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
from Components.Label import Label
from Components.Network import iNetwork
from Tools.Directories import fileExists
from enigma import eServiceCenter, eServiceReference, eTimer
from boxbranding import getImageDistro
from shutil import rmtree, move, copy
from Components.Language import language
from Components.ConfigList import ConfigListScreen
from enigma import getDesktop
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import gettext, os
import os

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


class TunerServerusb(Screen, ConfigListScreen):
	screenWidth = getDesktop(0).size().width()
	if screenWidth and screenWidth == 1920:
		skin = """<screen position="center,center" size="1000,755" backgroundColor="white" flags="wfNoBorder">
		<widget name="lab1" position="15,79" size="971,514" font="Regular; 25" transparent="0" foregroundColor="black" backgroundColor="transpWhite1" halign="left" />
		<widget name="lab2" position="170,630" size="300,30" font="Caviar_bold; 20" valign="center" halign="right" transparent="0" foregroundColor="black" backgroundColor="transpWhite1" />
		<widget name="lab3" position="467,78" size="300,30" font="Regular; 25" valign="center" halign="left" transparent="1" foregroundColor="black" backgroundColor="transpWhite1" zPosition="10" />
                <widget name="labstop" position="480,630" size="260,30" font="Caviar_bold; 20" valign="center" halign="center" backgroundColor="red" foregroundColor="white" />
		<widget name="labrun" position="480,630" size="260,30" zPosition="1" font="Caviar_bold; 20" valign="center" halign="center" backgroundColor="green" foregroundColor="white" />
		<widget name="key_yellow" position="385,705" zPosition="1" size="240,40" font="Caviar_bold; 18" halign="center" valign="center" backgroundColor="yellow" transparent="0" foregroundColor="white" />
		<widget name="key_green" position="25,705" zPosition="1" size="240,40" font="Caviar_bold; 18" halign="center" valign="center" backgroundColor="green" transparent="0" foregroundColor="white" />
		<widget name="key_red" position="746,705" zPosition="1" size="240,40" font="Caviar_bold; 18" halign="center" valign="center" backgroundColor="red" transparent="0" foregroundColor="white" />
                <eLabel position="0,0" size="1000,68" transparent="0" foregroundColor="white" backgroundColor="transpblue" zPosition="-10" />
                <eLabel position="0,68" size="1000,710" transparent="0" foregroundColor="white" backgroundColor="transpWhite1" zPosition="-10" />
                <widget source="Title" transparent="1" render="Label" zPosition="2" valign="center" halign="left" position="22,10" size="953,50" font="Caviar_bold; 32" backgroundColor="transpblue" foregroundColor="white" noWrap="1" />
</screen>"""
	else:
		skin = """<screen position="center,center" size="800,700" flags="wfNoBorder">
                <widget name="lab1" position="10,53" size="780,509" font="Regular;20" transparent="0" foregroundColor="metrixAccent1" backgroundColor="metrixBackground" />
		<widget name="lab2" position="80,580" size="300,30" font="Regular;20" valign="center" halign="right" transparent="0" backgroundColor="metrixBackground" />
		<widget name="lab3" position="361,50" size="300,30" font="Regular; 20" valign="center" halign="left" transparent="1" zPosition="10" foregroundColor="metrixAccent1" backgroundColor="metrixBackground" />
                <widget name="labstop" position="390,580" size="260,30" font="Regular;20" valign="center" halign="center" backgroundColor="red" foregroundColor="white" />
		<widget name="labrun" position="390,580" size="260,30" zPosition="1" font="Regular;20" valign="center" halign="center" backgroundColor="green" foregroundColor="white" />
		<widget name="key_yellow" position="280,635" zPosition="1" size="240,40" font="Regular;18" halign="center" valign="center" backgroundColor="yellow" transparent="0" foregroundColor="white" />
		<widget name="key_green" position="25,635" zPosition="1" size="240,40" font="Regular;18" halign="center" valign="center" backgroundColor="green" transparent="0" foregroundColor="white" />
		<widget name="key_red" position="535,635" zPosition="1" size="240,40" font="Regular;18" halign="center" valign="center" backgroundColor="red" transparent="0" foregroundColor="white" />
                <widget source="Title" transparent="1" render="Label" zPosition="2" valign="center" halign="left" position="10,0" size="780,50" noWrap="1" font="SetrixHD; 28" backgroundColor="metrixBackground" />
</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("OPTuner Server setup USB"))

		self["lab1"] = Label(_("This plugin implements the Tuner Server feature included. It will allow you to share the tuners of this box with another STB, PC and/or another compatible device in your home network.\nThe server will build a virtual channels list in the folder /media/usb/tuner on this box.\nYou can access the tuner(s) of this box from clients on your internal lan using nfs, cifs, UPnP or any other network mountpoint.\nThe tuner of the server (this box) has to be avaliable. This means that if you have ony one tuner in your box you can only stream the channel you are viewing (or any channel you choose if your box is in standby).\nRemember to select the correct audio track in the audio menu if there is no audio or the wrong language is streaming.\nNOTE: The server is built, based on your current ip and the current channel list of this box. If you change your ip or your channel list is updated, you will need to rebuild the server database.\n\n\t\t"))
		self["lab2"] = Label(_("Current Status:"))
                self["lab3"] = Label()
		self["labstop"] = Label(_("Server Disabled"))
		self["labrun"] = Label(_("Server Enabled"))
		self["key_green"] = Label(_("Build Server"))
		self["key_red"] = Label(_("Close"))
		self["key_yellow"] = Label(_("Disable Server"))
		self.my_serv_active = False
		self.ip = "0.0.0.0"

		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"ok": self.close,
			"back": self.close,
			"green": self.ServStartu,
			"yellow": self.ServStopu,
			"red": self.close
		})
		self.activityTimeru = eTimer()
		self.activityTimeru.timeout.get().append(self.doServStartu)
		self.onClose.append(self.delTimeru)
		self.onLayoutFinish.append(self.updateServu)

	def ServStartu(self):
		if os.path.ismount("/media/usb"):
			self["lab1"].setText(_("Your server is now building\nPlease wait ..."))
			self.activityTimeru.start(10)
		else:
			self.session.open(MessageBox, _("Sorry, but you need to have a device mounted at '/media/usb'"), MessageBox.TYPE_INFO)

	def doServStartu(self):
		self.activityTimeru.stop()
		if os.path.exists("/media/usb/tuner"):
			rmtree("/media/usb/tuner")
		ifaces = iNetwork.getConfiguredAdapters()
		for iface in ifaces:
			ip = iNetwork.getAdapterAttribute(iface, "ip")
			ipm = "%d.%d.%d.%d" % (ip[0], ip[1], ip[2], ip[3])
			if ipm != "0.0.0.0":
				self.ip = ipm

		os.mkdir("/media/usb/tuner", 0755)
		s_type = '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 22) || (type == 25) || (type == 134) || (type == 195)'
		serviceHandler = eServiceCenter.getInstance()
		services = serviceHandler.list(eServiceReference('%s FROM BOUQUET "bouquets.tv" ORDER BY bouquet'%(s_type)))
		bouquets = services and services.getContent("SN", True)
		count = 1
		for bouquet in bouquets:
			self.poPulateu(bouquet, count)
			count += 1

		mytextipu = "IP %s" % (self.ip)
		self["lab1"].setText(_("Server avaliable on........                             \nTo access this box's tuners you can connect via Lan or UPnP.\n\n1) To connect via lan you have to mount the /media/usb folder of this box in the client /media/usb folder. Then you can access the tuners server channel list from the client Media player -> USB -> tuner.\n2) To connect via UPnP you need an UPnP server that can manage .m3u files like Xupnpd included in Openplus."))
                self["lab3"].setText(_(mytextipu))
		self.session.open(MessageBox, _("Build Complete!"), MessageBox.TYPE_INFO)
		self.updateServu()


	def poPulateu(self, bouquet, count):
		n = "%03d_" % (count)
		name = n + self.cleanName(bouquet[1])
		#path = "/media/hdd/tuner/" + name
		path = "/media/usb/tuner/"
		#os.mkdir(path, 0755)
		serviceHandler = eServiceCenter.getInstance()
		services = serviceHandler.list(eServiceReference(bouquet[0]))
		channels = services and services.getContent("SN", True)
		count2 = 1
		for channel in channels:
			if not int(channel[0].split(":")[1]) & 64:
				n2 = "%03d_" % (count2)
				#filename = path + "/" + n2 + self.cleanName(channel[1]) + ".m3u"
				filename = path + "/" + name + ".m3u"
				try:
					out = open(filename, "a")
				except:
					continue
				out.write("#EXTM3U\n")
				out.write("#EXTINF:-1," + channel[1] + "\n")
				out.write("http://" + self.ip + ":8001/" + channel[0]+ "\n\n")
				out.close()
				count2 += 1

	def cleanName(self, name):
		name = name.replace(" ", "_")
		name = name.replace('\xc2\x86', '').replace('\xc2\x87', '')
		name = name.replace(".", "_")
		name = name.replace("<", "")
		name = name.replace("<", "")
		name = name.replace("/", "")
		return name

	def ServStopu(self):
		if self.my_serv_active == True:
			self["lab1"].setText(_("Your server is now being deleted\nPlease Wait ..."))
			if os.path.exists("/media/usb/tuner"):
				rmtree("/media/usb/tuner")
			mybox = self.session.open(MessageBox, _("Tuner Server Disabled."), MessageBox.TYPE_INFO)
			mybox.setTitle(_("Info"))
			self.updateServu()
		self.session.open(MessageBox, _("Server now disabled!"), MessageBox.TYPE_INFO)

	def updateServu(self):
		self["labrun"].hide()
		self["labstop"].hide()
		self.my_serv_active = False

		if os.path.isdir("/media/usb/tuner"):
			self.my_serv_active = True
			self["labstop"].hide()
			self["labrun"].show()
		else:
			self["labstop"].show()
			self["labrun"].hide()

	def delTimeru(self):
		del self.activityTimeru


class TunerServerhdd(Screen, ConfigListScreen):
	screenWidth = getDesktop(0).size().width()
	if screenWidth and screenWidth == 1920:
		skin = """<screen position="center,center" size="1000,755" backgroundColor="white" flags="wfNoBorder">
		<widget name="lab1" position="15,79" size="971,514" font="Regular; 25" transparent="0" foregroundColor="black" backgroundColor="transpWhite1" halign="left" />
		<widget name="lab2" position="170,630" size="300,30" font="Caviar_bold; 20" valign="center" halign="right" transparent="0" foregroundColor="black" backgroundColor="transpWhite1" />
                <widget name="lab3" position="467,78" size="300,30" font="Regular; 25" valign="center" halign="left" transparent="1" foregroundColor="black" backgroundColor="transpWhite1" zPosition="10" />                <widget name="labstop" position="480,630" size="260,30" font="Caviar_bold; 20" valign="center" halign="center" backgroundColor="red" foregroundColor="white" />
		<widget name="labrun" position="480,630" size="260,30" zPosition="1" font="Caviar_bold; 20" valign="center" halign="center" backgroundColor="green" foregroundColor="white" />
		<widget name="key_yellow" position="385,705" zPosition="1" size="240,40" font="Caviar_bold; 18" halign="center" valign="center" backgroundColor="yellow" transparent="0" foregroundColor="white" />
		<widget name="key_green" position="25,705" zPosition="1" size="240,40" font="Caviar_bold; 18" halign="center" valign="center" backgroundColor="green" transparent="0" foregroundColor="white" />
		<widget name="key_red" position="746,705" zPosition="1" size="240,40" font="Caviar_bold; 18" halign="center" valign="center" backgroundColor="red" transparent="0" foregroundColor="white" />
                <eLabel position="0,0" size="1000,68" transparent="0" foregroundColor="white" backgroundColor="transpblue" zPosition="-10" />
                <eLabel position="0,68" size="1000,710" transparent="0" foregroundColor="white" backgroundColor="transpWhite1" zPosition="-10" />
                <widget source="Title" transparent="1" render="Label" zPosition="2" valign="center" halign="left" position="22,10" size="953,50" font="Caviar_bold; 32" backgroundColor="transpblue" foregroundColor="white" noWrap="1" />
</screen>"""
	else:
		skin = """<screen position="center,center" size="800,700" flags="wfNoBorder">
                <widget name="lab1" position="10,53" size="780,509" font="Regular;20" transparent="0" foregroundColor="metrixAccent1" backgroundColor="metrixBackground" />
		<widget name="lab2" position="80,580" size="300,30" font="Regular;20" valign="center" halign="right" transparent="0" backgroundColor="metrixBackground" />
		<widget name="lab3" position="361,50" size="300,30" font="Regular; 20" valign="center" halign="left" transparent="1" zPosition="10" foregroundColor="metrixAccent1" backgroundColor="metrixBackground" />
                <widget name="labstop" position="390,580" size="260,30" font="Regular;20" valign="center" halign="center" backgroundColor="red" foregroundColor="white" />
		<widget name="labrun" position="390,580" size="260,30" zPosition="1" font="Regular;20" valign="center" halign="center" backgroundColor="green" foregroundColor="white" />
		<widget name="key_yellow" position="280,635" zPosition="1" size="240,40" font="Regular;18" halign="center" valign="center" backgroundColor="yellow" transparent="0" foregroundColor="white" />
		<widget name="key_green" position="25,635" zPosition="1" size="240,40" font="Regular;18" halign="center" valign="center" backgroundColor="green" transparent="0" foregroundColor="white" />
		<widget name="key_red" position="535,635" zPosition="1" size="240,40" font="Regular;18" halign="center" valign="center" backgroundColor="red" transparent="0" foregroundColor="white" />
                <widget source="Title" transparent="1" render="Label" zPosition="2" valign="center" halign="left" position="10,0" size="780,50" noWrap="1" font="SetrixHD; 28" backgroundColor="metrixBackground" />
</screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("OPTuner Server setup HDD"))

		self["lab1"] = Label(_("This plugin implements the Tuner Server feature included. It will allow you to share the tuners of this box with another STB, PC and/or another compatible device in your home network.\nThe server will build a virtual channels list in the folder /media/hdd/tuner on this box.\nYou can access the tuner(s) of this box from clients on your internal lan using nfs, cifs, UPnP or any other network mountpoint.\nThe tuner of the server (this box) has to be avaliable. This means that if you have ony one tuner in your box you can only stream the channel you are viewing (or any channel you choose if your box is in standby).\nRemember to select the correct audio track in the audio menu if there is no audio or the wrong language is streaming.\nNOTE: The server is built, based on your current ip and the current channel list of this box. If you change your ip or your channel list is updated, you will need to rebuild the server database.\n\n\t\t"))
		self["lab2"] = Label(_("Current Status:"))
                self["lab3"] = Label()
		self["labstop"] = Label(_("Server Disabled"))
		self["labrun"] = Label(_("Server Enabled"))
		self["key_green"] = Label(_("Build Server"))
		self["key_red"] = Label(_("Close"))
		self["key_yellow"] = Label(_("Disable Server"))
		self.my_serv_active = False
		self.ip = "0.0.0.0"

		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"ok": self.close,
			"back": self.close,
			"green": self.ServStart,
			"yellow": self.ServStop,
			"red": self.close
		})
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.doServStart)
		self.onClose.append(self.delTimer)
		self.onLayoutFinish.append(self.updateServ)

	def ServStart(self):
		if os.path.ismount("/media/hdd"):
			self["lab1"].setText(_("Your server is now building\nPlease wait ..."))
			self.activityTimer.start(10)
		else:
			self.session.open(MessageBox, _("Sorry, but you need to have a device mounted at '/media/hdd'"), MessageBox.TYPE_INFO)

	def doServStart(self):
		self.activityTimer.stop()
		if os.path.exists("/media/hdd/tuner"):
			rmtree("/media/hdd/tuner")
		ifaces = iNetwork.getConfiguredAdapters()
		for iface in ifaces:
			ip = iNetwork.getAdapterAttribute(iface, "ip")
			ipm = "%d.%d.%d.%d" % (ip[0], ip[1], ip[2], ip[3])
			if ipm != "0.0.0.0":
				self.ip = ipm

		os.mkdir("/media/hdd/tuner", 0755)
		s_type = '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 22) || (type == 25) || (type == 134) || (type == 195)'
		serviceHandler = eServiceCenter.getInstance()
		services = serviceHandler.list(eServiceReference('%s FROM BOUQUET "bouquets.tv" ORDER BY bouquet'%(s_type)))
		bouquets = services and services.getContent("SN", True)
		count = 1
		for bouquet in bouquets:
			self.poPulate(bouquet, count)
			count += 1

		mytextip = "IP %s" % (self.ip)
		self["lab3"].setText(_(mytextip))
                self["lab1"].setText(_("Server avaliable on........                             \nTo access this box's tuners you can connect via Lan or UPnP.\n\n1) To connect via lan you have to mount the /media/hdd folder of this box in the client /media/hdd folder. Then you can access the tuners server channel list from the client Media player -> Harddisk -> tuner.\n2) To connect via UPnP you need an UPnP server that can manage .m3u files like Xupnpd included in Openplus."))
		self.session.open(MessageBox, _("Build Complete!"), MessageBox.TYPE_INFO)
		self.updateServ()


	def poPulate(self, bouquet, count):
		n = "%03d_" % (count)
		name = n + self.cleanName(bouquet[1])
		#path = "/media/hdd/tuner/" + name
		path = "/media/hdd/tuner/"
		#os.mkdir(path, 0755)
		serviceHandler = eServiceCenter.getInstance()
		services = serviceHandler.list(eServiceReference(bouquet[0]))
		channels = services and services.getContent("SN", True)
		count2 = 1
		for channel in channels:
			if not int(channel[0].split(":")[1]) & 64:
				n2 = "%03d_" % (count2)
				#filename = path + "/" + n2 + self.cleanName(channel[1]) + ".m3u"
				filename = path + "/" + name + ".m3u"
				try:
					out = open(filename, "a")
				except:
					continue
				out.write("#EXTM3U\n")
				out.write("#EXTINF:-1," + channel[1] + "\n")
				out.write("http://" + self.ip + ":8001/" + channel[0]+ "\n\n")
				out.close()
				count2 += 1

	def cleanName(self, name):
		name = name.replace(" ", "_")
		name = name.replace('\xc2\x86', '').replace('\xc2\x87', '')
		name = name.replace(".", "_")
		name = name.replace("<", "")
		name = name.replace("<", "")
		name = name.replace("/", "")
		return name

	def ServStop(self):
		if self.my_serv_active == True:
			self["lab1"].setText(_("Your server is now being deleted\nPlease Wait ..."))
			if os.path.exists("/media/hdd/tuner"):
				rmtree("/media/hdd/tuner")
			mybox = self.session.open(MessageBox, _("Tuner Server Disabled."), MessageBox.TYPE_INFO)
			mybox.setTitle(_("Info"))
			self.updateServ()
		self.session.open(MessageBox, _("Server now disabled!"), MessageBox.TYPE_INFO)

	def updateServ(self):
		self["labrun"].hide()
		self["labstop"].hide()
		self.my_serv_active = False

		if os.path.isdir("/media/hdd/tuner"):
			self.my_serv_active = True
			self["labstop"].hide()
			self["labrun"].show()
		else:
			self["labstop"].show()
			self["labrun"].hide()

	def delTimer(self):
		del self.activityTimer