class Field:	#класс поля
    parameters_order = None  # список имен пар-ров огр для RAM->XML
    name = None
    rname = None
    domain = None  # name of Domain
    props = None
    position = None
    description = None

    def __init__(self, name, position):	#конструктор
        self.parameters_order = []
        if (name is not None) & (name != ""):
            self.name = name
            self.parameters_order.append("name")
        if (position is not None) & (position != ""):
            self.position = int(position)

    def set_name(self, name):
        if (name is not None) & (name != ""):
            self.name = name
            self.parameters_order.append("name")

    def get_name(self):
        return self.name

    def set_rname(self, rname):	#задание эр-нейм???
        if (rname is not None) & (rname != ""):
            self.rname = rname
            self.parameters_order.append("rname")

    def get_rname(self):
        return self.rname

    def set_domain(self, domain):	#задание доменного имени
        if (domain is not None) & (domain != ""):
            self.domain = domain.replace(" ", "_").\
                replace("\\", "_")\
                .replace("-", "_").\
                replace(".", "").\
                replace("/", "_")
            self.parameters_order.append("domain")

    def get_domain(self):
        return self.domain

    def set_props(self, props):	#задание свойств
        props_temp = []	#промежуточный список
        for prop in props.split(","):
            props_temp.append(prop.strip())	#пробелы
        if (props_temp is not None) & (len(props_temp) != 0):	#если список не пустой
            self.parameters_order.append("props")	#добавляем к списку имен параметров ограничений
        props_temp_set = set(props_temp)	#кладём во множество списков
        props_temp.clear()	#очищаем
        for p in props_temp_set:	#идём по множеству списков
            if not (p == ""):	#если список не пустой
                props_temp.append(p)	#добавляем в промеж. список
        self.props = set(props_temp)	#итого имеем готовый список свойств

    def get_props(self):
        return self.props

    def if_prop_exists(self, prop):
        if (prop in self.props):
            return True
        else:
            return False

    def set_description(self, description):
        if (description is not None) & (description != ""):
            self.description = description
            self.parameters_order.append("description")

    def get_description(self):
        return self.description