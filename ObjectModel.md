# Articles #

The main function of AmCAT is to store and process texts, so naturally storing texts and information about these texts takes a central place in the AmCAT database. The picture below shows the tables involved in storing texts. The `articles` table is the main table that has a row for each text (document, article) in the system. Each article is 'owned' by a single project and can be in one or more article sets, which are also owned by a project. Articles have a 'medium' that specifies their source. Finally, the text in an article can be split into sentences, which create a row per sentence in the `sentences` table.

![http://amcat.vu.nl/api/img/articles.png](http://amcat.vu.nl/api/img/articles.png)

# Projects #

As seen above, articles and article sets are owned by projects. The project is the main organising principle, and most authorisation is based on project membership. As can be seen below, a user can have a role in a project through the ProjectRole table. Roles confer a number of privileges such as being allowed to create article sets. A project also has a 'guest role': this defines what non-members are allowed to see and do in the project. Finally, users have a global role that determines whether they are allowed to create projects, users, etc.

Note that in general, an object can refer to objects from a different project. For example, an article set in project 2 can contain articles that are in project 1. This means that the owner of project 2 can modify the set, for example change the name or add/remove articles, while the owner of project 1 can modify these articles.

![http://amcat.vu.nl/api/img/projects__authorisation.png](http://amcat.vu.nl/api/img/projects__authorisation.png)

# Coding #

One of the ways to analyse text is by manual coding. Manual coding is organised in Coding Jobs: a job is a set of articles that is assigned to be coded by a specific user using a certain coding schema. A coding schema consists of a number of schema fields, each of which has a type. Jobs can have two different schemas: a schema for coding at the article level, and a schema for coding at the sentence level.

![http://amcat.vu.nl/api/img/coding_jobs.png](http://amcat.vu.nl/api/img/coding_jobs.png)