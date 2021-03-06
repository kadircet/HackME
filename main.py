#!/usr/bin/python
import Tkinter
from source import *
import os
import threading

class HackMEWindow(Tkinter.Tk):
	def __init__(self, width=800, height=600, bgcolor="black"):
		Tkinter.Tk.__init__(self)
		self.title("HackME")
		if os.name == "posix":
			self.iconbitmap(bitmap="@./hackme.xbm")
		elif os.name == "nt":
			self.iconbitmap("./hackme.ico")
		self.bind_all("<Key>", self.eventHandler)
		self.bind_all("<Button>", self.eventHandler)
		self.bind_all("<<boot>>", self.eventHandler)

		self.bind_all("<<shut>>", self.shutDownHandler)
		self.bind_all("<<alias>>", self.eventHandler)
		self.bind_all("<<lang>>", self.langHandler)
		self.bind_all("<<files>>", self.fileHandler)

		self.config(bg=bgcolor)

		self.options = options.Options()
		self.opts = self.options.getOpts()

		lang = self.opts["lang"]
		self.loadLang(lang)

		self.width, self.height = self.winfo_screenwidth(), self.winfo_screenheight()

		self.bgcolor = bgcolor
		self.initView()

	def loadLang(self, lang, chg = False):
		langs = []
		for dirpath, dirnames, filenames in os.walk("./Content"):
			for dir in dirnames:
				langs.append(dir)
		langDir = "./Content/EN"
		if lang in langs:
			langDir = "./Content/" + lang
		else:
			self.terminal1.printOut(self.lang["lang_notfnd"].format(lang))
		langFile = langDir + "/templates.txt"
		f = open(langFile)
		langParams = f.read()
		f.close()

		exec("self.lang = " + langParams)
		self.lang["boot"] = langDir + "/boot.txt"
		self.lang["shutdown"] = langDir + "/shutdown.txt"
		self.lang["initialize"] = langDir + "/initialize.txt"

		if chg:
			for i in range(3):
				self.explorers[i].loadLang(self.lang)
			self.terminal1.lang = self.lang
			self.terminal2.lang = self.lang
			self.boot.lang = self.lang
			self.shut.lang = self.lang

			self.terminal1.lang2 = None
			self.terminal1.loadCommands()
			
		if "terminal1" in self.__dict__:
			self.terminal1.printOut(self.lang["lang_set"].format(self.lang["lang_code"]) + '\n')
	
	def initView(self):
		bgcolor = self.bgcolor
		width, height = self.width, self.height
		if os.name == "nt":
			self.wm_attributes("-fullscreen", 1)

		self.focus_set()

		bootTime = 3.0
		initTime = 2.0
		shutTime = 1.0

		self.boot = boot.Boot(self, width, height, bgcolor, self.lang, bootTime=bootTime)
		self.boot.pack(fill=Tkinter.BOTH, expand=True)

		self.shut = shutdown.Shutdown(self, width, height, bgcolor, self.lang, shutTime=shutTime)
		
		self.explorerFrame = Tkinter.Frame(self, width=width, height=height/3*2)

		explorerNames = ["fileexplorer", "texteditor", "aliases"]
		self.explorers = []

		for i in range(3):
			self.explorers.append(explorer.Explorer(self.explorerFrame, explorerNames[i], width/3, height/3*2, bgcolor, self.lang))
			self.explorers[i].pack(fill=Tkinter.BOTH, side=Tkinter.LEFT, expand=True)
		
		self.terminalFrame = Tkinter.Frame(self)
		self.terminalFrame.pack(side=Tkinter.BOTTOM, fill=Tkinter.BOTH, expand=True)

		self.terminal1 = terminal.Terminal(self.terminalFrame, width/2, height/3, bgcolor, self.lang, self.options, self.opts["tcol"], initTime=initTime)
		self.terminal1.pack(fill=Tkinter.BOTH, side=Tkinter.LEFT, expand=True)
		self.bind_all("<Tab>", self.terminal1.autoComp)
		
		self.terminal2 = terminal.Terminal(self.terminalFrame, width/2, height/3, bgcolor, self.lang, self.options, self.opts["tcol"])
		self.terminal2.pack(fill=Tkinter.BOTH, side=Tkinter.LEFT, expand=True)

	def shutDownHandler(self, event=None):
		if self.shut.state == const.states.hack:
			for i in range(3):
				self.explorers[i].destroy()
			self.explorerFrame.destroy()
			self.terminal2.destroy()
			self.terminalFrame.destroy()

			self.shut.pack(fill=Tkinter.BOTH, expand=True)
			if self.terminal1.state == const.states.restart:
				threading.Thread(target=self.shut.shutDown, args=(True,)).start()
			else:
				threading.Thread(target=self.shut.shutDown).start()
		elif self.shut.state == const.states.shutdown:
			del self.terminal1
			del self.terminal2
			del self.terminalFrame
			for i in range(3):
				del self.explorers[0]
			del self.explorerFrame

			self.destroy()
			self.quit()
		elif self.shut.state == const.states.restart:
			self.shut.destroy()
			self.initView()
	
	def langHandler(self, event=None):
		self.loadLang(self.terminal1.lang2, chg=True)
	
	def fileHandler(self, event=None):
		opti = options.Options()
		opti.uID = self.options.uID
		if "files" in self.terminal1.__dict__:
			self.files = self.terminal1.files
			opti.setOpts(hdd = self.files.hdd)
		else:
			self.opts = opti.getOpts()
			self.files = filesystem.FileSystem(self.opts["hdd"])
			self.terminal1.files = self.files
		
		del opti
		self.explorers[0].loadHDD(self.files)

	def eventHandler(self, event=None):
		if event.type == "2":
			self.terminal1.keyPressed(event)
			self.terminal2.keyPressed(event)
		elif event.type == "35":
			if self.terminal1.state == const.states.boot:
				self.boot.destroy()
				self.terminal1.printOut(self.lang["login"])
				self.terminal1.state = const.states.login
			elif self.terminal1.state == const.states.login:
				self.terminal1.state = const.states.init
				self.explorerFrame.pack(fill=Tkinter.BOTH, side=Tkinter.TOP, expand=True)
			elif self.terminal1.state == const.states.hack:
				self.explorers[2].updAlias(self.terminal1.aliases)
		
		#for key in event.__dict__:
		#	print key, ':', event.__dict__[key]

def main():
	width, height = 1024, 768
	mWindow = HackMEWindow()
	mWindow.mainloop()

if __name__ == "__main__":
	if os.name == "nt" or os.name == "posix":
		main()

