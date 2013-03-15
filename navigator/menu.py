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

from amcat.tools import toolkit
from amcat.tools.classtools import import_attribute

from django.views.generic import View, TemplateView
from django.utils.functional import Promise
from django.core.urlresolvers import resolve

import logging; log = logging.getLogger(__name__)

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

class MenuView(TemplateView):
    """
    MenuView contains two extra properties: menu_parent and menu_item. It is
    furthermore a TemplateView, which inserts a context-variable menu. This
    variable is a tuple with the first, second, .. menu levels.
    """
    menu_parent = None
    menu_item = None

    def get_menu(self):
        return _get_menu(self.request, tuple(get_empty_menu()))

    def get_menu_levels(self):
        menu = self.get_menu()

    @classmethod
    def _get_path(cls):
        return (cls.menu_item[0],) + (cls.menu_parent._get_path() if cls.menu_parent else ())

    @classmethod
    def get_path(cls):
        """
        Get the menu-path to the current view. For example:

            ("Users", "Affiliated Users")
        """
        return tuple(reversed(cls._get_path()))

    def get_context_data(self, *args, **kwargs):
        ctx = super(MenuView, self).get_context_data(*args, **kwargs)
        ctx.update({"menu" : tuple(self.get_menu_levels())})
        return ctx

### MENU RENDERING ###
def get_submenu(menu, level):
    """
    Get a sublevel of the given menu (probably returned by get_menu()). Level
    must be a tuple. For example:

    menu: [{"name" : "Users", ...}, { .. }]
    level: ("Users", "Affiliated")

    Returns None if level is not found.
    """
    # Base case
    if not level: return menu

    for sub in menu:
        if sub["name"] == level[0]:
            return get_submenu(sub["children"], level[1:])


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
    path_kwargs = resolve(request.META["PATH_INFO"]).kwargs
    path_keys = set(path_kwargs.keys())

    if isinstance(url, tuple):
        # This is a reverse_with url
        view, args, kwargs = url

        if (set(args) - path_keys):
            # There are arguments which are requested for this menu item
            # to resolve, which are not in the url.
            log.debug("Could not resolve {url} with only {path_keys} available".format(**locals()))
            return

        # We can resolve it!
        kwargs.update({ a : path_kwargs.get(a) for a in args})
        return reverse(view, kwargs=kwargs)

    # We don't know this type, probably just a string (URL)
    return url


def _get_hierarchy(views=None, parent=None):
    views = tuple(_get_views()) if views is None else views
    children = (v for v in views if v.menu_parent == parent)

    for view in children:
        yield (view, _get_hierarchy(views, view))
        
def _get_classes(module):
    attrs = (getattr(module, a) for a in dir(module))
    return (a for a in attrs if isclass(a))

def _get_views(inspect=INSPECT_MODULES):
    """Get all views which inherit from MenuView"""
    for mod in (import_attribute(m) for m in inspect):
        for view in _get_classes(mod):
            if issubclass(view, MenuView):
                yield view

###########################################################################
#                          U N I T   T E S T S                            #
###########################################################################

from amcat.tools import amcattest
from django.core.urlresolvers import reverse_lazy

class _RootTestView(MenuView):
    """This view is not used for anything but testing"""
    menu_item = ("Root", "/test/")

class MenuTest(amcattest.PolicyTestCase):
    """This test assumes there is an url with name=index"""
    class NoMenuView(View):
        pass

    class ReverseWithView(MenuView):
        menu_parent = _RootTestView
        menu_item = ("Reverse", reverse_with("index", "article_id"))

    class LazyView(MenuView):
        menu_parent = _RootTestView
        menu_item = ("Lazy", reverse_lazy("index"))

    def setUp(self):
        global _get_classes
        self._get_classes = _get_classes
        _get_classes = lambda x: [_RootTestView, self.NoMenuView, self.ReverseWithView, self.LazyView]

    def tearDown(self):
        global _get_classes
        _get_classes = self._get_classes

    def test_get_views(self):
        self.assertEquals(3, len(list(_get_views())))
        self.assertTrue(self.NoMenuView not in _get_views())
        self.assertTrue(_RootTestView in _get_views())

    def test_get_hierarchy(self):
        roots = tuple(_get_hierarchy())
        children = [c[0] for c in roots[0][1]]

        self.assertEquals(_RootTestView, roots[0][0])
        self.assertEquals(2, len(children))
        self.assertTrue(self.ReverseWithView in children)
        self.assertTrue(_RootTestView not in children)

    def test_get_empty_menu(self):
        roots = tuple(get_empty_menu())
        root = roots[0]

        self.assertEquals(1, len(roots))
        self.assertEquals("Root", root["name"])
        self.assertEquals(2, len(root["children"]))

        for child in root["children"]:
            # Check whether get_empty_menu resolves promises..
            self.assertFalse(isinstance(child["url"], Promise))

    def test_get_menu(self):
        from django.test.client import RequestFactory
        req = RequestFactory().get(reverse_lazy("index"))

        roots = tuple(get_menu(req))
        children = roots[0]["children"]

        # Of course, no reverse_with could be resolved
        self.assertFalse(all(c["url"] for c in children))

    def test_get_submenu(self):
        menu = tuple(get_empty_menu())

        self.assertEquals(1, len(get_submenu(menu, ())))
        self.assertEquals(2, len(get_submenu(menu, ("Root",))))
        self.assertEquals(0, len(get_submenu(menu, ("Root", "Lazy"))))
        self.assertEquals(None, get_submenu(menu, ("Non-existent",)))

    def test_get_path(self):
        self.assertEquals(get_path(self.LazyView), ("Root", "Lazy"))
        self.assertEquals(get_path(_RootTestView), ("Root",))

