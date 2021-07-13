FROM quay.io/centos/centos:stream8


COPY scripts/setup_env.sh /usr/local/bin
RUN chmod +x /usr/local/bin/setup_env.sh
RUN /usr/local/bin/setup_env.sh
COPY scripts/bootstrap_dex.sh /usr/local/bin
RUN chmod +x /usr/local/bin/bootstrap_dex.sh

WORKDIR /opt/

VOLUME [ "/data" ]

CMD [ "bootstrap_dex.sh" ]
