﻿Documentacion de la instalacion del servidor Sismoide
Fecha: 2018-06-04
Autor: Vicente Oyanedel Muñoz [vicente.oyanedel@ing.uchile.cl]

En este archivo se documentan los pasos necesarios para montar el servidor de desarollo y produccion.

Indice:

	1. Contenido
	2. Dependencias
	3. Instalacion y configuracion
	4. Ejecucion y mantencion

1. Contenido

	El servidor fue programado en Python con el framework web Django.
	El codigo se puede encontrar en GitHub: https://github.com/sismoide/server
	
	Django es capaz de servir hacia el internet pero se recomienda complementar con un gestor mas robusto como Apache o NGinx.
	Django se comunica con estos gestores a través de interfaz WSGI o UWSGI.

	He aqui algunos documentos para configuracion:
		https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
		https://gist.github.com/evildmp/3094281
		
		
	1.1. Recursos REST:

		El servidor probee toda su funcionalidad por medio de una API REST. 
		
		Los recursos dispoibles se pueden consultar en:
			``` ./web/templates/docs/docs.html ```
		O accediendo al landing-page del servidor mediante HTTP:
			``` http://URL/ ```

2. Dependencias

	- Python 3.5+
	- PostgreSQL
	- PIP

	Además, hay que instalar los paquetes de Python contenidos en el archivo:
		- ``` ./requirements.txt ```
	Mediante ``` pip install -r <filename> ```

3. Instalacion y configuracion

	3.1. Base de datos

		Pasos de configuracion:

			1. Crear un rol (usuario + contraseña) y una base de datos limpia en PSQL.
			2. Configurar datos de conexión en ``` ./web/web/settings.py ```
			3. Ejecutar ``` python ./web/manage.py makemigrations ``` para estructurar migraciones.
			3. Ejecutar ``` python ./web/manage.py migrate ``` para ejecutar migraciones.
		
	3.2. Creacion de usuarios

		3.2.1. Usuario Administrador

			Este usuario tiene la facultad de acceder al panel de administracion (URL/admin/), desde el cual puede:
				- Crear, ver y modificar datos almacenados en BD
				- Crear usuarios web
				
			Se crea mediante la ejecución en terminal del comando:
				``` python ./web/manage.py createsuperuser ```
			Y siguiendo las instrucciones en pantalla.
			
		3.2.2. Usuario Web:

			Este usuario puede acceder a la plataforma Web de visualizacion y control de datos.
			Este es el tipo de usuario visualizador.
			
			Tiene los siguientes permisos:
				- Acceder al portal web de visualizacion
				- Utilizar todos los recursos REST disponibles en el servidor
			
			El usuario web se crea mediante la ejecucion del comando:
				``` python ./web/manage.py createwebuser ```
			Y siguiendo las instrucciones en pantalla.
			
		3.2.3. Usuario Mobil:

			Este usuario se genera desde la aplicación movil y solo tiene acceso a los recuros rest con prefijo /mobile/ y /map/.

			También se puede generar mediante comando:
                ``` python ./web/manage.py createmobileuser ```
			Y siguiendo las instrucciones en pantalla.

	3.3. Creacion de cuadrantes:

		Para que funcione el sistema debe discretizarse la superficie del pais (Chile) en cuadrados o cuadrantes.
		Hay 2 metodos para generar la discretizacion:
		
			3.3.1. Cargar cuadrantes de respaldo:

				Una vez configurada la BD se puede cargar los datos.
				
				Pasos:

					1. Ubicar archivo 'fixture' llamado 'quadrants.json'.
					2. Cargar fixture al sistema mediante ``` python ./web/manage.py loaddata <fixture-file>```
					
			3.3.2. Generar cuadrantes desde 0:

				Si no funciona, o no se ubica el archivo fixture; se pueden re-generar los cuadrantes mediante el comando:
					``` python ./web/manage.py createquadrants```
					Advertencias:
						- Este comando puede tardar mucho. 
						- Procure no interrumpirlo, dado que puede generar inconsistencias que requieran limpiar la BD.
						
	3.4. Configuracion de lectura de informacion de sismos (QuakeML):

		Para que funcionen los recursos que retornan información de los eventos sismicos se debe configurar el directorio en el cual se encuentran los archivos QuakeML.
		
		La lectura de estos archivos solo soporta directorios locales.
		
		Pasos:

			1. Ingresar a archivo de configuracion del servidor: ``` ./server/web/web/settings.py ```.
			2. Modificar variable QUAKEML_PATH para que apunte a carpeta donde se encuentran los archivos QuakeML.
			
		El servidor comenzará a cargar los archivos a su BD cuando se encienda el servidor web.
		
		Precaución:

			1. Los archvos QuakeML se eliminan del directorio luego de cargarse en la BD.
			2. En la BD solo queda la ultima version del evento sismico. (i.e. se sobre-escribe con la ultima version)

	3.5. Configuracion Nginx:

	    3.5.1. Creacion de ambiente nginx:

	        El archivo ``` nginx.conf ```, dentro del cuerpo de ````http {``` agregar linea:
	            ```
	            include /etc/nginx/sites-enabled/*;
	            ```

	        Ir a ``` /etc/nginx/sites-available/  ```.

	        Notas:

	        * El directorio de nginx puede cambiar, pero es donde esta ``` nginx.conf ```.
	        * Crear carpetas: "sites-{enabled, available}" si no existen.

	        Crear archivo ``` <site-conf-name> ``` en este directorio e ingresar:

            ```
            upstream django_app_Produccion {
              # gunicorn address
              server localhost:<gunicorn-port> fail_timeout=0 fail_timeout=0;
            }

            server {
              listen <gninx-listen-port> default;
              server_name <domain-name>;
              access_log off;

              location / {
                proxy_pass http://localhost:<gunicorn-port>;
                proxy_set_header Host $http_host;
                proxy_set_header X-Real-IP $remote_addr;
                add_header P3P 'CP="ALL DSP COR PSAa PSDa O
            UR NOR ONL UNI COM NAV"';
              }

              location /static/ {
                 alias <BASE-DIR>/web/static/;
                 autoindex on;
              }

              location /route {
                proxy_pass http://localhost:<gunicorn-port>;
              }
            }
            ```

            Crear un 'link' a ``` sites-avaiable ``` con:

            ```
            cd  /etc/nginx/sites-enabled
            sudo ln  -s  -f  /etc/nginx/sites-available/<site-conf-name>
            ```

            Reiniciar Nginx (cerrar main thread con kill)

    3.6. Carga de edificios o hitos al sistema:

        El servidor soporta la carga de archivos adquiridos de ``` http://www.ide.cl/descarga/capas ``` en formato DBF (SHP).

        El script de carga pedirá al usuario ingresar nombres de columnas que son especificos para cada archivo DBF, para extraer los datos del archivo. Lo cual requerirá una inspección de los datos, por parte del usuario, para obtener los nombres de las columnas que incluyen los datos basicos (requeridos): nombre y coordenadas (latitud y longitud en decimales). Además, soporta los datos recomendados: dirección y descripción, que se incluiran en las aplicación movil y web.


4. Ejecucion y mantencion

    4.1. Notas:

        Se recomienda ejecutar servidor en un screen o con su salida a un log-file para leer mensajes del sistema.

	4.2. [Django] Ejecutar servidor desarrollo Django.

		``` python ./web/manage.py runserver 0.0.0.0:<port> ```
		
		Nota:

			1. No se recomienda utilizar solo este servidor Django en producción. Se recomienda complementar con Apache o NGinx.

	4.3. [Nginx] Ejecutar servidor produccion Django + Gunicorn + Nginx

	   4.3.1. Ejecutar Gunicorn

	   Ubicado en ```./web```
	   ``` gunicorn web.wsgi:application --bind 0.0.0.0:<gunicorn-port>```

	   4.3.2. Ejecutar NGinx

	   ``` nginx ```

	   Nota: Tiene que configurarse nginx para escuchar <gunicorn-port>, referirse a seccion 3 para más información.

	
		