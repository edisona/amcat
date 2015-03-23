# Database #

Legacy: The SQL Server database is backed up locally only. This is not a good thing!

The amcat database at 'amcatdev' is now considered the production database. The backup strategy currently consists of pulling it from different locations, in casu my house.

To run a full backup of the 'amcat' database at the 'amcatdev' host, use the following command:

```
pg_dump -Fc -h amcatdev -f backup_amcat_`date +%F`.sqlc  amcat
```

This will save it to a file called backup\_amcat\_YYYY-mm-dd.sqlc

# Source Code #

Source Code is backed up by virtue of being located in the google code repository.

# Other Files #

All files except for the database and source code are **not** backed up. This is intentional: all data should reside in the database and all source code in the repositories.