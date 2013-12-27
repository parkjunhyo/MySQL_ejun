#! /usr/bin/env bash

### current directory and source env file
working_directory=`pwd`
access_info=$working_directory/utils/system_info.py
log_directory="$working_directory/log"
source $working_directory/mysql.cnf

### server or client selection
if [[ $# != 1 ]]
then
 echo "command usage : $0 [server or client]"
 exit
fi
mode=$1

### log folder creation
if [[ ! -f $log_directory ]]
then
 mkdir -p $log_directory
fi

### init variable creation
mysql_pass=${mysql_pass:='mysql'}
mysql_bind_iface=${mysql_bind_iface:='eth0'}
mysql_bind="''"

### setup common (server and client)
apt-get install -y expect python-mysqldb

### server setup
if [[ $mode = 'server' ]]
then

 ### change the password for mysql root user
 sed -i 's/\<changepass\>/'$mysql_pass'/' $working_directory/mysql_setup.exp
 sed -i 's/\<changepass\>/'$mysql_pass'/' $working_directory/mysql_secure_setup.exp

 ### setup the bind ip address to make sure it work
 mysql_bind=`ip addr show $mysql_bind_iface | grep -i '\<inet\>' | awk -F'[ /]' '{print $6}'`

 ### mysql server install
 $working_directory/mysql_setup.exp

 ### configuration bind ip address
 sed -i '/#*[[:space:]]*bind-address[[:space:]]*=[[:space:]]*/d' /etc/mysql/my.cnf
 sed -i 's/\[mysqld\]/\[mysqld\]\nbind-address = '$mysql_bind'/' /etc/mysql/my.cnf

 ### mysql restart
 /etc/init.d/mysql restart

 ### tesing table delete
 mysql_install_db
 $working_directory/mysql_secure_setup.exp

 ### mysql restart
 /etc/init.d/mysql restart

 ### root account privlege from remote site
 $working_directory/run_mysqlcmd.py priv_user root $mysql_pass
fi

## create the python system_info files
if [ ! -f $access_info ]
then
 touch $access_info
 echo "database_passwd='$mysql_pass'" >> $access_info
 echo "client_mode='$mode'" >> $access_info
 echo "database_host='$mysql_bind'" >> $access_info
 echo "log_directory='$log_directory'" >> $access_info
fi

## give auth to make possible remote acceess
if [[ $mode = 'server' ]]
then
 ./run_MySQLcmd.py priv_user root $mysql_pass 
fi
