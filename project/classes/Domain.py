class Domain:	#класс домена
    parameters_order = None  # список имен параметров ограничений, полезных для RAM-> XML
    name = None		#имя 
    type = None		#тип
    align = None	#выравнивание
    width = None	#ширина
    char_length = None	#??? длина символа?
    description = None	#определение
    props = None  #множество свойств
    precision = None	#точность
    scale = None	#масштаб
    length = None	#длина
    unnamed = None	#безвмянная величина???
    position_for_unnamed = None  # список из 2 элементов: 0 - имя таблицы, 1 - поле таблицы

    def __init__(self, name, type, unnamed):	#конструктор
        self.unnamed = unnamed	#поле для поддержки неименованных доменов
        self.parameters_order = []	#задаём пустой сп.им.пар.огр.
        if (name is not None) & (name != ""):	#если есть имя
            self.name = name.replace(" ", "_").\#то задаём ему подобающий вид
                replace("\\", "_")\
                .replace("-", "_").\
                replace(".", "").\
                replace("/", "_")
            self.parameters_order.append("name")	#добавляем в список ипо
        if (type is not None) & (type != ""):	#если есть значение типа
            self.type = type	#присваеваем  
            self.parameters_order.append("type")	#добавляем 

    def set_position_for_unnamed(self, table_name, field_name):
        self.position_for_unnamed = []
        self.position_for_unnamed.append(table_name)
        self.position_for_unnamed.append(field_name)

    def set_name(self, name):	#задание доменного имени
        if (name is not None) & (name != ""):
            self.name = name.replace(" ", "_").\
                replace("\\", "_")\
                .replace("-", "_").\
                replace(".", "").\
                replace("/", "_")
            self.parameters_order.append("name")

    def get_name(self):
        return self.name

    def set_type(self, type):	#задание типа
        if (type is not None) & (type != ""):
            self.type = type
            self.parameters_order.append("type")

    def get_type(self):
        return self.type

    def set_align(self, align):	#задание выравнивания
        if (align is not None) & (align != ""):
            self.align = list(align).pop(0)	#присв. 0-й элемент , удаляя его из списка. ???
            self.parameters_order.append("align")

    def get_align(self):
        return self.align

    def set_width(self, width):	
        if (width is not None) & (width != ""):
            self.width = int(width)
            self.parameters_order.append("width")

    def get_width(self):
        return self.width

    def set_char_length(self, char_length):	#?????????
        if (char_length is not None) & (char_length != ""):
            self.char_length = int(char_length)
            self.parameters_order.append("char_length")

    def get_char_length(self):
        return self.char_length

    def set_description(self, description):	#задание определения
        if (description is not None) & (description != ""):
            self.description = description
            self.parameters_order.append("description")

    def get_description(self):
        return self.description

    def set_props(self, props):	#задание свойств
        props_temp = []		#промежуточный список
        for prop in props.split(","):	#разбиваем строку на список элементов и идём по нему
            props_temp.append(prop.strip())	#и добавляем их в список свойств, удаляя пробелы
        if (props_temp is not None) & (len(props_temp) != 0): #если значение не пусто
            self.parameters_order.append("props")	#добавляем его в список ограничений
        props_temp_set = set(props_temp)	#сохраняем в множестве списков
        props_temp.clear()	#очищаем список
        for p in props_temp_set:	#проверяем элементы множества
            if not (p == ""):		#если не пустой
                props_temp.append(p)#добавляем в промежуточный список
        self.props = set(props_temp)#итого сохраняем множество промежуточных списков как множество свойств


    def get_props(self):	#вызов значения свойства
        return self.props

    def if_prop_exists(self, prop):	#проверка наличия свойства
        if (prop in self.props):
            return True
        else:
            return False

    def set_precision(self, precision):	#задание точности
        if (precision is not None) & (precision != ""):
            self.precision = int(precision)
            self.parameters_order.append("precision")

    def get_precision(self):
        return self.precision

    def set_scale(self, scale):	#задание масштаба
        if (scale is not None) & (scale != ""):
            self.scale = int(scale)
            self.parameters_order.append("scale")

    def get_scale(self):
        return self.scale

    def set_length(self, length):	#задание длины
        if (length is not None) & (length != ""):
            self.length = int(length)#не забыть перевести в инт
            self.parameters_order.append("length")#и добавить в список ипо

    def get_length(self):
        return self.length
