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
This module contains all views which render users-lists.
"""

from api.rest import Datatable
from api.rest.resources import UserResource

from django.views.generic import TemplateView
from django.core.urlresolvers import reverse_lazy

class AllUsers(TemplateView):
    def _get_table(self, **filters):
        return Datatable(UserResource).filter(**filters)

    def get_context_data(self, **kwargs):
        ctx = super(AllUsers, self).get_context_data(**kwargs)
        ctx.update({"table":self._get_table()})
        return ctx

class AllAffiliatedUsers(AllUsers):
    def _get_table(self, **filters):
        return super(AllAffiliatedUsers, self)._get_table(
            userprofile__affiliation=request.user.userprofile.affiliation, **filters
        )

class AllActiveAffiliatedUsers(AllAffiliatedUsers):
    def _get_table(self, **filters):
        return super(AllAffiliatedUsers, self)._get_table(is_active=True)

