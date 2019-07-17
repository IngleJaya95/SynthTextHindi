#!/usr/bin/env bash
git clone https://github.com/ldo/harfpy.git
cd harfpy
python setup.py install
cd ..
git clone https://github.com/ldo/qahirah.git
cd qahirah
python setup.py install
cd ..
git clone https://github.com/ldo/python_freetype.git
cd python_freetype
python setup.py install
cd ..
git clone https://github.com/ldo/pybidi.git
cd pybidi
python setup.py install
pip install wget
pip install pillow
pip install opencv-python=3.4.2.17
pip install pygame
pip install h5py
pip install matplotlib
pip install scipy