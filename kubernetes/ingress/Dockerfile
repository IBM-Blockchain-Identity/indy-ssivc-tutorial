FROM ubuntu

RUN apt update && apt install -y software-properties-common && \
    apt-add-repository ppa:certbot/certbot && apt update && \
    apt install -y certbot

CMD ["/bin/sleep", "10d"]
