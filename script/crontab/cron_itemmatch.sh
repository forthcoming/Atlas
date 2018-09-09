path=$(cd `dirname $0`;pwd)
cd $path/../../atlas/models

python item_match.py
