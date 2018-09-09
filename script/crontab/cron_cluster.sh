path=$(cd `dirname $0`;pwd)
cd $path/../../atlas/models

python cluster_add.py > cluster_add.log 2>&1
