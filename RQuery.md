# Introduction #

Quite frequently, we want to get information from AmCAT in order to use it to test models in R. Because AmCAT3 offers 'web service' access to its data and APIs, it is possible to get the needed information in R directly, i.e. without using the navigator web site.

# AmCAT web service API #

AmCAT offers two types of APIs:

  1. A 'REST' API for reading (and editing) objects
  1. Actions: Web services that provide functionality that goes beyond the simple selectin or editing of objects

# General R functions #

We will provide an R package to easily connect to AmCAT as soon as things are stabilized. In the meantime, the following two functions might be helpful:

```r

library(rjson)
library(RCurl)

amcat.getobjects <- function(resource, passwd, username='reader', format='csv',
host='https://130.37.193.14', limit=99999999, filters=list()) {
url = paste(host, '/api/v3/', resource, '/?format=', format, '&limit=', limit, sep='')
for (k in names(filters))
url = paste(url, '&', k, '=', filters[[k]], sep='')

result = getURL(url, .opts=opts)
if (result == '401 Unauthorized')
stop("401 Unauthorized")
if (format == 'json') {
result = fromJSON(result)
} else  if (format == 'csv') {
con <- textConnection(result)
result = read.csv(con)
}
result
}

amcat.runaction <- function(action, passwd, username='reader', format='csv',
host='https://130.37.193.14', ...) {

resource = 'api/action'
url = paste(host, resource, action, sep="/")
url = paste(url, '?format=', format, sep="")
opts = list(userpwd=paste(username, passwd, sep=":"), ssl.verifypeer = FALSE)
result = postForm(url, ..., .opts=opts)
if (result == '401 Unauthorized')
stop("401 Unauthorized")
if (format == 'json') {
result = fromJSON(result)
} else  if (format == 'csv') {
con <- textConnection(result)
result = read.csv2(con)
}
result
}
```

# Querying an AmCAT Solr index #

A common use case (and currently the only one :))  is to query the AmCAT index to get the number of hits per article for one or more search strings.  For this example, I am assuming that the articles we want to query are in one set: 22727 (a small set containing 68 articles about the US elections).

To get the needed data, we need to make one call to get the metadata and one call per query. Let's assume we want to query for 'mccain' and 'obama':

```R

articlesets = "22727"
passwd = "XXXXXX"
d = amcat.getobjects('article', passwd, filters=list(articlesets=articlesets))
for (query in c("obama", "palin")) {
data = amcat.runaction('Query', passwd, articlesets=articlesets, query=query)
colnames(data)[2] = query
d = merge(d, data, by="id", all.x=T)
d[is.na(d[query]), query] = 0
}
names(d)
head(d[, c("id", "date", "medium", "obama", "palin")])```

This yields the result (after replacing the passwd by the current 'reader' password):

```R

> names(d)
[1] "id"           "medium"       "parent"       "author"       "headline"     "project"
[7] "url"          "externalid"   "date"         "pagenr"       "resource_uri" "obama"
[13] "palin"
> head(d[, c("id", "date", "medium", "obama", "palin")])
id                date medium obama palin
1 36697040 2008-10-07T00:00:00    307     6     0
2 36697108 2008-10-05T00:00:00    307     1    12
3 36697140 2008-10-04T00:00:00    307     2     1
4 36697192 2008-10-03T00:00:00    310     9     0
5 36697197 2008-10-03T00:00:00    310     9     0
6 36742822 2008-10-09T00:00:00    307     6     0
```

Note that the getobjects call is probably not the most efficient way to query metadata. Getting all metadata for set 22763 (a WODC set containing around 80,000 articles) took about 5 minutes from my home computer. A direct database query with output to a csv document is probably more efficient.