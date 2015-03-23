

# Introduction #

Apache Solr is a search platform written in Java. We use it to search through documents. The advantage of Solr over Lucene is that it runs as a web service, so it can be easily accessed from Python. It also supports more advanced features, such as Unique Keys, that are very useful.
See the [Solr Wiki](http://wiki.apache.org/solr/FrontPage) for more information on Solr.

The user interface of Solr in AmCAT is the [Selection Page](selectionPage.md).


# Modifications #

One of the features required in AmCAT is to be able to count the number of hits in a document. This is not as trivial to retrieve from Solr/Lucene as it sounds, since it uses it's own scoring mechanism that we don't need. This is why we need to implement our own Similarity class that simply returns the number of hits, instead of a more complicated score.
So all scores that Solr returns are the number of hits in that document.

Another difference with the default Solr package is that we include the ComplexPhrase query language. This is needed since search queries such as "(Obama OR Bush) president"~10 should be supported. The Phrase Query from the default Solr/Lucene query language does not support boolean or any other operators inside the query.

Both Java classes can be found in the Amcat-solr repository. They have to be build with ant to a .jar file. These files have to be manually added to the .war file
The reason for this is that Solr else will return an error. It might be possible that this no longer happens in more recent versions of Solr. You can try to add them to the solr/lib directory.


# starting Solr #

simply use this command in the amcat-solr directory:

`java -jar start.jar`

or

`nohup java -jar ~/amcat3/amcatSolr/start.jar  > ~/amcat3/amcatSolr/logs/solr.out 2> ~/amcat3/amcatSolr/logs/solr.err < /dev/null &`

Solr runs by default on port 8983.


# Schema #

The Solr schema is almost a direct mapping of the basic attributes of the `amcat.model.article.Article` class. See solr/conf/schema.xml

  * `id`
  * `body` (analyzed, stored, indexed)
  * `headline` (analyzed, stored, indexed)
  * `byline` (analyzed, indexed)
  * `section` (indexed)
  * `mediumid` (stored, indexed)
  * `projectid` (stored, indexed)
  * `date` (stored, indexed)
  * `sets` (multivalued, stored, indexed)

Analyzed means that the input is parsed through a Tokanizer and several Filters.
First the characters `#` and `@` are mapped to normal words, to make it possible to search for them. This is useful for Twitter data, where these characters are important.
Secondly the text is split into words, using the default StandardTokenizerFactory. Thirdly every word will be lowercased. Forthly non-ascii characters will be mapped to ascii (such as `e` with an apostrophe will change into `e`). And finally `'s` is removed at the end of words and `l'` and other French prefixes (or whatever they are really called) are removed. This is useful if you search for 'taxi' or 'avion'. Results as "taxi's" and "l'avion" are also relevant, so they are stored as 'taxi' and 'avion'.

Stored means the field can be included in the Solr output, indexed means you can search for it.
'section' is not analyzed since it normally only contains one word, for instance 'economy'.
'sets' are included as well, because it is important to be able to search through sets.

In addition, there is also a `text` field, which is the default search field. This contains the `headline`, `byline` and `body` fields.
For performance reasons it is more efficient to search through one field. And by keeping `headline`, `byline` and `body` separate, it is still possible to do a query for a specific field, for instance `headline:obama`.


# Web interface #

Solr contains a web interface that can be accessed on port 8983 of the amcat-sql2 server. It can be useful for debugging queries and viewing statistics of the index and performance.

# Solr Daemon #

There is a daemon that automatically adds documents to Solr when they are added/updated in the database. This is done using Database triggers. Currently only the triggers for PostGreSQL are provided.
When an article is added/updated, the article\_id is added to the solr\_articles table (the `amcat.model.article_solr.SolrArticle` model).
The daemon checks if there are any SolrArticle objects, and adds them to Solr. See `amcat.scripts.deamons.solrdaemon`.
It uses the [Solrpy](http://code.google.com/p/solrpy/) Python client to communicate with Solr.

The daemon can be (re)started using the command:
`python amcat/scripts/deamons/solrdaemon.py restart`



# Querying documents #

Example query:
```
import solr
s = solr.SolrConnection('http://localhost:8983/solr')

response = s.query('{!complexphrase}"premi* (sal* OR balk*)"~10', highlight=True, fields="*", hl_usePhraseHighlighter='true', hl_highlightMultiTerm='true')
print response.__dict__
for hit in response.results:
    print hit
for hl in response.highlighting.iteritems():
    print hl
```

See `amcat.scripts.searchscripts.tools.solrlib` for more examples.