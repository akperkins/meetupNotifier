import urllib2
import json
import sys
from Event import Event
from EventDAO import EventDAO

import ConfigParser
config = ConfigParser.ConfigParser()
config.read('settings.cfg')

ERROR_LOG_LOCATION = config.get('section', 'ERROR_LOG_LOCATION')
INFO_LOG_LOCATION = config.get('section', 'INFO_LOG_LOCATION')
WEB_SERVICE_URL = config.get('section', 'WEB_SERVICE_URL')
SMTP_SERVER = config.get('section', 'SMTP_SERVER')
SMTP_SERVER_PORT = int(config.get('section', 'SMTP_SERVER_PORT'))
EMAIL_USERNAME = config.get('section', 'EMAIL_USERNAME')
EMAIL_PASSWORD = config.get('section', 'EMAIL_PASSWORD')
EMAIL_RECEPIENT = config.get('section', 'EMAIL_RECEPIENT')

INFO_PRIORITY = "i"
ERROR_PRIORITY = "e"


#sendEmail sends sn email reporting that a new event has been listed
def sendEmail(message):
    import smtplib
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText

    msg = MIMEMultipart()
    msg['From'] = EMAIL_USERNAME
    msg['To'] = EMAIL_RECEPIENT
    msg['Subject'] = "New Meetup Listed"
    msg.attach(MIMEText(message))

    mailServer = smtplib.SMTP(SMTP_SERVER, SMTP_SERVER_PORT)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    mailServer.sendmail(EMAIL_USERNAME, EMAIL_RECEPIENT, msg.as_string())
    mailServer.close()
    
    writeOut("E-mail sent to "+recipient, INFO_PRIORITY)
    
#returns a new string that is identical to the string passed except all the ascii characters are removed
def removeNonAscii(phrase): 
    return "".join(i for i in phrase if ord(i)<128)

#writes a message to either the info or error log and prints the message
def writeOut(message, priority):
    print message
    logFile = ""
    if priority == INFO_PRIORITY:
        logFile = INFO_LOG_LOCATION
    elif priority == ERROR_PRIORITY:
        logFile = ERROR_LOG_LOCATION
    else:
        print "invalid priority reached"

    with open(logFile, "a") as myfile:
        import datetime
        myfile.write("\nTime: " + str(datetime.datetime.now().time()) + " - " + message + "\n*******************")
    

#obtains current meetup in JSON format from web service        
def getWebServiceResponse():
    response = urllib2.urlopen(WEB_SERVICE_URL)
    data = json.loads(response.read())
    return data

#creates event objects for each object found in JSON
def extractCurrentEvents(json):
    currentEvents = []
    for event in json["results"]:
        eventId = event["id"]
        eventName = event["name"]
        eventDescription = removeNonAscii( event["description"] )
        eventIsPublic = False
        if event["visibility"] == "public":
            eventIsPublic = True
        currentEvents.append(Event(eventId,eventName,eventDescription,eventIsPublic))
    return currentEvents

#error handling code - error message ( and trace ) is written to the log
def notifyOfException(exception):
        import traceback
        tb = traceback.format_exc()
        errorMessage = "An exception was thrown. Exception: " + str(exception) + ". Traceback: " + str(tb)
        writeOut(errorMessage, ERROR_PRIORITY)

def main():
    try:
        writeOut("starting script...", INFO_PRIORITY)
        json = getWebServiceResponse()
        writeOut("JSON response " + str(json), INFO_PRIORITY)

        currentEvents = extractCurrentEvents(json)
        knownEvents = EventDAO().readAllEvents()

        #compares each event found from web request and see if it is already stored, if not, then email is reported and the event is stored
        for event in currentEvents:
            if event not in knownEvents :
                writeOut( "New event found! Sending an email for event: \"" + event.name + "\". ", INFO_PRIORITY)
                sendEmail("New event listed for meetup: " + str(event))
                EventDAO().createNewEventRecord(event)
            else:
                writeOut( str(event.name) + " was already stored", INFO_PRIORITY)
        writeOut("script terminated successfully!", INFO_PRIORITY)
    except:
        notifyOfException(sys.exc_info()[0])
        
#start of application
main()
