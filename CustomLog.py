import time
import ConstantsAndStructures

class Log:

	def __init__(self, oLogFile):
		self.oLogFile = oLogFile

	def Log(self, sMessage):
		self.oLogFile.writeline(sMessage)

	def IngestReportAndLog(self, tReport):
		pass
		
