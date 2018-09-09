path=$(cd `dirname $0`;pwd)
cd $path/../../atlas/models

python img_match.py
