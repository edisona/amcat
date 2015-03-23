

# Introduction #

The Query tab is the main interface that can be used to retrieve and process a set of articles. The main design principle is to have each query be executed as a set of modular units of code called Scripts _(or Plugins? - I feel that that is a better name?)_. These Scripts perform the tasks needed to present data to the user - (1) query the system, (2) process the results, (3) output of visualise them in the correct way.

# Status #

In 3.0 the Query tab uses Webscripts, but the way they are implemented and presented caused some confusion among developers and users, and did not reach the goal of easy extendability. We are currently discussing a good way of re-implementing this system. The goal is to have a system with minimal technical redundancy, and easy to use interface, easy integration in API/CLI based workflows, and easy extendability of processing scripts.

_(Warning: This is not yet implemented. You could consider this as a design proposal, which may need further [discussion](http://code.google.com/p/amcat/issues/detail?id=200).)_

## Requirements ##

  * The Scripts should be able to be used standalone, i.e. as CLI or Web Service scripts. This means that the input and output should be reasonable outside of the Query tab pipeline.

  * The framework should be easy to extend. AmCAT users should be able to use their own scripts without modifying "our" code.

## Design (proposal) ##

The current amcat.scripts.script.Script class is the basis for the Scripts. Each Script has a django options form that specifies the required input of the script, which can include a file or text field with data. The output of each script is not currently formalized, but it should be clear from its type, e.g. part of the 'class' contract is the output type. [1](1.md)

There will be four types of Scripts:

```
ListQuery
  input form:   article sets, media/date range, other criteria, solr queries (optional), selected columns
  output:       "list table" of articles (rows) x selected columns, 
                e.g. article id, headline, date, text, queries  
  description:  This script queries the database or solr index with the required selection criteria, and 
                creates a table with the requested columns. 
                It is very similar to the current 'show as list' interface and the query web service 

TableQuery
  input form:   article sets, media/date range, other criteria, solr queries (optional), 
                column and row group-by field, cell option (#articles (=count), #hits (=sum(hits))
  output:       "aggregated table" of row x group field with #articles/hits in the cells
  description:  This script queries the database or solr index with the required selection criteria. For the 
                database it will use a GROUP BY query. [2]
                It is very similar to the current 'show as table' interface

Processor:
  input form:   input data (list table), optional custom parameters
  output:       "list table", "aggregated table", or "network table"  [script should specify which it outputs]
                (network=nodes in rows and columns, edges in cells, possibly allow sparse representation)
  description:  This is the kind of script that can be customized. Can do things like count words, calculate assocations,
                run a clustering algorithm etc

Visualizer: (misnomer? it can also create e.g. excel files etc)
  input form:   "list table", "aggregated table", and/or "network table"  [can be multiple, script specifies what it accepts]
  output form:  binary, should probably specify per-script whether content can be displayed inline or offered as download?
  description:  Script to turn a table into a file (excel, gephi etc) or visual representation (graph, network diagram, etc)
                

Pipeline:
  input form:   ListQuery input form plus processor and optional visualiser and their forms
  output form:  "list table", "aggregated table", "network table", or binary, depending on chosen processor and/or visualiser
  description:  Because it is difficult to do arbitrary configuration of scripts, this allows for the creation of mini 
                pipelines. On the CLI, the following should have the same results

                python pipeline.py OPTIONS --processor MyProcessor --visualiser MyVisualiser
                python ListQuery.py OPTIONS | python MyProcessor.py OPTIONS - | python MyVisualiser OPTIONS 

                (since that is most convenient with HTTP forms and django handling, I simply offer all options to all scripts,
                 so processors should not use 'reserved' option names for themselves, but can accept these options if they
                 e.g. want to say something about how the selection was made, maybe in the 'save as set' script so it can set
                 provenance?)
```

Of course, this needs to be fleshed out and implemented. Note that the default 'show as list/table' screens only use the ListQuery or TableQuery. Also note that processors can only use ListQuery output for the moment. During implementing I hope it will be clear how to deal with output correctly. Input tables should probably be specified as FileFields to allow streaming and uploading.

The output tables should probably be returned by the python implementation as a sequence of useful values, or as a table3 like object with that sequence embedded, so a pipeline within python does not require (de)serialization or have the whole table in-memory.

It would be a bonus if the output can also be 'streamed' for CLI pipelining, but that is less urgent.

[1](1.md) _This implies removing the input and output class property of Scripts, they are currently not formalized and used properly. An alternative is to use an output form the same way as the options form, but that seems to make less sense. It is analogous to functions is python having somewhat specified arguments but no specification at all for the return value._
[2](2.md) In principle, aggregation can be seen as a processor, and that would also explain why processing can only use list queries: the aggregation _is_ the processing step. For SOLR, this could also be implemented this way if that is most convenient

## Further discussion ##
See [issue #200](http://code.google.com/p/amcat/issues/detail?id=200).