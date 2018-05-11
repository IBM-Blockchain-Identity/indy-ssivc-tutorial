ARG imagenamespace
FROM ${imagenamespace}libindy:latest

# Install environment
RUN apt-get update -y && apt-get install -y \
    python3.5 \
    python3-pip \
    python-setuptools \
    python3-nacl

ENV HOME=/app
WORKDIR $HOME

# - Create a Python virtual environment for use by any application to avoid
#   potential conflicts with Python packages preinstalled in the main Python
#   installation.
# - In order to drop the root user, we have to make some directories world
#   writable as OpenShift default security model is to run the container
#   under random UID.
RUN ln -sf /usr/bin/python3 /usr/bin/python
RUN ln -sf /usr/bin/pip3 /usr/bin/pip
RUN pip install virtualenv
RUN virtualenv $HOME

ARG indy_plenum_ver=1.2.237
ARG indy_anoncreds_ver=1.0.32
ARG indy_node_ver=1.2.297
ARG python3_indy_crypto_ver=0.2.0
ARG indy_crypto_ver=0.2.0

RUN apt-get update -y && apt-get install -y \
        indy-plenum=${indy_plenum_ver} \
        indy-anoncreds=${indy_anoncreds_ver} \
        indy-node=${indy_node_ver} \
        python3-indy-crypto=${python3_indy_crypto_ver} \
        libindy-crypto=${indy_crypto_ver} \
        vim
