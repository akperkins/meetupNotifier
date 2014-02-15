
#Class used to manage log files
class Logger:
    def __init__(self, log):
        self.log = log
        
        #writes the message passed to the log file, creates the log file if the file does not already exist
    def logMessage(self, message):
        with open(self.log, "a") as myfile:
            import datetime
            myfile.write("\nTime: " + str(datetime.datetime.now().time()) + " - " + message + "\n*******************")
