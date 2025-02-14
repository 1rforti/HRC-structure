# Use uma imagem base do Python
FROM python:3.9-slim

# Instale as dependências necessárias
RUN apt-get update && apt-get install -y build-essential python-dev

# Defina o diretório de trabalho
WORKDIR /app

# Copie todos os arquivos do projeto para o diretório de trabalho
COPY . /app

# Instale as dependências do Python
RUN pip install -r requirements.txt

# Comando para iniciar o aplicativo
CMD ["python", "main.py"]
