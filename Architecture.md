

# Introduction #

AmCAT is a system for document management and analysis. The purpose of AmCAT is to make it easier to conduct manual or automatic analyses of texts for (social) scientific purposes. AmCAT can improve the use and standard of content analysis in the social sciences and stimulate sharing data and analyses.

AmCAT is designed as an open system. The data is stored in a standard database, to which every user has access for his own projects. The source code for the scripts and web site are open source, so everyone is free to setup his/her own server. The system is designed to make it easy to integrate new analyses, through the web site, web services, or through direct access.

This document gives a brief technical overview of the different components of AmCAT, and is intended as a 'getting started' guide for the rest of the documentation on this site and the [API documentation](http://amcat.vu.nl/api).

# Components #

AmCAT consists of the following components:

| **Layer** | **Implementation** |
|:----------|:-------------------|
| Data  | Postgres database |
| Object | Django ORM in `amcat.model` |
| Business | Python code in `amcat`, `amcatscraping` |
| Presentation | Django web site in `amcatnavigator` |

Besides this, `AmCAT Solr` is a slightly customized version of the Apache Solr search platform used for searching through documents.

# More Information #

  * [ObjectModel](ObjectModel.md) Django ORM Object Model and DB Schema
  * [DjangoSetup](DjangoSetup.md) Django set-up
  * [SourceCode](SourceCode.md) Source Code overview