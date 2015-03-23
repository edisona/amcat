# Check #

A daily email is sent to the [amcat-scraping](http://groups.google.com/group/amcat-scraping) google group. If one or more scrapers did not work as expected:

  1. Send an email to the google group that you are working on it
  1. Re-run that scraper for that date on the development server
  1. If it does not work, try to repair the srcaper
  1. As soon as the scraper works, commit/push and run the scraper on the production server
  1. Check that the article set is now complete
  1. Send an email to the google group that the missing days are added

# Test #

The username and password of a scraper, which are required for some scrapers, can be found in the database inside the "scraper" table. The articleset should have the same value as the one under "label".
The project id is 258