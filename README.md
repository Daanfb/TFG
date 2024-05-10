# Introducción
TFG realizado por Daniel Frías Balbuena.

Este repositorio contiene el código necesario para realizar el despliegue del TFG.

## Requisitos

Para poder realizar el despligue se necesita lo siguiente:

- Disponer de más de 20GB de almacenamiento para los imágenes.
- Tener una GPU NVIDIA y los drivers para poder realizar inferencia del modelo.
- Tener Docker instalado.
- Tener libres los puertos 5554 y 5555.
- Tener los pesos del modelo en la carpeta ficheros, que está dentro del directorio api. Dicho archivo debe ser guardado con el nombre model.pth.tar. Para descargar los pesos visite el siguiente enlace: https://drive.usercontent.google.com/download?id=199mfhGYSuf2bieMAMR1FNn1vwl8qhDKW&export=download&authuser=0

# Instrucciones para realizar la instalación de Docker en Ubuntu 

Instrucciones obtenidas de https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository

`sudo apt-get update`  
`sudo apt-get install ca-certificates curl`  
`sudo install -m 0755 -d /etc/apt/keyrings`  
`sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc`  
`sudo chmod a+r /etc/apt/keyrings/docker.asc`  


`echo \`  
`"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \`  
`$(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \`  
`sudo tee /etc/apt/sources.list.d/docker.list > /dev/null`  
`sudo apt-get update`  
  
`sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin `

### Instalación Nvidia Container Toolkit

Para poder utilizar la GPU en Ubuntu también se necesita Nvidia Container Toolkit

`distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \`  
`      && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \`  
`      && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \`  
`            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \`  
`            sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list`  

`sudo apt-get update`  
`sudo apt-get install -y nvidia-docker2`  
`sudo systemctl restart docker`

# Pasos para el despliegue

**ADVERTENCIA**: Este proceso puede tardar hasta 20 minutos debido a la cantidad de librerías que han de ser instaladas.

Abrir una terminal ubicada en el directorio principal y ejecutar los siguientes comandos:

1. **docker compose build**: En el directorio donde se encuentra el archivo *docker-compose.yml* y las carpetas *web* y *api*, ejecutamos este comando para construir las imágenes para cada servicio.
2. **docker compose up -d**: Una vez se hayan construido las imágenes, iniciamos los contenedores con este comando. Con la bandera *-d* ejecutamos los contenedores en segundo plano.	
3. **docker compose ps**: Con este comando sabremos si los contenedores se encuentran en ejecución.

Una vez realizados dichos pasos correctamente, buscamos en el navegador la ruta *http://localhost:5554*

Cualquier cambio realizado en las carpetas *web* y *api* se muestran automáticamente en el contenedor, y viceversa.

### Otros comandos
A continuación, se muestran otros comandos interesantes:

- **docker compose logs -f [web|api]**: Para ver el log de alguno de los dos contenedores (*-f* para verlo en tiempo real). *[web|api]* indica que se debe escribir web o api en función del contenedor en el que estamos interesados.
- **docker compose stop [web|api]**: Para la ejecución del contenedor.
- **docker compose down**: Para la ejecución de los contenedores y los elimina, al igual, que sus imágenes.
- **docker compose start [web|api]**: Reanuda la ejecución del contenedor.
- **docker compose exec -it [web|api] bin/bash**: Para entrar en la terminal del contenedor.
- **docker system prune --volumes -a**: Elimina los contenedores detenidos, todas las imágenes detenidas, redes que no se usan y volúmenes de persistencia que no están siendo utilizados, ya que cuando se eliminan con los anteriores comandos, se siguen quedando almacenados en el sistema.
