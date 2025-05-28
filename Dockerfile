# C:\Users\ianes\Desktop\BigData-2025.1\app\DockerFile

FROM python:3.13-slim

# dependências do sistema para compilar mysqlclient
RUN apt-get update && \
    apt-get install -y \
      gcc \
      python3-dev \
      default-libmysqlclient-dev \
      pkg-config && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY ./app /usr/src/app/app
COPY .env /usr/src/app/
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.main:app"]


