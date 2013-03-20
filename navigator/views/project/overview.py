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

from navigator.menu import MenuView
from navigator.utils.auth import AuthView

from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.forms.models import modelform_factory

from api.rest import Datatable
from api.rest.resources import ProjectResource

from amcat.models import Project

"""
This module contains all pages with links to projects (my projects,
all projects, active projects..)
"""

__all__ = ("ProjectOverview", "ProjectEdit")

class ProjectOverview(AuthView, MenuView, TemplateView):
    template_name = "navigator/project/overview/view.html"
    check_instances = (Project,)

class ProjectEdit(AuthView, MenuView, FormView):
    template_name = "navigator/project/overview/edit.html"
    form_class = modelform_factory(Project, exclude=("insert_user",))
    succes_url = reverse_lazy("bla")
    check_instances = (Project,)

    def get_form_kwargs(self, **kwargs):
        return dict(instance=self.object_map["project"])

