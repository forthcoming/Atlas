path=$(cd `dirname $0`;pwd)
cd $path/../../atlas/spider/bi_spider

export LD_LIBRARY_PATH=/usr/lib/oracle/12.2/client64/lib:$LD_LIBRARY_PATH

python bi.py
python bi_final.py
python bi2atlas.py
python syncPriceFromAtlas.py