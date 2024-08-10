#!/bin/bash

sudo apt-get update
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
