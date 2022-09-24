FROM ubuntu:16.04
MAINTAINER Mari Hernaes <mari.hernaes@gmail.com>
RUN apt-get update && apt-get install -y make vim python3 python3-pip locales bash-completion
RUN sed -i -e 's/# en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8
ENV LANG en_US.UTF-8
RUN pip3 install --upgrade pip
RUN pip3 install sklearn-crfsuite
COPY Makefile Makefile
COPY bashrc bashrc
COPY scripts scripts
CMD ["/bin/bash", "--rcfile", "bashrc"]

# docker build -t mari-hernaes-thesis .
# docker run -it -v /nfs/students/mari-hernaes:/extern/data
#	     --name mari-hernaes-thesis
#            mari-hernaes-thesis
