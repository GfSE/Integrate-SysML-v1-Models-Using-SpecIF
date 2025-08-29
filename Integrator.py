from Modell import *

#Methodendefinition

#Fügt die Daten eines Types(type) aus den Datenstrukturen data1 und data2 zusammen. Hierbei werden identische Daten gelöscht.
def mergeData(type, data1, data2):
    metadata = []
    metadataList= []
    for element in data1[type]:
        if element.get("id") in metadataList: 
            print("MergeError")
        else:
            metadata.append(element)
            metadataList.append(element.get("id"))
    for element in data2[type]:
        if element.get("id") in metadataList: 
            pass
        else:
            metadata.append(element)
            metadataList.append(element.get("id"))
    return metadata

# Erstellt ein defaultSignalEvent mit dem Namen eines Signals
def createdefaultSignalEvent(element):
    defaultSignalEvent = {
        "name": "Event_" + element[0],
        "{http://www.omg.org/spec/XMI/20131001}type": "uml:SignalEvent"
    }
    return defaultSignalEvent

#Prüft ob die title-Strings zweier Elemente ohne beachtung von Groß- und Kleinschreibung übereinstimmen
def matchElementTitleStrings(element1, element2):
    str1 = element1.get("title")
    str2 = element2.get("title")
    if str1.lower() == str2.lower() and element1.get("id") != element2.get("id"):
        return True
    else: return False

#Überprüft ob ein Element vom Typ Signal ist
def isASignal(element):
    if element.get("class") != "RC-Event": return False
    else: 
        for property in element["properties"]:
            if property.get("value") == "uml:Signal":
                return True
    return False

# Gibt die Beschreibung eines Elementes aus
def getDescription(element):
    for prop in element["properties"]:
        if prop.get("class") == "PC-Description":
            return prop.get("value")

# main-Methode des Integrators
def main(specifModel1, specifModel2):
    intModel = dict()
    data1 = specifModel1
    data2 = specifModel2

    #Metadaten zusammenfassen
    intModel.update({"dataTypes" : mergeData("dataTypes", data1, data2)})
    intModel.update({"resourceClasses" : mergeData("resourceClasses", data1, data2)})
    intModel.update({"propertyClasses" : mergeData("propertyClasses", data1, data2)})
    intModel.update({"statementClasses" : mergeData("statementClasses", data1, data2)})

    #Ressourcen und Statements zusammenfassen
    intModel.update({"statements" : mergeData("statements", data1, data2)})
    intModel.update({"resources" : mergeData("resources", data1, data2)})

    #Hierarchies zusammenfassen, und doppelte Modellinformationen in einem Element zusammenfassen
    intModel.update({"hierarchies" : mergeData("hierarchies", data1, data2)})
    modelDescription = ""
    for element in intModel["hierarchies"]:
        for compElement in intModel["resources"]:
            if element.get("resource") == compElement.get("id"):
                if compElement.get("class") == "RC-Collection":
                    stringElement = getDescription(compElement)
                    modelDescription = modelDescription + stringElement
                    intModel["hierarchies"].remove(element)
                    intModel["resources"].remove(compElement)
    description = Description(defaultProperty)
    description.value = modelDescription
    collection = toDict(Collection(defaultModel))
    collection["properties"].append(toDict(description))
    intModel["resources"].append(collection)
    for element in intModel["resources"]:
        if element.get("class") == "RC-Collection":
            hierarchy = Hierarchy(element)
            hierarchy.setResource(element.get("id"))
            intModel["hierarchies"].append(toDict(hierarchy))

    #Integration der CallBehaviorActions und Activities
    cbaList = []
    for element in intModel["resources"]:
        if element.get("class") == "RC-Actor":
            for element2 in intModel["resources"]:
                if element2.get("class") == "RC-Actor":
                        if element.get("title") == element2.get("title"):
                            if element.get("id") != element2.get("id"):
                                for node in intModel["hierarchies"]:
                                    if element.get("id") == node.get("resource"):
                                        cbaList.append([element, element2])
    for element in cbaList:
        precedes = Precedes(defaultStatement)
        precedes.setSubjectandObject(element[1].get("id"), element[0].get("id"))
        intModel["statements"].append(toDict(precedes))

    # Integration der Signale
    for element in intModel["resources"]:
        if isASignal(element):
            for compElement in intModel["resources"]:
                if isASignal(compElement):
                    if matchElementTitleStrings(element, compElement):
                        for relation in intModel["statements"]:
                            if compElement.get("id") == relation.get("object"):
                                relation["object"] = element.get("id")
                            if compElement.get("id") == relation.get("subject"):
                                relation["subject"] = element.get("id")
                            for node in intModel["hierarchies"]:
                                if node.get("resource") == compElement.get("id"):
                                    intModel["hierarchies"].remove(node)
                            try: intModel["resources"].remove(compElement)
                            except: pass

    #Generation und einfügen eines SpecIF-Headers
    header = {
        "specifVersion" : "0.10.8",
        "title" : "Integrated Model",
        "id" : "Model_" + getRandomID()
    }
    intModel.update(header)

    return intModel




