# Usa una imagen base oficial de Python
FROM python:3.8-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo de requisitos al directorio de trabajo
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación al directorio de trabajo
COPY . .

# Expone el puerto en el que el servidor escuchará
EXPOSE 8000

# Comando para ejecutar Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
