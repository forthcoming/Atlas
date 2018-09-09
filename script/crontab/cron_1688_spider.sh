path=$(cd `dirname $0`;pwd)
cd $path/../../atlas/spider/1688_spider

python alibaba_app_spider.py > spider.log 2>&1