import argparse
from Dbdtr import DbdToRam
from rtx import RamToXdb


if __name__ == "__main__":
    program = 'project'
    description = """ DBD в XDB."""
    epilog = ''

    argparser = argparse.ArgumentParser(prog=program, description=description, epilog=epilog)
    argparser.add_argument('-f', '--file', type=str, default='source/task.db',
                           help='Конвертирование DBD -> XDB. Результат - файл .xdb',
                           metavar='file.db - файл DBD-описателя')

    arguments = argparser.parse_args()

    dbd_file = arguments.file  # DBD-файл, поданый на вход

    dbd_parser = DbdToRam(dbd_file)

    ram = dbd_parser.parse()

    xdb_generator = RamToXdb(dbd_file.replace('.db', '.xdb'), ram)
    xdb_generator.generate()

    print("Finished")
