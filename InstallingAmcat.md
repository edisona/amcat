

# Introduction #

This page helps new users to setup their own AmCAT instance on their
own server. This page contains a script that is tested to work on a
clean ubuntu 13.04 install, but might work on other debian like
systems (debian, ubuntu, mint) as well. The current version does not
work on Ubuntu's ``Long Term Support'' (LTS) release 12.04.
The function of the script is more a ``proof of installability'' than a tool to apply with your eyes closed.

# Basic installation #

The following installation script is tested to work on a clean install
of ubuntu 13.04 (Raring Ringtail):

```
#!/bin/bash
# Install Debian/Ubuntu packages
# 20131001 Paul Huygen
# Set the directory in which Amcat will be installed:
INSTALLDIR=~/amcat
# Make your OS up-to-date if you wish:
sudo apt-get -y update
sudo apt-get -y dist-upgrade

# Install Debian/Ubuntu packages
APT_PYTHON="python-dev python-pip"
APT_TOOLS="mercurial postgresql postgresql-contrib memcached"
APT_TOOLS="$APT_TOOLS memcached openjdk-7-jre-headless imagemagick unrtf"
# The following packages serve to install scikit-learn properly on pre-13.04 installations of Ubuntu.
# i.e. install libopenblas-dev instead of libatlas-dev and libatlas3-base.
# cf. <http://scikit-learn.org/stable/install.html>
APT_TOOLS="$APT_TOOLS build-essential python-setuptools python-scipy libopenblas-dev"
APT_LIBRARIES="libxml2-dev libxslt1-dev postgresql-server-dev-9.1 libpq-dev libxslt1-dev libxml2-dev python-dev"
sudo apt-get -y install $APT_PYTHON $APT_TOOLS $APT_LIBRARIES
# Upgrade pip
sudo easy_install -U distribute
# We need django and a lot of other Python packages
PIP_DJANGO="django django-debug-toolbar  django-sentry django_extensions django-boolean-sum"
PIP_DJANGO="$PIP_DJANGO django-compressor djangorestframework django_filter"
PIP_OTHER="solrpy lxml html2text psycopg2 openpyxl"
PIP_OTHER="$PIP_OTHER requests rdflib simplejson httplib2 cssselect"
PIP_OTHER="$PIP_OTHER unidecode jsonrpclib rtf2xml pexpect pdfminer sh"
PIP_OTHER="$PIP_OTHER beautifulsoup nltk numpy raven"
sudo pip install -U $PIP_DJANGO $PIP_OTHER
#
# Clone AmCAT Repositories
#
#
mkdir $INSTALLDIR 
cd $INSTALLDIR
hg clone https://code.google.com/p/amcat/
hg clone https://code.google.com/p/amcat.amcat-solr/ amcatsolr
hg clone https://code.google.com/p/amcat.scraping amcat/scrapers
#
# Set python path and settings module in bashrc
#
echo "export PYTHONPATH='$INSTALLDIR/amcat'" >> ~/.bashrc
echo "export DJANGO_SETTINGS_MODULE='settings'" >> ~/.bashrc
export PYTHONPATH='$INSTALLDIR/amcat'
export DJANGO_SETTINGS_MODULE='settings'
# source ~/.bashrc  # I have no idea why this doesn't work.
#
# Solr - create and install upstart file
#
SOLRCONFFILE=/etc/init/solr.conf
SOLRTMPFILE=/tmp/solr.conf
SOLRLOCATION=$INSTALLDIR/amcatsolr
cat >$SOLRTMPFILE <<EOF
description "Solr Search Server"

start on runlevel [2345]
stop on runlevel [!2345]

respawn
exec /usr/bin/java -Xms128m -Xmx1024m -Dsolr.solr.home=$SOLRLOCATION/solr -Djetty.home=$SOLRLOCATION -jar $SOLRLOCATION/start.jar >> /var/log/solr.log 2>&1
EOF
sudo mv $SOLRTMPFILE $SOLRCONFFILE
sudo start solr
#
# Create database user and db
#
sudo -u postgres createuser --superuser $USER
createdb amcat
#
# Initialize database and create superuser
#
cd $INSTALLDIR/amcat
./manage.py syncdb 
```


**LvdM:
$ psql amcat -c 'CREATE EXTENSION "uuid-ossp";**


# Running indexing daemon #
AmCAT can index articlesets for you if you're running solr. The daemon lives in `scripts/daemons/indexdaemon.py` and can be manually started by executing it. To enable indexing on startup, place the following [upstart](http://upstart.ubuntu.com/) script in `/etc/init/amcat_index.conf`:

```
description "AmCAT Index Daemon"
start on runlevel [2345]
stop on runlevel [!2345]

env AMCATROOT=/srv/amcat3.0
env PYTHONPATH=/srv/amcat3.0
env DJANGO_DB_HOST=amcatdb2
env DJANGO_SETTINGS_MODULE=amcat.settings
env DJANGO_DB_USER=amcat
env DJANGO_DB_PASSWORD="geheim!"
env DJANGO_DEBUG=0

respawn
exec /usr/bin/python $AMCATROOT/amcat/scripts/daemons/indexdaemon.py inprocess > /var/log/amcat_index.log 2>&1

```

You can run this script as a specific user, thus eliminating the need for providing a username and password. The documentation on how to do that, is available on the upstart [wiki](http://upstart.ubuntu.com/cookbook/#setuid).

If you do not do that, make sure that the upstart script with the password is not world-readable:

```
chmod 640 amcat_index.conf
```

# Testing, running webserver #

To run the webserver using django's builtin ('testing') you can use the following code:

```
cd $INSTALLDIR/amcatnavigator
./manage.py runserver
```

If all goes well, the response of the computer ends with the line "Quit the server with CONTROL-C". Leave it running and load http://127.0.0.1:8000/ in your browser. A log-in screen opens in which you can log in as user "amcat" with password "amcat".

To run the unit tests for a particular module, use code like the following: (see [UnitTests#Calling\_unit\_tests\_using\_Django](UnitTests#Calling_unit_tests_using_Django.md) for more info)

```
PYLINT=N DJANGO_DB_ENGINE=django.db.backends.sqlite3 python manage.py test amcat.TestProject
```

# Improving Postgres Performance (optional) #

This section is here mainly to avoid having to look it up every time...

(http://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server)

In order to improve performance, it is advised to increase the amount of memory available to postgres. The most important option is `shared_buffers`. The standard advice is to set this to 25% of available RAM. In `postgresql.conf`, set:

```
shared_buffers = 24MB                 # min 128kB
```

Important: If you increase `shared_buffers`, you probably also need to increase the kernel parameters SHMMAX and SHMALL. If you don't, you will get an error like:

```
$ sudo service postgresql restart
 * Restarting PostgreSQL 9.1 database server

2012-01-23 21:38:21 CET DETAIL:  Failed system call was shmget(key=5432001, size=8818180096, 03600).
2012-01-23 21:38:21 CET HINT:  This error usually means that PostgreSQL's request 
for a shared memory segment exceeded your kernel's SHMMAX parameter.  
```


You can do this by editing `/etc/sysctl.conf`. The number to set for `kernel.shmmax` is the size of the failed `shmget` call displayed in the error message. `kernel.shmall` should be this number divided by 4096 (`getconf PAGE_SIZE`):

```
kernel.shmmax=8818180096
kernel.shmall=2152876
```

Now, load the new parameters and restart postgres:

```
wva@amcat-dev:~/amcat$ sudo sysctl -p 
kernel.shmmax = 8818180096
kernel.shmall = 2152876
wva@amcat-dev:~/amcat$ sudo service postgresql restart
 * Restarting PostgreSQL 9.1 database server                [ OK ] 
```

# Running AmCAT over nginx+uwsgi #

For a production environment you probably don't want AmCAT running using the django builtin webserver. AmCAT needs a http server that can handle wsgi. Although apache + mod\_wsgi is possible, we got better results with the more lightweight ngingx plus uwsgi.

## ngingx ##

Our /etc/nginx/sites\_available/amcat.conf:

```
server {
    listen 80;
    server_name localhost;

    location /media/ {
      alias /srv/amcat3.0/amcatnavigator/media/;
    }
    location / {          
        include uwsgi_params;
        uwsgi_pass unix:///tmp/amcat.socket;
        uwsgi_read_timeout 60000;
        uwsgi_send_timeout 60000;
}

location /nginx_status {
            stub_status on;
            access_log   off;
        }
}
```

This basically serves /media files directly and passes all other requests to uwsgi.

## uwsgi ##

We don't use /etc/uwsgi/sites-enabled, but rather use an upstart script /etc/init/amcat\_uwsgi.conf:

```
description "uWSGI server for AmCAT"
start on runlevel [2345]
stop on runlevel [!2345]

env AMCATROOT=/srv/amcat3.0
env AMCATUSER=amcat
env AMCATGROUP=amcat

respawn
exec /usr/bin/uwsgi --logto /var/log/amcat_uwsgi.log --socket /tmp/amcat.socket --uid $AMCATUSER --gid $AMCATGROUP --chdir $AMCATROOT --ini $AMCATROOT/amcatnavigator/navigator_uwsgi.ini 
```


## Installation on nginx/uwsgi with conf files from repository ##

```
$ sudo apt-get install uwsgi nginx uwsgi-plugin-python
$ sudo cp $INSTALLDIR/amcatnavigator/etc/amcat_wsgi.conf  /etc/init
$ sudo cp $INSTALLDIR/amcatsolr/etc/solr.conf /etc/init
$ sudo amcat_wsgi start
$ sudo /etc/init.d/nginx restart
```

# Running AmCAT in Apache/wsgi #

If you are stubborn like me and yet want to run Amcat in Apache, proceed as follows:

  * Amcat cannot run in a subdirectory of a domain. Get/install a domain to serve amcat, e.g. `amcat.ourfineinstitute.org`.
  * Make sure that Amcat finds the domain name acceptable. Check the content of variable `ALLOWED_HOSTS` in `amcat/settings/base.py`.
  * Make sure that wsgi is activated, e.g. that directory `/etc/apache2/mods-available/` contains `wsgi.conf` and `wsgi.load`.
  * Generate a wsgi script.
  * Configure the domain in Apache. E.g. make a suitable entry in a file `/etc/apache2/sites-available/ourfineinstitute.org` and link this file to `/etc/apache2/sites-enabled/ourfineinstitute.org`
  * Restart apache2

If Amcat has been installed in `/usr/local/share/amcat`, the following is an example of a wsgi script `/usr/local/share/amcat/app.wsgi`:

```
import os
import sys

path = '/usr/local/share/amcat'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
```

In this example installation, file `/etc/apache2/sites-available/ourfineinstitute.org` might contain:

```
<VirtualHost *:80 >
    ServerName amcat.ourfineinstitute.org
    Alias /media /srv/amcat/amcat/navigator/media
    WSGIDaemonProcess amcat user=amcat group=amcat processes=1 threads=5
    WSGIScriptAlias / "/srv/amcat/amcat/app.wsgi" 
    <Directory /srv/amcat/amcat >
        WSGIProcessGroup amcat
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>
    ErrorLog /var/log/apache2/amcat-error.log
    CustomLog /var/log/apache2/amcat-access.log combined
</VirtualHost>
```

Restart apache 2 and then load amcat in your browser.
