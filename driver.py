import urllib2
import json
import sys
from Event import Event
from EventDAO import EventDAO
from Logger import Logger

import ConfigParser
config = ConfigParser.ConfigParser()
config.read('settings.cfg')

#treat as constants
ERROR_LOG_LOCATION = config.get('section', 'ERROR_LOG_LOCATION')
INFO_LOG_LOCATION = config.get('section', 'INFO_LOG_LOCATION')
WEB_SERVICE_URL = config.get('section', 'WEB_SERVICE_URL')
SMTP_SERVER = config.get('section', 'SMTP_SERVER')
SMTP_SERVER_PORT = int(config.get('section', 'SMTP_SERVER_PORT'))
EMAIL_USERNAME = config.get('section', 'EMAIL_USERNAME')
EMAIL_PASSWORD = config.get('section', 'EMAIL_PASSWORD')
EMAIL_RECEPIENT = config.get('section', 'EMAIL_RECEPIENT')

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
def writeOut(message, logger):
    print message
    logger.logMessage(message)

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
def notifyOfException(exception, logger):
        import traceback
        tb = traceback.format_exc()
        errorMessage = "An exception was thrown. Exception: " + str(exception) + ". Traceback: " + str(tb)
        writeOut(errorMessage, logger)

"""
Created by: Andre Perkins
Date: 2/14/2014
The purpose of this application is to notify me when new meetup events are posted to the Android meetup group. It queries the meetup.com restful api and checks if any new 
meetup has been listed. If a new meetup has been listed, then an email is sent to me.
"""
def main():
    try:
        errorLog = Logger(ERROR_LOG_LOCATION)
        infoLog = Logger(INFO_LOG_LOCATION)


        writeOut("starting script...", infoLog)
        json = getWebServiceResponse()
        writeOut("JSON response " + str(json), infoLog)

        currentEvents = extractCurrentEvents(json)
        knownEvents = EventDAO().readAllEvents()

        #compares each event found from web request and see if it is already stored, if not, then email is reported and the event is stored
        for event in currentEvents:
            if event not in knownEvents :
                writeOut( "New event found! Sending an email for event: \"" + event.name + "\". ", infoLog)
                sendEmail("New event listed for meetup: " + str(event))
                EventDAO().createNewEventRecord(event)
            else:
                writeOut( str(event.name) + " was already stored", infoLog)
        writeOut("script terminated successfully!", infoLog)
    except:
        notifyOfException(sys.exc_info()[0], errorLog)
        
#start of application
main()
