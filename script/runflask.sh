#!/usr/bin/env bash
# 提供环境搭建入口

##############################################################
path=$(cd `dirname $0`;pwd)
ATLAS_APP_DIR=$path/../atlas/flasksev/

cd $ATLAS_APP_DIR
apidoc

python api.py
