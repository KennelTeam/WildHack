FROM ubuntu

RUN apt-get update -y
RUN apt-get install -y python3
RUN apt-get install -y python3-pip

WORKDIR /app

RUN apt-get install wget -y
RUN wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
RUN apt-get install apt-transport-https
RUN echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | tee /etc/apt/sources.list.d/elastic-7.x.list
RUN apt-get update && apt-get install elasticsearch

RUN systemctl daemon-reload && systemctl enable elasticsearch.service
RUN systemctl start elasticsearch.service

# COPY es_config.sh .
# RUN bash es_config.sh

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

COPY . .

WORKDIR /app/website

CMD ["python3", "website.py"]
