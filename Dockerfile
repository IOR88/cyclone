FROM ubuntu:bionic
#RUN apt-get update

#################
# POSGRESQL
#################
RUN apt-get -y install gnupg2 wget

# Add the PostgreSQL PGP key to verify their Debian packages.
# It should be the same key as https://www.postgresql.org/media/keys/ACCC4CF8.asc
RUN wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O- | apt-key add -

RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ bionic-pgdg main" > /etc/apt/sources.list.d/pgdg.list
RUN apt-get update

RUN apt-get install -y software-properties-common postgresql-10 postgresql-client-10 postgresql-contrib-10

# Run the rest of the commands as the ``postgres`` user created by the ``postgres`` package when it was ``apt-get installed``
USER postgres

RUN /etc/init.d/postgresql start &&\
    psql --command "CREATE USER admin WITH LOGIN PASSWORD '1234';" &&\
    createdb -O admin cyclone

## Adjust PostgreSQL configuration so that remote connections to the
## database are possible.
#RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/10/main/pg_hba.conf
#
#RUN echo "listen_addresses='*'" >> /etc/postgresql/10/main/postgresql.conf
#
## Expose the PostgreSQL port
#EXPOSE 5432
#
# Add VOLUMEs to allow backup of config, logs and databases
VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]


######################
# PYTHON AND SCRAPY
######################
RUN apt-get -y install python3-pip python3-dev build-essential
RUN pip3 install -y virtualenv virtualenvwrapper
RUN pip3 install -y --upgrade pip

RUN mkdir /home/cyclone
RUN mkdir /home/cyclone/src
RUN mkdir /home/cyclone/.virtualenvs
COPY . /home/cyclone/src
RUN export WORKON_HOME=/home/cyclone/virtualenvs
RUN . /usr/local/bin/virtualenvwrapper.sh
RUN mkvirtualenv -p $(which python3.6) cyclone

RUN activate cyclone
RUN cd /home/cyclone/src
RUN python setup.py install -e .

COPY crontab /etc/cron.d/cyclone-crawl-task
RUN chmod 0644 /etc/cron.d/cyclone-crawl-task

# Set the default command to run when starting the container
CMD ["/usr/lib/postgresql/10/bin/postgres", "-D", "/var/lib/postgresql/10/main", "-c", "config_file=/etc/postgresql/10/main/postgresql.conf"]
RUN service cron start