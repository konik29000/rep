from xml.dom import minidom	#Minimal DOM Implementation‭ – ‬это упрощённая‭ ‬реализация объектной модели документа‭ (‬Document Object Model,‭ ‬DOM‭)‬.‭ ‬DOM‭ – ‬это интерфейс программирования приложений‭ (‬Application Programming Interface,‭ ‬API‭)‬,‭ ‬рассматривающий XML как древовидную структуру,‭ ‬где каждый узел в дереве есть объект.

from classes.DBDSchema import DBDSchema
from classes.Domain import Domain
from classes.Table import Table
from classes.Field import Field
from classes.Constraint import Constraint
from classes.Index import Index


def create_list_of_objects_from_xml(paths):
    schemas = []	#создаём пустой список схем
    for path in paths:
        doc = minidom.parse(path)
        xml_schema = doc.getElementsByTagName("dbd_schema")[0] #getElementsByTagName()возвращает объекты с их исх. интерфейсом для представления результатов запроса
        schema = DBDSchema(xml_schema.getAttribute("fulltext_engine")) #присв. значение атрибута с именем fulltext_engine в виде строки. Если такого атрибута не существует, возвращается пустая строка, как если бы атрибут не имел значения.
        schema.set_version(xml_schema.getAttribute("version"))	#задаём версию, имя и определение схамы бд
        schema.set_name(xml_schema.getAttribute("name"))
        schema.set_description(xml_schema.getAttribute("description"))

        xml_domains = doc.getElementsByTagName("domain")	#берём список доменных имён 
        for xml_domain in xml_domains:	#идём по списку
            domain_name = xml_domain.getAttribute("name")	#присвоили
            if (schema.get_domain(domain_name) is None):	#если такого дом. имени нет в схеме,то
                domain = Domain(domain_name,xml_domain.getAttribute("type"), False)	#последовательно вызываем все функции его задания
                domain.set_align(xml_domain.getAttribute("align"))
                domain.set_width(xml_domain.getAttribute("width"))
                domain.set_char_length(xml_domain.getAttribute("char_length"))
                domain.set_description(xml_domain.getAttribute("description"))
                domain.set_props(xml_domain.getAttribute("props"))
                domain.set_precision(xml_domain.getAttribute("precision"))
                domain.set_length(xml_domain.getAttribute("length"))
                domain.set_scale(xml_domain.getAttribute("scale"))
                schema.set_domain(domain.name, domain)
		
        xml_tables = doc.getElementsByTagName("table")	#задание данных таблицы
        for xml_table in xml_tables:
            table = Table(xml_table.getAttribute("name"))
            table.set_description(xml_table.getAttribute("description"))
            table.set_props(xml_table.getAttribute("props"))
            table.set_ht_table_flags(xml_table.getAttribute("ht_table_flags"))
            table.set_access_level(xml_table.getAttribute("access_level"))

            xml_fields = xml_table.getElementsByTagName("field")	#зад. дн. полей
            position = 1
            for xml_field in xml_fields:
                field = Field(xml_field.getAttribute("name"), position)
                field.set_rname(xml_field.getAttribute("rname"))

                if ((xml_field.getAttribute("type") is not None) and
                        (xml_field.getAttribute("type") != "")):	#если есть тип
                    domain = Domain("Unnamed_" + xml_table.getAttribute("name") +
                                    "_" + xml_field.getAttribute("name"),
                                    xml_field.getAttribute("type"), True)
                    domain.set_position_for_unnamed(xml_table.getAttribute("name"),
                                                    xml_field.getAttribute("name"))
                    domain.set_align(xml_field.getAttribute("align")) #так же записываем и ост. атрибуты поля
                    domain.set_width(xml_field.getAttribute("width"))
                    domain.set_char_length(xml_field.getAttribute("char_length"))
                    domain.set_description(xml_field.getAttribute("description"))
                    domain.set_props(xml_field.getAttribute("type_props"))
                    domain.set_precision(xml_field.getAttribute("precision"))
                    domain.set_length(xml_field.getAttribute("length"))
                    domain.set_scale(xml_field.getAttribute("scale"))	#после чего добавляем в классы ыхемы и поля это доменное имя
                    schema.set_domain(domain.name, domain)
                    field.set_domain(domain.name)
                else:	#если значения типа нет
                    field.set_domain(xml_field.getAttribute("domain"))	#просто записываем в класс поля доменное имя

                field.set_description(xml_field.getAttribute("description"))	#и остальные атрибуты
                field.set_props(xml_field.getAttribute("props"))
                table.set_field(field.name, field)
                position += 1	#таким образом проходим на след. позицию 
			#повторяем эту процедуру для ограничений
            position = 1
            xml_constraints = xml_table.getElementsByTagName("constraint")
            for xml_constraint in xml_constraints:
                constraint = Constraint(xml_constraint.getAttribute("kind"), position)
                constraint.set_props(xml_constraint.getAttribute("props"))
                constraint.set_reference(xml_constraint.getAttribute("reference"))
                constraint.set_items(xml_constraint.getAttribute("items"))
                table.set_constraint(constraint)
                position += 1
			#и индексов
            position = 1
            xml_indices = xml_table.getElementsByTagName("index")
            for xml_index in xml_indices:
                index = Index(xml_index.getAttribute("field"), position)
                index.set_props(xml_index.getAttribute("props"))
                table.set_index(index)
                position += 1

            schema.set_table(table)	#задаём таблицу 
        schemas.append(schema)	#добавляем схему в список схем
    return schemas	#на выходе имеем этот список
