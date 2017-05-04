FROM ubuntu:16.04

RUN apt-get update \
    && apt-get -y install openssh-client git python3 python3-pip \
    && rm -rf /var/lib/apt

COPY requirements.txt /
RUN pip3 install -r /requirements.txt && pip3 install coverage
COPY test/ssh/ /ssh/
COPY test/repo /test/repo
COPY commit_report.py /
COPY test/test_commit_report.py /
ADD test/app/entrypoint.sh /

CMD [ "bash", "/entrypoint.sh" ]
