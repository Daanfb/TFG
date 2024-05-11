# syntax=docker/dockerfile:1

# Imagen base
FROM nvidia/cuda:11.3.1-cudnn8-devel-ubuntu20.04

# Zona horaria
ENV TZ=Europe/Madrid
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Actualiza lista de paquetes
RUN apt-get update && apt-get upgrade -y

# Instala paquetes necesarios
RUN apt-get install -y \
    python3.8 \
    python3-pip \
    python3-dev \
    ffmpeg \
    libsm6 \
    libxext6

# Variables de entorno
RUN echo 'alias [python](https://saturncloud.io/glossary/python)="python3" ' >> ~/.bashrc
RUN echo 'alias pip="pip3" ' >> ~/.bashrc

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia los archivos necesarios al contenedor
COPY requirements.txt .
COPY app.py .
COPY ficheros/ ./ficheros
COPY json/ ./json
COPY highlights/ ./highlights
COPY videos/ ./videos

# Instala las dependecias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto 5555 para que Flask pueda ejecutarse
EXPOSE 5555

# Comando para ejecutar el servidor Flask
CMD ["python3", "app.py"]