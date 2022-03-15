#!/bin/bash

#ONE LINE
#sudo wget -Nnv 'https://gist.githubusercontent.com/kydouglas/1f68d69e856fd6d7dc223f8e1f5ae3b3/raw/f8c3b22b9d9c41093150b96c815776956b523d9d/elk.sh' && bash elk.sh && rm -f elk.sh

# Checking whether user has enough permission to run this script
sudo -n true
if [ $? -ne 0 ]
    then
        echo "This script requires user to have passwordless sudo access"
        exit
fi

dependency_check_deb() {
java -version
if [ $? -ne 0 ]
    then
        # Installing Java 8 if it's not installed
        sudo apt-get install openjdk-8-jre-headless -y
    # Checking if java installed is less than version 7. If yes, installing Java 7. As logstash & Elasticsearch require Java 7 or later.
    elif [ "`java -version 2> /tmp/version && awk '/version/ { gsub(/"/, "", $NF); print ( $NF < 1.8 ) ? "YES" : "NO" }' /tmp/version`" == "YES" ]
        then
            sudo apt-get install openjdk-8-jre-headless -y
fi
}

dependency_check_rpm() {
    java -version
    if [ $? -ne 0 ]
        then
            #Installing Java 8 if it's not installed
            sudo yum install jre-1.8.0-openjdk -y
        # Checking if java installed is less than version 7. If yes, installing Java 8. As logstash & Elasticsearch require Java 7 or later.
        elif [ "`java -version 2> /tmp/version && awk '/version/ { gsub(/"/, "", $NF); print ( $NF < 1.8 ) ? "YES" : "NO" }' /tmp/version`" == "YES" ]
            then
                sudo yum install jre-1.8.0-openjdk -y
    fi
}

debian_elk() {
    # resynchronize the package index files from their sources.
    sudo apt-get update
    # Downloading debian package of logstash
    sudo wget --directory-prefix=/opt/ https://artifacts.elastic.co/downloads/logstash/logstash-6.0.0-rc2.deb
    # Install logstash debian package
    sudo dpkg -i /opt/logstash-6.0.0-rc2.deb
    # Downloading debian package of elasticsearch
    sudo wget --directory-prefix=/opt/ https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.0.0-rc2.deb
    # Install debian package of elasticsearch
    sudo dpkg -i /opt/elasticsearch-6.0.0-rc2.deb
    # install kibana
    sudo apt-get install apt-transport-https
    sudo wget --directory-prefix=/opt/ https://artifacts.elastic.co/downloads/kibana/kibana-6.0.0-rc2-amd64.deb
    sudo dpkg -i /opt/kibana-6.0.0-rc2-amd64.deb
    # Starting The Services
    sudo systemctl restart logstash
    sudo systemctl enable logstash
    sudo systemctl restart elasticsearch
    sudo systemctl enable elasticsearch
    sudo systemctl restart kibana
    sudo systemctl enable kibana
}

rpm_elk() {
    #Installing wget.
    sudo yum install wget -y
    # Downloading rpm package of logstash
    sudo wget --directory-prefix=/opt/ https://artifacts.elastic.co/downloads/logstash/logstash-6.0.0-rc2.rpm
    # Install logstash rpm package
    sudo rpm -ivh /opt/logstash-6.0.0-rc2.rpm
    # Downloading rpm package of elasticsearch
    sudo wget --directory-prefix=/opt/ https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.0.0-rc2.rpm
    # Install rpm package of elasticsearch
    sudo rpm -ivh /opt/elasticsearch-6.0.0-rc2.rpm
    # Download kibana tarball in /opt
    sudo wget --directory-prefix=/opt/ https://artifacts.elastic.co/downloads/kibana/kibana-6.0.0-rc2-linux-x86_64.tar.gz
    # Extracting kibana tarball
    sudo tar zxf /opt/kibana-6.0.0-rc2-linux-x86_64.tar.gz -C /opt/
    # Starting The Services
    sudo service logstash start
    sudo service elasticsearch start
    sudo /opt/kibana-6.0.0-rc2-linux-x86_64/bin/kibana &
}

# Installing ELK Stack
if [ "$(grep -Ei 'debian|buntu|mint' /etc/*release)" ]
    then
        echo " It's a Debian based system"
        dependency_check_deb
        debian_elk
        
        
elif [ "$(grep -Ei 'fedora|redhat|centos' /etc/*release)" ]
    then
        echo "It's a RedHat based system."
        dependency_check_rpm
        rpm_elk
else
    echo "This script doesn't support ELK installation on this OS."
fi