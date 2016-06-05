#!/bin/bash
mkdir data &>/dev/null
SCRAPY=`which scrapy`
echo '已包含如下爬虫:'
$SCRAPY list
echo '请输入想要运行的爬虫名,如amazon'
read NAME
echo "The $NAME spider is running !"
$SCRAPY crawl $NAME
