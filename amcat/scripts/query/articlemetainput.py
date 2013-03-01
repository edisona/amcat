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
Input script that yields 'meta' data about articles, including headline and text
"""

from __future__ import unicode_literals, print_function, absolute_import
from amcat.scripts.query import input

class ArticleMetaInput(input.QueryInput):
    """QueryInput Script based on article meta data"""

    @classmethod
    def get_fields(cls, project, sets):
        return [article_field(f) for f in ['Medium', 'Author', 'Section', 'Date']]

    def _run(self, **options):
        raise Exception(options)

###########################################################################
#                          U N I T   T E S T S                            #
###########################################################################

from amcat.tools import amcattest
    
class TestArticleMetaInput(input.InputTestSetup, amcattest.PolicyTestCase):

    def test_get_sets(self):
        self.assertEqualsAsSets(ArticleMetaInput.get_sets(self.p), self.all_sets)
        
