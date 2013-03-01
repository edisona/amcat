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

from django.conf.urls.defaults import patterns, url
from django.contrib.auth.views import password_change, password_change_done

from navigator.views import report
from navigator.views import project

urlpatterns = patterns(
    '',
    url(r'^$', report.IndexView.as_view(), name="index"),
    url(r'^media$', report.MediaView.as_view(), name="media"),
    url(r'^project/', include(project.urls)),

    # User report
    url(r'^users$', 'navigator.views.user.my_affiliated_active', name='users'),
    url(r'^users/my_all$', 'navigator.views.user.my_affiliated_all'),
    url(r'^users/all$', 'navigator.views.user.all', name='all-users'),

    url(r'^selection$', 'navigator.views.selection.index', name='selection'),

    # Media
    url(r'^medium/add$', 'navigator.views.medium.add', name='medium-add'),

    # Users
    url(r'^user/(?P<id>[0-9]+)?$', 'navigator.views.user.view', name='user'),
    url(r'^user/edit/(?P<id>[0-9]+)$', 'navigator.views.user.edit', name='user-edit'),
    url(r'^user/add$', 'navigator.views.user.add', name='user-add'),
    url(r'^user/add-submit$', 'navigator.views.user.add_submit', name='user-add-submit'),
    url(r'^user/change-password$', password_change, name='user-change-password',
        kwargs=dict(
            template_name="navigator/user/change_password.html",
            post_change_redirect='change-password-done'
        )),
    url(r'^user/change-password-done$', password_change_done,
        kwargs=dict(
            template_name="navigator/user/change_password_done.html"
        )),


    # Plugins
    url(r'^plugins$', 'navigator.views.plugin.index', name='plugins'),
    url(r'^plugins/(?P<id>[0-9]+)$', 'navigator.views.plugin.manage', name='manage-plugins'),
    url(r'^plugins/(?P<id>[0-9]+)/add$', 'navigator.views.plugin.add', name='add-plugin'),
    
    # Coding
    url(r'^coding/schema-editor$', 'navigator.views.schemas.index'),
    url(r'^coding/codingschema/(?P<id>[0-9]+)$', 'navigator.views.schemas.schema',
        name='codingschema'),
    url(r'^codingjob/(?P<codingjob>[0-9]+)/export-unit$', 'navigator.views.project.codingjob_unit_export', name='project-codingjob-unit-export'),
    url(r'^codingjob/(?P<codingjob>[0-9]+)/export-article$', 'navigator.views.project.codingjob_article_export', name='project-codingjob-article-export'),


    #url(r'^codingjobs/(?P<coder_id>\d+|all)/(?P<status>all|unfinished)/$' ,'navigator.views.codingjob.index', name='codingjobs'),
    #url(r'^codingjobs$' ,'navigator.views.codingjob.index', name='codingjobs'),
    url(r'^codingjobs/(?P<coder_id>\d+)?$' ,'navigator.views.codingjob.index', name='codingjobs'),
    url(r'^codingjobs/(?P<coder_id>\d+)/all$' ,'navigator.views.codingjob.all', name='codingjobs-all'),

    # Preprocessing
    url(r'^analysis/(?P<id>[0-9-]+)$', 'navigator.views.analysis.demo', name='analysis-demo'),
    url(r'^analysissentence/(?P<id>[0-9]+)$', 'navigator.views.analysis.sentence', name='analysis-sentence'),
    
    # Scrapers
    url(r'^scrapers$', 'navigator.views.scrapers.index', name='scrapers'),


    url(r'^semanticroles$', 'navigator.views.semanticroles.index', name='semanticroles'),
    url(r'^semanticroles/(?P<id>[0-9]+)$', 'navigator.views.semanticroles.sentence', name='semanticroles-sentence'),

) 
