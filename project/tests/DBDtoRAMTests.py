from utils.RAMtoXDBConverter import RAMToXDBConverter
from utils.XmlParser import *
from utils.DBInitializer import *
from utils.RAMToDBDConverter import *
from utils.DBDtoRAMConverter import *
import os

DATABASE_NAME = "../database.db"
XML_FILE_NAME_1 = "../resources/tasks.xml"
XML_FILE_NAME_2 = "../resources/prjadm.xml"

schemas = create_list_of_objects_from_xml([XML_FILE_NAME_1, XML_FILE_NAME_2])

create = not os.path.exists(DATABASE_NAME)
if create:
    initializer = DBInitializer(DATABASE_NAME)
    initializer.init_database()
    converter_to_database = RAMToDBDConverter(DATABASE_NAME)
    converter_to_database.RAM_to_DBD(schemas)

dbd_to_ram = DBDtoRAM(DATABASE_NAME)
schema = dbd_to_ram.get_schema()
schema = dbd_to_ram.get_schema()



converter = RAMToXDBConverter(schema)
schema_xml = converter.create_schema(schema)
print(schema_xml)