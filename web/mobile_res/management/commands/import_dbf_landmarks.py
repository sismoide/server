from dbfread import DBF
from django.core.management import BaseCommand

from map.models import LandmarkType, Landmark, Coordinates


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('info: starting dbf loader')

        file_path = input('ingrese ruta a archivo DBF con edificios o hitos a cargar al sistema: ')
        table = DBF(file_path, encoding='utf8')

        landmark_type = input('ingrese nombre corto del tipo de edificio o hitos: ')
        description = input('ingrese descripcion del tipo de edificio o hitos: ')

        print('\ninfo: a continuacion se consultaran nombres de columnas del archivo DBF a parsear')
        print('info: Ingrese nombres de columnas requeridos')

        name_column = input('ingrese nombre de columna que contiene nombre de los hitos: ')
        latitud_column = input('ingrese nombre de columna que contiene latitud (float) de los hitos: ')
        longitud_column = input('ingrese nombre de columna que contiene longitud (float) de los hitos: ')

        print('info: Ingrese nombres de columnas recomendados. <Enter> para omitir.')
        address_column = input(
            'ingrese nombre de columna que contiene direccion postal de los hitos (Enter para omitir campo): ')

        name_contain_type = input(
            'responda con S o N. ¿el nombre del tipo de edificio se encuentra en los nombres de los records?')
        if name_contain_type is "s" or name_contain_type is "S":
            name_contain_type = True
        else:
            name_contain_type = False

        type = LandmarkType.objects.get_or_create(name=landmark_type, description=description)[0]
        print('info: loading records to db')

        if name_contain_type:
            for record in table:
                if landmark_type in record[name_column] or not name_contain_type:
                    name = record[name_column]
                    # remove landmarkType and symbols from name
                    name = name.replace(landmark_type, "")
                    name = name.replace('-', "")
                    name = name.strip()

                    address = None
                    if address_column is not "" or address_column is not None:
                        address = record[address_column]
                    latitude = record[latitud_column]
                    longitude = record[longitud_column]
                    Landmark.objects.create(
                        name=name,
                        address=address,
                        coordinates=Coordinates.objects.get_or_create(
                            latitude=latitude,
                            longitude=longitude
                        )[0],
                        type=type
                    )

        print('info: done loading data into db')
        print('info: thank you for using this tool')
