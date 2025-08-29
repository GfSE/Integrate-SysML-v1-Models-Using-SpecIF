from xml.dom import minidom
from lxml import etree
from Modell import *
from Nodes import *

etree.register_namespace("xmi","http://www.omg.org/spec/XMI/20131001")
etree.register_namespace("uml","http://www.omg.org/spec/UML/20131001")

#Methodendefinition
# Passt die Namen der Eigenschaftt tagName von classElement an, und erstellt hieraus ein etree-Subelement mit dem Tag "tag" unter dem etree-Element "parent"
def convertToXML(parent, classElement):
    tag = classElement.tagName
    if "uml:" in tag: 
        tag = tag.replace("uml:", "{http://www.omg.org/spec/UML/20131001}")
    del classElement.tagName
    return etree.SubElement(parent, tag, applyAttributeNamespace(toDict(classElement)))

# Passt keys von dictionary an und gibt dieses aus
def applyAttributeNamespace(dictionary):
        try:dictionary["{http://www.omg.org/spec/XMI/20131001}id"] = dictionary.pop("xmiID")
        except: pass
        try:dictionary["{http://www.omg.org/spec/XMI/20131001}type"] = dictionary.pop("xmiType")
        except: pass
        try:dictionary["{http://www.omg.org/spec/XMI/20131001}idref"] = dictionary.pop("xmiIDref")
        except: pass
        return dictionary

# Gibt eine Liste von Resourcen aus, die mit einem Statement mit element verbunden sind
def findNeighbours(element, intModel):
    neighbourList = []
    for statement in intModel["statements"]:
        if statement.get("subject") == element.get("id"):
            for resource in intModel["resources"]:
                if statement.get("object") == resource.get("id"):
                    neighbourList.append([statement, resource])
        elif statement.get("object") == element.get("id"):
            for resource in intModel["resources"]:
                if statement.get("subject") == resource.get("id"):
                    neighbourList.append([statement, resource])
    return neighbourList

# Generiert ein ObjectFlow-Objekt mit der Klasse edge und ordnet diesem ein Objekt der Klasse Weight als Subelement zu
def CreateObjectflow(ofState, subject, object, edgeList, usedStatements, ctr, read, write):
        edge = Edge(ofState, subject, object)
        weight = Weight(ofState)
        edgeList.append({edge:[weight]})
        usedStatements.append(ctr.get("id"))
        usedStatements.append(read.get("id"))
        usedStatements.append(write.get("id"))

# Gibt eine ID aus den values des Dictionaries signalMap aus, wenn die Eingabe id in den keys des Dictionarys enthalten ist
def mapSignalID(id, signalMap):
    if id in signalMap:
        return signalMap.get(id)

# main-Methode des SpecIFtoSysML Transformators
def main(integratedModel):
    #Erstellen von Datenstrukturen
    usedStatements = []
    structureList = []
    classStructure = dict()
    structureMap = dict()
    dnElements = dict()
    elementList = []
    signalMap = dict()

    #Parsen eines XML-Templates mit etree
    roottree = etree.parse("XML_Template.xml", parser=etree.XMLParser())
    root = roottree.getroot()
    #Speichern der Eingabedaten in die Variable intModel
    intModel = integratedModel

    #Erstellen des Dictionaries structureMap, welches die Modellstruktur beschreibt
    for node in intModel["hierarchies"]:
        for element in intModel["resources"]:
            if node.get("resource") == element.get("id") and getSpecIFProperty("PC-Type", element) == "uml:Activity":
                for subnode in node["nodes"]:
                        idList = []
                        for subsubnode in subnode["nodes"]:
                            idList.append(subsubnode.get("resource"))
                try: structureMap.update({node.get("resource") : idList})
                except: pass

    #Transformation von Elementen
    for element in intModel["resources"]:
        subElementList= []
        if getSpecIFProperty("PC-Type", element) == "uml:Signal":
            packagedElement = PackagedElement(element)
            packagedElement2 = PackagedElement(DEFAULT_ELEMENT)
            packagedElement2.xmiType = "uml:SignalEvent"
            packagedElement2.signal = packagedElement.xmiID
            signalMap.update({packagedElement.xmiID : packagedElement2.xmiID})
            structureList.append(packagedElement)
            structureList.append(packagedElement2)
        elif getSpecIFProperty("PC-Type", element) == "uml:CallBehaviorAction":
            node = Node(element)
            neighbours = findNeighbours(element, intModel)
            for pair in neighbours:
                if pair[0].get("class") == "SC-contains":
                    if getSpecIFProperty("PC-Type", pair[1]) == "uml:OutputPin":
                        result = Result(pair[1])
                        subElementList.append(result)
                    if getSpecIFProperty("PC-Type", pair[1]) == "uml:InputPin":
                        argument = Argument(pair[1])
                        subElementList.append(argument)
                if pair[0].get("class") == "SC-precedes":
                    if getSpecIFProperty("PC-Type", pair[1]) == "uml:Activity":
                        node.behavior = pair[1].get("id")
                        usedStatements.append(pair[0].get("id"))
            if subElementList== []:
                subElementList.append(["NoSubelement"])
            elementList.append({node:subElementList})
        elif getSpecIFProperty("PC-Type", element) in SINGLENODES:
            node = Node(element)
            elementList.append({node : "NoSubelement"})
        elif getSpecIFProperty("PC-Type", element) == "uml:AcceptEventAction":
            node = Node(element)
            trigger = Trigger(DEFAULT_ELEMENT)
            neighbours = findNeighbours(element, intModel)
            for pair in neighbours:
                if getSpecIFProperty("PC-Type", pair[1]) == "uml:Signal":
                    trigger.event = mapSignalID(pair[1].get("id"), signalMap)
                    subElementList.append(trigger)
                    usedStatements.append(pair[0].get("id"))
                if pair[0].get("class") == "SC-contains":
                    if getSpecIFProperty("PC-Type", pair[1]) == "uml:OutputPin":
                        result = Result(pair[1])
                        subElementList.append(result)
                    if getSpecIFProperty("PC-Type", pair[1]) == "uml:InputPin":
                        argument = Argument(pair[1])
                        subElementList.append(argument)
            elementList.append({node : subElementList})
        elif getSpecIFProperty("PC-Type", element) == "uml:SendSignalAction":
            node = Node(element)
            neighbours = findNeighbours(element, intModel)
            for pair in neighbours:
                if getSpecIFProperty("PC-Type", pair[1]) == "uml:Signal":
                    node.signal = pair[1].get("id")
                    usedStatements.append(pair[0].get("id"))
                if pair[0].get("class") == "SC-contains":
                    if getSpecIFProperty("PC-Type", pair[1]) == "uml:OutputPin":
                        result = Result(pair[1])
                        subElementList.append(result)
                    if getSpecIFProperty("PC-Type", pair[1]) == "uml:InputPin":
                        argument = Argument(pair[1])
                        subElementList.append(argument)
            elementList.append({node : subElementList})
        elif getSpecIFProperty("PC-Type", element) == "uml:DecisionNode" and element.get("class") == "RC-Actor":
            node = Node(element)
            elementList.append({node : "NoSubelement"})
            neighbours = findNeighbours(element, intModel)
            dnIDs = [element.get("id")]
            for pair in neighbours:
                if getSpecIFProperty("PC-Type", pair[1]) == "uml:DecisionNode" and pair[0].get("class") == "SC-signals":
                    usedStatements.append(pair[0].get("id"))
                    dnIDs.append(pair[1].get("id"))
            dnElements.update({dnIDs[0] : dnIDs})
        elif getSpecIFProperty("PC-Type", element) == "uml:ActivityPartition":
            node = Node(element)
            containmentList = []
            neighbours = findNeighbours(element, intModel)
            for pair in neighbours:
                if pair[0].get("class") == "SC-contains":
                    subnode = SubNode(pair[1])
                    containmentList.append(subnode)
            elementList.append({node : containmentList})
            partition = Partition(element)
            elementList.append({partition : "NoSubelement"})

    #Filtern von Relationen (reads, writes, precedes, signals und triggers)
    connectorFilter = ["SC-reads", "SC-writes", "SC-precedes", "SC-signals", "SC-triggers"]
    connectorList = []
    edgeList = []
    for statement in intModel["statements"]:
        if statement.get("class") in connectorFilter:
            connectorList.append(statement)

    #Transformation von Statements zu einem ObjectFlow
    for write in connectorList:
        if write.get("class") == "SC-writes":
            for read in connectorList:
                if read.get("class") == "SC-reads":
                    if write.get("object") == read.get("object"):
                        objectEl = read.get("subject")
                        subjectEl = write.get("subject")
                        ofState = write.get("object")
                        for resource in intModel["resources"]:
                            if resource.get("id") == objectEl:
                                neighboursObject = findNeighbours(resource, intModel)
                                ctrObject = resource
                            elif resource.get("id") == subjectEl:
                                neighboursSubject = findNeighbours(resource, intModel)
                                ctrSubject = resource
                            elif resource.get("id") == ofState:
                                objectFlowEl = resource
                        for pair in neighboursObject:
                            if pair[0].get("class") == "SC-contains" and getSpecIFProperty("PC-Type", pair[1]) in ["uml:CallBehaviorAction", "uml:AcceptEventAction", "uml:SendSignalAction"]:
                                ctrObject = pair[1]
                        for pair in neighboursSubject:
                            if pair[0].get("class") == "SC-contains" and getSpecIFProperty("PC-Type", pair[1]) in ["uml:CallBehaviorAction", "uml:AcceptEventAction", "uml:SendSignalAction"]:
                                ctrSubject = pair[1]
                        for ctr in connectorList:
                            if ctr.get("class") in ["SC-triggers", "SC-signals", "SC-precedes"]:
                                if getSpecIFProperty("PC-Type", ctrSubject) == "uml:DecisionNode":
                                    if ctr.get("subject") in dnElements.get(ctrSubject.get("id")) and ctr.get("object") == ctrObject.get("id"):
                                        #print("Case1")
                                        CreateObjectflow(objectFlowEl, subjectEl, objectEl, edgeList, usedStatements, ctr, read, write)
                                elif getSpecIFProperty("PC-Type", ctrObject) == "uml:DecisionNode":
                                    if ctr.get("subject") == ctrSubject.get("id") and ctr.get("object") == ctrObject.get("id"):
                                        #print("Case2")
                                        CreateObjectflow(objectFlowEl, subjectEl, objectEl, edgeList, usedStatements, ctr, read, write)
                                elif objectEl != ctrObject.get("id") and subjectEl != ctrSubject.get("id"):
                                    if ctr.get("subject") == ctrSubject.get("id") and ctr.get("object") == ctrObject.get("id"):
                                        #print("Case3")
                                        CreateObjectflow(objectFlowEl, subjectEl, objectEl, edgeList, usedStatements, ctr, read, write)
                                elif objectEl == ctrObject.get("id") and subjectEl != ctrSubject.get("id"):
                                    if ctr.get("subject") == ctrSubject.get("id") and ctr.get("object") == ctrObject.get("id"):
                                        #print("Case4")
                                        CreateObjectflow(objectFlowEl, subjectEl, objectEl, edgeList, usedStatements, ctr, read, write)
                                elif objectEl != ctrObject.get("id") and subjectEl == ctrSubject.get("id"):
                                    if ctr.get("subject") == ctrSubject.get("id") and ctr.get("object") == ctrObject.get("id"):
                                        #print("Case5")
                                        CreateObjectflow(objectFlowEl, subjectEl, objectEl, edgeList, usedStatements, ctr, read, write)
                                elif objectEl == ctrObject.get("id") and subjectEl == ctrSubject.get("id"):
                                    if ctr.get("subject") == ctrSubject.get("id") and ctr.get("object") == ctrObject.get("id"):
                                        #print("Case6")
                                        CreateObjectflow(objectFlowEl, subjectEl, objectEl, edgeList, usedStatements, ctr, read, write)

    # Nicht genutzte Statements aus der Liste connectorList ausfiltern und in filteredStatements hinzufügen
    filteredStatements = []
    for element in connectorList:
        if element.get("id") not in usedStatements:
            filteredStatements.append(element)

    # Transformation der Statements aus der Liste filteredStatements in ControlFlows
    for statement in filteredStatements:
        for resource in intModel["resources"]:
            if statement.get("subject") == resource.get("id") and getSpecIFProperty("PC-Type", resource) == "uml:DecisionNode" :
                edge = EdgeCF(statement)
                neighbours = findNeighbours(resource, intModel)
                for pair in neighbours:
                    if getSpecIFProperty("PC-Type", pair[1]) == "uml:DecisionNode" and pair[1].get("class") == "RC-Actor":
                        edge.source = pair[1].get("id")
                weight = Weight(DEFAULT_ELEMENT)
                edgeList.append({edge:[weight]})
            elif statement.get("subject") == resource.get("id"):
                if getSpecIFProperty("PC-Type", resource) != "uml:DecisionNode":
                    edge = EdgeCF(statement)
                    weight = Weight(DEFAULT_ELEMENT)
                    edgeList.append({edge:[weight]})

    #Elemente zu den Aktivitäten zuordnen
    for element in structureMap.items():
        filteredElements = []
        for resource in intModel["resources"]:
            if element[0] == resource.get("id"):
                packagedElement3 = PackagedElement(resource)
                break
        for resource in elementList:
            for comp in resource.keys():
                try:
                    if comp.xmiID in element[1]:
                        filteredElements.append(resource)
                except: pass
                try:
                    if comp.xmiIDref in element[1]:
                        filteredElements.append(resource)
                except: pass
        for edge in edgeList:
            for comp in edge.keys():
                try:
                    if comp.target in element[1] or comp.source in element[1]:
                        filteredElements.append(edge)
                except: pass
        structureList.append({packagedElement3 : filteredElements})

    # Transformation der Resource die das Modell repräsentiert und erstellen des Dictionarys classStructure
    for element in intModel["resources"]:
        if getSpecIFProperty("PC-Type", element) == "uml:Model":
            model = UmlModel(element)
            comment = OwnedComment(element)
            structureList.append(comment)
            classStructure.update({model : structureList})

    # Elemente aus der Liste classStructure in etree-Objekte konvertieren und nach der Struktur anlegen
    for umlModel in classStructure:
        model = convertToXML(root, umlModel)
        for structuredElement in classStructure[umlModel]:
            if str(type(structuredElement)) == "<class 'dict'>":
                for strEl in structuredElement.keys():
                    strElement = convertToXML(model, strEl)
                for strEl in structuredElement.values():
                    for elEl in strEl:
                        for elElKeys in elEl.keys():
                            try: elElement = convertToXML(strElement, elElKeys)
                            except: pass
                        for subelement in elEl.values():
                            for subEL in subelement:
                                try: subElement = convertToXML(elElement, subEL)
                                except:pass
            else: strElement = convertToXML(model, structuredElement)
    # etree-Objekt in Pretty String konvertieren
    root.append(model)
    roughString = etree.tostring(root)
    reparsed = minidom.parseString(roughString)
    exportFile = reparsed.toprettyxml(indent="  ")

    return exportFile


