#!/bin/bash

echo -n "Enter Version:"                   
read version 

python setup.py sdist bdist_wheel
twine upload dist/bjut_internet_login_tool-$version*