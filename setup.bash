#!/usr/bin/env bash
rm -rf ./src/gen
rm -rf ./venv
./setup_venv.bash
source ./venv/bin/activate
pip install -U pip
pip install -r requirements.txt
./compile_proto.bash
