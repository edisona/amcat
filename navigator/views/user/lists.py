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

class BaseUserView(TemplateView):
    """Class used for menu rendering and subclassing"""
    template = "navigator/user/table.html"
    menu_item = ("Users", reverse_lazy("affiliated-users"))

class AllUsers(BaseUserView):
    menu_parent = BaseUserView
    menu_item = ("All users", reverse_lazy("all-users"))

    def _get_table(self, **filters):
        return Datatable(UserResource).filter(**filters)

    def get_context_data(self, **kwargs):
        return dict(table=self._get_table())

class AllAffiliatedUsers(AllUsers):
    menu_item = ("All affiliated users", reverse_lazy("all-affiliated-users"))

    def _get_table(self, **filters):
        return super(AllAffiliatedUsers, self)._get_table(
            userprofile__affiliation=request.user.userprofile.affiliation, **filters
        )

class AllActiveAffiliatedUsers(AllAffiliatedUsers):
    menu_item = ("Active affiliated users", reverse_lazy("affiliated-users"))

    def _get_table(self, **filters):
        return super(AllAffiliatedUsers, self)._get_table(is_active=True)

