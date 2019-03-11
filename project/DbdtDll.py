import argparse	#для обработки аргументов (параметров, ключей) командной строки
from Dbdtr import DbdToRam		#содержит Парсер ".db" файла
from rtDdl import RamToPgDdl	#сод. ген. элементов бд и преобразование типов


if __name__ == "__main__":
    program = 'project'
    description = """Программа для генерации DDL для PostgreSQL из DBD"""
    #epilog = ''

    #argparser = argparse.ArgumentParser(prog=program, description=description, epilog=epilog)
	argparser = argparse.ArgumentParser(prog=program, description=description)
    argparser.add_argument('-f', '--file', type=str, default='source/task.db',
                           help='Конвертирование DBD -> DDL для PostgreSQL. Результат - файл .Ddl',
                           metavar='file.db - файл DBD-описателя')

    arguments = argparser.parse_args()

    dbd_file = arguments.file  # на вход подаём DBD ФАЙЛ
    dbd_parser = DbdToRam(dbd_file)	
    ram = dbd_parser.parse()	# получаем RAM-представление
	#и уже его преобразуем в Ddl
	#self.filename = file (из rtDdl)
    Ddl_generator = RamToPgDdl(dbd_file.replace('.db', '.Ddl'), ram)	
    Ddl_generator.generate()	

    print("done")
