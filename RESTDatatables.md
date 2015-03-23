# Contents #



# Introduction #

AmCAT Navigator offers a REST API which allows developers to easily interact with the database, without direct access to it. It not only offers raw data; it can also display various properties of the existing API models. This behaviour can be exploited to build rich tables, without hardcoding too much of those properties. Libraries have been written (although they are not yet standalone, but tightly coupled to AmCAT) to create tables in such a manner.

This page aims to ease the process of creating tables within the AmCAT Navigator. Skip to tutorial for a programming guide, instead of more information about the API.


# API #
The API can reveal various details about models, which are not given by default, through the HTTP OPTIONS method. This method does not allow for more arguments and will, if given, ignore them. OPTIONS returns a JSON object containing the following fields:

## description ##
This is a description of the requested model. The description matches the docstring of a class representing the model in the Python Navigator library.

## fields ##
Returns all fields which could possibly be returned by the API for the given model. Again, it is an JSON-object mapping the fieldname to the type of that field. This can be any field in the standard Django library. Examples include: `IntegerField`, `CharField` and `ModelChoiceField`.

## label ##
This property indicates how to display an object of the requested type, when displaying it in a textual manner. We use it exclusively for displaying objects in a table, but it could very well be used for other, similar purposes. The syntax is, expressed in a regular expression, `\{([^}]+)\}`. In other words, this means the following two labels are valid:

```
{headline}
Article {id}, with headline {headline}
```

An extra requirement is that a field used in a label must occur in `fields`, although this only concerns server-side developers.

## models ##
For a field of type `ModelChoiceField` an URL can be (but does not _have_ to be) given in this mapping. For example, an owner field (on project) could point to `/api/v4/user`, since it refers to an user model.

## name ##
A short name describing this API model. For example: "Article List".

## parses / renders ##
Indicates which mime-types it can interpret and display, respectively.

# Further API documentation #
Go to `/api/v4` in a local Navigator instance to receive more information about filtering, pagination and URLs.

# Programming tutorial #
We wrote an extension for datatables which uses the dynamically accessible information described above to render rich and consistent tables across the Navigator. They automatically provide pagination, filtering, single-column sorting, label-generation and "infinite" scrolling.

The Javascript code lives in `media/js/amcat.js`, specifically the functions `check_fetch_results`, `single_fetch_finished`, `fetch_labels` and `create_serverside_table` with the last being the most important for developers.

The Python code for generating tables lives in `api.rest.tools.datatable`. It contains a class `Datatable` which can be instantiated to provide easy access to common features.

## Python code ##
You first need to import the relevant Python code in the following manner:

```
from api.rest.tools.datatable import Datatable
```

Notice this can only be done from within a Django (Navigator) application. To import it when not running it, prepend `amcatnavigator` or make sure `amcatnavigator` is on your `PYTHONPATH`.

After that, you can run it easily by importing a resource (`ArticleResource` below) and instantiating it with the resource as the constructors first argument. Some methods, of which `filter` is given in an example below, are available to modify tables to specific needs.

```
p_articles = Datatable(ArticleResource).fitler(project__id=43)
p2_articles = Datatable(ArticleResource).fitler(project=Project.objects.all()[0])
some_p_articles = Datatable(ArticleResource).filter(project__id__in=[2, 3])
```

To render this table, include the needed Javascript libraries and pass the resulting objects to a template renderer. Then, in your template, write:

```
{{ p_articles|safe }}
```

Note that the `__str__` method on a `Datatable` instance renders the needed Javascript code, so you could also access it using `str(p_articles)`.For more options refer to the class' docstrings.

## Javascript code ##
To render a table using pure Javascript somewhat more (complex) function calls are needed. This needs fixing in the future (automatic resolving of columns could be automated for example), but isn't an issue for now since most of the tables are rendered using Python-code above.