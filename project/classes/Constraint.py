class Constraint:			#класс ограничений	
# Дескриптор - т.е. класс, который хранит и контролирует атрибуты других классов.
    parameters_order = None	# список имен параметров ограничений, полезных для RAM-> XML
    kind = None			#вид
    items = None  		#имя поля
    reference = None	#имя таблицы
    props = None		#свойства
    position = None		#позиция
    name = None			#имя 

    def __init__(self, kind, position):	#конструктор класса
        self.parameters_order = []		#задаём пустой список параметров ограничений
        if (kind is not None) & (kind != ""):	#если не пустое множество,
            self.kind = kind	#присваеваем его
            self.parameters_order.append("kind")	#и заносим в список
        if (position is not None) | (position != ""):	#если позиция уже задана,
            self.position = int(position)	#конвертируем в числовой формат и присваеваем
	
    def set_kind(self, kind):	#задание вида
        if (kind is not None) & (kind != ""):	#если уже задан
            self.kind = kind	#присваиваем
            self.parameters_order.append("kind")	#и заносим в список ограничений

    def getKind(self):	#вызов значения вида
        return self.kind

    def set_name(self, name):	#задание имени
        if (name is not None) & (name != ""):
            self.name = name
            self.parameters_order.append("name")

    def get_name(self):	#вызов значения имени
        return self.name

    def set_reference(self, reference):	#задание имени таблицы
        if (reference is not None) & (reference != ""):
            self.reference = reference	#присваиваем
            self.parameters_order.append("reference")	#вносим

    def get_reference(self):	#вызов знач. имени таблицы
        return self.reference

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

    def get_props(self): #вызов значения свойств 
        return self.props

    def if_prop_exists(self, prop):	#проверка наличия свойств
        if (prop in self.props):	
            return True
        else:
            return False

    def set_items(self, items):	#поля
        if (items is not None) & (items != ""):	#если значение поля не пустое
            self.items = items	#присваиваем это значение элементу
            self.parameters_order.append("items")	#и добавляем его в список параметров ограничений

    def get_items(self):#вызов значения поля
        return self.items
