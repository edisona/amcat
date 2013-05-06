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
from amcat.tools.caching import cached

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

from copy import copy

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

class AuthViewMixin(object):
    """
    This view aims to provide an easy way of denying / granting users access
    to resources.
    """
    # This property will be used to store modelobjects in, and can be used
    # by other views. Do not define this on your view.
    object_map = None

    # Should the objects gathered be passed to the template? (Only for
    # TemplateView's).
    pass_to_template = True

    # Assign everything in object_map to view object
    pass_to_object = True

    # Check for these globally defined permissions
    global_permissions = ()

    # Check for these permissions on the current project. If project_id is
    # not defined in the url but this variable is, a HTTP 500 will be
    # raised.
    project_permissions = ()

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

    # Use check_instances to define which models should be checked on instance
    # level. For example, defining a list with User in it will result in
    # a call to user.can_read with HTTP method == GET.
    check_instances = ()

    # When using PUT, we assume the object doesn't exist yet so it can't be
    # checked on instance level. 
    check_models = ()

    def __init__(self, *args, **kwargs):
        self.object_map = {}

        super(AuthViewMixin, self).__init__(*args, **kwargs)

    def _get_names(self, model):
        """Get url-namespace and context name for this model"""
        return self.get_kwargs_mapping()[model]

    def _get_checkfunc_name(self, http_method):
        return "can_{}".format(self.method_mapping[http_method])

    def _check_objects(self, objs):
        check_func_name = self._get_checkfunc_name(self.request.META["REQUEST_METHOD"])

        for obj in objs:
            try:
                check_func = getattr(obj, check_func_name)
            except AttributeError:
                log.warning("{obj} does not have {check_func_name} method")
            else:
                if not check_func(self.request.user):
                    raise PermissionDenied

    @cached
    def get_kwargs_mapping(self):
        return copy(self.kwargs_mapping)

    @cached
    def get_method_mapping(self):
        return copy(self.method_mapping)

    def get_instances(self, path_kwargs):
        """"""
        for mod in self.check_instances or ():
            kwarg, name = self._get_names(mod)

            if self.request.META["REQUEST_METHOD"] in self.models_methods and (
                    mod in self.check_models): 
                # Do not try to fetch not yet existing objects
                continue

            try:
                yield (name, mod.objects.get(pk=path_kwargs.get(kwarg)))
            except mod.DoesNotExist:
                raise Http404("Could not find {mod} with pk={pk}".format(pk=path_kwargs.get(kwarg), **locals()))

    def check_permissions(self):
        # Check global permissions
        for p in self.global_permissions:
            if not self.request.user.has_perm(p):
                raise PermissionDenied

        # Check if we need to check project permissions, and whether we've got
        # a project present.
        if self.project_permissions:
            # Raises KeyError if no project avaiable..
            project = self.object_map[self.get_kwargs_mapping()[models.Project][1]]

        for p in self.project_permissions:
            if not self.request.user.has_perm(p, obj=project):
                raise PermissionDenied

    def get_context_data(self, **kwargs):
        """
        If pass_to_template is true, object_map will be added to the context data
        of the template.
        """
        ctx = super(AuthViewMixin, self).get_context_data(**kwargs)

        if self.pass_to_template:
            ctx.update(self.object_map)

        return ctx
            
    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.object_map = dict(self.get_instances(kwargs))

        if self.pass_to_object:
            self.__dict__.update(self.object_map)

        # Check everything
        self._check_objects(self.object_map.values())
        self.check_permissions()

        if request.META["REQUEST_METHOD"] in self.models_methods:
            self._check_objects(self.check_models)

        # No PermissionDenied thrown!
        return super(AuthViewMixin, self).dispatch(request, *args, **kwargs)

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
