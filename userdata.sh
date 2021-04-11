#!/bin/bash

# install and start apache
yum update -y
yum install httpd -y
service httpd start
chkconfig httpd on

# create a simple web page
cd /var/www/html
echo "<html><body>IP address of this instance: " > index.html
curl http://169.254.169.254/latest/meta-data/public-ipv4 >> index.html
echo "</body></html>" >> index.html

# install stress utility
amazon-linux-extras install epel -y
yum install stress -y

# wait 3 minutes and start stress tool
sleep 180
stress -c 1