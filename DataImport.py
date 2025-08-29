import xml.etree.ElementTree as ET

# Namespace
NS = {
    'type': 'http://www.omg.org/spec/XMI/20131001',
    'model': 'http://www.omg.org/spec/UML/20131001'
}

# Methodendefinition

# Sucht alle Unterelemente von root mit dem gegebenen elementName und typeName
def findByElementAndType(root, elementName, typeName):
    return root.findall(".//" + elementName + "[@type:type='" + typeName + "']", NS)

# Sucht alle Unterelemente vom root mit dem angegebenen childElementName. Von den Elementen wird der Text zurückgegeben 
def getTextOfSubElements(root, childElementName):
    textElementList = []
    for element in root.iter(childElementName):
        textElementList.append(element.text)
    return textElementList

# Findet alle Unterelemente unterhalb von packagedElement mit dem gegebenen tagName
def findTags(root, tagName):
    if root.findall(".//ownedBehavior[@type:type='uml:Activity']/" + tagName, NS) != []:
        return root.findall(".//ownedBehavior[@type:type='uml:Activity']/" + tagName, NS)
    else: 
        return root.findall(".//packagedElement[@type:type='uml:Activity']/" + tagName, NS)

# Gibt ein Element als JSON mit allen Unterlementen zurück
def getElementAsJsonObject(element):
    dictEl = dict()
    dictEl.update(element.attrib)
    subElementList = []
    for subElement in list(element):
        subElementList.append(subElement.attrib)
    dictEl.update({'sub': subElementList})
    return dictEl

# Main-Methode des DataImports
def main(fileName):
    #Definition von Elementen für die Datenstruktur
    modelinformation = dict()
    diagrams = []
    relations = []
    elements = []

    # Parsen der XMI-Datei
    docXML = ET.parse(fileName + '.xml')
    root = docXML.getroot()
    del docXML

    # Modelldaten auslesen und zur Datenstruktur hinzufügen
    model = root.find("{http://www.omg.org/spec/UML/20131001}Model")
    comment = model.find("ownedComment")
    modelinformation.update(model.attrib)
    modelinformation.update({"ownedComment":comment.attrib})
    #Diagramm informationen auslesen und zur Datenstruktur hinzufügen
    for el in findByElementAndType(root, "packagedElement", "uml:Activity"):
        diagramDict = dict()
        diagramDict.update(el.attrib)
        sublist = []
        try:
            if el.find("ownedBehavior") == None:
                sub = dict()
                text_elements = getTextOfSubElements(el, "usedElements")
                sub.update({"usedElements" : text_elements})
                diagramElement = findByElementAndType(el, "ownedDiagram", "uml:Diagram")
                owneddiagram = diagramElement[0].attrib
                sub.update({"ownedDiagram" : owneddiagram})
                diagramDict.update({"sub": [sub]});
                diagrams.append(diagramDict)
            else:
                for subel in el.findall("ownedBehavior"):
                    sub = subel.attrib
                    text_elements = getTextOfSubElements(subel, "usedElements")
                    sub.update({"usedElements" : text_elements})
                    diagramElement = findByElementAndType(subel, "ownedDiagram", "uml:Diagram")
                    owneddiagram = diagramElement[0].attrib
                    sub.update({"ownedDiagram" : ownedDiagram})
                    diagramDict.update({"sub" : [sub]})
                diagrams.append(diagramDict)
        except: pass

    #Modellelemente auslesen und zur Liste sortList hinzufügen
    tagList = []
    for tagName in ['edge','node','group']:
        tagList.extend(findTags(root, tagName))
    sortList = []
    for el in tagList:
        sortList.append(getElementAsJsonObject(el))
    for el in findByElementAndType(root, "packagedElement", "uml:Signal"):
        sortList.append(getElementAsJsonObject(el))
    for el in findByElementAndType(root, "nestedClassifier", "uml:Signal"):
        sortList.append(getElementAsJsonObject(el))
    for el in findByElementAndType(root, "packagedElement", "uml:SignalEvent"):
        sortList.append(getElementAsJsonObject(el))
    # Sortieren der Elemente in der Liste sortList in relations und elements
    for el in sortList:
        if el.get("{http://www.omg.org/spec/XMI/20131001}type") == "uml:ObjectFlow" or el.get("{http://www.omg.org/spec/XMI/20131001}type") == "uml:ControlFlow":
            relations.append(el)
        else:
            elements.append(el)

    #Zusammenfügen der Datenstruktur
    data = {
        "model": modelinformation,
        "relations": relations,
        "elements": elements,
        "diagrams": diagrams
    }

    return data

