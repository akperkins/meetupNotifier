import cPickle
import os
from Event import Event

"""
Data access object for Event objects
"""
class EventDAO:
    #file that the cPickle module will read/write to
    PICKLE_FILE = os.path.abspath("eventDAO_PK.txt")
    
    #addANewEvent to the collection of stored events
    def createNewEventRecord(self,event):
        storedEvents = self.readAllEvents()
        storedEvents.append(event)
        with open(self.PICKLE_FILE, "wb") as f:
            storedEvents = cPickle.dump(storedEvents, f)
            
    #returns all stored events
    def readAllEvents(self):
        with open(self.PICKLE_FILE, "rb") as f:
            try:
                return cPickle.load(f)
            except EOFError:
                return []
