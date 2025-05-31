FROM python:3.9-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de requisitos e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação para o diretório de trabalho
COPY app.py .

# Expõe a porta que a aplicação Dash irá usar
EXPOSE 8050

# Comando para rodar a aplicação usando Gunicorn (servidor WSGI)
# O Gunicorn é recomendado para produção. Para desenvolvimento, você pode usar `python app.py`
CMD ["gunicorn", "-b", "0.0.0.0:8050", "app:server"]

