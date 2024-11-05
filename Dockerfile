FROM python:3-slim

RUN apt-get -y update; apt-get -y install curl

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY index.html python_docker_test.sh *.py /app/
EXPOSE 7000

CMD python3 -m http.server 7000

# docker build -t simple-server .
# docker run --rm -it --name simple-server-instance -p 80:7000 simple-server
