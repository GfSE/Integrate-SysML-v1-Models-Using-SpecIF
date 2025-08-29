from Modell import getRandomID
#FunctionSpace

def getSpecIFProperty(property, element):
    for prop in element["properties"]:
        if prop.get("class") == property:
            return prop.get("value")
        
#Element-Classes

class Elements:
    def __init__(self, element):
        try: self.xmiType = getSpecIFProperty("PC-Type", element)
        except: pass
        try: self.xmiID = element.get("id")
        except: pass
        try: 
            self.visibility = getSpecIFProperty("PC-Visibility", element)
            if self.visibility == "V-VisibilityKind-0":
                self.visibility = "public"
            else: del self.visibility
        except: pass
        try: 
            if element.get("title") == "NoName":
                pass
            else: 
                self.name = element.get("title")
        except: pass
class Edge(Elements):
    def __init__(self, element, source, target):
        Elements.__init__(self, element)
        self.tagName = "edge"
        self.source = source
        self.target = target
        self.xmiType = "uml:ObjectFlow"
        
class EdgeCF(Elements):
    def __init__(self, element):
        Elements.__init__(self, element)
        self.tagName = "edge"
        self.source = element.get("subject")
        self.target = element.get("object")
        self.xmiType = "uml:ControlFlow"
class Group(Elements):
    def __init__(self, element):
        Elements.__init__(self, element)
        self.tagName = "group"
class Node(Elements):
    def __init__(self, element):
        Elements.__init__(self, element)
        self.tagName = "node"
        
class Partition(Elements):
    def __init__(self, element):
        self.xmiIDref = element.get("id")
        self.tagName = "partition"
        
        
#Subelement-Classes
 
class Subelements:
    def __init__(self, element):
        try: self.xmiType = getSpecIFProperty("PC-Type", element)
        except: pass
        try: self.xmiID = element.get("id")
        except: pass
        try: 
            self.visibility = getSpecIFProperty("PC-Visibility", element)
            if self.visibility == "V-VisibilityKind-0":
                self.visibility = "public"
            else: del self.visibility
        except: pass
        try: 
            if element.get("title") == "NoName":
                pass
            else: 
                self.name = element.get("title")
        except: pass
        
class Weight(Subelements):
    def __init__(self, element):
        self.xmiType = "uml:LiteralUnlimitedNatural"
        self.xmiID = getRandomID()
        self.tagName = "weight"
        try: self.value = "1"
        except: pass
class InPartition(Subelements):
    def __init__(self, element):
        self.xmiIDref = element.get("id")
        self.tagName = "inPartition"
class Result(Subelements):
    def __init__(self, element):
        Subelements.__init__(self, element)
        self.tagName = "result"
class Trigger(Subelements):
    def __init__(self, element):
        self.xmiType = "uml:Trigger"
        self.tagName = "trigger"
        self.xmiID = getRandomID()
        self.event = "eventID"
class Argument(Subelements):
    def __init__(self, element):
        Subelements.__init__(self, element)
        self.tagName = "argument"
class SubNode(Subelements):
    def __init__(self, element):
        self.xmiIDref = element.get("id")
        self.tagName = "node"
class SubEdge(Subelements):
    def __init__(self, element):
        self.xmiIDref = element.get("id")
        self.tagName = "edge"
class AnnotatedElement(Subelements):
    def __init__(self, element):
        self.xmiIDref = ""
        self.tagName = "annotatedElement"

#Structure-Classes
        
class Structure:
    def __init__(self, element):
        try: self.xmiType = getSpecIFProperty("PC-Type", element)
        except: pass
        try: self.xmiID = element.get("id")
        except: pass
        try: 
            self.visibility = getSpecIFProperty("PC-Visibility", element)
            if self.visibility == "V-VisibilityKind-0":
                self.visibility = "public"
            else: del self.visibility
        except: pass
        try: self.name = getSpecIFProperty("PC-Name", element)
        except: pass
class OwnedComment(Structure):
    def __init__(self, element):
        self.tagName = "ownedComment"
        self.xmiType = "uml:Comment"
        self.xmiID = getRandomID()
        self.body = getSpecIFProperty("PC-Description", element)

class PackagedElement(Structure):
    def __init__(self, element):
        Structure.__init__(self, element)
        self.tagName = "packagedElement"
class NestedClassifier(Structure):
    def __init__(self, element):
        Structure.__init__(self, element)
        self.tagName = "nestedClassifier"
class UmlModel(Structure):
    def __init__(self, element):
        Structure.__init__(self, element)
        self.tagName = "uml:Model"
class OwnedBehavior(Structure):
    def __init__(self, element):
        Structure.__init__(self, element)
        self.tagName = "ownedBehavior"