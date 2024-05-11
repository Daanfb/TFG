# syntax=docker/dockerfile:1

# Imagen de Nginx
FROM nginx:latest

# Copia los archivos en la carpeta de trabajo
COPY ./ /usr/share/nginx/html

# Expone el puerto 80
EXPOSE 80

# Comando para ejecutar el servidor Nginx
CMD ["nginx", "-g", "daemon off;"]