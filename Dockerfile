FROM alpine:latest
LABEL org.opencontainers.image.description="This is a sample test docker container that does absolutely nothing."
# Apline has both an arm and amd image
CMD [ "echo", "Hello World X Platform!!!!!!" ]