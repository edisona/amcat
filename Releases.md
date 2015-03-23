# Contents #



# Introduction #

For differentiating between the development branch and stable/released branches, AmCAT uses the mercurial feature of ['Named Branches'](http://mercurial.selenic.com/wiki/NamedBranches). This means that there is a separate branch of the source tree for ongoing development and for (emergency fixes to) the stable web site.

Currently, there are two branches:

| **Branch**  | **Description** |
|:------------|:----------------|
| `default` | The development branch                |
| `3.0`     | The first 'release' of AmCAT3 |

The web server at `amcat-dev.labs.vu.nl` in principle runs the latest released version, currently 3.0.

# Policy #

In keeping with the principles of [Semantic Versioning](http://semver.org/), a version number consists of `major.minor.patch`. An increment to major means a significant and/or backwards incompatible rewrite. An increment to the minor numbers means an introduction of new features. An increment to patch means that something was fixed but no new features were added or incompatible changes were made.

This translates to mercurial branches as follows:

  * New feature development is done in the default/trunk branch (but see below)
  * A hg branch is made for each 'released version', which consists of a major.minor number (e.g. "3.1").
  * Small changes (patches) within a released branch are made by tagging that changeset with a patch version, e.g. 3.1.0 or 3.1.0-alpha
  * Releasing new features means that a new 'released branch' is made, with a new minor version number (e.g. "3.1").
  * Patches are preferably created in trunk first, then patched to the applicable released branch(es).
  * Long running development that might interfere with other work can be made in a 'feature' branch that is intended to merge back into trunk and close; this isolates the feature development from other ongoing development work. This is not preferred: if a feature can be developed incrementally without breaking other things too badly, it is best to keep development in the main branch to avoid merging problems later.

# Mercurial tags #

http://mercurial.selenic.com/wiki/Tag

In mercurial, a 'tag' is a sort of label attached to a changeset. Adding a tag makes it convenient to go back to a specific version. For example, if something went wrong in updating to 3.0.02, it is easy to just go back to 3.0.01 and then see what went wrong.

You can 'tag' a changeset by running `hg tag NAME` and then pushing. `hg tags` gives a list of existing tags and the changesets they are associated with. Internally, tags are stored in the file `.hgtags`

```
wva@yup:~/amcat$ hg tag "3.0.00"
wva@yup:~/amcat$ cat .hgtags
85d00368d57c21cdbf6aec828b7bfb3195ea609c alpha 1
1c30eaa9181516e64473b5fb65949b573538da2f 3.0.00
wva@yup:~/amcat$ hg push
pushing to https://code.google.com/p/amcat
searching for changes
remote: Success.
wva@yup:~/amcat$ hg tags
tip                             1529:772cdb887dfb
3.0.00                          1528:1c30eaa91815
alpha 1                         1476:85d00368d57c
wva@yup:~/amcat$ hg log -l 1
changeset:   1529:772cdb887dfb
branch:      3.0a1
tag:         tip
user:        Wouter van Atteveldt <wouter@vanatteveldt.com>
date:        Wed Nov 07 14:59:25 2012 +0100
summary:     Added tag 3.0.00 for changeset 1c30eaa91815
```

Since the .hgtag entry is made before the new changeset id is known, tags are applied to the previous version. As you can see in the output of hg tags above, the **old** changeset 1528 is now labeled as "3.0.00", while the new changeset 1529 (the one that introduced the tag) does not have a normal tag; the magic tag tip always points to the latest changeset.

Given the way tags work, the procedure is to first commit the changes that constitute the new 'patched version' (=tag), and then commit the tag.

# Mercurial branches #

In mercurial, use the `hg branches` command to get a list of branches, and the `hg branch` command to find out which branch you're in:

```
wva@wvametro:~/lib/amcatnavigator$ hg branches
3.0a1                        472:840be121a37a
default                      471:4f93200f7ea4
wva@wvametro:~/lib/amcatnavigator$ hg branch
default
```

On my local computer, there are two navigator branches: default and alpha 1. I'm currently 'in' branch default, so any updates will go to/from that branch.

To switch to a different branch, supply the name with the update command. Caution: this will delete any local changes!

```
wva@wvametro:~/lib/amcatnavigator$ hg branch
default
wva@wvametro:~/lib/amcatnavigator$ hg up -C 3.0a1
2 files updated, 0 files merged, 0 files removed, 0 files unresolved
wva@wvametro:~/lib/amcatnavigator$ hg branch
3.0a1
```

# How to make updates to a different branch #

If you need to make an update to a released branch, use the following procedure:

  1. Make sure that there are no local changes
  1. Pull the latest version and update to the branch
  1. Make the changes and **test whether it works**
  1. Commit the changes
  1. Update the web server
  1. Change back to the default branch

Alternatively, you can create a new clone for just that branch, but you might have to do some pythonpath fiddling...

# How to apply a changeset/patch from development to a release #

If a change made to development has to be 'backported' to a released branch to fix a 'critical' bug, the procedure is as follows:

  1. Make the change in development (and test there)
  1. Apply the change to the released branch on a development machine
  1. If it passes the test, push it to the production server

Step 1 and 3 are 'business as usual', but step 2 requires some hg commands that will be shown below:

## Make the patch ##

Use the `hg export REVISION` command to make a changeset patch from a specific revision (or list of revisions). The patch contains some metadata and the diff of the changed files. The code below shows an example where I had to change a line in the articlelist\_to\_table code to fix a bug in the 'show article list' function:

```
wva@yup:~/amcat$ hg export 1473:e0d1c0050eba > /tmp/patch
```
Let's see what we have:
```
wva@yup:~/amcat$ cat /tmp/patch
# HG changeset patch
# User Wouter van Atteveldt <wouter@vanatteveldt.com>
# Date 1349769274 -7200
# Branch trunk
# Node ID e0d1c0050eba5ab5d7ffa93b769d03cc81df48f5
# Parent  d7c84cfeed049c05b76dc6411d19907e421f1bc9
added author to column list to fix 'error running webscript'

diff -r d7c84cfeed04 -r e0d1c0050eba scripts/processors/articlelist_to_table.py
--- a/scripts/processors/articlelist_to_table.py        Sun Oct 07 17:43:07 2012 +0200
+++ b/scripts/processors/articlelist_to_table.py        Tue Oct 09 09:54:34 2012 +0200
@@ -75,6 +75,7 @@
             'externalid': table.table3.ObjectColumn('External ID', lambda a:a.externalid),
             'additionalMetadata': table.table3.ObjectColumn('Additional Metadata', lambda a:a.metastring),
             'headline': table.table3.ObjectColumn('Headline', lambda a:a.headline),
+            'author': table.table3.ObjectColumn('Author', lambda a:a.author),
             'text': table.table3.ObjectColumn('Article Text', textLambda),
             'interval':table.table3.ObjectColumn(
                 'Interval', lambda a:dateToInterval(a.date, self.options['columnInterval'])),
```

## Apply the patch to a released branch ##

Now that we have a patch, let's apply to the released branch, is this case `3.0a1`:

First, switch to that branch:

```
wva@yup:~/amcat$ hg branch
trunk
wva@yup:~/amcat$ hg up -C 3.0a1
10 files updated, 0 files merged, 0 files removed, 0 files unresolved
wva@yup:~/amcat$ hg branch
3.0a1
```

Now, import the patch:

```
wva@yup:~/amcat$ hg import /tmp/patch
applying /tmp/patch
```

This automatically makes the change as a 'committed changeset', i.e. the status will be empty, but the outgoing changes queue will contain the patch:

```
wva@yup:~/amcat$ hg st
wva@yup:~/amcat$ hg out
comparing with https://code.google.com/p/amcat/
searching for changes
changeset:   1482:4f9c953d184a
branch:      3.0a1
tag:         tip
parent:      1476:4c5acd075013
user:        Wouter van Atteveldt <wouter@vanatteveldt.com>
date:        Tue Oct 09 09:54:34 2012 +0200
summary:     added author to column list to fix 'error running webscript'
```

Now, **after we test the change**, we can push the change to the repository, go to the production server, and update. (Presumably, in the future the process of actually updating the production server will be make a bit more formal...). After pushing, it is best to branch back to the development branch to make sure you don't accidentally keep working in production. (An alternative is to use a different directory for the released branch but that might require some pythonpath fiddling to make sure that your test actually uses the code from the released branch.)

```
wva@yup:~/amcat$ hg push
pushing to https://code.google.com/p/amcat/
searching for changes
remote: Success.
wva@yup:~/amcat$ hg up -C trunk
```

(Note that development is called 'trunk' in the `amcat` repository but 'default' in `amcatnavigator`. This is something that could use unification)

Now we are ready to update the 'production' web server as usual:

```
wva@yup:~/amcat$ ssh amcat3
[...]
wva@amcat3:~$ cd /srv/amcat3.0/
wva@amcat3:/srv/amcat3.0$ sudo bash updateServer.sh 
[sudo] password for wva: 
pulling from https://code.google.com/p/amcat
searching for changes
adding changesets
adding manifests
adding file changes
added 3 changesets with 1 changes to 1 files
(run 'hg update' to get a working copy)
1 files updated, 0 files merged, 0 files removed, 0 files unresolved
pulling from https://code.google.com/p/amcat.navigator
searching for changes
no changes found
0 files updated, 0 files merged, 0 files removed, 0 files unresolved

You have requested to collect static files at the destination
location as specified in your settings.

This will overwrite existing files!
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel: yes

0 static files copied, 73 unmodified.
amcat_wsgi stop/waiting
amcat_wsgi start/running, process 9040
wva@amcat3:/srv/amcat3.0$ 
```