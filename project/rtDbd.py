# coding: utf-8
import sqlite3
from common.dbd_const import *
import os.path


class RamToDbd:
    def __init__(self, file, schema):
        self.schema = schema

        # Текущий порядковый номер индексов и констрейнтов. Для формирования временных имён.
        self.current_index_number = 0
        self.current_constraint_number = 0

        if not os.path.exists(file):
            self.connection = sqlite3.connect(file)
        else:
            print("'" + file + "' - файл с таким именем уже существует!")
            exit(-1)
            
        self.cursor = self.connection.cursor()
    
    def generate(self):
        # Преобразование RAM в DBD и запись в БД
        
        # Создание таблиц описателя
        self.cursor.executescript(SQL_DBD_INIT)
        self.connection.commit()

        self.__generate_domains()
        self.__generate_tables()
        self.__generate_fields()
        self.__generate_indexes()
        self.__generate_constraints()

        self.connection.commit()
        self.connection.close()

    # Формирование временных имён индексов
    def __get_temp_index_name(self):
        self.current_index_number += 1
        return 'temp_' + str(self.current_index_number)

    # Формирование временных имён ограничений
    def __get_temp_constraint_name(self):
        self.current_constraint_number += 1
        return 'temp_' + str(self.current_constraint_number)

    def __generate_schema_properties(self):
        pass

    def __generate_domains(self):
        # SQL-константы

        DML_INSERT_DOMAIN = """
            INSERT INTO dbd$domains (
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
                case_sensitive)
            VALUES (?, ?, (SELECT id FROM dbd$data_types WHERE type_id = ?), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

        SQL_CREATE_TEMP_DOMAINS = """
            CREATE TEMP TABLE temp_domains (
                id  integer primary key autoincrement default(null),
                name varchar unique default(null),  -- имя домена
                description varchar default(null),  -- описание
                data_type_id integer not null,      -- идентификатор типа (dbd$data_types)
                length integer default(null),       -- длина
                char_length integer default(null),  -- длина в символах
                precision integer default(null),    -- точность
                scale integer default(null),        -- количество знаков после запятой
                width integer default(null),        -- ширина визуализации в символах
                align char default(null),           -- признак выравнивания
                show_null boolean default(null),    -- нужно показывать нулевое значение?
                show_lead_nulls boolean default(null),      -- следует ли показывать лидирующие нули?
                thousands_separator boolean default(null),  -- нужен ли разделитель тысяч?
                summable boolean default(null),             -- признак того, что поле является суммируемым
                case_sensitive boolean default(null)       -- признак необходимости регистронезависимого поиска для поля
            );
            """

        DML_INSERT_TEMP_DOMAIN = """
                INSERT INTO temp_domains (
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
                    case_sensitive)
                VALUES (?, ?, (SELECT id FROM dbd$data_types WHERE type_id = ?), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

        DML_JOIN_AND_SAVE_DOMAINS = """
                INSERT INTO dbd$domains (
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
                )
                SELECT DISTINCT
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
                FROM temp_domains;
                """

        self.cursor.executescript(SQL_CREATE_TEMP_DOMAINS)

        if len(self.schema.domains) > 0:
            for domain in self.schema.domains:
                target_domain = ()
                target_domain += domain.name,
                target_domain += is_null(domain.description),
                target_domain += is_null(domain.type),
                target_domain += is_null(domain.length),
                target_domain += is_null(domain.char_length),
                target_domain += is_null(domain.precision),
                target_domain += is_null(domain.scale),
                target_domain += is_null(domain.width),
                target_domain += is_null(domain.align),

                # Props
                target_domain += 'TRUE' if domain.show_null else 'FALSE',
                target_domain += 'TRUE' if domain.show_lead_nulls else 'FALSE',
                target_domain += 'TRUE' if domain.thousands_separator else 'FALSE',
                target_domain += 'TRUE' if domain.summable else 'FALSE',
                target_domain += 'TRUE' if domain.case_sensitive else 'FALSE',

                self.connection.execute(DML_INSERT_DOMAIN, target_domain)

        for table in self.schema.tables:
            for field in table.fields:
                # Добавляем в temp_domains все неименованные домены
                if field.domain.unnamed:
                    target_domain = ()
                    target_domain += domain.name,
                    target_domain += is_null(domain.description),
                    target_domain += is_null(domain.type),
                    target_domain += is_null(domain.length),
                    target_domain += is_null(domain.char_length),
                    target_domain += is_null(domain.precision),
                    target_domain += is_null(domain.scale),
                    target_domain += is_null(domain.width),
                    target_domain += is_null(domain.align),

                    # Props
                    target_domain += 'TRUE' if domain.show_null else 'FALSE',
                    target_domain += 'TRUE' if domain.show_lead_nulls else 'FALSE',
                    target_domain += 'TRUE' if domain.thousands_separator else 'FALSE',
                    target_domain += 'TRUE' if domain.summable else 'FALSE',
                    target_domain += 'TRUE' if domain.case_sensitive else 'FALSE',

                    self.connection.execute(DML_INSERT_TEMP_DOMAIN, target_domain)

        # Уникализируем временные домены и заполняем таблицу dbd$domains
        self.cursor.executescript(DML_JOIN_AND_SAVE_DOMAINS)

    def __generate_tables(self):
        # SQL-константы
        
        DML_INSERT_TABLE = """
            INSERT INTO dbd$tables (
                schema_id,
                name,
                description,
                can_add,
                can_edit,
                can_delete,
                temporal_mode,
                means)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """

        for table in self.schema.tables:
            target_table = ()
            target_table += "",  # schema_id
            target_table += is_null(table.name),
            target_table += is_null(table.description),

            # Props
            target_table += 'TRUE' if table.can_add else 'FALSE',
            target_table += 'TRUE' if table.can_edit else 'FALSE',
            target_table += 'TRUE' if table.can_delete else 'FALSE',

            target_table += is_null(table.temporal_mode),  # temporal_mode
            target_table += is_null(table.means),  # means

            self.connection.execute(DML_INSERT_TABLE, target_table)

    def __generate_fields(self):
        # SQL-константы

        SQL_CREATE_TEMP_FIELDS = """
            DROP TABLE IF EXISTS temp_dbd$fields;
            CREATE TEMP TABLE temp_dbd$fields (
                id integer primary key autoincrement default(null),
                t_id varchar not null,
                position integer not null,
                name varchar not null,
                russian_short_name varchar not null,
                description varchar default(null),
                d_id varchar not null,
                d_description varchar default(null),  -- описание
                d_data_type_id integer not null,      -- идентификатор типа (dbd$data_types)
                d_length integer default(null),       -- длина
                d_char_length integer default(null),  -- длина в символах
                d_precision integer default(null),    -- точность
                d_scale integer default(null),        -- количество знаков после запятой
                d_width integer default(null),        -- ширина визуализации в символах
                d_align char default(null),           -- признак выравнивания
                d_show_null boolean default(null),    -- нужно показывать нулевое значение?
                d_show_lead_nulls boolean default(null),      -- следует ли показывать лидирующие нули?
                d_thousands_separator boolean default(null),  -- нужен ли разделитель тысяч?
                d_summable boolean default(null),             -- признак того, что поле является суммируемым
                d_case_sensitive boolean default(null),       --
                can_input boolean default(null),
                can_edit boolean default(null),
                show_in_grid boolean default(null),
                show_in_details boolean default(null),
                is_mean boolean default(null),
                autocalculated boolean default(null),
                required boolean default(null)
            );
            """

        DML_INSERT_TEMP_FIELD = """
            INSERT INTO temp_dbd$fields (
                t_id,
                position,
                name,
                russian_short_name,
                description,
                d_id,
                d_description,
                d_data_type_id,
                d_length,
                d_char_length,
                d_precision,
                d_scale,
                d_width,
                d_align,
                d_show_null,
                d_show_lead_nulls,
                d_thousands_separator,
                d_summable,
                d_case_sensitive,
                can_input,
                can_edit,
                show_in_grid,
                show_in_details,
                is_mean,
                autocalculated,
                required)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

        DML_JOIN_AND_SAVE_FIELDS = """
            INSERT INTO dbd$fields (
                table_id,
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
             )
            SELECT
                dbd$tables.id table_id,
                temp_dbd$fields.position,
                temp_dbd$fields.name,
                temp_dbd$fields.russian_short_name,
                temp_dbd$fields.description,
                dbd$domains.id domain_id,
                temp_dbd$fields.can_input,
                temp_dbd$fields.can_edit,
                temp_dbd$fields.show_in_grid,
                temp_dbd$fields.show_in_details,
                temp_dbd$fields.is_mean,
                temp_dbd$fields.autocalculated,
                temp_dbd$fields.required
            FROM temp_dbd$fields, dbd$domains, dbd$tables
            WHERE temp_dbd$fields.t_id = dbd$tables.name
                AND temp_dbd$fields.d_id IS dbd$domains.name
                AND temp_dbd$fields.d_description IS dbd$domains.description
                AND temp_dbd$fields.d_length IS dbd$domains.length
                AND temp_dbd$fields.d_char_length IS dbd$domains.char_length
                AND temp_dbd$fields.d_precision IS dbd$domains.precision
                AND temp_dbd$fields.d_scale IS dbd$domains.scale
                AND temp_dbd$fields.d_width IS dbd$domains.width
                AND temp_dbd$fields.d_align IS dbd$domains.align
                AND temp_dbd$fields.d_show_null IS dbd$domains.show_null
                AND temp_dbd$fields.d_show_lead_nulls IS dbd$domains.show_lead_nulls
                AND temp_dbd$fields.d_thousands_separator IS dbd$domains.thousands_separator
                AND temp_dbd$fields.d_summable IS dbd$domains.summable
                AND temp_dbd$fields.d_case_sensitive IS dbd$domains.case_sensitive;
            """

        self.cursor.executescript(SQL_CREATE_TEMP_FIELDS)

        for table in self.schema.tables:
            for field in table.fields:
                field_index = table.fields.index(field) + 1
                target_field = ()
                target_field += table.name,
                target_field += field_index,
                target_field += is_null(field.name),
                target_field += is_null(field.rname),
                target_field += is_null(field.description),

                # Собираем свойства домена поля
                # Временная таблица полей содержит всю сигнатуру их домена для того, чтобы
                # В dbd$fields каждое поле ссылалось на уникальный домен
                if field.domain is not None:
                    domain = field.domain
                    target_field += domain.name,
                    target_field += is_null(domain.description),
                    target_field += is_null(domain.type),
                    target_field += is_null(domain.length),
                    target_field += is_null(domain.char_length),
                    target_field += is_null(domain.precision),
                    target_field += is_null(domain.scale),
                    target_field += is_null(domain.width),
                    target_field += is_null(domain.align),

                    # Props
                    target_field += 'TRUE' if domain.show_null else 'FALSE',
                    target_field += 'TRUE' if domain.show_lead_nulls else 'FALSE',
                    target_field += 'TRUE' if domain.thousands_separator else 'FALSE',
                    target_field += 'TRUE' if domain.summable else 'FALSE',
                    target_field += 'TRUE' if domain.case_sensitive else 'FALSE',
                else:
                    target_field += "",
                    target_field += "",
                    target_field += "",
                    target_field += "",
                    target_field += "",
                    target_field += "",
                    target_field += "",
                    target_field += "",
                    target_field += "",
                    target_field += "",
                    target_field += "",
                    target_field += "",
                    target_field += "",
                    target_field += "",

                # Props
                target_field += 'TRUE' if field.can_input else 'FALSE',
                target_field += 'TRUE' if field.can_edit else 'FALSE',
                target_field += 'TRUE' if field.show_in_grid else 'FALSE',
                target_field += 'TRUE' if field.show_in_details else 'FALSE',
                target_field += 'TRUE' if field.is_mean else 'FALSE',
                target_field += 'TRUE' if field.autocalculated else 'FALSE',
                target_field += 'TRUE' if field.required else 'FALSE',

                self.connection.execute(DML_INSERT_TEMP_FIELD, target_field)

        # Заполняем таблицу dbd$fields
        # При заполнении в поле domain_id записывается id уникального домена из таблицы dbd$domains
        self.cursor.executescript(DML_JOIN_AND_SAVE_FIELDS)

    def __generate_indexes(self):
        # SQL-константы

        SQL_CREATE_TEMP_INDEXES = """
            DROP TABLE IF EXISTS temp_dbd$indexes;
            CREATE TEMP TABLE temp_dbd$indexes (
                id integer primary key autoincrement default(null),
                t_name varchar not null,
                name varchar default(null),
                local boolean default(0),
                kind char default(null)
            );
            """

        SQL_CREATE_TEMP_INDEXES_DETAILS = """
        DROP TABLE IF EXISTS temp_dbd$index_details;
        CREATE TEMP TABLE temp_dbd$index_details (
            id integer primary key autoincrement default(null),
            index_name varchar not null,
            position integer not null,
            field_name varchar default(null),
            expression varchar default(null),
            descend boolean default(null),
            tab_name varchar not null
        )
        """

        DML_ADD_TEMP_INDEX = """
        INSERT INTO temp_dbd$indexes (
            t_name,
            name,
            local,
            kind)
        VALUES (?, ?, ?, ?);
        """

        DML_ADD_TEMP_INDEX_DETAIL = """
        INSERT INTO temp_dbd$index_details (
            index_name,
            position,
            field_name,
            expression,
            descend,
            tab_name)
        VALUES (?, ?, ?, ?, ?, ?)
        """

        DML_JOIN_AND_SAVE_INDEXES = """
        INSERT INTO dbd$indices
            SELECT
                null,
                dbd$tables.id table_id,
                temp_dbd$indexes.name,
                temp_dbd$indexes.local,
                temp_dbd$indexes.kind
            FROM temp_dbd$indexes
            LEFT JOIN dbd$tables ON temp_dbd$indexes.t_name = dbd$tables.name;

        INSERT INTO dbd$index_details
            SELECT
                null,
                temp_dbd$indexes.id,
                temp_dbd$index_details.position,
                dbd$fields.id,
                temp_dbd$index_details.expression,
                temp_dbd$index_details.descend
            FROM temp_dbd$index_details
            LEFT JOIN temp_dbd$indexes ON temp_dbd$index_details.index_name = temp_dbd$indexes.name
            LEFT JOIN dbd$tables ON temp_dbd$index_details.tab_name = dbd$tables.name
            LEFT JOIN dbd$fields ON (temp_dbd$index_details.field_name = dbd$fields.name) AND (dbd$fields.table_id = dbd$tables.id);
        """

        DELETE_TEMP_INDEXES_NAMES = """
            UPDATE dbd$indices
            SET name=NULL
            WHERE name LIKE 'temp_%';
        """

        self.cursor.executescript(SQL_CREATE_TEMP_INDEXES)
        self.cursor.executescript(SQL_CREATE_TEMP_INDEXES_DETAILS)

        for table in self.schema.tables:
            for index in table.indexes:

                # Получаем имя индекса, либо создаём временное
                name = index.name
                if name is None:
                    name = self.__get_temp_index_name()

                target_index, target_index_detail = (), ()
                target_index += table.name,
                target_index += name,
                target_index += 'TRUE' if index.local is not None else 'FALSE',

                # Props
                if index.uniqueness is not None:
                    target_index += 'U',
                elif index.fulltext is not None:
                    target_index += 'T',
                else:
                    target_index += '',

                self.cursor.execute(DML_ADD_TEMP_INDEX, target_index)

                # Позиция индекса
                position = table.indexes.index(index) + 1

                target_index_detail += name,
                target_index_detail += position,
                target_index_detail += is_null(index.field),
                target_index_detail += is_null(index.expression),

                target_index_detail += 'TRUE' if index.descend is not None else 'FALSE',

                target_index_detail += is_null(table.name),
                
                self.cursor.execute(DML_ADD_TEMP_INDEX_DETAIL, target_index_detail)

        # Заполняем таблицу dbd$indices и удаляем временные имена
        self.cursor.executescript(DML_JOIN_AND_SAVE_INDEXES)
        self.cursor.executescript(DELETE_TEMP_INDEXES_NAMES)

    def __generate_constraints(self):
        # SQL-константы

        SQL_CREATE_TEMP_CONSTRAINTS = """
            DROP TABLE IF EXISTS temp_dbd$constraints;
            CREATE TEMP TABLE temp_dbd$constraints (
                id integer primary key autoincrement default (null),
                table_name varchar not null,
                constraint_name varchar default(null),
                constraint_type char default(null),
                reference_name varchar default(null),
                unique_key_id integer default(null),
                has_value_edit boolean default(null),
                cascading_delete boolean default(null),
                expression varchar default(null)
            );
            """

        SQL_CREATE_TEMP_CONSTRAINT_DETAILS = """
            DROP TABLE IF EXISTS temp_dbd$constraint_details;
            CREATE TEMP TABLE temp_dbd$constraint_details (
                id integer primary key autoincrement default(null),
                constraint_name varchar not null,
                position integer not null,
                field_name varchar not null default(null),
                tab_name varchar not null
            );
            """

        DML_ADD_TEMP_CONSTRAINT = """
            INSERT INTO temp_dbd$constraints (
                table_name,
                constraint_name,
                constraint_type,
                reference_name,
                unique_key_id,
                has_value_edit,
                cascading_delete,
                expression)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """

        DML_ADD_TEMP_CONSTRAINT_DETAIL = """
            INSERT INTO temp_dbd$constraint_details (
                constraint_name,
                position,
                field_name,
                tab_name)
            VALUES (?, ?, ?, ?);
            """

        DML_JOIN_AND_SAVE_CONSTRAINTS = """
            INSERT INTO dbd$constraints
                SELECT
                null,
                table_id,
                constraint_name,
                constraint_type,
                dbd$tables.id reference_id,
                unique_key_id,
                has_value_edit,
                cascading_delete,
                expression
                FROM
                (SELECT
                    temp_dbd$constraints.id const_id,
                    dbd$tables.id table_id,
                    temp_dbd$constraints.constraint_name,
                    temp_dbd$constraints.constraint_type,
                    temp_dbd$constraints.reference_name,
                    temp_dbd$constraints.unique_key_id,
                    temp_dbd$constraints.has_value_edit,
                    temp_dbd$constraints.cascading_delete,
                    temp_dbd$constraints.expression
                FROM temp_dbd$constraints
                LEFT JOIN dbd$tables ON temp_dbd$constraints.table_name = dbd$tables.name)
                LEFT JOIN dbd$tables ON reference_name = dbd$tables.name;
        
            INSERT INTO dbd$constraint_details
            SELECT
                null,
                temp_dbd$constraints.id const_id,
                temp_dbd$constraint_details.position,
                dbd$fields.id field_id
            FROM temp_dbd$constraint_details
            LEFT JOIN temp_dbd$constraints ON temp_dbd$constraint_details.constraint_name = temp_dbd$constraints.constraint_name
            LEFT JOIN dbd$tables ON temp_dbd$constraint_details.tab_name = dbd$tables.name
            LEFT JOIN dbd$fields ON (temp_dbd$constraint_details.field_name = dbd$fields.name) AND (dbd$fields.table_id = dbd$tables.id)
            """

        DELETE_TEMP_CONSTRAINTS_NAMES = """
                UPDATE dbd$constraints
                SET name=NULL
                WHERE name LIKE 'temp_%';
            """

        self.cursor.executescript(SQL_CREATE_TEMP_CONSTRAINTS)
        self.cursor.executescript(SQL_CREATE_TEMP_CONSTRAINT_DETAILS)

        for table in self.schema.tables:
            for constraint in table.constraints:

                # Получаем имя констрейнта, либо создаём временное
                name = constraint.name
                if name is None:
                    name = self.__get_temp_constraint_name()

                target_constraint, target_constraint_detail = (), ()
                target_constraint += table.name,
                target_constraint += name,
                target_constraint += "P" if "PRIMARY" in constraint.kind else "F",
                target_constraint += is_null(constraint.reference),
                target_constraint += "",

                # Props
                target_constraint += 'TRUE' if constraint.has_value_edit is not None else 'FALSE',

                if constraint.full_cascading_delete is not None:
                    target_constraint += 'TRUE',
                elif constraint.cascading_delete is not None:
                    target_constraint += "FALSE",
                else:
                    target_constraint += "NULL",

                target_constraint += is_null(constraint.expression),
                self.cursor.execute(DML_ADD_TEMP_CONSTRAINT, target_constraint)

                # Позиция констрейнта
                position = table.constraints.index(constraint) + 1

                target_constraint_detail += name,
                target_constraint_detail += position,
                target_constraint_detail += is_null(constraint.items),
                target_constraint_detail += table.name,
                self.cursor.execute(DML_ADD_TEMP_CONSTRAINT_DETAIL, target_constraint_detail)

        # Заполняем таблицу dbd$indices и удаляем временные имена
        self.cursor.executescript(DML_JOIN_AND_SAVE_CONSTRAINTS)
        self.cursor.executescript(DELETE_TEMP_CONSTRAINTS_NAMES)


def is_null(value):
    if value == "" or value is None:
        return ""
    else:
        return value
