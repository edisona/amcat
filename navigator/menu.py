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
This module contains all logic which is needed to render all menu's within
the navigator. Since 3.2 it is really simplified, and hopefully well-
documented.

The main idea is very simple: there are primary, secundary, .. menu's, which
all have a items (menu-items). All these items point to a resource, somewhere
internal or external.

= Implementing =
In order to implement a menu-item on your view you need to do two things:

 1) Define menu_parent and menu_item
 2) Import views to this menu

An example could be:

 class TestView(View):
    menu_parent = SomeView
    menu_item = ("My project", reverse_lazy("test"))

"""

from inspect import isclass
from itertools import groupby

from amcat.tools import toolkit
from amcat.tools.classtools import import_attribute

from django.views.generic import View
from django.utils.functional import Promise

INSPECT_MODULES = ["navigator.views"]

### MENU TOOLS ###
def reverse_with(view, *args, **kwargs):
    """
    An url will be generated using django's reverse() with the provided kwargs
    and the "filled" args. So, when "project_id" is passed as an (non-keyword)
    argument it is filled using the arguments provided in the current requests
    url.
    """
    return (view, args, kwargs)

### MENU RENDERING ###
def get_menu(request):
    """
    Get a menu structure based in imported views, filled in according to the
    current request.
    """
    return _get_menu(request, get_empty_menu())

def get_empty_menu(views=None):
    """Returns an iterator with dictionaries, each representing a menu-item.
    
    TODO: This function can be cached per Python session. It needs to be
    serialised and deserialised, because the returned objects are used
    and modified in other functions."""
    views = _get_hierarchy() if views is None else views

    for view, children in views:
        dest = view.menu_item[1]

        yield {
            "name" : view.menu_item[0],
            # Resolve Django Promises so this function can be cached.
            "url" : str(dest) if isinstance(dest, Promise) else dest,
            "children" : tuple(get_empty_menu(children))
        }

### PRIVATE HELPER FUNCTIONS ###
def _get_menu(request, menu):
    for sub in menu:
        sub.update({
            "url" : _get_url(request, sub["url"]),
            "children" : _get_menu(request, sub["children"])
        })

    return menu

def _get_url(request, url):
    # To resolve reverse_with urls, we neeed the kwargs of the currently
    # requested url.
    path_kwargs = resolve(request.META["PATH_INFO"])
    path_keys = set(path_kwargs.keys())

    if isinstance(url, tuple):
        # This is a reverse_with url
        view, args, kwargs = url

        if (set(args) - path_keys):
            # There are arguments which are requested for this menu item
            # to resolve, which are not in the url.
            return

        # We can resolve it!
        kwargs.update({ a : path_kwargs.get(a) for a in args})
        return reverse(view, kwargs=kwargs)

    # We don't know this type, probably just a string (URL)
    return url


def _get_hierarchy(views=None, parent=None):
    views = tuple(_get_views()) if views is None else views
    children = (v for v in views if getattr(v, "menu_parent", None) == parent)

    for view in children:
        yield (view, _get_hierarchy(views, view))
        
def _get_django_views(module):
    attrs = (getattr(module, a) for a in dir(module))
    return (a for a in attrs if isclass(a) and issubclass(a, View))

def _get_views(inspect=INSPECT_MODULES):
    """Get all views with either a menu_parent or menu_item property defined"""
    for mod in (import_attribute(m) for m in inspect):
        for view in _get_django_views(mod):
            if hasattr(view, "menu_item"):
                yield view

