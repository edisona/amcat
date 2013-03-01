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
Input script that yields information from the manual coding results
(in addition to article meta data)
"""

from __future__ import unicode_literals, print_function, absolute_import
from amcat.scripts.query import input

class CodingInput(input.QueryInput):
    """QueryInput Script based on manually coded data"""
    @classmethod
    def get_sets(cls, project):
        """Use only sets that are used as a coding job"""
        return super(CodingInput, cls).get_sets(project).filter(codingjob_set__isnull=False)
