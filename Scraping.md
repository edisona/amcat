

# Introduction #

Scraping Internet sources is an important way of getting texts to analyse into AmCAT. Such sources can include news sites, discussion forums, twitter, etc. AmCAT has a structure in place for scraping articles that makes it easy to add new scrapers.

# Technical Overview #

Scraping involves downloading content from an Internet source, parsing the content into text and metadata (e.g. title, date, etc), and inserting this data in the database. In AmCAT, scraping is divided into two classes with separate responsibilities: `Scraper` and `Controller`. Briefly put, the scraper is responsible for downloading content and parsing it into text and metadata (the substantive part of scraping), while the controller is responsible for control flow, multithreading, error handling and logging, and inserting parsed articles into the right project in the database.

## Interface Definition ##

The Scraper interface defines two methods: `get_units` and `scrape_unit`. The former method yields arbitrary objects (such as urls or xml documents) that are than passed on to the latter method for parsing. The controller has a single method, scrape, that makes calles to these methods and to the save method of the resulting articles.

**class** `amcat.scraping.scraper.Scraper` (_subclass of_ `amcat.scripts.script.Script`)
  * **constructor**
    * parameters: Script form fields, generally information such as date, username, password
  * **method** `get_units`
    * parameters: _None_
    * returns: A sequence of arbitrary _objects_. These objects represent units to be scraped, such as urls or HTML documents. They can be (a subclass of) `amcat.scraping.document.Document` but need not be.
  * **method** `scrape_unit`
    * parameters: _object_ unit. These units are the same objects yielded by the `get_units` method.
    * returns: a sequence of `amcat.models.article.Article` ready to be saved to the database.

**class** `amcat.scraping.controller.Controller`
  * **constructor**
    * parameters: the `Project` and optional `Articleset` to insert the articles into
  * **method** `scrape`
    * parameters: a `Scraper` ready to start scraping
    * returns: a sequence of `Article` objects inserted into the database (i.e. with a valid identifier).

To make it easier to write scrapers, the `get_units` and `scrape_unit` have a default implementation that wraps around 'protected' methods `_get_units` and `_scrape_unit` (with leading underscores), that allow initialization of the scraper (e.g. logging in) and postprocessing of documents (e.g. assigning project, medium, and date, where known) by the superclass, allowing the subclass to focus on the substantive parts. See 'Writing a new scraper', below.

## Call Flow ##

The image below shows the call flow of a call to a controler to scrape an article.

![http://wiki.amcat.googlecode.com/hg/img/Scraping/scraping2.png](http://wiki.amcat.googlecode.com/hg/img/Scraping/scraping2.png)

**NOTE: This image is slightly outdated: project is now passed to the scraper and added to the project in the postprocessing method in the scraper**

Note that both get\_units() and scrape\_unit(unit) return a sequence. It is advised to do this by _yielding_ results rather than creating a list, as a multithreaded controller will probably start scraping as soon as the first unit is yielded, and likewise start saving as soon as the first article is yielded from scraping.

## Thread safety ##

There is no guarantee that the calls to `scrape_unit` will be made from a single thread or in the order that they were returned by `get_units`. So, scrape\_unit should not access any Scraper members in a thread-unsafe manner, eg iterating over and manipulating the same list or dictionary.

## Scraping and Scripts ##

AmCAT has the notion of a `amcat.scripts.script.Script` to define a runnable piece of code with options, input, and output. A Scraper is a Script subclass because it has well-defined options (e.g. date, username, password), input (None) and output (a sequence of Articles). Moreover, it can be called on the command line or web site if the needed options are provided. Making Scrapers a script makes it easier to allow plug-in of new scraper classes.

A Controller is not a Script because it can't be called without a Scraper instance, and at the moment there is no way to provide an instance as a form option. This is a technical limitation rather than a principled choice, as there is nothing wrong _per se_ with calling scrapers directly, e.g. on the command line, provided there is some way of choosing the Scraper to use.

# Writing a new scraper #

## Substantive Choices ##

Three substantive choices are important to consider before writing a new scraper.

  1. What are the parameters/arguments needed for the scraper, e.g. date, password etc. These determine the right subclass of `Scraper` to use.
  1. What are the logical _units_ to use, e.g. web pages, forum threads, newspapers articles. The optimal unit is a unit of which there are a lot of (so multithreading is useful) while determining which units is easy (so the `get_units` call is not too heavy).
  1. What is a good technical unit object to pass around, e.g. url strings or a subclass of Document.

## A minimal scraper ##

An article object needs a text, headline (title), date, medium, and project. Project is by default specified in the Scraper constructor (e.g., the input\_form fields). By inheriting from DatedScraper and specifying a class variable `medium_name`, the date and medium are also supplied. So, the following minimal scraper will insert 10 articles:

```
from amcat.scraping.scraper import DatedScraper
from amcat.models.article import Article
class MinimalScraper(DatedScraper): 
  def _get_units(self): 
    return range(10)
  def _scrape_unit(self, unit):
    yield Article(headline=str(unit), text=str(unit))
```

## A general internet scraper template ##

The general template of a scraper is as follows:

```
from amcat.scraping.scraper import DBScraper, HTTPScraper
class MyScraper(Subclass):
  def _get_units(self):
    page = download_page(self.options['date'])
    for doc in parse_page(information):
      yield doc
  
  def _scrape_unit(self, unit):
    doc = download_article(unit)
    art = parse_article(doc)
    yield art
```

Where (obviously) the download\_page, parse\_page, download\_aricle and parse\_article are placeholders for the substantive scraping code. Subclass refers to the sensible subclass of Scraper for this scraper (see below).

After creating this scraper, it can be called using the command line interface inherited from `Script`, or using one of the available controllers.

## Code overview ##

The relevant modules and classes in the amcat repository are:

  * `amcat.scraping.scraper`
    * `Scraper` - base scraper class defining the interface and command line action
    * `DatedScraper` - a scraper with a date object as argument
    * `DBScraper` - a scraper with date, username, and password as arguments (called DB Scraper because these argumentt can be instantiated from the `scrapers` database table / `amcat.models.scraper.Scraper` model object).
    * `HTTPScraper` - a scraper with an HTTPOpener attached and a getdoc convenience method to download and parse an HTML document.
  * `amcat.scraping.controller`
    * `Controller` - base controller class definining the interface and save implementation
    * `SimpleController` - a simple linear controller
    * `ThreadedController` - a controller that uses a queue for units and a number of worker threads for scraping these untis.
  * `amcat.scraping.htmltools`
    * `HTMLOpener` - auxiliary class for opening web sites using session cookies and cookie-based authentication
    * `get_unicode` - method for decoding http response content based on the encoding declared in the http header
  * `amcat.scraping.document`
    * Document - a simple class with assignable properties (e.g. `doc.headline = 'x'`) that can be converted to an Article using `doc.create_article`
    * HTMLDocument - a subclass of Document that is useful for working with `lxml` based HTML trees.
  * `amcat.models.scraper`
    * `Scraper` - model class defining a scraper class from the database (by module and class name) along with username and password needed to run this scraper. This defines the scrapers to be run regularly, as the (open) source code of the scrapers can't contain sensitive information.