class Index:
    field_name = None  # имя поля
    props = None
    position = None
    name = None

    def __init__(self, field_name, position):	#конструктор класса
        if (field_name is not None) & (field_name != ""):
            self.field_name = field_name
        if (position is not None) & (position != ""):
            self.position = int(position)

    def set_field_name(self, field_name):
        if (field_name is not None) & (field_name != ""):
            self.field_name = field_name

    def get_field_name(self):
        return self.field_name

    def set_name(self, name):
        if (name is not None) & (name != ""):
            self.name = name

    def get_name(self):
        return self.name

    def set_props(self, props):	#задание свойств
        props_temp = []	#пром. список
        for prop in props.split(","):
            props_temp.append(prop.strip())
        props_temp_set = set(props_temp)	#задаём св-во
        props_temp.clear()
        for p in props_temp_set:
            if not (p == ""):
                props_temp.append(p)	#добавляем во мн-во списков св-в
        self.props = set(props_temp)

    def get_props(self):
        return self.props

    def if_prop_exists(self, prop):
        if ((self.props is not None) and (prop in self.props)):
            return True
        else:
            return False