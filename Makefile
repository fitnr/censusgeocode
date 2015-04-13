# This file is part of censusgeocode.
# https://github.com/fitnr/censusgeocode

# Licensed under the General Public License (version 3)
# http://opensource.org/licenses/LGPL-3.0
# Copyright (c) 2015, Neil Freeman <contact@fakeisthenewreal.org>

.PHONY: install
install: readme.rst
	python setup.py install

readme.rst: readme.md
	which pandoc && pandoc $< -o $@ || touch $@
