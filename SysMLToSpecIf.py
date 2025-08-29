from Modell import *

#Methodendefinition

# Gibt Eigenschaften der Start- und Endelemente in einem Array aus [subjectType, subjectID, objectType, objectID, parentSubjectType, parentSubjectID, parentObjectType, parentObjectID]
def getConnectedTypes(relation, data, idMap):
    subject = relation.get("source")
    object = relation.get("target")
    subjectType = ""
    objectType = ""
    parentObjectType = ""
    parentSubjectType = ""
    subjectID = ""
    objectID = ""
    parentObjectID = ""
    parentSubjectID = ""
    for element in data["elements"]:
        if subject == element.get(XMI_ID):
            parentSubjectType = element.get(XMI_TYPE)
            parentSubjectID = mapID(element.get(XMI_ID), idMap)
        elif object == element.get(XMI_ID):
            parentObjectType = element.get(XMI_TYPE)
            parentObjectID = mapID(element.get(XMI_ID), idMap)
        for subelement in element["sub"]:        
            if subject == subelement.get(XMI_ID):
                subjectType = subelement.get(XMI_TYPE)
                subjectID = mapID(subelement.get(XMI_ID), idMap)
                parentSubjectType = element.get(XMI_TYPE)
                parentSubjectID = mapID(element.get(XMI_ID), idMap)
            elif object == subelement.get(XMI_ID):
                objectType = subelement.get(XMI_TYPE)
                objectID = mapID(subelement.get(XMI_ID), idMap)
                parentObjectType = element.get(XMI_TYPE)
                parentObjectID = mapID(element.get(XMI_ID), idMap)
    types = [subjectType, subjectID, objectType, objectID, parentSubjectType, parentSubjectID, parentObjectType, parentObjectID]
    return types

# Gibt je nach Verbindungsart ein precedes, signals oder triggers Statement aus
def statementFactory(types, relation):
    if types[4] in ACTORS and types[6] in ACTORS:
        precedes = Precedes(relation)
        precedes.subject = types[5]
        precedes.object = types[7]
        return precedes
    elif types[4] in ACTORS and types[6] in EVENTS:
        signals = Signals(relation)
        signals.subject = types[5]
        signals.object = types[7]
        return signals
    elif types[4] in EVENTS and types[6] in ACTORS:
        triggers = Triggers(relation)
        triggers.subject = types[5]
        triggers.object = types[7]
        return triggers

# Gibt je nach Verbindungsart ein precedes oder triggers Statement aus
def statementFactory3(types, relation):
    if types[4] in ACTORS:
        precedes = Precedes(relation)
        precedes.subject = types[5]
        precedes.object = types[7]
        return precedes
    elif types[4] in EVENTS:
        triggers = Triggers(relation)
        triggers.subject = types[5]
        triggers.object = types[7]
        return triggers

#Fügt ein Element zum Dictionary idMap hinzu, welches eine alte ID als des Elementes als Key und eine neue ID als Value enthält
def appendToIDMap(element, instance, idMap):
    varID = element.get(XMI_ID)
    if varID in idMap:
        list = idMap.get(varID)
        list.append(instance.id)
        idMap.update({varID : list})
    else:
        list = [instance.id]
        idMap.update({varID : list})

# Erstellt ein Dictionary Element, welches die ursprügliche ID eines DecisionNodes mit den erstellten Ressourcen und benachbarten Resourcen in Verbindung setzt.
# {dnID: [dnActor, dnEvent1, dnEvent2, NachbarIn, NachbarInPort, NachbarOut1, NachbarOut1Port, NachbarOut2, NachbarOut2Port, Counter = 0]}
def createDNmap(element, dnList, data, idMap):
    dnID = mapID(element.get(XMI_ID), idMap)
    connectorList = []
    dnItem = []
    outputList = []
    inList = []
    for filterelement in getElements(data, CONNECTORS):
        connectorList.append(filterelement)
    for connector in connectorList:
        types = getConnectedTypes(connector, data, idMap)
        if types[6] == DECISIONNODE[0]:
            if dnID == types[7]:
                if types[1] == "":
                    act1 = types[5]
                    act1Port = types[5]
                else:
                    act1 = types[5]
                    act1Port = types[1]
                inList.extend([act1, act1Port])
        elif types[4] == DECISIONNODE[0]:
            if dnID == types[5]:
                act = types[7]
                if types[3] != "":
                    actPort = types[3]
                else: actPort = types[7]
                outputList.extend([act, actPort])
    dnItem.extend(dnList)
    dnItem.extend(inList)
    dnItem.extend(outputList)
    dnItem.extend("0")
    return {dnID : dnItem}

#Filtert data nach Elementen die den Typ aus einer typeList haben und gibt diese Elemente aus
def getElements(data, typeList):
    elements = []
    for element in data["elements"]:
        if hasType(element, typeList):
            elements.append(element)
        for sub in element["sub"]:
            if sub.get(XMI_TYPE) in typeList:
                elements.append(sub)
    for element in data["relations"]:
        if hasType(element, typeList):
            elements.append(element)        
    return elements

#Überprüft ob ein element einen Typ aus eine Liste hat
def hasType(element, typeList):
    found = False
    for comp in typeList:
         if element.get(XMI_TYPE) == comp:
             found = True
    return found

# Überprüft ob ein Element in der idMap vorhanden ist. Wenn dies zutrifft wird die zugeordnete ID ausgegeben
def mapID(id, idMap, zahl = 0):
    idMapped = ""
    if id in idMap:
        compID = idMap.get(id)
        idMapped = compID[zahl]
    return idMapped

# Gibt je nach Verbindungsart ein precedes oder triggers Statement aus und passt dieses an
def statementFactoryCFDNout(types, relation, dnMap):
    DNArray = dnMap.get(types[5])
    if types[6] in ACTORS:
        precedes = Precedes(relation)
        zahl = int(DNArray[9])
        neue_zahl = zahl + 1
        DNArray[9] = str(neue_zahl)
        precedes.subject = DNArray[int(DNArray[9])]
        precedes.object = types[7]
        return precedes
    elif types[6] in EVENTS:
        triggers = Triggers(relation)
        triggers.subject = DNArray[i]
        triggers.object = types[7]
        return triggers

# Gibt je nach Verbindungsart ein precedes oder triggers Statement aus und passt dieses an
def statementFactoryCFDNin(types, relation):
    DNArray = dnMap.get(types[7])
    if types[6] in ACTORS:
        precedes = Precedes(relation)
        precedes.subject = types[5]
        precedes.object = DNArray[0]
        return precedes
    elif types[6] in EVENTS:
        triggers = Triggers(relation)
        triggers.subject = types[5]
        triggers.object = DNArray[0]
        return triggers

# Main-Methode des SysMLtoSpecIF-Transformators
def main(dataInput):
    # Definition von Datenstrukturen
    specifResources = []
    specifStatements = []
    specifHierarchies = []
    idMap = dict()
    dnMap = dict()
    #Speichern der Eingabedaten in die Variable data
    data = dataInput
    #Transformation von Elementen von SysML auf SpecIF

    #Diagramm
    for element in data["diagrams"]:
        activity = Actor(element)
        appendToIDMap(element, activity, idMap)
        specifResources.append(toDict(activity))
        for subelement in element["sub"]:
            diagram = Diagram(subelement["ownedDiagram"])
            appendToIDMap(subelement["ownedDiagram"], diagram, idMap)
            specifResources.append(toDict(diagram))
            if subelement.get(XMI_TYPE) == "uml:Activity":
                activity = Actor(subelement)
                appendToIDMap(subelement, activity, idMap)
                specifResources.append(toDict(activity))
            else: pass
    # Modell
    collection = Collection(data["model"])
    appendToIDMap(data["model"], collection, idMap)
    specifResources.append(toDict(collection))

    #Modellelemente
    # Transformation der Elemente aus der Liste ACTORS
    for element in getElements(data, ACTORS):
        actor = Actor(element)
        appendToIDMap(element, actor, idMap)
        specifResources.append(toDict(actor))

    # Transformation der Elemente aus der Liste EVENTS
    for element in getElements(data, EVENTS):
        event = Event(element)
        appendToIDMap(element, event, idMap)
        specifResources.append(toDict(event))

    # Transformation der Elemente aus der Liste STATES
    for element in getElements(data, STATES):
        state = State(element)
        appendToIDMap(element, state, idMap)
        specifResources.append(toDict(state))

    # Transformation der Elemente aus der Liste PORTS
    for element in getElements(data, PORTS):
        port = Actor(element)
        appendToIDMap(element, port, idMap)
        specifResources.append(toDict(port))

    # Transformation des Elementes uml:Signal
    for element in getElements(data, ["uml:Signal"]):
        node = Hierarchy(element)
        node.setResource(mapID(node.resource, idMap))
        specifHierarchies.append(toDict(node))

    # Transformation der DecisionNodes
    for element in getElements(data, DECISIONNODE):
        DN_elementlist = []
        OutList = []
        DN_in = Actor(element)
        appendToIDMap(element, DN_in, idMap)
        specifResources.append(toDict(DN_in))
        InID = DN_in.id
        dnCompID= element.get(XMI_ID)
        for relation in getElements(data, CONNECTORS):
            types = getConnectedTypes(relation, data, idMap)
            if DECISIONNODE[0] in types[4] and dnCompID== relation.get("source"):
                dnOut = Event(element)
                appendToIDMap(element, dnOut, idMap)
                specifResources.append(toDict(dnOut))
                OutList.append(dnOut.id)
        DN_elementlist.append(InID)
        DN_elementlist.extend(OutList)
        dnMap.update(createDNmap(element, DN_elementlist, data, idMap))

    #Transformation der ControlFlows
    for relation in getElements(data, CONTROLFLOW):
        types = getConnectedTypes(relation, data, idMap)
        if types[4] not in DECISIONNODE and types[6] not in DECISIONNODE:
            types = getConnectedTypes(relation, data, idMap)
            statement = statementFactory(types, relation)
            specifStatements.append(toDict(statement))
        else:
            for element in data["elements"]:
                if relation.get("source") == element.get(XMI_ID):
                    if types[4] in DECISIONNODE:
                        statement = statementFactoryCFDNout(types, relation, dnMap)
                        specifStatements.append(toDict(statement))
                        signals = Signals(relation)
                        signals.setSubjectandObject(dnMap.get(types[5])[0], statement.subject)
                        specifStatements.append(toDict(signals))
                elif relation.get("target") == element.get(XMI_ID):
                    if types[6] in DECISIONNODE:
                        statement = statementFactoryCFDNin(types, relation)
                        specifStatements.append(toDict(statement))

    # Transformation der ObjectFlows
    DN_relations = []
    for relation in getElements(data, OBJECTFLOW):
        types = getConnectedTypes(relation, data, idMap)
        if DECISIONNODE[0] not in types:
            write = Writes (relation)
            write.setSubjectandObject(write.setWriteSubject(types), mapID(relation.get(XMI_ID), idMap))
            specifStatements.append(toDict(write))
            read = Reads (relation)
            read.setSubjectandObject(read.setReadSubject(types), mapID(relation.get(XMI_ID), idMap))
            specifStatements.append(toDict(read))
            statement3 = statementFactory3(types, relation)
            specifStatements.append(toDict(statement3))
        else:
            DN_relations.append(relation)

    # Transformation der ObjectFlows in Verbindung mit DecisionNodes
    for element in getElements(data, DECISIONNODE):
        i = 0
        k = 3
        l = 0
        h = 4
        compDNID = mapID(element.get(XMI_ID), idMap)
        #Eingehende Verbindung
        for objectflow in DN_relations:
            if mapID(objectflow.get("target"), idMap) == compDNID:
                write = Writes (defaultStatement)
                write.setSubjectandObject(dnMap.get(compDNID)[4], mapID(objectflow.get(XMI_ID), idMap))
                specifStatements.append(toDict(write))
                read = Reads (defaultStatement)
                read.setSubjectandObject(dnMap.get(compDNID)[0], mapID(objectflow.get(XMI_ID), idMap))
                specifStatements.append(toDict(read))
                precedes = Precedes(defaultStatement)
                precedes.setSubjectandObject(dnMap.get(compDNID)[3], dnMap.get(compDNID)[0])
                specifStatements.append(toDict(precedes))
        #Ausgehende Verbindung
            elif mapID(objectflow.get("source"), idMap) == compDNID:
                i = i+1
                k = k+2
                l = l+1
                h= h+2
                write = Writes (defaultStatement)
                write.setSubjectandObject(dnMap.get(compDNID)[0], mapID(objectflow.get(XMI_ID), idMap))
                specifStatements.append(toDict(write))
                read = Reads (defaultStatement)
                read.setSubjectandObject(dnMap.get(compDNID)[h], mapID(objectflow.get(XMI_ID), idMap))
                specifStatements.append(toDict(read))
                signals = Signals(defaultStatement)
                signals.setSubjectandObject(dnMap.get(compDNID)[0], dnMap.get(compDNID)[l])
                specifStatements.append(toDict(signals))
                triggers = Triggers(defaultStatement)
                triggers.setSubjectandObject(dnMap.get(compDNID)[l], dnMap.get(compDNID)[k])
                specifStatements.append(toDict(triggers))

    #Erstellen von Statements für die Elemente SendSignalAction und AcceptEventAction
    for el1 in getElements(data, ["uml:SendSignalAction"]):
        for el2 in getElements(data, ["uml:Signal"]):
            if el1["signal"] == el2[XMI_ID]:
                signals = Signals(el2)
                signals.setSubjectandObject(mapID(el1[XMI_ID], idMap) , mapID(el2[XMI_ID], idMap))
                specifStatements.append(toDict(signals))
    for el1 in getElements(data, ["uml:AcceptEventAction"]):
        for el2 in el1["sub"]:
            try:
                if el2[XMI_TYPE] == "uml:Trigger":
                    for el3 in getElements(data, ["uml:SignalEvent"]):
                        if el2["event"] == el3[XMI_ID]:
                            for el4 in getElements(data, ["uml:Signal"]):
                                if el3["signal"] == el4[XMI_ID]:
                                    triggers = Triggers(el3)
                                    triggers.setSubjectandObject(mapID(el4[XMI_ID], idMap) , mapID(el1[XMI_ID], idMap))
                                    specifStatements.append(toDict(triggers))
            except: pass

    # Erstellen eines Contains Statements für Ports
    for el in getElements(data, ["uml:CallBehaviorAction", "uml:AcceptEventAction", "uml:SendSignalAction"]):
        for subel in el["sub"]:
            if subel.get(XMI_TYPE) in PORTS:
                contains = Contains(subel)
                contains.setSubjectandObject(mapID(el.get(XMI_ID), idMap), mapID(subel.get(XMI_ID), idMap))
                specifStatements.append(toDict(contains))

    #Erstellen von Contains Statements für ActivityPartitions erstellen
    for el in data["elements"]:
        if el.get(XMI_TYPE) == "uml:ActivityPartition":
            for subel in el["sub"]:
                varID = subel.get(XMI_IDREF)
                if varID in idMap:
                    elementList = idMap.get(varID)
                    for object in elementList:
                        contains = Contains(defaultStatement)
                        contains.setSubjectandObject(mapID(el.get(XMI_ID), idMap) , object)
                        specifStatements.append(toDict(contains))

    # Erstellen eines Precedes Statements, falls eine Aktivität im Modell von einer CallBehaviorAction aufgerufen wird
    for relation in data["elements"]:
        if relation.get("behavior") != None:
            precedes = Precedes(defaultStatement)
            precedes.setSubjectandObject(mapID(relation.get(XMI_ID), idMap), mapID(relation.get("behavior"), idMap))
            specifStatements.append(toDict(precedes))

    # Erstellen von Shows Statements für Elemente in Diagrammen
    for diagrams in data["diagrams"]:
        for element in diagrams["sub"]:
            diagram_id = mapID(element["ownedDiagram"].get(XMI_ID), idMap)
            for subelement in element["usedElements"]:
                    if subelement in idMap:
                        elementList = idMap.get(subelement)
                        for object in elementList:
                            shows = Shows(defaultStatement)
                            shows.setSubjectandObject(diagram_id, object)
                            specifStatements.append(toDict(shows))

    #Erzeugen einer Hierarchy
    nodeList = []
    nodeList2 = []
    hierarchy = Hierarchy(data["model"])
    hierarchy.resource = mapID(hierarchy.resource, idMap)
    for element in data["diagrams"]:
        nodeList3 = []
        for subelement in element["sub"]:
            nodeList4 = []
            for item in subelement["usedElements"]:
                try:
                    if len(idMap.get(item)) > 1:
                        for listElement in idMap.get(item):
                            node4 = Hierarchy(defaultStatement)
                            node4.setResource(listElement)
                            nodeList4.append(toDict(node4))
                    else:
                        node4 = Hierarchy(defaultStatement)
                        node4.setResource(mapID(item, idMap))
                        nodeList4.append(toDict(node4))
                except: pass
            node3 = Hierarchy(subelement["ownedDiagram"])
            node3.setNodeList(nodeList4)
            node3.resource = mapID(node3.resource, idMap)
            nodeList3.append(toDict(node3))
            if subelement.get("name") != None:
                node2 = Hierarchy(subelement)
                node2.resource = mapID(node2.resource, idMap)
                node2.setNodeList(nodeList3)
                nodeList2.append(toDict(node2))
            else: nodeList2 = nodeList3
        node = Hierarchy(element)
        node.setResource(mapID(node.resource, idMap))
        node.setNodeList(nodeList2)
        nodeList.append(toDict(node))
    specifHierarchies.append(nodeList[0])
    specifHierarchies.append(toDict(hierarchy))

    #SpecIF-Template mit Metadaten aus JSON importieren
    with open('SpecIF_SysML_Template.json') as json_file:
        template = json.load(json_file)

    # SpecIF-Datenstruktur zusammensetzen
    SpecIF_data = {"resources":specifResources, "statements":specifStatements, "hierarchies" : specifHierarchies}
    SpecIF_data.update(template)

    return SpecIF_data
