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

from navigator.utils.auth import AuthViewMixin

from django.views.generic import View
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.models import User
from django.forms.models import modelform_factory

#from navigator.forms import UserForm
from navigator.menu import MenuViewMixin
from django.utils.datastructures import MergeDict

class UserDetailView(AuthViewMixin, MenuViewMixin, FormView):
    template_name = "navigator/user/details/view.html"
    form_class = modelform_factory(User, exclude=("password", "user_permissions", "groups"))
    check_instances = (User,)

    def get_table(self):
        return Datatable(ProjectResource).filter(projectpermission__user=self.user)

    def get_context_data(self, **kwargs):
        return MergeDict(
            super(UserDetailView, self).get_context_data(**kwargs),
            {"projects" : self.get_table()}
        )

    def get_success_url():
        return reverse("user", kwargs=dict(user_id=self.user.id))

class SelfDetailView(UserDetailView):
    # A user can always edit / view itself, so we don't need additional checks
    def dispatch(self, request, *args, **kwargs):
        kwargs[self.kwargs_mapping[User][0]] = request.user.id
        return super(SelfDetailView, self).dispatch(request, *args, **kwargs)

