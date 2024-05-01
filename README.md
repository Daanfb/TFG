# Introducción
TFG realizado por Daniel Frías Balbuena.

Este repositorio contiene el código necesario para realizar el despliegue del TFG.

## Requisitos

Para poder realizar el despligue se necesita lo siguiente:

- Tener una GPU NVIDIA para poder realizar inferencia del modelo.
- Tener Docker instalado.
- Tener libres los puertos 5554 y 5555.
- Tener los pesos del modelo en la carpeta ficheros, que está dentro del directorio api. Dicho archivo debe ser guardado con el nombre model.pth.tar. Para descargar los pesos visite el siguiente enlace: https://drive.usercontent.google.com/download?id=199mfhGYSuf2bieMAMR1FNn1vwl8qhDKW&export=download&authuser=0

# Pasos

**ADVERTENCIA**: Este proceso puede tardar hasta 30 minutos debido a la cantidad de librerías que han de ser instaladas.

Abrir una terminal ubicada en el directorio principal y ejecutar los siguientes comandos:

1. **docker-compose build**: En el directorio donde se encuentra el archivo *docker-compose.yml* y las carpetas *web* y *api*, ejecutamos este comando para construir las imágenes para cada servicio.
2. **docker-compose up -d**: Una vez se hayan construido las imágenes, iniciamos los contenedores con este comando. Con la bandera *-d* ejecutamos los contenedores en segundo plano.	
3. **docker-compose ps -a**: Con este comando sabremos si los contenedores se encuentran en ejecución.

Una vez realizados dichos pasos correctamente, buscamos en el navegador la ruta *http://localhost:5554*

Cualquier cambio realizado en las carpetas \textit{web} y \textit{api} se muestran automáticamente en el contenedor, y viceversa.

Si queremos ver el log de alguno de los dos contenedores escribimos el comando *docker-compose logs -f [web|api]* donde *-f* es para verlo en tiempo real y *[web|api]* indica que se debe escribir web o api en función del contenedor en el que estamos interesados.

Por otro lado, para parar un contenedor escribimos *docker-compose stop [web|api]*, y para reanudarlo, *docker-compose start [web|api]*.

