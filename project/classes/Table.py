class Table:
    parameters_order = None  # для RAM->XML
    #fieldsOrder = None # список имен параметров поля
    #constraintsOrder = None # список элементов параметров ограничения
    #indicesOrder = None # список полей параметров индекса
    name = None
    description = None
    props = None
    ht_table_flags = None
    access_level = None
    fields = None  # словарь объектов типа поля
    constraints = None  # список ограничений
    indices = None  # список индексов
    temporal_mode = None	#режим времени
    means = None	#значения

    def __init__(self, name):	#конструктор
        self.fields = {}
        self.constraints = []
        self.indices = []
        self.parameters_order = []
        if (name is not None) & (name != ""):
            self.name = name
            self.parameters_order.append("name")
        #self.constraints_order = []
        #self.fieldsOrder = []
        #self.indicesOrder = []

    def set_name(self, name):
        if (name is not None) & (name != ""):
            self.name = name
            self.parameters_order.append("name")

    def get_name(self):
        return self.name

    def set_description(self, description):
        if (description is not None) & (description != ""):
            self.description = description
            self.parameters_order.append("description")

    def get_description(self):
        return self.description

    def set_props(self, props):
        props_temp = []
        for prop in props.split(","):
            props_temp.append(prop.strip())
        if (props_temp is not None) & (len(props_temp) != 0):
            self.parameters_order.append("props")
        props_temp_set = set(props_temp)
        props_temp.clear()
        for p in props_temp_set:
            if not (p == ""):
                props_temp.append(p)
        self.props = set(props_temp)

    def get_props(self):
        return self.props

    def if_prop_exists(self, prop):
        if (prop in self.props):
            return True
        else:
            return False

    def set_ht_table_flags(self, ht_table_flags ):
        if (ht_table_flags is not None) & (ht_table_flags != ""):
            self.ht_table_flags = ht_table_flags
            self.parameters_order.append("ht_table_flags")

    def get_ht_table_flags(self):
        return self.ht_table_flags

    def set_access_level(self, access_level):
        if (access_level is not None) & (access_level != ""):
            self.access_level = int(access_level)
            self.parameters_order.append("access_level")

    def get_access_level(self):
        return self.access_level

    def set_field(self, field_name, field):
        self.fields[field_name] = field
        #if (self.fields is not None) | (len(self.fields) != 0):
            #self.fields_order.append(field.rname)

    def get_field(self, field_name):
        return self.fields.get(field_name)

    def get_fields(self):
        return self.fields

    def set_constraint(self, constraint):
        self.constraints.append(constraint)
        #self.constraints_order.append(constraint.getItems())

    def get_constraints(self):
        return self.constraints

    def set_index(self, index):
        self.indices.append(index)
        #self.indicesOrder.append(index.getFieldName())

    def get_indices(self):
        return self.indices

    def set_means(self, means):
        if (means is not None) & (means != ""):
            self.means = means
            self.parameters_order.append("means")

    def get_means(self):
        return self.means

    def set_temporal_mode(self, temporal_mode):
        if (temporal_mode is not None) & (temporal_mode != ""):
            self.temporal_mode = temporal_mode
            self.parameters_order.append("temporal_mode")

    def get_temporal_mode(self):
        return self.temporal_mode