


# Introduction #

Certain functionality of AmCAT is implemented using scripts.
A Script is a generic "pluggable" functional element that can be
called from e.g. the Django site, as a standalone web interface, or as
a command line script.

The concept of webscripts is described on the [Selection Page](selectionPage#WebScripts.md).


# Structure #

Scripts have three key parameters, specified as class variables:
  * `input_type`: a class representing the type of input expected by the script, such as None, unicode, Table, or ArticleList. The command line equivalent would be a (deserialized) stdin stream
  * `options`: a Django form of required and optional options. The CLI equivalent are the command line options and arguments. Can be None
  * `output_type`: a class representing the output that the script will produce.


Scripts can be found in `amcat.scripts`.
They are stored in the subdirectories:
  * `amcat.scripts.tools`: contains helper classes that are used by the scripts
  * `amcat.scripts.searchscripts`: contains scripts that search Solr or the database
  * `amcat.scripts.processors`: contains scripts that process the input of a script
  * `amcat.scripts.output`: contains scripts that output script results in various formats, such as csv and html.
  * `amcat.scripts.to_be_updated`: contains legacy scripts that still have to be updated.


## Script Manager ##

`amcat.script.scriptmanager.findScript` is a function that can be used to find a script with a certain `inputClass` and `outputClass`. `outputClass` can also be a string such as 'csv' or 'html'.


# Overview of main scripts #

## Selecting articles ##
Selecting a specific set of articles can be done using the `amcat.scripts.searchscripts.articlelist.ArticleListScript` script.
As input it requires a project and the columns to select. There are also many other parameters which are not required, such as the number of results to return, the offset, the start/end date, sort order, a list of mediums and sets and a Solr query.

The result will be an iterator that returns Article objects. Optionally the searchterms can be highlighted (if a Solr query is present).

## Converting a list of articles to a table ##
Conversion from an articlelist to a table can be performed using `amcat.script.processors.articlelist_to_table.ArticleListToTable`. A list of column should be present, that indicate the columns of the table.

## Converting a table to Html, CSV or other output format ##

In the `amcat.script.output` various output scripts are present. You can use the ScriptManager to automatically pick the correct Script to output to a certain format.
Most of these scripts do not require any options, but for the html output scripts a django template can be specified for custom markup.


# Example #

To be written
