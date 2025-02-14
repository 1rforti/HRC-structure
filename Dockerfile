# Use uma imagem base do Python
FROM python:3.9-slim

# Instale as depend�ncias necess�rias
RUN apt-get update && apt-get install -y build-essential python-dev

# Defina o diret�rio de trabalho
WORKDIR /app

# Copie todos os arquivos do projeto para o diret�rio de trabalho
COPY . /app

# Instale as depend�ncias do Python
RUN pip install -r requirements.txt

# Comando para iniciar o aplicativo
CMD ["python", "main.py"]
