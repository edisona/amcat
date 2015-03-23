

# Introduction #

Unit Tests are an important tool to preserve code quality. They will not catch all problems, but they will catch some, and especially prevent regressions to parts of the code that might not be tested a lot normally.

Run the unit tests before merging to the main development branch, and don't merge if any tests fail.

# How to use unit tests #

Similar to [Documentation](Documentation.md), unit testing can either be an annoying task that has to be done after the real work is done, or an integral part of development and debugging.

## Test Driven Development ##

The idea of test drive development is that the test comes before the code. When writing code, one is normally calling something to test whether it works during writing, e.g. an `if __name__ == __main__:` block. Replace this with the unit test, and just use the unit test after every change to see whether it worked. Don't be afraid to put debugging statements (print etc) in the unit test while developing, but remove them afterwards to keep the test clean.

See e.g.: http://en.wikipedia.org/wiki/Test-driven_development

In test-driven development, the development sequence is:
  1. Write a test for the new functionality
  1. Run the tests to make sure the new test fails (and no other tests do)
  1. Write a first quick, non-optimized solution
  1. Run the tests to make sure it works
  1. Optimize the solution if needed
  1. Run the tests to make sure it still works, and no regressions occurred
  1. Commit the changes (obviously, can be done after each step, presumable even best to also commit after step 4)

## Test Driven Bug Fixing ##

Similar to Test Driven Development, bug fixing is now started by writing a test that will reproduce the bug:

  1. Write a new test case that reproduces the bug. Reference the issue number/link in the test (if applicable).
  1. Run the tests to make sure it fails, and no others do.
  1. Fix the bug
  1. Run the tests to make sure they all pass
  1. If possible, try to reproduce the original bug report. If it is not fixed, update the test case to catch the problem, and repeat.
  1. Commit the changes (obviously, can be done after each step, presumable even best to also commit after step 4)
  1. Close the issue, if applicable, mentioning the mercurial changeset id in which it was closed. A good commit message is "fix for issue XXX: some substantive message". Obviously, commit early, commit often still holds.
  1. If the issue is reopened, update the test case and repeat.

## Testing Django views ##

**TODO: Can somebody who knows something about Django write this part? :-)**

# Calling unit tests using Django #

As explained below, we use the normal python unittest framework, so the tests can be called as normal. However, Django has some very useful extra functionality for testing, especially in creating a fresh 'test' database for every run, so objects can be created as needed without affecting the 'real' database.

The call to invoke all unit tests in the amcat APP is:

```
python manage.py test amcat
```

If you only want to run one test case, you can use e.g.:

```
python manage.py test amcat.TestProject
```

Don't forget to run all cases before pushing/merging!

In general, it is much quicker to run the tests on SQLite rather than postgres, since creating the database and all tables takes a number of  seconds in postgres and is instantaneous in SQLite. To make it easier to override the .amcatrc3 value, you can use the DJANGO\_DB\_ENGINE environment variable


```
DJANGO_DB_ENGINE=django.db.backends.sqlite3 python manage.py test amcat
```

**TODO: I've hacked this into amcat.settings, presumably this can be done more elegantly?**

Note: the final run before a push/merge/promotion should be done on the postgres database (because we can never be sure...)

By default, the 'policy' unit tests run pylint over all code to be tested. As this might be slow, it is possible to disable this using the PYLINT=NONE or PYLINT=ERRORS environment variables:

```
PYLINT=NONE python manage.py test amcat.TestProject
```

# Writing unit tests #

Write a unit test case by creating a class that inherits from amcattest.PolicyTestCase. Using that superclass ensures that AmCAT policy is enforced through pylint

http://docs.python.org/library/unittest.html

## Unit tests and AmCAT Policy ##

amcattest.PolicyTestCase has two test methods that enforce AmCAT policy: test\_policy\_license tests for the AmCAT license banner, and test\_policy\_pylint tests whether the module passes the pylint code checker. The latter enforces docstrings, variable names etc.

IF you think a pylint message is plain stupid, consider adding it to amcattest.PYLINT\_IGNORE. IF a pylint message is normally ok, but not for this module, create a member PYLINT\_IGNORE\_EXTRA in your testcase class.

By default, the module containing the test case is checked. If the test case is in a separate module, add that module using the TARGET\_MODULE member in the testcase class.

For example, a separate test module for testing the toolkit could start with:

```
from amcat.tools import amcattest, toolkit

class TestToolkit(amcattest.PolicyTestCase):
    TARGET_MODULE = toolkit
    PYLINT_IGNORE_EXTRA = "W0703",  # don't forget the comma!
```


## Test Case location and Django discovery ##

By default, Django looks for test cases in two locations:
  * models.py (including, via the importing there, all model files)
  * tests.py

So, for your model files you should normally have the test case in the same module, at the end.

For other files, the test case should normally be at the bottom of the module that is being tested. Then, `import *` from that module in tests.py

If the test spans multiple modules, or it would be cumbersome to include it in the target module, create a separate test\_modulename module and import that in tests.py