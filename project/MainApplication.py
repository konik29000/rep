from utils.XmlParser import *			#содержит функцию` create_list_of_objects_from_xml`, 
from utils.DBInitializer import *		#класс, который содержит функции для инициализации базы данных
from utils.RAMToDBDConverter import *	# содержит функции для вставок в бд
import os		#содержит функции для работы с ОС, независ. от конкретной ОС.

DATABASE_NAME = "database.db"
XML_FILE_NAME_1 = "./resources/tasks.xml"
XML_FILE_NAME_2 = "./resources/prjadm.xml"

schemas = create_list_of_objects_from_xml([XML_FILE_NAME_1, XML_FILE_NAME_2]) #создает классы из описания xml

create = not os.path.exists(DATABASE_NAME)	#проверка существования такой базы
if create:	
    initializer = DBInitializer(DATABASE_NAME) #созд. экземпляр класса, иниц. БД
    initializer.init_database()		
    converter_to_database = RAMToDBDConverter(DATABASE_NAME) #созд. экз. класса вставок
    converter_to_database.rtDbd(schemas)	#выз. ф-цию вставки схем
	#Схема базы данных — это её структура, описанная на формальном языке, поддерживаемом СУБД, вкл. таблицы, их поля итд.





