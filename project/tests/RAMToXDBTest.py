from utils.RAMtoXDBConverter import *
from utils.XmlParser import *

XML_FILE_NAME_1 = "../resources/tasks.xml"
XML_FILE_NAME_2 = "../resources/prjadm.xml"

schemas = create_list_of_objects_from_xml([XML_FILE_NAME_1, XML_FILE_NAME_2])

# This is for test
converter = RAMToXDBConverter(schemas[0])
schema = converter.create_schema(schemas[0])
print(schema)