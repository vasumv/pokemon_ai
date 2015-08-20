compile:
	python setup.py install
	yes | pyinstaller showdownai.spec || mkdir -p $(dir $@)
	cp -r teams dist/showdownai/
	zip -r dist/showdownai-linux64.zip dist/showdownai/

clean:
	rm -rf build dist
