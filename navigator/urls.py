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

from django.conf.urls.defaults import patterns, url, include
from django.contrib.auth.views import password_change, password_change_done

from navigator.views import report
from navigator.views import project
from navigator.views import user
from navigator.views import plugin

import navigator.views.project.urls
import navigator.views.user.details
import navigator.views.user.lists

specific_user_patterns = patterns('',
    url(r'$', user.details.UserDetailView.as_view(), name='user'),
) 

user_patterns = patterns('',
    url(r'^(?P<user_id>[0-9]+)/', include(specific_user_patterns)),

    # Password recovery
    url(r'^change-password$', password_change, name='user-change-password', kwargs= {
        "template_name" : "navigator/user/change_password.html",
        "post_change_redirect"  : "change-password-done"
    }),

    url(r'^change-password-done$', password_change_done, kwargs={
        "template_name" : "navigator/user/change_password_done.html"
    }),

    # "Simple" actions
    #url(r'^add-submit$', 'navigator.views.user.add_submit', name='user-add-submit'),
    #url(r'^self$', user.view_self, "user-self"),
    #url(r'^add$', user.add, name="user-add"),

    # Report
    url(r'^active-affiliated$', user.lists.AllAffiliatedUsers.as_view(), name="affiliated-users"),
    url(r'^all-affiliated$', user.lists.AllActiveAffiliatedUsers.as_view(), name="all-affiliated-users"),
    url(r'^all$', user.lists.AllUsers.as_view(), name='all-users'),
)

specific_codingjob_patterns = patterns('',
    url(r'^export-unit$', 'navigator.views.project.project.codingjob_unit_export', name='project-codingjob-unit-export'),
    url(r'^export-article$', 'navigator.views.project.project.codingjob_article_export', name='project-codingjob-article-export'),
)

codingjob_patterns = patterns('',
    url(r'^job/(?P<codingjob_id>[0-9]+)/', include(specific_codingjob_patterns)),
    url(r'^by-coder/(?P<coder_id>\d+)/active$' ,'navigator.views.codingjob.index', name='codingjobs'),
    url(r'^by-coder/(?P<coder_id>\d+)/all$' ,'navigator.views.codingjob.all', name='codingjobs-all'),
)

urlpatterns = patterns(
    '',
    url(r'^$', report.IndexView.as_view(), name="index"),
    url(r'^media$', report.MediaView.as_view(), name="media"),
    url(r'^project/', include(project.urls)),
    url(r'^user/', include(user_patterns)),
    url(r'^codingjobs/', include(codingjob_patterns)),

    url(r'^selection$', 'navigator.views.selection.index', name='selection'),

    # Media
    url(r'^medium/add$', 'navigator.views.medium.add', name='medium-add'),

    # Plugins
    url(r'^plugins$', plugin.index, name='plugins'),
    url(r'^plugins/(?P<id>[0-9]+)$', plugin.manage, name='manage-plugins'),
    url(r'^plugins/(?P<id>[0-9]+)/add$', plugin.add, name='add-plugin'),
    
    # Coding
    #url(r'^coding/schema-editor$', 'navigator.views.schemas.index'),
    #url(r'^coding/codingschema/(?P<id>[0-9]+)$', 'navigator.views.schemas.schema',
    #    name='codingschema'),

    # Preprocessing
    url(r'^analysis/(?P<id>[0-9-]+)$', 'navigator.views.analysis.demo', name='analysis-demo'),
    url(r'^analysissentence/(?P<id>[0-9]+)$', 'navigator.views.analysis.sentence', name='analysis-sentence'),
    
    # Scrapers
    url(r'^scrapers$', 'navigator.views.scrapers.index', name='scrapers'),

    #url(r'^semanticroles$', 'navigator.views.semanticroles.index', name='semanticroles'),
    #url(r'^semanticroles/(?P<id>[0-9]+)$', 'navigator.views.semanticroles.sentence', name='semanticroles-sentence'),

) 
