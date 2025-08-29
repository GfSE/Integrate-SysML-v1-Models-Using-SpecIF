import DataImport
import SysMLToSpecIf
import SpecIFtoSysML
import Integrator
from Modell import *
from Nodes import *
# Ausführen der Main Funktion von DataImport - Input: Bezeichnung der exportierten Modelle im XMI-Format
model1Data = DataImport.main("IntModell_Cabin")
model2Data = DataImport.main("IntModell_Airport")
# Ausführen der Main Funktion von SysMLToSpecIF - Input: Modelldaten in Datenstruktur
specIFModel1 = SysMLToSpecIf.main(model1Data)
specIFModel2 = SysMLToSpecIf.main(model2Data)
with io.open("Model2.specif", "w", encoding="utf8") as outfile:
    str_ = json.dumps(specIFModel2,
                  indent=4, sort_keys=True,
                  separators=(',', ': '), ensure_ascii=False)
    outfile.write(to_unicode(str_))
# Ausführen der Main Funktion von Integrator - Input: Modelldaten in SpecIF-Notation
integratedModel = Integrator.main(specIFModel1, specIFModel2)
# Ausgabe des integrierten Modelles im SpecIF-Format
with io.open("Integrated_Model.specif", "w", encoding="utf8") as outfile:
    str_ = json.dumps(integratedModel,
                  indent=4, sort_keys=True,
                  separators=(',', ': '), ensure_ascii=False)
    outfile.write(to_unicode(str_))
# Ausführen der Main Funktion von SpecIFtoSysML - Input: Integriertes SpecIF-Modell
export_file = SpecIFtoSysML.main(integratedModel)
# Ausgabe des integrierten Modelles im XMI-Format
with open("Integrated_Model.xml", "w") as f:
    f.write(str(export_file))