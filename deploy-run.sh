#!/bin/bash
app_root=$(dirname $(readlink -f $0))
# git pull for update repo
cd "$app_root"
rm -rf venv #purge already installed dependecy
git pull

# install dependencies
cd "$app_root"
python3 -m venv venv # create venv
activate venv/bin/activate # active venv
if [ -f requirements.txt ]; then pip3 install -r requirements.txt; fi #install dependencies

# run program
pm2 reload appstart.sh