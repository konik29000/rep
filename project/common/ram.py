# RAM представление базы данных


class Schema:
    def __init__(self):

        self.fulltext_engine = None
        self.version = None
        self.name = None
        self.description = None

        self.domains = []
        self.tables = []

    def get_domain_by_name(self, name):
        for domain in self.domains:
            if domain.name == name:
                return domain
        return None

    def find_table_by_name(self, name):
        # Проверка существования заданной таблицы name
        for table in self.tables:
            if table.name == name:
                return table
        return None


class Domain:
    def __init__(self):
        self.name = None
        self.align = None
        self.type = None
        self.width = None
        self.char_length = None
        self.description = None
        self.precision = None
        self.scale = None
        self.length = None
        self.unnamed = False  # Неименованный домен?

        # Props
        self.show_null = None
        self.show_lead_nulls = None
        self.thousands_separator = None
        self.summable = None
        self.case_sensitive = None

    def __eq__(self, other):
        equal = True
        equal = equal and self.type == other.type
        equal = equal and self.align == other.align
        equal = equal and self.length == other.length
        equal = equal and self.char_length == other.char_length
        equal = equal and self.description == other.description
        equal = equal and self.width == other.width
        equal = equal and self.precision == other.precision
        equal = equal and self.scale == other.scale
        equal = equal and self.show_null == other.show_null
        equal = equal and self.show_lead_nulls == other.show_lead_nulls
        equal = equal and self.thousands_separator == other.thousands_separator
        equal = equal and self.summable == other.summable
        equal = equal and self.case_sensitive == other.case_sensitive
        equal = equal and self.unnamed == other.unnamed
        return equal


class Table:
    def __init__(self):
        self.name = None
        self.description = None
        self.temporal_mode = None
        self.means = None

        self.fields = []
        self.indexes = []
        self.constraints = []

        # Props
        self.can_add = None
        self.can_edit = None
        self.can_delete = None

    def find_field_by_name(self, name):
        for field in self.fields:
            if field.name == name:
                return field
        return None


class Field:
    def __init__(self):
        self.name = None
        self.domain = None
        self.type = None
        self.char_length = None
        self.rname = None
        self.description = None

        # Props
        self.can_input = None
        self.can_edit = None
        self.show_in_grid = None
        self.show_in_details = None
        self.is_mean = None
        self.autocalculated = None
        self.required = None

    def __eq__(self, other):
        equal = True
        equal = equal and self.name == other.type
        equal = equal and self.type == other.type
        equal = equal and self.domain == other.domain
        equal = equal and self.char_length == other.char_length
        equal = equal and self.description == other.description
        equal = equal and self.can_input == other.can_input
        equal = equal and self.can_edit == other.can_edit
        equal = equal and self.show_in_grid == other.show_in_grid
        equal = equal and self.show_in_details == other.show_in_details
        equal = equal and self.is_mean == other.is_mean
        equal = equal and self.autocalculated == other.autocalculated
        equal = equal and self.required == other.required
        equal = equal and self.rname == other.rname
        return equal


class Index:
    def __init__(self):
        self.name = None
        self.field = None
        self.local = None

        # Props
        self.uniqueness = None
        self.fulltext = None

        self.expression = None
        self.kind = None
        self.direction = None
        self.descend = None


class Constraint:
    def __init__(self):
        self.name = None
        self.items = None
        self.kind = None
        self.reference = None
        self.expression = None

        # Props
        self.has_value_edit = None
        self.cascading_delete = None
        self.full_cascading_delete = None
