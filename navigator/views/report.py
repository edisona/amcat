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
from api.rest.resources import MediumResource
from amcat.models.medium import Medium

import logging; log = logging.getLogger(__name__)

from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = "navigator/report/index.html"

class MediaView(TemplateView):
    template_name = "navigator/report/media.html"

    def get_context_data(self, **kwargs):
        return { 
            "can_add" : Medium.can_create(self.request.user),
            "media" : Datatable(MediumResource)
        }
