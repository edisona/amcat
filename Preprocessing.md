# Introduction #

Frequently, it is useful to preprocess documents in AmCAT in some way before analyzing them. Examples are SOLR indexing, lemmatizing, parsing, etc.

The strategy for preprocessing in AmCAT is that a project has a setting to turn the various preprocessing steps on or off. Every time an article is added, modified, or deleted, the necessary preprocessing is done.

This wiki page details the technical choices and implementation of the processing.

# Considerations and decisions #

## Terms ##

**Analysis**: a preprocessing analysis that can be applied to an article, listed in table `analyses`

**Project**: a project in AmCAT, with options for toggling analyses as active or not

**Set**: an article set, belonging to a project with a many-to-many relation with articles.

## Desiderata ##

An article should be preprocessed with analysis A if it is owned by a project with A active or belongs to any set that is owned by such a project.

After an article is created, deleted, or modified (including changing set assignment), it should be preprocessed automatically and as soon as reasonable.

It should be possible to view the status of preprocessing per project and/or per set, and manually 'redo' the preprocessing of articles.

The preprocessing should as much as possible happen in the background, i.e. without interrupting the user activity that triggered the preprocessing.

## Considerations and Design Choices ##

In Django logic, the logical place to trigger preprocessing would be in the article.save method and related for the article sets. However, to determine which articles need to be processed by which analyses would require looking up all sets the article is part of and the involved projects. This is much more efficient if it can be done per batch rather than per article. However, it would require a lot of programming logic to facilitate batch processing.

Thus, it was decided to keep a queue of articles that need to be 'checked' for preprocessing. A background process (daemon) regularly checks this queue, determines if any of the articles need to be preprocessed, and places these articles on per-analysis tables. Background processes that do the actual analysis use these tables to do the actual processing. These tables can also be used as source of information for reporting

Since 'deleted' articles also need to be checked, esp. for removing them from the Solr index, articles cannot be deleted as long as they have active preprocessing. This is facilitated by including a 'delete' column in articles\_analysis. If this column is true, the preprocessors are requested to delete the processed results (eg from the index) and delete the articles\_analysis entry. In the web site, this should be done by sending 'to be deleted' articles to a recycling bin "project", and deleting them there after the preprocessing results have been removed.

# Involved database tables #

  * `articles_preprocessing_queue`
    * `article_id` (FK references articles)

  * `articles_analysis`
    * `article_id` (FK references articles)
    * `analysis_id` (FK references analyses)
    * `started` (boolean default false)
    * `done` (boolean default false)
    * `delete` (boolean default false)

# Preprocessing Flow #

**Trigger**: Any article that is deleted, updated, or created is placed in the check queue. If a set is created, deleted, moved, or has membership changes the whole set is placed on this queue. This is currently handled at the database level using a trigger, but could also be done in the .save() logic. The `articles_preprocessing_queue` table holds this queue. This table can contain duplicate articles and articles that have been deleted.

**Checking**: The `preprocess_distributor` background process (daemon) regularly checks whether the `articles_preprocessing_queue` has articles, and grabs a batch of articles from this queue if available. For these articles, it is determined

  * In which set(s) they belong
  * Which project owns the article and any sets
  * What the preprocessing settings for the involved projects are
  * Whether these articles are already on the analysis processing queues

**Distributing**: For each article and analysis, it is determined whether it needs to be processed by that analysis, and whether it is already on the analysis preprocessing table. Then, the following action is taken:

  * Does it need to be processed?
    * Yes:
      * Is it on the preprocessing table already?
        * Yes: Deletion marker set to false
        * No: Article is placed on the table
    * No:
      * Is it on the preprocessing table already?
        * Yes: Deletion marker set to true
        * No: No action

**Processing**: The actual processing is guided by the per analysis preprocessing table. The analysis process is presumably a background process but can also be running on a different computer or cluster for intensive processing such as syntax parsing. The processor selects a batch on unstarted articles from the `articles_analyses` table and marks them as started. It processes these articles, stores the results as appropriate, and marks the articles as done. Any errors are marked as unstarted, again.

## Multithreading and locking issues ##

The `articles_preprocessing_queue` table is allowed to be 'dirty' as all it does is control the checking.

The `articles_analysis` table, on the other hand, should be kept clean. Database table locking is used as the mechanism to avoid race conditions. Make sure that any modifications to this table are made in an ACID fashion.


# Installing the preprocessor tools #

## Frog ##

Create a file, e.g. `/etc/apt/sources.list.d/ticc.list` and add the following line:

```
deb http://apt.ticc.uvt.nl oneiric main contrib non-free
```

Install the key, update sources, and install frog and dependencies:

```
sudo apt-key adv --keyserver keys.gnupg.net --recv-keys B15CD6AC
sudo apt-get update
sudo apt-get install frog
```

Frog is now installed, but the configuration files for the dependency triples need to be installed manually. This step can be skipped if you only want to use Frog as a lemmatizer.

```
wget -O /tmp/frog.tgz http://ilk.uvt.nl/frog/Frog.mbdp-latest.tar.gz
cd /etc/frog
sudo tar xvzf /tmp/frog.tgz
```

Now, you can run frog in daemon mode using a command such as:

```
nohup frog --skip=p -S 12345 > /tmp/frog.log 2>&1 &
nohup frog -S 12346 > /tmp/frog.log 2>&1 &
```

For the version with and without triples, respectively. These port numbers are arbitrary but are the default ones in the AmCAT frog.py module.

(Based on the [ILK](http://ilk.uvt.nl/software/build-instructions-for-software-packages/get-install.html) and [frog](http://ilk.uvt.nl/frog/) installation instructions)


## Alpino ##

Alpino provides a linux 64 bit binary on their [download site](http://www.let.rug.nl/vannoord/alp/Alpino/binary/versions/). Installation is in principle as simple as downloading and unpacking the latest version.

```
wget -O /tmp/alpino.tgz http://www.let.rug.nl/vannoord/alp/Alpino/binary/versions/Alpino-x86_64-linux-glibc2.5-19545.tar.gz
tar xvzf /tmp/alpino.tgz
```

You can test by running a simple sentence through the parser:

```
echo "het werkt" | ALPINO_HOME=./Alpino Alpino/bin/Alpino -parse
```

Probably, you will need to install one or more dependencies. On the systems I tested I specifically needed three libboost libraries of version 1.47. You can test this using:

```
LD_LIBRARY_PATH=./Alpino/util:./Alpino/fadd:./Alpino/TreebankTools/IndexedCorpus:./Alpino/create_bin:./Alpino/util ldd Alpino/create_bin/Alpino.bin
```

Unfortunately, Ubuntu currently ships with version 1.46, so you need to get those somewhere. Hopefully, 12.04 will fix this, but in the meantime you can download and install the from [here](http://wiki.amcat.googlecode.com/hg/files/):

```
wget -O /tmp/boost.tgz http://wiki.amcat.googlecode.com/hg/files/libboost_1.47.0.tgz
cd Alpino/util
tar xvzf /tmp/boost.tgz
```