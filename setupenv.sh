#!/usr/bin/env bash
# 提供环境搭建入口
path=$(cd `dirname $0`;pwd)


pip install --upgrade pip

##############################################################
# Supply Echo Info
print_suc()
{
    echo -e "\033[32m $1 \033[0m"
}

print_fail()
{
    echo -e "\033[31m $1 \033[0m"
}


###############################################################
# setup mongodb
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
echo "deb [ arch=amd64 ] http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list
apt-get update
apt-get install -y mongodb-org


###############################################################
# setup apt-get package

echo '****************************************************'
for package in python-pip libxml2 libxml2-dev libxslt-dev python-libxml2 python-dev zlib1g-dev libtiff5-dev libjpeg8-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk liblapack-dev gfortran python-matplotlib
do

    echo '开始安装:' $package

    apt-get -y install $package

    if [ $? -eq 0 ]; then
        print_suc '****安装'$package'成功'
    else
        print_fail '****安装'$package'失败'
        exit -1
    fi

done

sed -i "s/from pip import main/from pip._internal import main/g" /usr/local/bin/pip




####################################################################
echo '**********************************************************'
echo '开始安装Python 依赖库'
# setup pip package
pip install numpy
pip install plan
pip install flask
pip install cx_Oracle
pip install crontab


echo '************************************************************'
echo '清理老环境'

cd /usr/lib/python2.7/dist-packages
mkdir bak_
mv requests* bak_/
pip uninstall requests -y

mv chardet* bak_/
pip uninstall chardet -y

mv urllib3* bak_/
pip uninstall urllib3 -y

pip install requests==2.17.3


mv setuptools* bak_/
pip uninstall setuptools -y

sudo wget https://bootstrap.pypa.io/ez_setup.py -O - | sudo python


pip install pymysql


cd $path
pip install -r ../requirements.txt

if [ $? -eq 0 ]; then
        print_suc '****安装成功'
    else
        print_fail '****安装失败'
        exit -1
fi

