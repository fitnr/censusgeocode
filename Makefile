# This file is part of censusgeocode.
# https://github.com/fitnr/censusgeocode

# Licensed under the General Public License (version 3)
# http://opensource.org/licenses/LGPL-3.0
# Copyright (c) 2015-9, Neil Freeman <contact@fakeisthenewreal.org>

.PHONY: install build upload clean deploy test

install: ; pip install .

test: ; python -m unittest tests/test_*.py

deploy: build
	twine upload dist/*

build: | clean
	python -m build

clean:; rm -rf dist build
