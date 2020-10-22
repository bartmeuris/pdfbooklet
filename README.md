# Generate PDF booklets

This small script generates an A6 sized booklet printed on A4 from a standard A4/A5 sized PDF. The result is a PDF that should be printed double-sided, with 4 small pages per side. Empty pages are automatically added to the end if the amount of pages is not a multiple of 8.

By it uses [easygui](http://easygui.sourceforge.net/) to prompt for a file to load, and where to save it.

## Commandline parameters

It accepts the following commandline parameters, mostly useful for testing:

* `-a`: Autogenerate output filename. It uses the input filename and prepends `booklet-` 
* `-n`: Non-interactive mode, doesn't show success box, and doesn't prompt for file to save to, also enables `-a`.

If a first filename is provided as a parameter, this is assumed to be the input file.

If a second filename is also provided as a parameter, this is assumed to be the output file, overriding any auto output filename generation.

Example:

```bash
python .\booklet4.py -n .\source.pdf # fully non-interactive, auto-generating 'booklet-source.pdf` output filename

python .\booklet4.py -n .\source.pdf booklet.pdf # fully non-interactive, specifying output filename

python .\booklet4.py -a .\source.pdf # Will show a 'success' gui window

```

## Developing

Environment uses pipenv to manage a virtual env. Tested with Python 3.8.2

```bash
pipenv install
pipenv run booklet4.py
```
## Building

Just run the `build.bat` file to generate a fully standalone windows executable.

## TODO / known issues

* Add some margin corrections, sub-pages are not positioned 100% correctly
* Only supports 4x4
* Does not take a maximum amount of pages into account for proper binding. It generates a single booklet set.