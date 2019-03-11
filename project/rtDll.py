class RamToPgDdl:
    def __init__(self, file, ram_model):

        self.schema = ram_model
        self.filename = file
        self.constraint_id = 0	
        self.index_id = 0
        self.Ddl = ""

    def generate(self):
        self.__generate_domains()
        self.__generate_tables()
        self.__generate_constraints()
        self.__generate_indexes()

        return self.Ddl

    def write_to_file(self):

        with open(self.filename, "w", encoding='utf-8') as f:
            f.write(self.Ddl)

    @staticmethod
    def ram_types_to_pg(data_type):
        if data_type == 'STRING':
            return 'VARCHAR'
        elif data_type == 'SMALLINT':
            return 'SMALLINT'
        elif data_type == 'INTEGER':
            return 'INTEGER'
        elif data_type == 'WORD':
            return 'SMALLINT'
        elif data_type == 'BOOLEAN':
            return 'BOOLEAN'
        elif data_type == 'FLOAT':
            return 'FLOAT'
        elif data_type == 'CURRENCY':
            return 'NUMERIC'
        elif data_type == 'BCD':
            return 'DECIMAL'
        elif data_type == 'DATE':
            return 'DATE'
        elif data_type == 'TIME':
            return 'TIME'
        elif data_type == 'DATETIME':
            return 'TIMESTAMP'
        elif data_type == 'TIMESTAMP':
            return 'TIMESTAMP'
        elif data_type == 'BYTES':
            return 'BYTEA'
        elif data_type == 'VARBYTES':
            return 'BYTEA'
        elif data_type == 'BLOB':
            return 'BYTEA'
        elif data_type == 'MEMO':
            return 'TEXT'
        elif data_type == 'GRAPHIC':
            return 'BYTEA'
        elif data_type == 'FMTMEMO':
            return 'TEXT'
        elif data_type == 'FIXEDCHAR':
            return 'VARCHAR'
        elif data_type == 'WIDESTRING':
            return 'TEXT'
        elif data_type == 'LARGEINT':
            return 'BIGINT'
        elif data_type == 'COMP':
            return 'BIGINT'
        elif data_type == 'ARRAY':
            return 'ARRAY'
        elif data_type == 'FIXEDWIDECHAR':
            return 'TEXT'
        elif data_type == 'WIDEMEMO':
            return 'TEXT'
        elif data_type == 'CODE':
            return 'TEXT'
        elif data_type == 'RECORDID':
            return 'INTEGER'
        elif data_type == 'SET':
            return 'ARRAY'
        elif data_type == 'PERIOD':
            return 'INTERVAL'
        elif data_type == 'BYTE':
            return 'BYTEA'

    def __write(self, string, indent):
        self.Ddl += indent + string + '\n'

    def __new_line(self):
        self.Ddl += '\n\n'

    @staticmethod
    def quotes(string):
        return "\"" + string + "\""

    def __generate_domains(self):
        for domain in self.schema.domains:

            Ddl = "CREATE DOMAIN {0} {1} {2};"

            name = self.quotes(domain.name)
            type = self.ram_types_to_pg(domain.type)

            if str(is_not_empty(domain.char_length)):
                length = "({0})".format(str(domain.char_length))
            else:
                length = ""

            self.__write(Ddl.format(name, type, length), indent='')

            self.__new_line()

        self.Ddl += '\n'

    def __generate_tables(self):
        for table in self.schema.tables:

            Ddl = "CREATE TABLE {} ("
            

            self.Ddl += ("CREATE TABLE \"%s\" (\n" % table.name)
            for field in table.fields:
                self.Ddl += (
                    "\t\"%s\"\t%s%s" % (field.name, ("\"" + field.domain.name + "\""),
                                        ',\n' if (table.fields.index(field)) < (len(table.fields) - 1) else ''))
            self.Ddl += ");\n\n"

    def __generate_constraints(self):
        for table in self.schema.tables:
            for constraint in table.constraints:

                if constraint.kind == 'PRIMARY':
                    self.Ddl += ("ALTER TABLE \"%s\"\n" % table.name)
                    self.Ddl += "\t ADD "
                    items = constraint.items.replace(' ', '').replace(',', '","')
                    self.Ddl += ("PRIMARY KEY (\"%s\");" % items)

                    self.Ddl += '\n\n'

        for table in self.schema.tables:
            for constraint in table.constraints:
                if constraint.kind == 'FOREIGN':
                    self.Ddl += ("ALTER TABLE \"%s\"\n" % table.name)
                    constraint_name = constraint.name if constraint.name is not None else self.__get_constraint_name()
                    self.Ddl += "\t ADD CONSTRAINT {0} ".format(constraint_name)
                    self.Ddl += (
                        "FOREIGN KEY (\"%s\") REFERENCES \"%s\"%s" % (
                            constraint.items, constraint.reference,
                            " ON DELETE CASCADE;" if (
                                constraint.cascading_delete or constraint.full_cascading_delete) else ";"
                        )
                    )
                    self.Ddl += '\n\n'

    def __generate_indexes(self):
        for table in self.schema.tables:
            for index in table.indexes:
                items = index.field.replace(' ', '').replace(',', '","')
                self.Ddl += ("CREATE %sINDEX \"%s_%s_idx\" ON \"%s\"(\"%s\");\n\n"
                             % (
                                 "UNIQUE " if index.uniqueness else "",
                                 table.name,
                                 items.replace(' ', '').replace('"', '').replace(',', '_'),
                                 table.name,
                                 items
                             )
                             )

    def __get_constraint_name(self):
        self.constraint_id += 1
        return 'constraint_' + str(self.constraint_id)

    def __get_index_name(self):
        self.index_id += 1
        return 'index_' + str(self.index_id)


def is_not_empty(value):
    return value is not None and value != ""
