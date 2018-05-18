VERSION = $(shell git describe --tags --match '[0-9]*.[0-9]' --abbrev=0)
REV = $(shell git rev-list $(VERSION)..HEAD | wc -l)

display:
	echo "Version $(VERSION) and Rev $(REV)"

build: 
	python setup.py sdist --formats=gztar,zip

init:
	pip install -r requirements.txt && pip install -r requirements-devel.txt

test:
	nosetests tests
