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
from api.rest import Datatable
from api.rest.resources import UserResource, ProjectResource

from django.views.generic import View
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse, reverse_lazy

from navigator.forms import UserForm
from navigator.menu import MenuViewMixin

class UserDetailView(MenuViewMixin, View):
    template = "navigator/user/view.html"
    form_class = UserForm

    def get_success_url():
        return reverse("user", kwargs=dict(user_id=self.request.user.id))

class SelfDetailView(UserDetailView):
    pass
