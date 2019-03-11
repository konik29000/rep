from xml.dom.minidom import parse
from common.ram import *	# RAM представление базы данных
from common.exceptions import *
import os.path


# Парсер ".xdb" файла
class XdbToRam:
    def __init__(self, file):

        if os.path.exists(file):
            self.parser = parse(file)
        else:
            print("'" + file + "' файл не существует.")
            exit(-1)

        self.schema = Schema()

    def parse(self):
        self.__fetch_data()
        return self.schema

    def __fetch_data(self):
        try:
            self.__fetch_schema_properties()
            self.__fetch_domains()
            self.__fetch_tables()
        except UnknownAttributeException as exception:
            print("Fatal error!")
            print(exception)
            exit(-1)

    def __fetch_schema_properties(self):
        # Сохраняем свойства тега <dbd_schema>
        dbd_schema = self.parser.getElementsByTagName("dbd_schema")[0]

        attributes = dbd_schema.attributes
        if dbd_schema is not None:
            for i in range(0, attributes.length):
                attribute = attributes.item(i)
                if attribute.name == 'fulltext_engine':
                    self.schema.fulltext_engine = attribute.value
                elif attribute.name == 'version':
                    self.schema.version = attribute.value
                elif attribute.name == 'name':
                    self.schema.name = attribute.value
                elif attribute.name == 'description':
                    self.schema.description = attribute.value
                else:
                    raise UnknownAttributeException(
                        "Недопустимый атрибут: {0} в теге <dbd_schema>".format(attribute.name))
        else:
            print("XDB-описатель не содержит тег <dbd_schema>")
            exit(-1)

    def __fetch_domains(self):
        # Сохраняем свойства доменов. Тег <domain>
        for domain_element in self.parser.getElementsByTagName("domain"):
            domain = Domain()

            # Разбор свойств домена
            attributes = domain_element.attributes
            for i in range(0, attributes.length):
                attribute = attributes.item(i)
                if attribute.name == 'name':
                    domain.name = attribute.value
                elif attribute.name == 'align':
                    domain.align = attribute.value
                elif attribute.name == 'type':
                    domain.type = attribute.value
                elif attribute.name == 'char_length':
                    domain.char_length = attribute.value
                elif attribute.name == 'width':
                    domain.width = attribute.value
                elif attribute.name == 'description':
                    domain.description = attribute.value
                elif attribute.name == 'scale':
                    domain.scale = attribute.value
                elif attribute.name == 'props':

                    # Разбор строки props
                    for p in attribute.value.split(","):

                        p = p.strip()  # Удаление пробелов в начале и конце строки

                        if p == 'show_null':
                            domain.show_null = True
                        elif p == 'show_lead_nulls':
                            domain.show_lead_nulls = True
                        elif p == 'thousands_separator':
                            domain.thousands_separator = True
                        elif p == 'summable':
                            domain.summable = True
                        elif p == 'case_sensitive':
                            domain.case_sensitive = True
                        else:
                            raise UnknownAttributeException(
                                "Домен {0} содержит недопустимое свойство: {1}".format(
                                    domain_element.getAttribute('name'), p))

                elif attribute.name == 'precision':
                    domain.precision = attribute.value
                elif attribute.name == 'length':
                    domain.length = attribute.value
                else:
                    raise UnknownAttributeException(
                        "Домен {0} содержит недопустимый атрибут: {1}".format(domain_element.getAttribute('name'),
                                                                              attribute.name))

                # Указываем, что домен именованный
                domain.unnamed = False

            self.schema.domains.append(domain)

    def __fetch_tables(self):
        # Сохраняем свойства таблиц. Тег <table>
        for table_element in self.parser.getElementsByTagName("table"):
            table = Table()

            # Разбор свойств таблицы
            attributes = table_element.attributes
            for i in range(0, attributes.length):
                attribute = attributes.item(i)
                if attribute.name == 'name':
                    table.name = attribute.value
                elif attribute.name == 'description':
                    table.description = attribute.value
                elif attribute.name == 'temporal_mode':
                    table.temporal_mode = attribute.value
                elif attribute.name == 'means':
                    table.means = attribute.value
                elif attribute.name == 'props':

                    for p in attribute.value.split(","):

                        p = p.strip()  # Удаление пробелов в начале и конце строки

                        if p == 'add':
                            table.can_add = True
                        elif p == 'edit':
                            table.can_edit = True
                        elif p == 'delete':
                            table.can_delete = True
                        else:
                            raise UnknownAttributeException(
                                "Таблица {0} содержит недопустимое свойство: {1}".format(
                                    table_element.getAttribute('name'),
                                    p))
                else:
                    raise UnknownAttributeException(
                        "Недопустимый атрибут {1} в таблице: {0}".format(table_element.getAttribute('name'),
                                                                         attribute.name))

            # Сбор полей таблицы
            for field_element in table_element.getElementsByTagName("field"):
                table.fields.append(self.__fetch_field(field_element, table.name))

            # Сбор индексов таблицы
            for index_element in table_element.getElementsByTagName("index"):
                table.indexes.append(self.__fetch_index(index_element, table.name))

            # Сбор констрейнтов таблицы
            for constraint_element in table_element.getElementsByTagName("constraint"):
                table.constraints.append(self.__fetch_constraint(constraint_element, table.name))

            self.schema.tables.append(table)

    def __fetch_field(self, field_element, table_name):
        # Извлекаем свойства поля
        field = Field()

        # Домен, присваиваемый полю. Переменная будет хранить либо именованный, либо неименованный домен
        domain = Domain()

        attributes = field_element.attributes
        for i in range(0, attributes.length):
            attribute = attributes.item(i)
            if attribute.name == 'name':
                field.name = attribute.value

            # Если условие выполнилось - поле содержит неименованный домен
            elif attribute.name == 'domain.type':
                domain.name = ""
                domain.unnamed = True
                domain.type = attribute.value
            elif attribute.name == 'domain.align':
                domain.align = attribute.value
            elif attribute.name == 'domain.char_length':
                domain.char_length = attribute.value
            elif attribute.name == 'domain.width':
                domain.width = attribute.value
            elif attribute.name == 'domain.description':
                domain.description = attribute.value
            elif attribute.name == 'domain.props':

                for p in attribute.value.split(","):

                    p = p.strip()

                    if p == 'show_null':
                        domain.show_null = True
                    elif p == 'show_lead_nulls':
                        domain.show_lead_nulls = True
                    elif p == 'thousands_separator':
                        domain.thousands_separator = True
                    elif p == 'summable':
                        domain.summable = True
                    elif p == 'case_sensitive':
                        domain.case_sensitive = True
                    else:
                        raise UnknownAttributeException(
                            "Поле {0} содержит недопустимое свойство домена: {1}".format(
                                field_element.getAttribute('name'), p))

            elif attribute.name == 'domain.scale':
                domain.scale = attribute.value
            elif attribute.name == 'domain.precision':
                domain.precision = attribute.value
            elif attribute.name == 'domain.length':
                domain.length = attribute.value
            elif attribute.name == 'domain':

                target_domain = self.schema.get_domain_by_name(attribute.value)

                if target_domain is not None:
                    domain = target_domain
                else:
                    raise ValueError("Домен не найден!")
            elif attribute.name == 'rname':
                field.rname = attribute.value
            elif attribute.name == 'props':

                for p in attribute.value.split(","):

                    p = p.strip()

                    if p == 'autocalculated':
                        field.autocalculated = True
                    elif p == 'input':
                        field.can_input = True
                    elif p == 'edit':
                        field.can_edit = True
                    elif p == 'show_in_details':
                        field.show_in_details = True
                    elif p == 'show_in_grid':
                        field.show_in_grid = True
                    elif p == 'is_mean':
                        field.is_mean = True
                    elif p == 'required':
                        field.required = True
                    else:
                        raise UnknownAttributeException(
                            "Поле {0} содержит неизвестное свойство: {1}".format(field_element.getAttribute('name'), p))

            elif attribute.name == 'description':
                field.description = attribute.value
            else:
                raise UnknownAttributeException(
                    "Таблица {0} содержит поле - {1} с недопустимым атрибутом: {2}".format(
                        table_name, field.name,
                        attribute.name))

        field.domain = domain

        return field

    @staticmethod
    def __fetch_index(index_element, table_name):
        # Извлекаем свойства индекса
        index = Index()

        attributes = index_element.attributes
        for i in range(0, attributes.length):
            attribute = attributes.item(i)
            if attribute.name == 'field':
                index.field = attribute.value
            elif attribute.name == 'props':

                for p in attribute.value.split(", "):
                    if p == 'uniqueness':
                        index.uniqueness = True
                    elif p == 'fulltext':
                        index.fulltext = True
                    else:
                        raise UnknownAttributeException(
                            "Таблица {0} содержит недопустимое свойство индекса: {1}".format(table_name,
                                                                                             p))
            elif attribute.name == 'local':
                index.local = attribute.value
            elif attribute.name == 'descend':
                index.descend = attribute.value
            elif attribute.name == 'expression':
                index.expression = attribute.value
            else:
                raise UnknownAttributeException(
                    "Таблица {0} содержит иднекс с недопустимым атрибутом: {1}".format(
                        table_name, attribute.name))

        return index

    @staticmethod
    def __fetch_constraint(constraint_element, table_name):
        # Извлекаем свойства констрейнта
        constraint = Constraint()

        attributes = constraint_element.attributes
        for i in range(0, attributes.length):
            attribute = attributes.item(i)
            if attribute.name == 'kind':
                constraint.kind = attribute.value
            elif attribute.name == 'items':
                constraint.items = attribute.value
            elif attribute.name == 'reference':
                constraint.reference = attribute.value
            elif attribute.name == 'props':

                for p in attribute.value.split(","):

                    p = p.strip()

                    if p == 'has_value_edit':
                        constraint.has_value_edit = True
                    elif p == 'cascading_delete':
                        constraint.cascading_delete = True
                    elif p == 'full_cascading_delete':
                        constraint.full_cascading_delete = True
                    else:
                        raise UnknownAttributeException(
                            "Таблица {0} содержит констрейнт с неизвестным свойством: {1}".format(
                                table_name, p))

            elif attribute.name == 'expression':
                constraint.expression = attribute.value
            else:
                raise UnknownAttributeException(
                    "Таблица {0} содержит констрейнт с неизвестным атрибутом: {1}".format(
                        table_name, attribute.name))

        return constraint
