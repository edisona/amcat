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
Processor Scripts for the Query Framework.

In principle, a processor takes the result of an input script and
returns useful output. The processor is responsible for selecting the
fields of the input script to use.

An example processor is a tabulator. If the user selects the 'display
as table' (or graph) option, the data needs to be tabulated. For this,
the user selects the fields to be used on the horizontal and vertical
axes and the information to be used in the cells. In the case of solr
or coding data, the tabulation is doing as a (in-python) stream
operation. For db data, the tabulation is done by converting the
queryset of the db source into an aggregate queryset. The result of
tabulation is a 'matrix': a table with (generally limited) rows and
columns drawn from the selected fields and numeric cell values.

Finally, a user can select to run a custom script instead of a
tabulation. This script needs to specify its choice of columns and its
output type. *beter uitwerken*
"""

from amcat.scripts.script import Script

class Processor(Script):
    @classmethod
    def suitable_for_input(cls, input_script):
        """Return whether this processor can process the results of the given input script"""
        raise NotImplementedError()

    @classmethod
    def get_options_form(cls, project, sets, input_script):
        """
        Return the form instance specific for the given project,
        aricle sets, and input script.
        """
        raise NotImplementedError()

class ArticleList(Processor):
    """Trivial processor to allow exporting a list directly"""

class Tabulator(Processor):
    """Stream tabulator for tabulating a list"""
    
    
