import sqlite3	#модуль для работы с БД

from classes.DBDSchema import DBDSchema
from classes.Domain import Domain
from classes.Table import Table
from classes.Field import Field
from classes.Constraint import Constraint
from classes.Index import Index


class DBDtoRAM:
    schema = None
    table = None

    def __init__(self, db_name):	#конструктор
        self.connection = sqlite3.connect(db_name)	#подкл. к бд
        self.connection.row_factory = sqlite3.Row	#бъекты Row, подобны словарям Python и дают вам доступ к полям строк точь в точь, как и словарь.

    def dbd_to_ram(self):
        return self.get_schema()

    def get_schema(self):
        cursor = self.connection.cursor()	

        schema_result = cursor.execute(	#выполняем
            """
            select
                name,
                fulltext_engine,
                version,
                description
            from dbd$schemas
            """).fetchone() #.fetchone (). Извлекает следующую строку (регистр) из активного набора 
			#данных. В результате получается один кортеж или тип данных Python None 
			#после прочтения последней строки. Значение None также возвращается на границе 
			#разделения. В этом случае последующий вызовfetchone извлечет первый случай 
			#следующей разделенной группы.

		#задаём атрибуты схемы
        schema_fulltext_engine = schema_result["fulltext_engine"]
        self.schema = DBDSchema(schema_fulltext_engine)
        self.schema.name = schema_result["name"]
        self.schema.description = schema_result["description"]
        self.schema.version = schema_result["version"]

        self.get_domains()
        self.get_tables()

        self.connection.commit()
        self.connection.close()

        return self.schema

    def get_domains(self):	#задаём домен
        cursor = self.connection.cursor()
        domain_attributes = cursor.execute("""select 
            name,
            description,
            data_type_id,
            length,
            char_length,
            precision,
            scale,
            width,
            align,
            show_null,
            show_lead_nulls,
            thousands_separator,
            summable,
            case_sensitive
            from dbd$domains
            """).fetchall()

        for value in domain_attributes:	#берём список атрибутов домена
            domain_name = value["name"]
            domain_type = cursor.execute("""
                select type_id
                from dbd$data_types 
                where dbd$data_types.id = ?""", (value["data_type_id"],)).fetchone()[0]
            if (domain_name.lower().count("unnamed") > 0):
                domain_unnamed = True
            else:
                domain_unnamed = False
            domain = Domain(domain_name, domain_type, domain_unnamed)
            domain.set_name(value["name"])
            domain.set_description(value["description"])
            domain.set_length(value["length"])
            domain.set_char_length(value["char_length"])
            domain.set_precision(value["precision"])
            domain.set_scale(value["scale"])
            domain.set_width(value["width"])
            domain.set_align(value["align"])
            props = ""	#формируем список свойств (в виде строки)
            first = True
            if (value["show_null"]):
                if (first):
                    first = False
                else:
                    props += ", "	
                props += "show_null"
            if (value["show_lead_nulls"]):
                if (first):
                    first = False
                else:
                    props += ", "
                props += "show_lead_nulls"
            if (value["case_sensitive"]):
                if (first):
                    first = False
                else:
                    props += ", "
                props += "case_sensitive"
            if (value["summable"]):
                if (first):
                    first = False
                else:
                    props += ", "
                props += "summable"
            domain.set_props(props)	#добавляем
            self.schema.set_domain(domain.name, domain)

    def get_tables(self):	#аналогично для таблиц
        cursor = self.connection.cursor()

        tables_attributes = cursor.execute("""\
            select
            id,
            name,
            description,
            can_add,
            can_edit,
            can_delete,
            ht_table_flags,
            access_level,
            temporal_mode,
            means
            from dbd$tables""").fetchall()	#fetchall - вызов всех строк результата

        for value in tables_attributes:
            table_id = value["id"]
            table_name = value["name"]
            table = Table(table_name)
            table.set_description(value["description"])
            props = ""
            first = True
            if (value["can_add"]):
                if (first):
                    first = False
                else:
                    props += ", "
                props += "can_add"
            if (value["can_edit"]):
                if (first):
                    first = False
                else:
                    props += ", "
                props += "can_edit"
            if (value["can_delete"]):
                if (first):
                    first = False
                else:
                    props += ", "
                props += "can_delete"
            table.set_props(props)
            table.set_ht_table_flags(value["ht_table_flags"])
            table.set_access_level(value["access_level"])
            table.set_temporal_mode(value["temporal_mode"])
            table.set_means(value["means"])

            self.table = table
            self.get_fields(table_id)
            self.get_constraints(table_id)
            self.get_indices(table_id)

            self.schema.set_table(self.table)
            self.table = None

    def get_fields(self, table_id):
        cursor = self.connection.cursor()

        filed_attributes = cursor.execute("""\
        select 
            position,
            name,
            russian_short_name,
            description,
            domain_id,
            can_input,
            can_edit,
            show_in_grid,
            show_in_details,
            is_mean,
            autocalculated,
            required 
        from dbd$fields
        where dbd$fields.table_id = ?""", (table_id,)).fetchall()

        for value in filed_attributes:
            field_name = value["name"]
            field_position = value["position"]
            field = Field(field_name, field_position)
            field.set_rname(value["russian_short_name"])
            field.set_description(value["description"])

            props = ""
            first = True
            if (value["can_input"]):
                if (first):
                    first = False
                else:
                    props += ", "
                props += "can_input"
            if (value["can_edit"]):
                if (first):
                    first = False
                else:
                    props += ", "
                props += "can_edit"
            if (value["show_in_grid"]):
                if (first):
                    first = False
                else:
                    props += ", "
                props += "show_in_grid"
            if (value["show_in_details"]):
                if (first):
                    first = False
                else:
                    props += ", "
                props += "show_in_details"
            if (value["is_mean"]):
                if (first):
                    first = False
                else:
                    props += ", "
                props += "is_mean"
            if (value["autocalculated"]):
                if (first):
                    first = False
                else:
                    props += ", "
                props += "autocalculated"
            if (value["required"]):
                if (first):
                    first = False
                else:
                    props += ", "
                props += "required"
            field.set_props(props)

            domain_id = value["domain_id"]
            domain_name = cursor.execute("""
                        select name 
                        from dbd$domains 
                        where dbd$domains.id = ?""", (domain_id,)).fetchone()[0]
            field.set_domain(domain_name)
            self.table.set_field(field.name, field)

    def get_constraints(self, table_id):	#ограничения
        cursor = self.connection.cursor()

        constraints_attributes = cursor.execute("""
            select
            id,
            table_id,
            name,
            constraint_type,
            reference,
            has_value_edit,
            cascading_delete
            from dbd$constraints
            where dbd$constraints.table_id = ?""", (table_id,)).fetchall()

        for value in constraints_attributes:
            id = value["id"]
            if (value["constraint_type"] == "P"):
                kind = "PRIMARY"
            elif (value["constraint_type"] == "F"):
                kind = "FOREIGN"

            constraint = Constraint(kind, 1)
            id_table_ref = value["reference"]
            if (id_table_ref is not None):
                reference_table = cursor.execute("""\
                        select
                        name
                        from dbd$tables where dbd$tables.id=?""", (id_table_ref,))\
                    .fetchone()
                constraint.set_reference(reference_table["name"])

            props = ""
            first = True
            if (value["has_value_edit"]):
                if (first):
                    first = False
                else:
                    props += ", "
                props += "has_value_edit"
            if (value["cascading_delete"]):
                if (first):
                    first = False
                else:
                    props += ", "
                props += "cascading_delete"
            constraint.set_props(props)

            constraint_items = cursor.execute("""
                    select name
                    from dbd$fields
                    where dbd$fields.id = (\
                            select field_id
                            from dbd$constraint_details\
                            where dbd$constraint_details.constraint_id = ?)""",
                                              (id,)).fetchone()[0]
            constraint.set_items(constraint_items)
            self.table.set_constraint(constraint)

    def get_indices(self, table_id):	#индексы
        cursor = self.connection.cursor()
        indices_attributes = cursor.execute("""
            select 
                id,
                table_id
            from dbd$indices\
            where dbd$indices.table_id = ?""", (table_id,)).fetchall()

        for value in indices_attributes:
            id = value["id"]
            table_id = value["table_id"]

            field = cursor.execute("""
                select 
                name,
                position
                from dbd$fields 
                where dbd$fields.id = (\
                    select 
                    field_id 
                    from dbd$index_details\
                    where dbd$index_details.index_id = ?)""", (id,)).fetchone()

            field_name = field["name"]
            index = Index(field_name, id)
            self.table.set_index(index)
