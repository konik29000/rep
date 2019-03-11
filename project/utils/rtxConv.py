from lxml import etree	#etree содержит множество функций и конструкторов классов.


class RAMToXDBConverter:
    schema = None	#пустая схема

    def __init__(self, schema):	#конструктор
        self.schema = schema

    def create_schema(self, schema):	#создание схемы бд

        schema_root = etree.Element('dbd_schema')	#корневой узел схемы 

        if ((schema.fulltext_engine is not None) and (schema.fulltext_engine != "")):	#если значение не пустое
            schema_root.set("fulltext_engine", schema.fulltext_engine)		#присваиваем
        if ((schema.version is not None) and (schema.version != "")):	
            schema_root.set("version", str(schema.version))
        if ((schema.name is not None) and (schema.name != "")):
            schema_root.set("name", schema.name)
        if ((schema.description is not None) and (schema.description != "")):
            schema_root.set("description", schema.description)

        custom_root = etree.Element("custom")	#custom - зачем-то эту величину программа требовала при создании
        schema_root.append(custom_root)		#добавляем её в схему

        # создание доменов
        domains_root = etree.Element("domains")
        for domain in schema.domains.values():
            if not(domain.unnamed):
                self.create_domain(domains_root, domain)
        schema_root.append(domains_root)


    def create_domain(self, root_elem, domain):
        element = etree.Element("domain")

        for p in domain.parameters_order:
            if ((p == "name") and (domain.name is not None) and (domain.name != "")):
                element.set("name", domain.name)
            if ((p == "type") and (domain.type is not None) and (domain.type != "")):
                element.set("type", domain.type)
            if ((p == "align") and (domain.align is not None) and (domain.align != "")):
                element.set("align", domain.align)
            if ((p == "width") and (domain.width is not None) and (domain.width != "")):
                element.set("width", str(domain.width))
            if ((p == "char_length") and (domain.char_length is not None) and (domain.char_length != "")):
                element.set("char_length", str(domain.char_length))
            if ((p == "description") and (domain.description is not None)
                    and (domain.description != "")):
                element.set("description", domain.description)
            if ((p == "props") and (domain.props is not None) and (len(domain.props) > 0)):
                element.set("props", ", ".join(domain.props))
            if ((p == "precision") and (domain.precision is not None) and (domain.precision != "")):
                element.set("precision", str(domain.precision))
            if ((p == "scale") and (domain.scale is not None) and (domain.scale != "")):
                element.set("scale", str(domain.scale))
            if ((p == "length ") and (domain.length  is not None) and (domain.length != "")):
                element.set("length", str(domain.length))

        root_elem.append(element)
		
	# создание таблиц
        tables_root = etree.Element("tables")
        for table in schema.tables.values():
            self.create_table(domains_root, table)
        schema_root.append(tables_root)
        
    def create_table(self, root_elem, table):
        element = etree.Element("table")
        for p in table.parameters_order:
            if ((p == "name") and (table.name is not None) and (table.name != "")):
                element.set("name", table.name)
            if ((p == "description") and (table.description is not None) and
                (table.description != "")):
                element.set("description", table.description)
            if ((p == "props") and (table.props is not None) and (len(table.props) > 0)):
                element.set("props", ", ".join(table.props))
            if ((p == "ht_table_flags") and (table.ht_table_flags is not None)
                    and (table.ht_table_flags != "")):
                element.set("ht_table_flags", table.ht_table_flags)
            if ((p == "access_level") and (table.access_level is not None) and (table.access_level != "")):
                element.set("access_level", str(table.access_level))
            if ((p == "means") and (table.means is not None) and (table.means != "")):
                element.set("means", str(table.means))

		# создание полей
        for field in table.fields.values():
            self.create_field(element, field, table.name)
			
    def create_field(self, root_elem, field, table_name):
        element = etree.Element("field")

        for p in field.parameters_order:
            if ((p == "name") and (field.name is not None) and (field.name != "")):
                element.set("name", field.name)
            if ((p == "rname") and (field.rname is not None) and (field.rname != "")):
                element.set("rname", field.rname)
            if ((p == "domain") and (field.domain is not None) and (field.domain != "")):
                domain = self.schema.get_domain(field.domain)
                if (domain.unnamed):
                    for p in domain.parameters_order:
                        if ((p == "type") and (domain.type is not None) and (domain.type != "")):
                            element.set("type", domain.type)
                        if ((p == "align") and (domain.align is not None) and (domain.align != "")):
                            element.set("align", domain.align)
                        if ((p == "width") and (domain.width is not None) and (domain.width != "")):
                            element.set("width", str(domain.width))
                        if ((p == "char_length") and (domain.char_length is not None) and (domain.char_length != "")):
                            element.set("char_length", str(domain.char_length))
                        if ((p == "description") and (domain.description is not None)
                                and (domain.description != "")):
                            element.set("type_description", domain.description)
                        if ((p == "props") and (domain.props is not None) and (len(domain.props) > 0)):
                            element.set("type_props", ", ".join(domain.props))
                        if ((p == "precision") and (domain.precision is not None) and (domain.precision != "")):
                            element.set("precision", str(domain.precision))
                        if ((p == "scale") and (domain.scale is not None) and (domain.scale != "")):
                            element.set("scale", str(domain.scale))
                        if ((p == "length ") and (domain.length is not None) and (domain.length != "")):
                            element.set("length", str(domain.length))
                else:
                    element.set("domain", field.domain)

            if ((p == "description") and (field.description is not None) and
                    (field.description != "")):
                element.set("description", field.description)
            if ((p == "props") and (field.props is not None) and (len(field.props) > 0)):
                element.set("props", ", ".join(field.props))

        root_elem.append(element)
		
		
		# создание индексов
        for constraint in table.constraints:
            self.create_constraint(element, constraint)
			
    def create_index(self, root_elem, index):
        element = etree.Element("index")

        if ((index.field_name is not None) and (index.field_name != "")):
            element.set("items", index.field_name)
        if ((index.props is not None) and (len(index.props) > 0)):
            element.set("props", ", ".join(index.props))

        root_elem.append(element)
		
		# создание ограничений
        for index in table.indices:
            self.create_index(element, index)

        root_elem.append(element)

    def create_constraint(self, root_elem, constraint):
        element = etree.Element("constraint")

        if ((constraint.kind is not None) and (constraint.kind != "")):
            element.set("kind", constraint.kind)
        if ((constraint.items is not None) and (constraint.items != "")):
            element.set("items", constraint.items)
        if ((constraint.reference is not None) and (constraint.reference != "")):
            element.set("reference", constraint.reference)
        if ((constraint.props is not None) and (len(constraint.props) > 0)):
            element.set("props", ", ".join(constraint.props))

        root_elem.append(element)

