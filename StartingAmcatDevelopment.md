# Introduction #

# Setting Up a Work Environment #

# Common Problems #
## Django Settings ##
```
ImportError: Settings cannot be imported, because environment variable DJANGO_SETTINGS_MODULE is undefined.
```
Define the DJANGO\_SETTINGS\_MODULE:
```
export DJANGO_SETTINGS_MODULE=amcat.settings
```
Make sure you have a ~/.amcatrc3 file as described in [InstallingAmcat](InstallingAmcat.md)

## Can't Find a Module ##
```
    from amcat.foo.bar import Something
ImportError: No module named amcat.foo.bar
```
You probably have not set your pythonpath. Try:
```
export PYTHONPATH=~/amcat3
```
PYTHONPATH should point to the folder that contains amcat.

# Testing #
## Unit Testing ##

## Regular Testing ##
Make sure your python file has
```
#!/usr/bin/python
```
on the first line.

Add the following for a console interface:
```
if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging

    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(SomeScraper)
```