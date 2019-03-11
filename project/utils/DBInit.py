import sqlite3

CURRENT_DBD_VERSION = '3.1'


class DBInitializer:

    file_name = None
    connection = None
    cursor = None

    def __init__(self, file_name):
        self.file_name = file_name
        self.connection = sqlite3.connect(self.file_name)

    # TODO:
    def init_database(self):
        self.cursor = self.connection.cursor()
        self.cursor.execute("pragma foreign_keys=on;")
        self.cursor.execute("begin transaction;")

        self.create_schemas_table()
        self.create_domains_table()
        self.create_tables_table()
        self.create_fields_table()
        self.create_settings_table()
        self.create_constraints_table()
        self.create_constraint_details_table()
        self.create_indices_table()
        self.create_index_details_table()
        self.create_data_types_table()
        self.insert_into_data_types_and_settings()
        self.create_view_fields()
        self.create_view_domains()
        self.create_view_constraints()
        self.create_view_indices()

        self.connection.commit()
        self.cursor.close()

    def create_schemas_table(self):
        self.cursor.execute(
            """create table dbd$schemas (
            id integer primary key autoincrement not null,
            name varchar not null,
            fulltext_engine varchar default(null),
            version varchar default(null),
            description varchar default(null)
            );"""
        )

    def create_domains_table(self):
        self.cursor.execute(
            """create table dbd$domains (
               id  integer primary key autoincrement not null,
               name varchar default(null),  -- имя домена
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
               case_sensitive boolean default(null),       -- признак необходимости регистронезависимого поиска для поля
               uuid varchar unique default(null) COLLATE NOCASE -- уникальный идентификатор домена
             );""")
        self.cursor.execute(
            """create index "idx.FZX832TFV" on dbd$domains(data_type_id);"""
        )
        self.cursor.execute(
            """create index "idx.4AF9IY0XR" on dbd$domains(uuid);"""
        )

    def create_tables_table(self):
        self.cursor.execute(
            """create table dbd$tables (
               id integer primary key autoincrement not null,
               schema_id integer not null,      -- идетификатор схемы (dbd$schemas)
               name varchar,                  -- имя таблицы
               description varchar default(null),    -- описание
               can_add boolean default(null),        -- разрешено ли добавление в таблицу
               can_edit boolean default(null),       -- разрешено ли редактирование  таблице?
               can_delete boolean default(null),     -- разрешено ли удаление в таблице
               ht_table_flags varchar default(null),
               access_level integer default(null),
               temporal_mode varchar default(null),  -- временная таблица или нет? Если временная, то какого типа?
               means varchar default(null),          -- шаблон описания записи таблицы
               uuid varchar unique default(null) COLLATE NOCASE  -- уникальный идентификатор таблицы
            );""")
        self.cursor.execute(
            """create index "idx.GCOFIBEBJ" on dbd$tables(name);"""
        )
        self.cursor.execute(
            """create index "idx.2J02T9LQ7" on dbd$tables(uuid);"""
        )

    def create_fields_table(self):
        self.cursor.execute(
            """create table dbd$fields (
               id integer primary key autoincrement default(null),
               table_id integer not null,             -- идентификатор таблицы (dbd$tables)
               position integer not null,             -- номер поля в таблице (для упорядочивания полей)
               name varchar not null,                 -- латинское имя поля (будет использовано в схеме Oracle)
               russian_short_name varchar not null,   -- русское имя поля для отображения пользователю в интерактивных режимах
               description varchar default(null),     -- описание
               domain_id integer not null,            -- идентификатор типа поля (dbd$domains)
               can_input boolean default(null),       -- разрешено ли пользователю вводить значение в поле?
               can_edit boolean default(null),        -- разрешено ли пользователю изменять значение в поле?
               show_in_grid boolean default(null),    -- следует ли отображать значение поля в браузере таблицы?
               show_in_details boolean default(null), -- следует ли отображать значение поля в полной информации о записи таблицы?
               is_mean boolean default(null),         -- является ли поле элементом описания записи таблицы?
               autocalculated boolean default(null),  -- признак того, что значение в поле вычисляется программным кодом
               required boolean default(null),        -- признак того, что поле дорлжно быть заполнено
               uuid varchar unique default(null) COLLATE NOCASE -- уникальный идентификатор поля
           );""")
        self.cursor.execute(
           """create index "idx.7UAKR6FT7" on dbd$fields(table_id);"""
        )
        self.cursor.execute(
            """create index "idx.7HJ6KZXJF" on dbd$fields(position);"""
        )
        self.cursor.execute(
           """create index "idx.74RSETF9N" on dbd$fields(name);"""
        )
        self.cursor.execute(
            """create index "idx.6S0E8MWZV" on dbd$fields(domain_id);"""
        )
        self.cursor.execute(
            """create index "idx.88KWRBHA7" on dbd$fields(uuid);"""
        )

    def create_settings_table(self):
        self.cursor.execute(
            """create table dbd$settings (
               key varchar primary key not null,
               value varchar,
               valueb BLOB
           );"""
        )

    def create_constraints_table(self):
        self.cursor.execute(
            """create table dbd$constraints (
               id integer primary key autoincrement default (null),
               table_id integer not null,                           -- идентификатор таблицы (dbd$tables)
               name varchar default(null),                          -- имя ограничения
               constraint_type char default(null),                  -- вид ограничения
               reference integer default(null),        -- идентификатор таблицы (dbd$tables), на которую ссылается внешний ключ
               unique_key_id integer default(null),    -- (опционально) идентификатор ограничения (dbd$constraints) таблицы, на которую ссылается внешний ключ (*1*)
               has_value_edit boolean default(null),   -- признак наличия поля ввода ключа
               cascading_delete boolean default(null), -- признак каскадного удаления для внешнего ключа
               expression varchar default(null),       -- выражение для контрольного ограничения
               uuid varchar unique default(null) COLLATE NOCASE -- уникальный идентификатор ограничения
           );""")
        self.cursor.execute(
           """create index "idx.6F902GEQ3" on dbd$constraints(table_id);"""
        )
        self.cursor.execute(
            """create index "idx.6SRYJ35AJ" on dbd$constraints(name);"""
        )
        self.cursor.execute(
            """create index "idx.62HLW9WGB" on dbd$constraints(constraint_type);"""
        )
        self.cursor.execute(
            """create index "idx.5PQ7Q3E6J" on dbd$constraints(reference);"""
        )
        self.cursor.execute(
            """create index "idx.92GH38TZ4" on dbd$constraints(unique_key_id);"""
        )
        self.cursor.execute(
            """create index "idx.6IOUMJINZ" on dbd$constraints(uuid);"""
        )

    def create_constraint_details_table(self):
        self.cursor.execute(
            """create table dbd$constraint_details (
               id integer primary key autoincrement default(null),
               constraint_id integer not null,          -- идентификатор ограничения (dbd$constraints)
               position integer not null,               -- номер элемента ограничения
               field_id integer not null default(null)  -- идентификатор поля (dbd$fields) в таблице, для которой определено ограничение
           );""")
        self.cursor.execute(
           """create index "idx.5CYTJWVWR" on dbd$constraint_details(constraint_id);"""
        )
        self.cursor.execute(
            """create index "idx.507FDQDMZ" on dbd$constraint_details(position);"""
        )
        self.cursor.execute(
            """create index "idx.4NG17JVD7" on dbd$constraint_details(field_id);"""
        )

    def create_indices_table(self):
        self.cursor.execute(
            """create table dbd$indices (
               id integer primary key autoincrement default(null),
               table_id integer not null,                          -- идентификатор таблицы (dbd$tables)
               name varchar default(null),                         -- имя индекса
               local boolean default(0),                           -- показывает тип индекса: локальный или глобальный
               kind char default(null),                            -- вид индекса (простой/уникальный/полнотекстовый)
               uuid varchar unique default(null) COLLATE NOCASE         -- уникальный идентификатор индекса
           );""")
        self.cursor.execute(
           """create index "idx.12XXTJUYZ" on dbd$indices(table_id);"""
        )
        self.cursor.execute(
            """create index "idx.6G0KCWN0R" on dbd$indices(name);"""
        )
        self.cursor.execute(
            """create index "idx.FQH338PQ7" on dbd$indices(uuid);"""
        )

    def create_index_details_table(self):
        self.cursor.execute(
            """create table dbd$index_details (
               id integer primary key autoincrement default(null),
               index_id integer not null,                          -- идентификатор индекса (dbd$indices)
               position integer not null,                          -- порядковый номер элемента индекса
               field_id integer default(null),                     -- идентификатор поля (dbd$fields), участвующего в индексе
               expression varchar default(null),                   -- выражение для индекса
               descend boolean default(null)                       -- направление сортировки
           );""")
        self.cursor.execute(
           """create index "idx.H1KFOWTCB" on dbd$index_details(index_id);"""
        )
        self.cursor.execute(
            """create index "idx.BQA4HXWNF" on dbd$index_details(field_id);"""
        )

    def create_data_types_table(self):
        self.cursor.execute(
            """create table dbd$data_types (
               id integer primary key autoincrement, -- идентификатор типа
               type_id varchar unique not null       -- имя типа
           );"""
        )

    def insert_into_data_types_and_settings(self):
        self.insert_data_type('STRING')
        self.insert_data_type('SMALLINT')
        self.insert_data_type('INTEGER')
        self.insert_data_type('WORD')
        self.insert_data_type('BOOLEAN')
        self.insert_data_type('FLOAT')
        self.insert_data_type('CURRENCY')
        self.insert_data_type('BCD')
        self.insert_data_type('FMTBCD')
        self.insert_data_type('DATE')
        self.insert_data_type('TIME')
        self.insert_data_type('DATETIME')
        self.insert_data_type('TIMESTAMP')
        self.insert_data_type('BYTES')
        self.insert_data_type('VARBYTES')
        self.insert_data_type('BLOB')
        self.insert_data_type('MEMO')
        self.insert_data_type('GRAPHIC')
        self.insert_data_type('FMTMEMO')
        self.insert_data_type('FIXEDCHAR')
        self.insert_data_type('WIDESTRING')
        self.insert_data_type('LARGEINT')
        self.insert_data_type('COMP')
        self.insert_data_type('ARRAY')
        self.insert_data_type('FIXEDWIDECHAR')
        self.insert_data_type('WIDEMEMO')
        self.insert_data_type('CODE')
        self.insert_data_type('RECORDID')
        self.insert_data_type('SET')
        self.insert_data_type('PERIOD')
        self.insert_data_type('BYTE')

        self.cursor.execute(
              """insert into dbd$settings(key, value) values ('dbd.version', '%(dbd_version)s');
           """ % {'dbd_version': CURRENT_DBD_VERSION}
        )

    def insert_data_type(self, value):
        self.cursor.execute(
            """insert into dbd$data_types(type_id) values ('%(value)s');
            """ % {'value' : value}
        )

    def create_view_fields(self):
        self.cursor.execute(
            """create view dbd$view_fields as
           select
             dbd$schemas.name "schema",
             dbd$tables.name "table",
             dbd$fields.position "position",
             dbd$fields.name "name",
             dbd$fields.russian_short_name "russian_short_name",
             dbd$fields.description "description",
             dbd$data_types.type_id "type_id",
             dbd$domains.length "length",
             dbd$domains.char_length,
             dbd$domains.width "width",
             dbd$domains.align "align",
             dbd$domains.precision "precision",
             dbd$domains.scale "scale",
             dbd$domains.show_null "show_null",
             dbd$domains.show_lead_nulls "show_lead_nulls",
             dbd$domains.thousands_separator "thousands_separator",
             dbd$domains.summable,
             dbd$domains.case_sensitive "case_sensitive",
             dbd$fields.can_input "can_input",
             dbd$fields.can_edit "can_edit",
             dbd$fields.show_in_grid "show_in_grid",
             dbd$fields.show_in_details "show_in_details",
             dbd$fields.is_mean "is_mean",
             dbd$fields.autocalculated "autocalculated",
             dbd$fields.required "required"
           from dbd$fields
             inner join dbd$tables on dbd$fields.table_id = dbd$tables.id
             inner join dbd$domains on dbd$fields.domain_id = dbd$domains.id
             inner join dbd$data_types on dbd$domains.data_type_id = dbd$data_types.id
             Left Join dbd$schemas On dbd$tables.schema_id = dbd$schemas.id
           order by
             dbd$tables.name,
             dbd$fields.position;"""
        )

    def create_view_domains(self):
        self.cursor.execute(
            """create view dbd$view_domains as
           select
             dbd$domains.id,
             dbd$domains.name,
             dbd$domains.description,
             dbd$data_types.type_id,
             dbd$domains.length,
             dbd$domains.char_length,
             dbd$domains.width,
             dbd$domains.align,
             dbd$domains.summable,
             dbd$domains.precision,
             dbd$domains.scale,
             dbd$domains.show_null,
             dbd$domains.show_lead_nulls,
             dbd$domains.thousands_separator,
             dbd$domains.case_sensitive "case_sensitive"
           from dbd$domains
             inner join dbd$data_types on dbd$domains.data_type_id = dbd$data_types.id
           order by dbd$domains.id;"""
        )

    def create_view_constraints(self):
        self.cursor.execute(
            """create view dbd$view_constraints as
           select
             dbd$constraints.id "constraint_id",
             dbd$constraints.constraint_type "constraint_type",
             dbd$constraint_details.position "position",
             dbd$schemas.name "schema",
             dbd$tables.name "table_name",
             dbd$fields.name "field_name",
             "references".name "reference"
           from
             dbd$constraint_details
             inner join dbd$constraints on dbd$constraint_details.constraint_id = dbd$constraints.id
             inner join dbd$tables on dbd$constraints.table_id = dbd$tables.id
             left join dbd$tables "references" on dbd$constraints.reference = "references".id
             left join dbd$fields on dbd$constraint_details.field_id = dbd$fields.id
             Left Join dbd$schemas On dbd$tables.schema_id = dbd$schemas.id
           order by
             constraint_id, position;"""
        )

    def create_view_indices(self):
        self.cursor.execute(
            """create view dbd$view_indices as
           select
             dbd$indices.id "index_id",
             dbd$indices.name as index_name,
             dbd$schemas.name "schema",
             dbd$tables.name as table_name,
             dbd$indices.local,
             dbd$indices.kind,
             dbd$index_details.position,
             dbd$fields.name as field_name,
             dbd$index_details.expression,
             dbd$index_details.descend
           from
             dbd$index_details
             inner join dbd$indices on dbd$index_details.index_id = dbd$indices.id
             inner join dbd$tables on dbd$indices.table_id = dbd$tables.id
             left join dbd$fields on dbd$index_details.field_id = dbd$fields.id
             Left Join dbd$schemas On dbd$tables.schema_id = dbd$schemas.id
           order by
             dbd$tables.name, dbd$indices.name, dbd$index_details.position;"""
        )
