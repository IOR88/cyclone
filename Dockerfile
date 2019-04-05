FROM ubuntu:bionic
RUN apt-get update

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

# create user admin with password 1234 and cyclone database
RUN /etc/init.d/postgresql start &&\
    psql --command "CREATE USER admin WITH LOGIN PASSWORD '1234';" &&\
    createdb -O admin cyclone


######################
# PYTHON AND SCRAPY
######################
USER root
RUN apt-get -y install python3-pip python3-dev build-essential
RUN pip3 install virtualenv
RUN pip3 install --upgrade pip

RUN mkdir /home/cyclone
RUN mkdir /home/cyclone/src
RUN mkdir /home/cyclone/virtualenv
COPY . /home/cyclone/src
RUN virtualenv -p $(which python3.6) /home/cyclone/virtualenv

RUN /bin/bash -c ". /home/cyclone/virtualenv/bin/activate && cd /home/cyclone/src && pip install -e ."
RUN /bin/bash -c ". /home/cyclone/virtualenv/bin/activate && service postgresql start && python /home/cyclone/src/src/cyclone/models.py && cd /home/cyclone/src/src/cyclone && python /home/cyclone/virtualenv/bin/scrapy crawl cyclone_spider && PGPASSWORD=1234 psql -U admin -d cyclone -h 127.0.0.1 -c 'SELECT track.hour, track.latitude, track.longitude, track.intensity, forecast.synoptic_time, cyclone.name AS cyclone_name, research_geographical_area.name as basin_name, forecast.type AS track_type FROM track JOIN forecast ON track.forecast=forecast.id JOIN cyclone ON forecast.cyclone=cyclone.id JOIN research_geographical_area ON forecast.research_geographical_area=research_geographical_area.id;' > /home/cyclone/output.txt"

RUN cat /home/cyclone/output.txt