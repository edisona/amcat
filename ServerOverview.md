# Index #



# Servers #

The main 'new' production servers `amcat3' (web server) and `amcatdb' (database) are both virtual servers hosted on the virtual host `sw-server'. Next to that, there is a development server `amcatdev' on an older (physical) server.

The old production servers `amcat' (web server) and `amcatsql' (database) are both physical machines which are to be removed as soon as amcat3 is live.

Note that the hostnames (esp. amcat-sql2 and amcat-dev) do not currently reflect actual status. When amcat3 is live, amcat.vu.nl will be used for the production server and the other hostnames will be remedied.

| **Nickname** | **Hostname** | **IP** | **Description** |
|:-------------|:-------------|:-------|:----------------|
| amcat3 |  `amcat‑dev.labs.vu.nl`| 130.37.193.14 | Web server (amcat3 Production) |
| amcatdb  |  | 2001:610:110:6e1:5054:ff:fe40:7f16² | (Postgres) Database (amcat3 Production) |
| amcatdev | `amcat‑sql2.vu.nl` | 130.37.31.157 |Discarded server from UCIT that is (was) supposed to replace amcatsql as the main database, but is currently functioning as the development server. It is an 1u hp server. |
| sw-server | `sw‑server.labs.vu.nl` | 130.37.193.139 | Virtual host for the `amcat3` and `amcatdb` guests |
| amcat | `amcat.vu.nl` | 130.37.31.154 | Web server (amcat2 production) **Note: use ssh port 2222!** Amcat is the name for the machine that runs the (old) web interface, ie http://amcat.vu.nl/. This is a Debian linux machine on a 1u dell server.  |
| amcatsql | `amcat-sql.vu.nl` | 130.37.31.156 / 192.168.1.3 | Database (amcat2 production) AmcatSQL is the current production database server. It is a Windows Server (2000?) running SQL Server (2000) on a 2u dell server that is getting pretty old. Note that amcat and amcalsql are connected (in addition to the normal connection via the switch) through a direct patch cable (there were spare network ports anyway...). On this network, amcat is 192.168.1.2 and amcatsql is 192.168.1.3. The 130.**address is not accessible from outside the VU Server network**|

²Linux users can install, depending on their distribution, _gogoc_ to connect to IPv6 networks.

# Passwords #

These servers are connected to the public internet and zombies will try to get in with random usernames and passwords. So please do not use an easy password (eg username or dictionary word) and please use key authentication whenever possible.

# SSH Configuration #

Below is part of my .ssh/config file that might be useful:

```
host amcat3
hostname amcat-dev.labs.vu.nl

host amcatdb
hostname 2001:610:110:6e1:5054:ff:fe40:7f16
addressfamily inet6
ServerAliveInterval 120

host amcatdev
hostname amcat-sql2.vu.nl

host swserver
hostname sw-server.labs.vu.nl

host amcat
hostname amcat.vu.nl
port 2222

Host *
  ServerAliveInterval 60
```

It is probably easier to use key authentication for ssh rather than passwords...