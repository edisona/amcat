The [api documentation](http://amcat.vu.nl/api/) contains a detailed description of all modules in AmCAT. This page provides a high-level overview of the different modules:

  * `amcat.model`: Classes for the general tables in AmCAT: projects, articlesets, users, etc. See [the graphical model structure](http://amcat.vu.nl/api/model_amcat_trunk.html) for an overview of available tables.
  * `amcat.tools`: General tools
    * `amcat.tools.table`: Abstraction over rectangular tables to enable processing of tables regardless of their origin.
    * `amcat.tools.logging`: Logging support
    * `amcat.tools.stat`: Statistics modules, including interfacing with R.
    * `amcat.tools.selection`: Modules to facilitate article selection, including using SolR index search.
  * `amcat.forms`: Auxillary classes to deal with django forms. TODO: move to tools
  * `amcat.db`: Auxillary classes to deal with the database, eg to enable things that are difficutlt to do with django ORM. TODO: move to tools
  * `amcat.scripts`: Interface and auxilliary modules for plugins.
  * `amcat.nlp`: Natural Language Technology Preprocessing and analysis
  * `amcat.ml`:  Machine Learning tools
  * `amcat.bin`: Executable scripts such as generating the api documentation.
  * `amcat.contrib`:  Third party modules that could not be installed as dependency, e.g. because they are not published.
