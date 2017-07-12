# This file is part of censusgeocode.
# https://github.com/fitnr/censusgeocode

# Licensed under the General Public License (version 3)
# http://opensource.org/licenses/LGPL-3.0
# Copyright (c) 2015-7, Neil Freeman <contact@fakeisthenewreal.org>

.PHONY: install upload clean deploy test
install: README.rst
	python setup.py install

README.rst: README.md
	- pandoc $< -o $@
	@touch $@
	- python setup.py check --restructuredtext --strict

test: ; python setup.py test

deploy: README.rst | clean
	python3 setup.py sdist bdist_wheel
	twine upload dist/*

clean:; rm -rf dist build
