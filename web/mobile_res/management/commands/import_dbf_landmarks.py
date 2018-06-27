from dbfread import DBF
from django.core.management import BaseCommand

from map.models import LandmarkType, Landmark, Coordinates


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('info: starting dbf loader')

        file_path = input('ingrese ruta a archivo DBF con edificios o hitos a cargar al sistema: ')
        landmark_type = input('ingrese nombre corto del tipo de edificio o hitos: ')
        description = input('ingrese descripcion del tipo de edificio o hitos: ')

        type = LandmarkType.objects.get_or_create(name=landmark_type, description=description)[0]
        print('info: loading records to db')
        with DBF(file_path, encoding='utf8', load=True) as table:
            for record in table:
                if landmark_type in record['NOMBRE']:
                    name = record['NOMBRE']
                    # remove landmarkType and symbols from name
                    name = name.replace(type, "")
                    name = name.replace('-', "")
                    name = name.strip()

                    address = record['DIRECCION_']
                    latitude = record['LATITUD_Y_']
                    longitude = record['LONGITUD_1']
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
