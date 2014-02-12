"""
Represents a meetup event
"""
class Event:
    #constructor
    def __init__(self, id, name, description, public):
        self.id = id
        self.name = name
        self.description = description
        self.public = public
        
    #compares two functions and see if they are equal by comparing their id fields
    def __eq__(self, other):
        return self.id == other.id

    #toString routine
    def __str__(self):
        return "id : " + self.id + ", name: " + self.name + ", descrition: " + self.description + ", public: " + str(self.public) 
