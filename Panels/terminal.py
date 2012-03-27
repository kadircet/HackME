import Tkinter
import threading
import const

class Terminal(Tkinter.Label):
	def __init__(self, mWindow, width, height, bgcolor, shutTime=2.0):
		Tkinter.Label.__init__(self, master=mWindow, foreground="green", background=bgcolor, anchor=Tkinter.SW, justify=Tkinter.LEFT)

		ch = 13
		cw = 7
		self.th = height/ch
		self.lw = width/cw

		self.height, self.width = height, width
		self.shutTime = shutTime
		self.userName = ""
		self.passWord = ""

		self.config(font=("courier",  8, "normal"), width=self.lw, height=self.th, relief=Tkinter.SUNKEN)

		self.text = ""
		self.lineL = 0
		self.lineC = 0
		self.last = -1
		
		self.state = const.states.boot
		self.game = mWindow
		self.sendCommands = []
		self.aliases = {}

		self.commands =	[
			['help', ['shows that menu', self.c_help]],
			['shutdown', ['shutdowns computer', self.c_shutdown]],
			['restart', ['restarts computer', self.c_restart]],
			['clear', ['clears terminal', self.c_clear]],
			['alias', ['declares a variable', self.c_alias]],
			['version', ['shows version info', self.c_version]],
			['whoami', ['shows user information', self.c_whoami]]
		]

	def keyPressed(self, event):
		if self.state == const.states.boot or self.state == const.states.init:
			return
		if event.keysym == "Return":
			print "enter geldi"
			command = self.getLastLine()
			print command
			self.printOut('\n')
			self.doCommand(command)
			if self.state == const.states.hack:
				self.printOut(":>")
		elif event.keysym == "BackSpace":
			line = self.getLastLine(clean=False)
			if self.state == const.states.login:
				if line == "Login: " or line == "Password: ":
					return
			if line == ":>":
				return
			self.printOut('\b')
		elif event.keycode == "Escape":
			pass
		elif event.keysym == "Up": #up arrow
			self.getPrevCommand()
		elif event.keysym == "Down": #down arrow
			self.getNextCommand()
		else:
			if len(event.char) == 1:
				self.printOut(event.char)
		for key in event.__dict__:
					print key, ':', event.__dict__[key]

	def updateText(self):
		self.config(text=self.text + '_')

	def doCommand(self, line, printout=True):
		command = line
		if self.state == const.states.login:
			if self.userName == "":
				self.userName = command[len("Login: "):]
				self.printOut("Password: ")
			else:
				self.passWord = command[len("Password: "):]
				self.login(self.userName, self.passWord)
			return
		
		cSplit = line.lower().split(' ', 1)
		command = cSplit[0]
		self.line = line
		if command in self.aliases:
			value = self.aliases[command]
			self.addCommand(line)
			for comEntry in self.commands:
				if value.lower() == comEntry[0]:
					comEntry[1][1]()
					command = ""
			if command != "" and printout:
				self.printOut(value + '\n')
			return value
		else:
			for comEntry in self.commands:
				if command == comEntry[0]:
					self.addCommand(line)
					return comEntry[1][1]()
		
		self.printOut(command + ": not found\n")
		self.addCommand(line)
		return -1
	
	def addCommand(self, command):
		if len(self.sendCommands)>0:
			if self.sendCommands[len(self.sendCommands)-1] == command:
				return
		self.sendCommands.append(command)
		self.last = len(self.sendCommands) - 1
	
	def c_version(self):
		self.printOut("KadOS v2.3\n")
		
	def c_whoami(self):
		self.printOut(self.userName + '\n')
		
	def c_whoareyou(self):
		self.printOut('\n')
	
	def c_alias(self):
		params = self.line.split(' ', 2)
		if len(params) == 2:
			if params[1] in self.aliases:
				del self.aliases[params[1]]
				self.event_generate("<<alias>>")
				self.printOut(params[1] + " has been deleted\n")
				return
		if len(params) != 3:
			self.printOut("Invalid Syntax: alias VAR_NAME VAR_VALUE\n")
			return
		variable = params[1]
		for comEntry in self.commands:
			if comEntry[0] == variable.lower():
				self.printOut("can't assign alias to commands \n")
				return
		value = params[2]
		self.aliases[variable] = value
		self.event_generate("<<alias>>")
		self.printOut(variable + " set to " + value + '\n')

	def c_shutdown(self):
		threading.Thread(target=self.shutDown).start()

	def c_restart(self):
		threading.Thread(target=self.reStart).start()

	def c_help(self):
		for comEntry in self.commands:
			self.printOut(comEntry[0] + ': ' + comEntry[1][0] + '\n')
	
	def c_clear(self):
		self.text = ""
		self.lineC = 0
		self.lineL = 0

		self.updateText()
	
	def getLastLine(self, clean=True):
		line = self.text
		if self.text.find('\n') == -1:
			line = self.text
		else:
			line = self.text[self.text.rfind('\n')+1:]
		
		if clean:
			if line.startswith(":>"):
				line = line[2:]
		if line.endswith('\n'):
			line = line[:-1]
		return line

	def autoComp(self, event=None):
		line = self.getLastLine()
		lineSplit = line.split(' ')
		if len(lineSplit) == 1:
			if line.startswith('./'):
				#file implement
				pass
			else:
				possibilities = []
				for comEntry in self.commands:
					if comEntry[0].startswith(line.lower()):
						possibilities.append(comEntry[0])
						
				for key in self.aliases:
					if key.startswith(line.lower()):
						possibilities.append(key)
						
				if len(possibilities) == 0:
					return
				if len(possibilities) == 1:
					self.printOut(possibilities[0][len(line):])
				else:
					self.printOut('\n')
					for poss in possibilities:
						self.printOut(poss + '\n')
					self.printOut(line)

	def getPrevCommand(self):
		if self.last >= 0:
			lcommand = self.sendCommands[self.last]
			self.last -= 1

			self.printOut("\r:>" + lcommand)
	
	def getNextCommand(self):
		if len(self.sendCommands) - 1 > self.last:
			self.last += 1
			lcommand = self.sendCommands[self.last]

			self.printOut("\r:>" + lcommand)
	
	def printOut(self, text):
		for c in text:
			if c=='\n':
				self.lineC += 1
				self.lineL = 0
				self.text += c
			elif c=='\b':
				if self.lineL > 0:
					self.lineL -= 1
					self.text = self.text[:-1]
			elif c=='\r':
				self.lineL = 0
				self.text = self.text[:self.text.rfind('\n')+1]
			else:
				self.lineL += 1
				self.text += c
			
			if self.lineL >= self.lw:
				command = self.getLastLine()
				self.text += '\n'
				self.lineL = 0
				self.lineC += 1
				self.printOut(": command not found\n:>")

			if self.lineC >= self.th:
				self.lineC -= 1
				self.text = self.text[self.text.find('\n')+1:]

		self.updateText()
		
	def initialize(self):
		f = open('./Content/initialize.txt')
		initText = f.read()
		f.close()

		initTime = 2.0 #secs
		timepl = initTime/len(initText.split('\n'))

		for c in initText.split('\n'):
			if len(c) > 1:
				if not c.endswith('.'):
					self.printOut(c + '\n')
				else:
					self.printOut(c)
			threading._sleep(timepl)
		self.printOut('\b' + self.userName + '\n')
		self.state = const.states.hack

		self.printOut(":>")

	def shutDown(self):
		f = open('./Content/shutdown.txt')
		shutText = f.read()
		f.close()

		self.text = ""
		self.updateText()
		self.state = const.states.shutdown1
		self.event_generate("<<shut>>")

		height = self.height*3
		width = self.width*2
		ch = 13
		cw = 7
		self.th = height/ch
		self.lw = width/cw
		self.config(foreground="white", height=self.th, width=self.lw)

		shutTime = self.shutTime #secs
		timepl = shutTime/len(shutText.split('\n'))

		for c in shutText.split('\n'):
			if len(c) > 1:
				if not c.endswith('.'):
					self.printOut(c + '\n')
				else:
					self.printOut(c)
			threading._sleep(timepl)

		self.state = const.states.shutdown2
		self.event_generate("<<shut>>")
	
	def reStart(self):
		f = open('./Content/shutdown.txt')
		shutText = f.read()
		f.close()

		self.text = ""
		self.updateText()
		self.state = const.states.restart1
		self.event_generate("<<shut>>")

		height = self.height*3
		width = self.width*2
		ch = 13
		cw = 7
		self.th = height/ch
		self.lw = width/cw
		self.config(foreground="white", height=self.th, width=self.lw)

		shutTime = self.shutTime #secs
		timepl = shutTime/len(shutText.split('\n'))

		for c in shutText.split('\n'):
			if len(c) > 1:
				if not c.endswith('.'):
					self.printOut(c + '\n')
				else:
					self.printOut(c)
			threading._sleep(timepl)

		self.state = const.states.restart2
		self.event_generate("<<shut>>")
		
	def login(self, userName, passWord):
		self.state = const.states.init
		threading.Thread(target=self.initialize).start()
	