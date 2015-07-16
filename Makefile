compile:
	python setup.py install
	pyinstaller showdownai.spec

clean:
	rm -rf build dist
