class DBDSchema:	#класс схемы бд формата дбд
    parameters_order = None  # список имен параметров ограничений, полезных для RAM-> XML
    tables_order = None  # список имён таблиц, полезных для  RAM->XML
    domains_order = None  # список доменных имён, полезных для RAM->XML
    fulltext_engine = None
    version = None #версия
    name = None	#имя 
    description = None	#определеие
    domains = None  # словарь доменных имён
    tables = None  # словарь объектов типа таблиц

    def __init__(self, fulltext_engine):	#конструктор класса
        self.domains = {}	#создаём пустой словарь доменных имён
        self.tables = {}	#создаём пустой словарь объектов-таблиц
        self.parameters_order = []	#задаём пустой список параметров ограничений
        if (fulltext_engine is not None) & (fulltext_engine != ""):	#если  существует
            self.fulltext_engine = fulltext_engine	#присваеваем сие элементу акт. экземпляра класса
            self.parameters_order.append("fulltext_engine")	#и добавляем в список имён параметров ограничений
        self.tables_order = []	#создаём пустой список имён таблиц
        self.domains_order = []	#создаём пустой список имён доменов

    def set_fulltext_engine(self, fulltext_engine):	#задание величины 
        if (fulltext_engine is not None) & (fulltext_engine != ""):	#если значение не пустое
            self.fulltext_engine = fulltext_engine	#присваеваем его
            self.parameters_order.append("fulltext_engine")	#добавляем в список имён параметров ограничений

    def get_fulltext_engine(self):
        return self.fulltext_engine

    def set_version(self, version):	#задание версии
        if (version is not None) & (version != ""):	#если значение не пустое
            self.version = version	#присваиваем его полю класса
            self.parameters_order.append("version")	#и добавляем в список параметров ограничений

    def get_version(self):#вызов значения версии
        return self.version

    def set_name(self, name):	#задание имени
        if (name is not None) & (name != ""):
            self.name = name	#присвоение
            self.parameters_order.append("name")	#добавление в список параметров ограничений

    def get_name(self):	#вызов значения имени
        return self.name

    def set_description(self, description):	#задание определения
        if (description is not None) & (description != ""):	#проверка
            self.description = description	#присвоение
            self.parameters_order.append("description")	#добавление в список пар.огр.

    def get_description(self):	#вызов 
        return self.description

    def set_domain(self, domain_name, domain): 	#задание доменного имени
        self.domains[domain_name] = domain		#задали
        self.domains_order.append(domain_name)	#добавили в список

    def get_domain(self, domain_name):	#вызов имени домена
        return self.domains.get(domain_name)

    def get_domains(self):	#вызов домена
        return self.domains

    def set_table(self, table):	#задание таблицы
        self.tables[table.name] = table	
        self.tables_order.append(table.name)	

    def get_table(self, table_name):	#вызов имени таблицы
        return self.tables.get(table_name)

    def get_tables(self):	#вызов таблицы
        return self.tables

    def get_parameters_order(self):	#вызов списка имён параметров ограничений
        return self.parameters_order

    def get_tables_order(self):		#вызов списка имён таблиц
        return self.tables_order	
