###########################################################################
#          (C) Vrije Universiteit, Amsterdam (the Netherlands)            #
#                                                                         #
# This file is part of AmCAT - The Amsterdam Content Analysis Toolkit     #
#                                                                         #
# AmCAT is free software: you can redistribute it and/or modify it under  #
# the terms of the GNU Affero General Public License as published by the  #
# Free Software Foundation, either version 3 of the License, or (at your  #
# option) any later version.                                              #
#                                                                         #
# AmCAT is distributed in the hope that it will be useful, but WITHOUT    #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or   #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public     #
# License for more details.                                               #
#                                                                         #
# You should have received a copy of the GNU Affero General Public        #
# License along with AmCAT.  If not, see <http://www.gnu.org/licenses/>.  #
###########################################################################

"""
Scripts for the Query facilities in AmCAT

The 'query' tab in a project is the main page for extracting, filtering, procesing, visualising
and/or exporting information from AmCAT projects. This information can consist of purely information
about the articles in the database (called 'db'), information from the solr full text index
('solr'), or from the stored results of manual coding ('coding'). 

Each query is executed by running an input script and optionally a processor. The input script gets
the information from the database, solr, or coding and returns a "list", i.e. a table of fields on
articles*. The options for the input scripts are the article set(s) to use as source, any filters on
the available fields, and the fields to include in the output.

If the user selects the 'Article List' output option this is the only script that is used, and the
resulting table is returned to the user in a requested output format (ie json for the datatables or
csv/excel/etc for exporting to a file.

If the user selects the 'display as table' (or graph) option, the data needs to be tabulated. For
this, the user selects the fields to be used on the horizontal and vertical axes and the information
to be used in the cells. In the case of solr or coding data, the tabulation is doing as a
(in-python) stream operation. For db data, the tabulation is done by converting the queryset of the
db source into an aggregate queryset. The result of tabulation is a 'matrix': a table with
(generally limited) rows and columns drawn from the selected fields and numeric cell values.  

Finally, a user can select to run a custom script instead of a tabulation. This script needs to
specify its choice of columns and its output type. *beter uitwerken*
"""
