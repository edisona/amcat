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

from navigator.menu import MenuViewMixin
from api.rest import Datatable
from api.rest.resources import ProjectResource
from django.views.generic.base import TemplateView

"""
This module contains all pages with links to projects (my projects,
all projects, active projects..)
"""

__all__ = ("MyProjects", "AllProjects", "MyActiveProjects")

class AllProjects(MenuViewMixin, TemplateView):
    template_name = "navigator/project/report.html"
    title = "All projects"

    def get_table(self):
        return Datatable(ProjectResource, rowlink="./{id}")

    def get_context_data(self, **kwargs):
        ctx = super(AllProjects, self).get_context_data(**kwargs)
        ctx.update({"table":self.get_table(), "title":self.title})
        return ctx

class MyProjects(AllProjects):
    title = "My projects"

    def get_table(self):
        return (super(MyProjects, self).get_table()
            .filter(projectpermission__user=self.request.user))

class MyActiveProjects(MyProjects):
    title = "My active projects"

    def get_table(self):
        return super(MyActiveProjects, self).get_table().filter(active=True)

