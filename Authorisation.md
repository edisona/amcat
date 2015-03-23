# Introduction #

AmCAT authorisation works at two levels. At the system level, authorisation determines whether a user can view or create other projects and users. Within a project, it determines whether a user can see that project, add articles and article sets, assign coding jobs etc.

AmCAT has four concepts related to authorisation:
  * **Privilege**`s` (aka permissions) are specific actions that a user might want to do, such as `add_articles`. Each privilege is connected to a Role.
  * **Role**`s` are hierarchical 'bundles' of privileges: a `super user` can do more than a normal user, but less than an `admin`.
  * **User**`s` have a system Role and can have a Role in one or more projects. In general, a user can delegate any role it has to another user.

# Implementation #

Since users can access AmCAT from outside Django (e.g. through direct database access or command-line python scripts), authentication and authorisation are handled by the database where possible.

Each user has an account on the database, and authentication is performed by logging on the database as that user. Currently, authorisation is handled by django, but this should be performed at the database as well (e.g. through stored procedures).