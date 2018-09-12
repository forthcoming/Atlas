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

cd $path
pip install -r ../requirements.txt

if [ $? -eq 0 ]; then
        print_suc '****安装成功'
    else
        print_fail '****安装失败'
        exit -1
fi

