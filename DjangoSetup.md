AmCAT uses [Django](https://www.djangoproject.com) both for the ORM and the web framework. However, AmCAT also differs from regular Django projects in at least two ways. These differences are caused by AmCAT being principally a 'database that needs a front-end' rather than a 'web site that needs a back-end':

  1. The Django object layer (ORM) is also used outside the context of the web site. For this reason, the `amcat` repository contains the object layer and auxilliary modules, while the `amcatnavigator` contains the web code and depends on `amcat`. `amcat` is a Django App but not a web site.
  1. We expect users to access the database directly, not just through the web site, web service, or ORM. Django offers a lot of nice ways to query the database, but nothing beats raw SQL for some (mainly one-time) purposes. Also, open access and standards are part of the AmCAT philosophy, and SQL is much more general and flexible than either Django or web services. A result of this is that we can't rely on Django to do authentication and authorisation, but rather have the database do authentication and (final) authorisation.

In the `amcat` repository root folder, there are a number of files that provide django functionality:

  * `settings.py`: general django settings, importing most user settings (including database details) from `~/.amcatrc3`
  * `manage.py`: executable python script to access django functions, like syncdb and test
  * `models.py`: module importing all models included in the 'amcat' django app
  * `tests.py`: module importing all unit tests except for those included in the models
  * `initial.data.json`: initial database records required for a functioning system, including authorisation, admin user etc.
