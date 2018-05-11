ARG imagenamespace
FROM ${imagenamespace}python-libindy:latest

ENV HOME=/app
WORKDIR $HOME

RUN mkdir -p /app/.indy_client/wallet

COPY ./src/requirements.txt $HOME/

RUN pip install -r requirements.txt

ADD ./src $HOME
ADD ./site_templates $HOME/site_templates
ADD ./docker/docker-entrypoint.sh /usr/local/bin/enter

RUN chgrp -R 0 $HOME /usr/local/bin /app/.indy_client/wallet \
  && chmod -R g+rwx $HOME /usr/local/bin /app/.indy_client/wallet

USER 10001

ENTRYPOINT ["enter"]
