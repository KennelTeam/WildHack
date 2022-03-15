#!/bin/bash
# import elasticseacrch PGP key
eval $"wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -"
# install apt-transport-https package
eval $"sudo apt-get install apt-transport-https"
# add elasticsearch repo
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-7.x.list
