#!/bin/sh

pip install setuptools wheel twine

pwd="$(pwd)"
name="${pwd##*/}"
pip uninstall -y $name

cp setup.py ..
(
cd ..

python setup.py sdist bdist_wheel

pip install dist/*.tar.gz
python -c 'import '${GITHUB_REPOSITORY#*/}

twine upload dist/*
)
