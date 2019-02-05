# This file is part of censusgeocode.
# https://github.com/fitnr/censusgeocode

# Licensed under the General Public License (version 3)
# http://opensource.org/licenses/LGPL-3.0
# Copyright (c) 2015-9, Neil Freeman <contact@fakeisthenewreal.org>

.PHONY: install build upload clean deploy test

install: ; python setup.py install

test: ; python setup.py test

deploy: build
	twine upload dist/*

build: | clean
	python3 setup.py bdist_wheel --universal
	python3 setup.py sdist

clean:; rm -rf dist build
