FROM ubuntu:16.04

RUN apt-get update \
    && apt-get -y install openssh-server git \
    && rm -rf /var/lib/apt

RUN adduser --disabled-password --gecos 'SSH USER'  git
USER git
RUN install -d -o git -g git -m 700 ~/.ssh
COPY test/ssh/*.pub /home/git/.ssh/
RUN cat ~/.ssh/*.pub > ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys
COPY test/repo /home/git/test.git
WORKDIR /home/git/test.git

ADD test/git-server/entrypoint.sh /
USER root
CMD [ "bash", "/entrypoint.sh" ]

EXPOSE 22