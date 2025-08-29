import time
import uuid
import json
import io
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

# Definition globaler Variablen
ACTORS = ["uml:CallBehaviorAction", "uml:MergeNode", "uml:SendSignalAction", "uml:AcceptEventAction", "uml:Activity",  "uml:ForkNode", "uml:JoinNode", "uml:ActivityPartition"]
EVENTS = ["uml:InitialNode", "uml:ActivityFinalNode", "uml:TimeEvent", "uml:FlowFinalNode", "uml:Signal"]
STATES = ["uml:Parameter", "uml:Property", "uml:ObjectFlow"]
SINGLENODES = ["uml:InitialNode", "uml:ActivityFinalNode", "uml:ForkNode", "uml:JoinNode", "uml:MergeNode", "uml:FlowFinalNode"]
CONTROLFLOW = ["uml:ControlFlow"]
OBJECTFLOW = ["uml:ObjectFlow"]
CONNECTORS = ["uml:ControlFlow", "uml:ObjectFlow"]
DECISIONNODE = ["uml:DecisionNode"]
PORTS = ["uml:InputPin", "uml:OutputPin"]
XMI_TYPE = "{http://www.omg.org/spec/XMI/20131001}type"
XMI_ID = "{http://www.omg.org/spec/XMI/20131001}id"
XMI_IDREF = "{http://www.omg.org/spec/XMI/20131001}idref"

#Methodendefinition
# Wandelt ein Klassenobjekt in ein Dictionary um und ändert den Schlüssel "className" in "class"
def toDict(object):
    obj_dict = object.__dict__
    # rename dict key "className" to "class
    try:obj_dict["class"] = obj_dict.pop("className")
    except: pass
    return obj_dict
# Erzeugt eine zufällige ID mit dem Modul uuid
def getRandomID():
    return str(uuid.uuid4())

# Definition von Default Elementen
defaultStatement = {
    "source" : "",
    "target" : "",
    "visibility" : "",
    "{http://www.omg.org/spec/XMI/20131001}type": "",
    "{http://www.omg.org/spec/XMI/20131001}id" : ""
}

defaultModel = {
    "name": "Integriertes Modell",
    "{http://www.omg.org/spec/XMI/20131001}id": "",
    "{http://www.omg.org/spec/XMI/20131001}type": "uml:Model"
}

defaultProperty = {
    "name": "Integriertes Modell",
    "ownedComment": {"body" : ""},
    "{http://www.omg.org/spec/XMI/20131001}type": "uml:Model"
}

DEFAULT_ELEMENT = {
    "id" : getRandomID()
}

#Klassendefinition

#PropertyClasses

class Property:
    def __init__(self, className, title, value ):
        self.className = className
        self.title = title
        self.value = value

class Name(Property):
    def __init__(self, element):
        value = "NoName"
        if element.get("name") != None:
            value = element.get('name')
        Property.__init__(self, "PC-Name", "dcterms:title", value)

class Description(Property):
    def __init__(self, element):
        #Property.__init__(self, element)
        self.title = "dcterms:description"
        self.className = "PC-Description"
        self.value = element["ownedComment"].get('body')
                 
class Visibility(Property):
    
    def getVisibility(self, element):
        if element.get('visibility') == None:
            visibility = "V-VisibilityKind-1"
        elif element.get('visibility') == "public": 
            visibility = "V-VisibilityKind-0"
        return visibility
    
    def __init__(self, element):
        #Property.__init__(self, element)
        self.title = "SpecIF:Visibility"
        self.className = "PC-Visibility"
        self.value = self.getVisibility(element)
        
class Type(Property):
    def __init__(self, element):
        #Property.__init__(self, element)
        self.title = "dcterms:type"
        self.className = "PC-Type"
        self.value = element.get(XMI_TYPE)

class Stereotype(Property):
    def __init__(self, element):
        #Property.__init__(self, element)
        self.title = "dcterms:title"
        self.className = "PC-Name"
        self.value = ""             

#ResourceClasses
class Resource:
    
    def __init__(self, element):
        self.id = "R-" + getRandomID()
        self.changedAt = time.strftime("%Y-%m-%dT%H:%M:%S+02:00")
        self.properties = Resource.generateProperties(element)
        if element.get("name") != None:
            for property in self.properties:
                if property.get("title") == "dcterms:type":
                    if property.get("value") == "uml:DecisionNode" or property.get("value") == "uml:ObjectFlow":
                        self.title = element.get("name") + " " + self.id
                    else: self.title = element.get("name")
        else:
            for property in self.properties:
                if property.get("title") == "dcterms:type":
                    self.title = property.get("value") + " " + self.id
    
    def generateProperties(element):
        properties = []
        name = Name(element)
        properties.append(toDict(name))
        try:
            description = Description(element)
            properties.append(toDict(description))
        except: pass
        element_type = Type(element)
        properties.append(toDict(element_type))
        visibility = Visibility(element)
        properties.append(toDict(visibility))
        return properties
                    
class Actor(Resource):
    def __init__(self,element):
        Resource.__init__(self, element)
        #self.title = "FMC:Actor"
        self.className = "RC-Actor"
                    
class Event(Resource):
    def __init__(self, element):
        Resource.__init__(self, element)
        #self.title = "FMC:Event"
        self.className = "RC-Event"
                    
class State(Resource):
    def __init__(self, element):
        Resource.__init__(self, element)
        #self.title = "FMC:State"
        self.className = "RC-State"
        
class Collection(Resource):
    def __init__(self, element):
        Resource.__init__(self, element)
        #self.title = "SpecIF:Collection"
        self.className = "RC-Collection"

class Diagram(Resource):
    def __init__(self, element):
        Resource.__init__(self, element)
        #self.title = "SpecIF:Diagram"
        self.className = "RC-Diagram"
      
#Statement Classes
class Statement:
    def __init__(self, relation):
        self.id = "S-" + getRandomID()
        self.changedAt = time.strftime("%Y-%m-%dT%H:%M:%S+02:00")
        self.subject = "default_subject"
        self.object = "default_object"
        try:
            if relation.get("name") != None:
                self.title = relation.get("name")
            else: self.title = "NoName"
        except: self.title = "NoName"
    
    def setSubjectandObject(self, subject, object):
        self.subject = subject
        self.object = object
       

class Shows(Statement):
    def __init__(self, relation):
        Statement.__init__(self, relation)
        self.className = "SC-shows"
        
class Precedes(Statement):
    def __init__(self, relation):
        Statement.__init__(self, relation)
        self.className = "SC-precedes"  
        
class Triggers(Statement):
    def __init__(self, relation):
        Statement.__init__(self, relation)
        self.className = "SC-triggers"
        
class Signals(Statement):
    def __init__(self, relation):
        Statement.__init__(self, relation)
        self.className = "SC-signals"                 
            
class Reads(Statement):
    def __init__(self, relation):
        Statement.__init__(self, relation)
        self.className = "SC-reads" 
        
    def setReadSubject(self, types):
            if types[3] != "":
                return types[3]
            else: return types[7]
class Writes(Statement):
    def __init__(self, relation):
        Statement.__init__(self, relation)
        self.className = "SC-writes"  
    
    def setWriteSubject(self, types):
            if types[1] != "":
                return types[1]
            else: return types[5]
        
class Contains(Statement):
    def __init__(self, relation):
        Statement.__init__(self, relation)
        self.className = "SC-contains" 
        
## Hierarchies
#Hierarchie Classes

class Hierarchy:
    def __init__(self, element):
        self.id = "H-" + str(getRandomID())
        self.changedAt = time.strftime("%Y-%m-%dT%H:%M:%S+02:00")
        self.className = "RC-Hierarchy"
        if element.get("name") != None:
            self.title = element.get("name")
        else: pass
        self.resource = element.get(XMI_ID)
        
    def setNodeList(self, nodeList):
        self.nodes = nodeList
        
    def setResource(self, resource):
        self.resource = resource
