

# Repository #

We (will) use a single repository with named branches for releases.

The repository for the amcat source code is located at google code. AmCAT is the 'default' repository under the amcat project, amcatnavigator and amcatscraping are the .scraping and .navigator subrepositories:

  * Amcat: https://code.google.com/p/amcat
  * Navigator:  https://code.google.com/p/amcat.navigator
  * Scraping : https://code.google.com/p/amcat.scraping
  * Solr: https://code.google.com/p/amcat.amcat-solr

# Some common tasks #

## My .hgrc file ##

The .hgrc file below sets up your user name and authentication with google.

```
[ui]
username = Wouter van Atteveldt <wouter@vanatteveldt.com>
merge = internal:merge


[trusted]
groups=amcat

[extensions]
convert=
color =
hgext.graphlog = 
fetch =


[auth]
google.prefix = https://code.google.com/
google.username = vanatteveldt
google.password = geheim!

[web]
cacerts = /etc/ssl/certs/ca-certificates.crt
```

The password for google code is **not** your default ("gmail") password, but a special googlecode password that can be found at:

https://code.google.com/hosting/settings


## Setting up on a new computer / folder ##

To start development, simply clone the main repository. Since the module structure assumes that the parent directories of the repositories you use should be on your pythonpath, it is easiest to create a folder and clone these three repositories there, and add amcat3 to the pythonpath. Since google uses a period to separate default and sub repository, and we use the reponame as part of the module structure, you need to specify the correct name for scraping and navigator:

```
mkdir amcat3
cd amcat3
hg clone https://code.google.com/p/amcat
hg clone https://code.google.com/p/amcat.scraping amcatscraping
hg clone https://code.google.com/p/amcat.scraping amcatnavigator
```

## Making a release branch ##

To be written

## Making a quick bugfix in a release branch ##

To be written


## Copying ('backporting'?) a change from development to a release branch ##

To be written

## Creating a short lived development 'branch' ##

Sometimes, you want to share changes between workplaces and/or with others without being ready to push to the main development branch.

In keeping with the guidelines on mercurial.com ([use branch names sparingly and for rather longer lived concepts like "release branches"](http://mercurial.selenic.com/wiki/Branch#Named_branches), [it is almost never a good idea to use (named branches) for short-term branching](http://mercurial.selenic.com/wiki/BranchingExplained#line-67)), we don't use branches for this.

The first guideline is "push it anyway", as the cost of a bad commit is normally not so high, and probably lower than divergent lines of development.

However, in the case where you don't want to do it, the hg approach seams to be using cloning rather than branching. What you want to do is make your locally cloned folder available for others / from elsewhere. If you develop on an ssh-connected machine, this is already the case. Otherwise, it seems that scp'ing your local folder to eg amcatsql2 is the easiest solution.

So, let's assume I am working 'thuis' and want to continue working on my current changes at 'vu', and at some point merge them back in. Instead of 'thuis'/'vu' you can also think 'wva'/'martijn'.

```
thuis$ scp amcat amcatsql2:~/amcatdev/ # make repo available
thuis$ rm -rf amcat # change local 'copy' into clone 
thuis$ hg clone ssh://amcatsql2/~/amcatdev/amcat
```
fietsfiets
```
vu$ hg clone ssh://amcatsql2/~/amcatdev/amcat
vu$ cd amcat
vu$ # do some work
vu$ hg commit -m werk && hg push  # push naar tijdelijk repo
```
fietsfiets
```
thuis$ cd amcat
thuis$ hg pull && hg up
thuis$ # do some more work
thuis$ hg commit -m "meer werk" && hg push
# <ready! time to push/merge back into development>
thuis$ ssh amcatsql2
amcatsql2$ cd amcatdev/amcat
amcatsql2$ hg pull # what changed?
amcatsql2$ hg merge # plus conflict resolution if needed
amcatsql2$ hg ci -m "merged" && hg push # push to main repo
amcatsql2$ cd ..
amcatsql2$ rm -rf amcat #discontinue this 'branch'
```

Obviously, the first three steps can be skipped if 'thuis' is accessible over the internet.

Please take care that these extra repositories don't become long lived, as nobody likes divergent code lines, aka forks!