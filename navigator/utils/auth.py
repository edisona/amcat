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
This module contains the authentication handling.
"""
from base64 import b64decode
from django.conf import settings
from django.contrib.auth import authenticate, login

from django.core.urlresolvers import resolve
from django.core.exceptions import PermissionDenied
from django.http import Http404
 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from functools import wraps

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View

from amcat.models.user import create_user as _create_user
from amcat.models.user import UserProfile
from amcat.models.project import Project
from amcat import models

from amcat.tools import toolkit
from amcat.tools import sendmail

import inspect
import threading

import logging; log=logging.getLogger(__name__)

def get_request():
    th = threading.current_thread()
    return th.request if hasattr(th, 'request') else None

def create_user(username, first_name, last_name, email, affiliation, language, role):
    """
    This function creates an user with the given properties. Moreover: it
    generates a passwords and emails it to the new user.

    Raises: smtplib.SMTPException, django.db.utils.DatabaseError
    """
    password = toolkit.random_alphanum(7)
    log.info("Creating new user: {username}".format(**locals()))
    
    u = _create_user(
        username, first_name, last_name, email,
        affiliation, language, role, password=password
    )
    
    log.info("Created new user, sending email...")
    html = render(get_request(), "utils/welcome_email.html", locals()).content
    text = render(get_request(), "utils/welcome_email.txt", locals()).content
    sendmail.sendmail(settings.DEFAULT_FROM_EMAIL, email, 'Welcome to AmCAT!',
                      html, text)
    log.info("Email sent, done!")
    return u

def _get_path_kwargs(request):
    return resolve(request.META["PATH_INFO"]).kwargs

class AuthView(View):
    """
    This view aims to provide an easy way of denying / granting users access
    to resources.
    """
    # This property will be used to store modelobjects in, and can be used
    # by other views. Do not define this on your view.
    object_map = None

    # Should the objects gathered be passed to the template? (Only for
    # TemplateView's)
    pass_to_template = True

    # Check for these globally defined privileges
    global_privileges = ()

    # Check for these privileges on the current project. If project_id is
    # not defined in the url but this variable is, a HTTP 500 will be
    # raised.
    project_privileges = ()

    kwargs_mapping = {
        # Model                    URL kwarg               Name in context
        models.Analysis         : ("analysis_id",          "analysis"),
        models.AnalysisSentence : ("analysis_sentence_id", "analysis_sentence"),
        models.Article          : ("article_id",           "article"),
        models.ArticleSet       : ("articleset_id",        "articleset"),
        models.CodingJob        : ("codingjob_id",         "codingjob"),
        models.CodingSchema     : ("codingschema_id",      "codingschema"),
        models.Plugin           : ("plugin_id",            "plugin"),
        models.PluginType       : ("plugin_type_id",       "plugin"),
        models.Project          : ("project_id",           "project"),
        models.User             : ("user_id",              "user")
    }

    method_mapping = { 
        "POST" : "update",
        "GET" : "read",
        "PUT" : "create",
        "DELETE" : "delete"
    }

    # Defines which (HTTP) methods check on model level. All other methods use
    # instance level verification instead.
    models_methods = ("PUT",)

    # Define these when subclassing. If a key collides with kwargs_mapping,
    # these will be used.
    kwargs_mapping_extra = None
    method_mapping_extra = None

    # Use check_instances to define which models should be checked on instance
    # level. For example, defining a list with User in it will result in
    # a call to user.can_read with HTTP method == GET.
    check_instances = ()

    # When using PUT, we assume the object doesn't exist yet so it can't be
    # checked on instance level. 
    check_models = ()

    def __init__(self, *args, **kwargs):
        self.object_map = {}
        self.kwargs_mapping_extra = self.kwargs_mapping_extra or {}
        self.method_mapping_extra = self.method_mapping_extra or {}

        super(AuthView, self).__init__(*args, **kwargs)

    def _get_names(self, mod):
        """Get url-namespace and context name for this model"""
        return self.kwargs_mapping_extra.get(mod, self.kwargs_mapping[mod])

    def _get_checkfunc_name(self, http_method):
        return "can_{}".format(self.method_mapping[http_method])

    def _check_objects(self, objs):
        check_func = self._get_checkfunc_name(self.request.META["REQUEST_METHOD"])

        for obj in objs:
            if not getattr(obj, check_func)(self.request.user):
                raise PermissionDenied

    def get_instances(self):
        """"""
        path_kwargs = _get_path_kwargs(self.request)
        for mod in self.check_instances or ():
            kwarg, name = self._get_names(mod)

            if self.request.META["REQUEST_METHOD"] in self.models_methods and (
                    mod in self.check_models): 
                # Do not try to fetch not yet existing objects
                continue

            try:
                yield (name, mod.objects.get(pk=path_kwargs.get(kwarg)))
            except mod.DoesNotExist:
                raise Http404

    def check_privileges(self):
        # Check global permissions
        for p in self.global_privileges:
            if not self.request.user.userprofile.haspriv(p):
                raise PermissionDenied

        # Check if we need to check project privileges, and whether we've got
        # a project present.
        if self.project_privileges:
            # Raises KeyError if no project avaiable..
            project = self.object_map[self.kwargs_mapping[models.Project][1]]

        for p in self.project_privileges:
            if not self.request.user.userprofile.haspriv(p, project=project):
                raise PermissionDenied

    def get_context_data(self, **kwargs):
        """
        If pass_to_template is true, object_map will be added to the context data
        of the template.
        """
        ctx = super(AuthView, self).get_context_data(**kwargs)

        if self.pass_to_template:
            ctx.update(self.object_map)

        return ctx
            
    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.object_map = dict(self.get_instances())

        # Check everything
        self._check_objects(self.object_map.values())
        self._check_objects(self.check_models)
        self.check_privileges()

        # No PermissionDenied thrown!
        return super(AuthView, self).dispatch(request, *args, **kwargs)

class RequireLoginMiddleware(object):
    """
    This middleware forces a login_required decorator for all views
    """
    def __init__(self):
        self.no_login = (
            settings.ACCOUNTS_URL,
            settings.MEDIA_URL,
            settings.STATIC_URL
        )

    def _login_required(self, url):
        """
        Check if login is required for this url. Excluded are the login- and
        logout url, plus all (static) media.
        """
        return not any([url.startswith(u) for u in self.no_login])

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated() and self._login_required(request.path):
            return login_required(view_func)(request, *view_args, **view_kwargs)

class BasicAuthenticationMiddleware(object):
    """
    This middleware tries to login a user if the Authorization-header is set. If it
    is not, it continues silently.
    """
    header = "HTTP_AUTHORIZATION"

    def _parse_header(self, header):
        """
        Parse basic auth header

        @return: (user, password)
        """
        return b64decode(header.split()[1]).split(':', 1)

    def _unauthorized(self):
        res = HttpResponse("401 Unauthorized", status=401)
        res['WWW-Authenticate'] = 'Basic realm="%s"' % settings.APPNAME_VERBOSE
        return res

    def process_request(self, request):
        assert hasattr(request, 'session'), "The Django authentication middleware\
                requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES\
                setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."

        b64 = request.META.get(self.header, None)

        # Check if header is in use
        if b64 is None:
            return

        user, passwd = self._parse_header(b64)
        user = authenticate(username=user, password=passwd)

        if user:
            login(request, user)
            return

        return self._unauthorized()

class NginxRequestMethodFixMiddleware(object):
    """
    nginx ignores the content written to the output buffer when:

    1) request.method == "POST"
    2) ~5000 > len(reponse) > 0
    3) request.POST is not read

    By reading request.POST by default, point 3 is eleminated and
    ngix will always return content.
    """
    def process_request(self, request):
        request.POST

class SetRequestContextMiddleware(object):
    """
    This middleware installs `request` in the local thread storage
    """
    def process_request(self, request):
        threading.current_thread().request = request
