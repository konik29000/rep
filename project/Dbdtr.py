from common.ram import *	# RAM представление базы данных
import sqlite3	#библиотека субд
from common.dbd_const import *	#конструктор
import os.path	#библиотека для работы с ос
# Парсер ".db" файла
class DbdToRam:
    def __init__(self, file):
        self.schema = Schema()
		#если файл схемы уже есть, подключаемся к нему
        if os.path.exists(file):
            self.connector = sqlite3.connect(file)
        else:
            print("'" + file + "' файл не существует.")
            exit(-1)
		#подсоединение
        self.cursor = self.connector.cursor()
		#получение данных
    def parse(self):
        self.__fetch_data()
        return self.schema
		#по всем свойствам
    def __fetch_data(self):
        self.__fetch_schema_properties()	#свойства схемы
        self.__fetch_domains()	
        self.__fetch_tables()
        self.__fetch_fields()
        self.__fetch_indexes()
        self.__fetch_constraints()	#ограничения
		 # Извлечение свойств схемы
    def __fetch_schema_properties(self):
        # for schema_prop in self.cursor.execute(SQL_GET_SCHEMA_PROPS):
        self.schema.fulltext_engine = "ORACLE TEXT"
        self.schema.version = "1.2"
        self.schema.name = "TASKS"
        self.schema.description = "Описатель БД TASKS"
    def __fetch_domains(self):
        # Извлечение доменов
		#поле для поддержки неименованных доменов - self.unnamed, здесь обрабатывать надеюсь что не требуется 
		#а спрашивать страшно оставлю так
        SQL_GET_DOMAINS = """
            SELECT
                dbd$domains.name,	
                dbd$domains.description,
                dbd$data_types.type_id,
                dbd$domains.length,
                dbd$domains.char_length,
                dbd$domains.precision,
                dbd$domains.scale,
                dbd$domains.width,
                dbd$domains.align,
                dbd$domains.show_null,
                dbd$domains.show_lead_nulls,
                dbd$domains.thousands_separator,
                dbd$domains.summable,
                dbd$domains.case_sensitive
            FROM dbd$domains
            LEFT JOIN dbd$data_types ON dbd$domains.data_type_id = dbd$data_types.id
        """
			#заполнение списка свойств
        for domain_element in self.cursor.execute(SQL_GET_DOMAINS):
            domain = Domain()
            domain.name = domain_element[0]
            domain.description = value_check(domain_element[1])
            domain.type = value_check(domain_element[2])
            domain.length = value_check(domain_element[3])
            domain.char_length = value_check(domain_element[4])
            domain.precision = value_check(domain_element[5])
            domain.scale = value_check(domain_element[6])
            domain.width = value_check(domain_element[7])
            domain.align = value_check(domain_element[8])
            # Props
            domain.show_null = True if domain_element[9] == 'TRUE' else False
            domain.show_lead_nulls = True if domain_element[10] == 'TRUE' else False
            domain.thousands_separator = True if domain_element[11] == 'TRUE' else False
            domain.summable = True if domain_element[12] == 'TRUE' else False
            domain.case_sensitive = True if domain_element[13] == 'TRUE' else False
            self.schema.domains.append(domain)
    def __fetch_tables(self):
        # Извлечение данных таблиц
        SQL_GET_TABLES = """
            SELECT
                dbd$tables.name,
                dbd$tables.description,
                dbd$tables.can_add,
                dbd$tables.can_edit,
                dbd$tables.can_delete
            FROM dbd$tables
        """
        for table_element in self.cursor.execute(SQL_GET_TABLES):
            table = Table()
            table.name = table_element[0]
            table.description = value_check(table_element[1])
            # Props
            table.can_add = True if table_element[2] == 'TRUE' else False
            table.can_edit = True if table_element[3] == 'TRUE' else False
            table.can_delete = True if table_element[4] == 'TRUE' else False
            self.schema.tables.append(table)
    def __fetch_fields(self):
        # Извлечение данных полей таблиц
        SQL_GET_FIELDS = """
            SELECT
                dbd$fields.table_id,
                dbd$fields.position,
                dbd$fields.name,
                dbd$fields.russian_short_name,
                dbd$fields.description,
                dbd$fields.domain_id,
                dbd$fields.can_input,
                dbd$fields.can_edit,
                dbd$fields.show_in_grid,
                dbd$fields.show_in_details,
                dbd$fields.is_mean,
                dbd$fields.autocalculated,
                dbd$fields.required
            FROM dbd$fields
            ORDER BY table_id, position
        """

        for field_element in self.cursor.execute(SQL_GET_FIELDS):
            field = Field()
            field.name = field_element[2]
            field.rname = value_check(field_element[3])
            field.domain = self.schema.domains[field_element[5] - 1]
            field.description = value_check(field_element[4])

            # Props
            field.can_input = True if field_element[6] == 'TRUE' else False
            field.can_edit = True if field_element[7] == 'TRUE' else False
            field.show_in_grid = True if field_element[8] == 'TRUE' else False
            field.show_in_details = True if field_element[9] == 'TRUE' else False
            field.is_mean = True if field_element[10] == 'TRUE' else False
            field.autocalculated = True if field_element[11] == 'TRUE' else False
            field.required = True if field_element[12] == 'TRUE' else False

            self.schema.tables[field_element[0] - 1].fields.append(field)

    def __fetch_indexes(self):
        # Извлечение данных индексов таблиц

        SQL_GET_INDICIES = """
            SELECT
                dbd$indices.table_id,
                dbd$index_details.position,
                dbd$fields.name,
                dbd$index_details.expression,
                dbd$indices.kind,
                dbd$index_details.descend,
                dbd$indices.local
            FROM dbd$index_details
            LEFT JOIN dbd$indices ON dbd$index_details.index_id = dbd$indices.id
            LEFT JOIN dbd$fields ON dbd$index_details.field_id = dbd$fields.id
            GROUP BY dbd$indices.table_id, dbd$index_details.position
        """

        for index_element in self.cursor.execute(SQL_GET_INDICIES):

            index = Index()
            index.field = index_element[2]
            index.expression = value_check(index_element[3])

            # Props
            index.kind = index_element[4]

            if index_element[4] == "U":
                index.uniqueness = True
            elif index_element[4] == "T":
                index.fulltext = True
            if index_element[5] == "TRUE":
                index.descend = True

            self.schema.tables[index_element[0] - 1].indexes.append(index)

    def __fetch_constraints(self):
        # Извлечение данных ограничений таблиц

        SQL_GET_CONSTRAINTS = """
            SELECT
                dbd$constraints.table_id,
                dbd$constraint_details.position,
                dbd$constraints.constraint_type,
                dbd$fields.name,
                dbd$tables.name,
                dbd$constraints.expression,
                dbd$constraints.has_value_edit,
                dbd$constraints.cascading_delete
            FROM dbd$constraint_details
            LEFT JOIN dbd$constraints ON dbd$constraint_details.constraint_id=dbd$constraints.id
            LEFT JOIN dbd$fields ON dbd$constraint_details.field_id = dbd$fields.id
            LEFT JOIN dbd$tables ON dbd$constraints.reference = dbd$tables.id
            GROUP BY dbd$constraints.table_id, dbd$constraint_details.position
        """

        for constraint_element in self.cursor.execute(SQL_GET_CONSTRAINTS):

            constraint = Constraint()
            constraint.kind = "PRIMARY" if constraint_element[2] is "P" else "FOREIGN"
            constraint.items = constraint_element[3]
            constraint.reference = "" if constraint.kind is "PRIMARY" else value_check(constraint_element[4])
            constraint.expression = value_check(constraint_element[5])

            # Props
            if constraint_element[6] == "TRUE":
                constraint.has_value_edit = True
            if constraint_element[7] == "TRUE":
                constraint.full_cascading_delete = True
            elif constraint_element[7] == "FALSE":
                constraint.cascading_delete = True

            self.schema.tables[constraint_element[0] - 1].constraints.append(constraint)
def value_check(data):
    if data == "NULL":
        return ""
    else:
        return data
