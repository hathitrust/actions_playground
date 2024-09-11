FROM python:3-slim

COPY index.html /
EXPOSE 7000

CMD python3 -m http.server 7000

# docker build -t simple-server .
# docker run --rm -it --name simple-server-instance -p 80:7000 simple-server
