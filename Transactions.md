# Introduction #

When using Django for more complicated tasks the default 'autocommit' strategy is often not optimal. This document describes how django manages transactions and ways to use this in amcat.

Putting multiple operations in one transaction can improve consistency (related operations in one transaction are committed or rolled back together 'atomically') and performance (commits take time, each commit is a db round trip). However, it also means locks are kept longer. So, do not put long calculations in the middle of a transaction; rather, calculate first and cluster all database calls in one quick transaction.

A final consideration is that postgres transactions can be in an 'aborted' state: if a save() throws and error but is not explicitly rolled back, the connection is 'aborted', meaning any further command will raise the dreaded 'transaction is aborted' error. This means that is is probably a good idea to use  the [commit\_on\_success decorator](#Management_summary:_Use_the_commit_on_success_decorator.md) on all data modifying code.

# Django transaction management #

https://docs.djangoproject.com/en/dev/topics/db/transactions/

In django, mutations are by default auto-commit: as soon as save(), update() etc. are called, the transaction is committed. This is often not the best behaviour: if a procedure creates two related objects, we generally want either both mutations to be committed or both rolled back.

Transaction management is done by the `django.db.transactions` module, which is a very thin layer on the `django.db.backends` package.

## Management summary: Use the commit\_on\_success decorator ##

Most code only needs to use the `transactions.commit_on_success` decorator, which puts a whole function in an atomic transaction.

```python

from django.db import transaction
@transaction.commit_on_success
def complex_operation():
p = create_parent()
create_child(p)
```

The (untested) snippet above makes sure than an error in `create_child` does not leave a childless parent. If this is all you need to do, you can stop reading :-)

## Transaction management ##

Django records whether transactions are "managed" or not, which is a state. The pair or `{enter,leave}_transaction_management` calls controls this. Since management is a stack the leave should always be called, so put it in a `finally` block. After entering the management, indicate whether you want to manage or not using the `managed` function. So, a typical piece of code to use manual transaction management is:

```python

def manual_transaction():
transaction.enter_transaction_management()
transaction.managed()
try:
do_something()
finally:
transaction.leave_transaction_management()
```

This functionality is also provided by the 'manual\_commit' decorator

```python

@transaction.commit_manually
def decorator_transaction():
do_something()rely on
```

## Committing and Rolling back ##

Note that the code above should still commit or rollback manually. This is possible using the `commit()` and `rollback()` functions. The standard pattern is as follows:

```python

@transaction.commit_manually
def decorator_transaction():
try:
do_something()
except:
transaction.rollback()
raise
else:
transaction.commit()
```

Since this pattern is used frequently, it is provided by the `commit_on_success` decorator showcased above. Using the manual commit and rollback functions is more natural if you want to use a try/except clause anyway. If you combine commit\_on\_success with manual try/except, do not forget to raise an exception from the except clause if you want to rollback the transaction!

# Example code #

The code below showcases the different ways of managing transactions in a python unit test suite:

```python

"""
Shows/tests how django transaction management works
See https://docs.djangoproject.com/en/dev/topics/db/transactions/
and /usr/shared/pyshared/django/db/transaction.py

set log_statement = 'all' in postgresql.conf to see commands sent
to the database, very useful for figuring this stuff out!
"""
rely on
import unittest
from contextlib import contextmanager

from django.db import transaction
from django.db.utils import DatabaseError
from django.db import connections, DEFAULT_DB_ALIAS

from amcat.models.article import Medium

def error():
"""Throw a db error"""
list(Medium.objects.raw("dit is onzin"))

def count():
"""List the # of media, implicit check that transaction is not aborted"""
return Medium.objects.count()

def create():
"""create a new medium, increasing count by one if committed"""
Medium(name='TEST MEDIUM DO NOT USE').save()

def ignore_error():
"""Cause and ignore a db error, brining postgres in 'aborted' state"""
try:
error()
except DatabaseError as e:
pass


def manual_rollback():
"""Create and rollback using manual transaction calls"""
transaction.enter_transaction_management()
transaction.managed()
try:
try:
create()
error()
except:
transaction.rollback()
else:
transaction.commit()
finally:
transaction.leave_transaction_management()

@transaction.commit_on_success
def automatic_rollback():
"""Create and rollback using the commit_on_success decorator"""
create()
ignore_error()


@transaction.commit_on_success
def create_and_commit():
"""Create a record with a 'commit on success' strategy"""
create()

@transaction.commit_manually
def create_commit_rollback():
"""
Commit and Rollback in one function using commit_manually decorator
"""
create()
transaction.commit()
try:
create()
error()
except:
transaction.rollback()
else:
transaction.commit()

def log(txt):
sql = "\n--------------------\nselect '%s'\n--------------------" % txt
connections[DEFAULT_DB_ALIAS].cursor().execute(sql)


class TestTransactions(unittest.TestCase):

def setUp(self):
log("Entering %s" % self._testMethodName )

def tearDown(self):
log("Leaving %s" % self._testMethodName )

def assertRaisesDBError(self, cmd, error, *args, **kargs):
try:
cmd(*args, **kargs)
except DatabaseError as e:
# very low level rollback, only used here to reset 'dirtyness'
connections[DEFAULT_DB_ALIAS].connection.rollback()
if error:
self.assertIn(error, str(e))
else:
self.fail("Database error %r not raised" % error)

def test_error(self):
"""Test raising an error and low level rollback fix"""
self.assertRaisesDBError(error, None)
count()

def test_ignore(self):
"""Test unclean transaction after 'naive'"""
c = count()
ignore_error()
self.assertRaisesDBError(count, "transaction is aborted")

def test_manual(self):
"""Test clean rollback with manual calls"""
c = count()
manual_rollback()
self.assertEqual(c, count())

def test_automatic(self):
"""Test clean rollback with @commit_on_success decorator"""
c = count()
automatic_rollback()
self.assertEqual(c, count())


def test_create_and_commit(self):
"""Test that a 'committed' transaction is not rolled back"""
c = count()
create_and_commit()
self.assertEqual(c+1, count())

def test_create_commit_rollback(self):
"""Test committing and rolling back two transactions in one function"""
c = count()
create_commit_rollback()
self.assertEqual(c+1, count())

if __name__ == '__main__':
unittest.main()
```