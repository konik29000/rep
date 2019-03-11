# coding: utf-8
from xml.dom import minidom
from common.minidom_patch import writexml_nosort, ensure_attributes_with_dict


class RamToXdb:
    def __init__(self, file, schema):
        self.file = file
        self.schema = schema

        # Построенный XDB-описатель
        self.doc = None

        # Переопределение методов класса minidom.Element.
        # Позволяет сохранять порядок записи xml-элементов
        minidom.Element._ensure_attributes = ensure_attributes_with_dict
        minidom.Element.writexml = writexml_nosort

        # Корневой узел xml-документа
        self.root = minidom.Document()

    def generate(self):
        # Генерация XDB-описателя и запись в файл.
        self.__generate_xdb_document()

        with open(self.file, "w", encoding='utf-8') as f:
            f.write(self.doc.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="utf-8"?>'))

    def __generate_xdb_document(self):
        # Создание тега <dbd_schema>
        dbd_schema = self.root.createElement('dbd_schema')

        # Заполнение атрибутов
        dbd_schema.setAttribute('fulltext_engine', self.schema.fulltext_engine)
        dbd_schema.setAttribute('version', self.schema.version)
        dbd_schema.setAttribute('name', self.schema.name)
        dbd_schema.setAttribute('description', self.schema.description)

        # Добавление тега в документ
        self.root.appendChild(dbd_schema)

        # Добавление тега <custom>
        dbd_schema.appendChild(self.root.createElement('custom'))

        # Создание и заполнение списка тегов <domain> и <table> со всеми дочерними узлами.
        dbd_domains = self.__generate_domains()
        dbd_tables = self.__generate_tables()

        # Добавление тегов в документ
        dbd_schema.appendChild(dbd_domains)
        dbd_schema.appendChild(dbd_tables)

        # Приведение документа к читаемому виду. Отступ - 2 пробела.
        self.doc = str(self.root.toprettyxml(indent="  "))

    def __generate_domains(self):
        # Добавление тега <domains>
        domains = self.root.createElement('domains')

        for domain in self.schema.domains:
            # Создаём дочерний узел
            current_domain = self.root.createElement('domain')

            if is_not_empty(domain.name):
                current_domain.setAttribute('name', str(domain.name))

            if is_not_empty(domain.description):
                current_domain.setAttribute('description', str(domain.description))

            if is_not_empty(domain.type):
                current_domain.setAttribute('type', str(domain.type))

            if is_not_empty(domain.align):
                current_domain.setAttribute('align', str(domain.align))

            if is_not_empty(domain.width):
                current_domain.setAttribute('width', str(domain.width))

            if is_not_empty(domain.length):
                current_domain.setAttribute('length', str(domain.length))

            if is_not_empty(domain.precision):
                current_domain.setAttribute('precision', str(domain.precision))

            # Список свойст домена
            props = []

            if domain.show_null:
                props.append('show_null')

            if domain.show_lead_nulls:
                props.append('show_lead_nulls')

            if domain.thousands_separator:
                props.append('thousands_separator')

            if domain.summable:
                props.append('summable')

            if domain.case_sensitive:
                props.append('case_sensitive')

            if len(props) > 0:
                # Создание строки свойств
                domain_props = ", ".join(props)
                current_domain.setAttribute('props', domain_props)

            if is_not_empty(domain.char_length):
                current_domain.setAttribute('char_length', str(domain.char_length))

            if is_not_empty(domain.scale):
                current_domain.setAttribute('scale', str(domain.scale))

            # Добавляем дочерний узел
            domains.appendChild(current_domain)

        # Возвращаем узел <domains>, содержащий все домены
        return domains

    def __generate_tables(self):
        # Добавление тега <tables>
        tables = self.root.createElement('tables')

        for table in self.schema.tables:
            # Создаём дочерний узел
            current_table = self.root.createElement('table')

            if is_not_empty(table.name):
                current_table.setAttribute('name', str(table.name))

            if is_not_empty(table.description):
                current_table.setAttribute('description', str(table.description))

            if is_not_empty(table.temporal_mode):
                current_table.setAttribute('temporal_mode', str(table.temporal_mode))

            if is_not_empty(table.means):
                current_table.setAttribute('means', str(table.means))

            # Список свойстd таблицы
            props = []

            if table.can_add:
                props.append('add')

            if table.can_edit:
                props.append('edit')

            if table.can_delete:
                props.append('delete')

            if len(props) > 0:
                # Создание строки свойств
                table_props = ", ".join(props)
                current_table.setAttribute('props', table_props)

            # Создание и заполнение тегов <field>, <constraint>, <index> для текущей таблицы
            fields = self.__generate_fields(table)
            constraints = self.__generate_constraints(table)
            indexes = self.__generate_indexes(table)

            # Добавляем узлы, содержащие поля для текущей таблицы
            for field in fields:
                current_table.appendChild(field)

            # Добавляем узлы, содержащие констрейнты для текущей таблицы
            for constraint in constraints:
                current_table.appendChild(constraint)

            # Добавляем узлы, содержащие индексы для текущей таблицы
            for index in indexes:
                current_table.appendChild(index)

            # Добавляем дочерний узел таблицы
            tables.appendChild(current_table)

        # Возвращаем узел <tables>, содержащий все таблицы и принадлежащие им поля, констрейнты и индексы.
        return tables

    def __generate_fields(self, table):
        # Список сгенерированных тегов <field> для заданной таблицы
        fields = []

        for field in table.fields:
            # Создаём дочерний узел
            current_field = self.root.createElement('field')

            if is_not_empty(field.name):
                current_field.setAttribute('name', str(field.name))

            if is_not_empty(field.rname):
                current_field.setAttribute('rname', str(field.rname))

            if field.domain is not None:
                # Получаем домен для текущего поля
                domain = field.domain

                # Если домен именованный - заполняем атрибут поля
                if not domain.unnamed:
                    current_field.setAttribute('domain', str(domain.name))
                # Иначе заполняем все свойства домена для текущего поля
                else:
                    if is_not_empty(domain.description):
                        current_field.setAttribute('domain.description', str(domain.description))

                    if is_not_empty(domain.type):
                        current_field.setAttribute('domain.type', str(domain.type))

                    if is_not_empty(domain.align):
                        current_field.setAttribute('domain.align', str(domain.align))

                    if is_not_empty(domain.width):
                        current_field.setAttribute('domain.width', str(domain.width))

                    if is_not_empty(domain.length):
                        current_field.setAttribute('domain.length', str(domain.length))

                    if is_not_empty(domain.precision):
                        current_field.setAttribute('domain.precision', str(domain.precision))

                    # Список свойств домена
                    props = []

                    if domain.show_null:
                        props.append('show_null')

                    if domain.show_lead_nulls:
                        props.append('show_lead_nulls')

                    if domain.thousands_separator:
                        props.append('thousands_separator')

                    if domain.summable:
                        props.append('summable')

                    if domain.case_sensitive:
                        props.append('case_sensitive')

                    if len(props) > 0:
                        # Создание строки свойств
                        domain_props = ", ".join(props)
                        current_field.setAttribute('domain.props', domain_props)

                    if is_not_empty(domain.char_length):
                        current_field.setAttribute('domain.char_length', str(domain.char_length))

                    if is_not_empty(domain.scale):
                        current_field.setAttribute('domain.scale', str(domain.scale))

            if is_not_empty(field.description):
                current_field.setAttribute('description', str(field.description))

            # Список свойств поля
            props = []

            if field.can_input:
                props.append('input')

            if field.can_edit:
                props.append('edit')

            if field.show_in_grid:
                props.append('show_in_grid')

            if field.show_in_details:
                props.append('show_in_details')

            if field.is_mean:
                props.append('is_mean')

            if field.autocalculated:
                props.append('autocalculated')

            if field.required:
                props.append('required')

            if len(props) > 0:
                # Создание строки свойств
                field_props = ", ".join(props)
                current_field.setAttribute('props', field_props)

            # Добавляем дочерний узел к списку
            fields.append(current_field)

        # Возвращаем список узлов <field>
        return fields

    def __generate_indexes(self, table):
        # Список сгенерированных тегов <index> для заданной таблицы
        indexes = []

        for index in table.indexes:
            # Создаём дочерний узел
            current_index = self.root.createElement('index')

            if is_not_empty(index.name):
                current_index.setAttribute('name', str(index.name))

            if is_not_empty(index.field):
                current_index.setAttribute('field', str(index.field))

            if is_not_empty(index.local):
                current_index.setAttribute('local', str(index.local))

            if is_not_empty(index.descend):
                current_index.setAttribute('descend', str(index.descend))

            # Заполнение атрибута props
            if is_not_empty(index.kind):

                if index.kind == 'U':
                    current_index.setAttribute('props', 'uniqueness')

                elif index.kind == 'T':
                    current_index.setAttribute('props', 'fulltext')

            # Добавляем дочерний узел к списку
            indexes.append(current_index)

        # Возвращаем список узлов <index>
        return indexes

    def __generate_constraints(self, table):
        # Список сгенерированных тегов <constraint> для заданной таблицы
        constraints = []

        for constraint in table.constraints:
            # Создаём дочерний узел
            current_constraint = self.root.createElement('constraint')

            if is_not_empty(constraint.name):
                current_constraint.setAttribute('name', str(constraint.name))

            if is_not_empty(constraint.kind):
                current_constraint.setAttribute('kind', str(constraint.kind))

            if is_not_empty(constraint.items):
                current_constraint.setAttribute('items', str(constraint.items))

            if is_not_empty(constraint.reference):
                current_constraint.setAttribute('reference', str(constraint.reference))

            if is_not_empty(constraint.expression):
                current_constraint.setAttribute('expression', str(constraint.reference))

            # Список свойств констрейнта
            props = []

            if constraint.has_value_edit:
                props.append('has_value_edit')

            if constraint.full_cascading_delete:
                props.append('full_cascading_delete')
            elif constraint.cascading_delete:
                props.append('cascading_delete')

            if len(props) > 0:
                # Создание строки свойств
                constraint_props = ", ".join(props)
                current_constraint.setAttribute('props', constraint_props)

            # Добавляем дочерний узел к списку
            constraints.append(current_constraint)

        # Возвращаем список узлов <constraint>
        return constraints


def is_not_empty(value):
    return value is not None and value != ""
