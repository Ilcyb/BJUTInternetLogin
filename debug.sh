#!/bin/bash

echo -n "Enter Version:"                   
read version 

python setup.py sdist bdist_wheel
cd dist
pip install bjut_internet_login_tool-$version-py3-none-any.whl