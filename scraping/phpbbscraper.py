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
A Scraper for the most common internet forum.
"""

from amcat.scraping.document import HTMLDocument
from amcat.scraping.scraper import HTTPScraper
from urlparse import urljoin, urlunsplit, parse_qs, urlsplit
from urllib import urlencode

from amcat.tools import toolkit

class PhpBBScraper(HTTPScraper):
    index_url = None
    medium_name = "PhpBB - forum"
    
    def _login(self, username, password):
        form = self.getdoc(self.index_url).cssselect('form')[0]

        self.opener.open(form.get('action'), urlencode({
            'user' : username,
            'passwrd' : password,
            'cookielength' : '-1'
        })).read()
    
    def _get_units(self):
        """
        PhpBB forum scraper
        """
        index = self.getdoc(self.index_url)

        for cat_title, cat_doc in self.get_categories(index):
            for page in self.get_pages(cat_doc):
                for fbg in page.cssselect('.forumbg'):
                    if 'announcement' in fbg.get('class'):
                        continue

                    for a in fbg.cssselect('.topics > li a.topictitle'):
                        url = urljoin(self.index_url, a.get('href'))
                        yield HTMLDocument(headline=a.text, url=url, category=cat_title)

    def get_pages(self, page):
        """Get each page specified in pagination division."""
        
        yield page # First page, is always available
        
        nav = page.cssselect('.pagination')[0]

        if len(nav.cssselect('a')) > 1:
            # Pagination available    

            try:
                pages = int(nav.cssselect('a')[-1].text)
            except ValueError: # "volgende", "next" etc.
                pages = int(nav.cssselect('a')[-2].text)

            spage = nav.cssselect('a')[0].get('href')
            
            url = list(urlsplit(spage))
            query = dict([(k, v[-1]) for k,v in parse_qs(url[3]).items()])
            try:
                ppp = int(query['start'])
            except:
                ppp = 0
            
            for pag in range(1, pages):
                query['start'] = pag*ppp
                url[3] = urlencode(query)
                
                yield self.getdoc(urljoin(self.index_url, urlunsplit(url)))

    def get_categories(self, index):
        """
        @yield: (category_name, lxml_doc)
        """
        hrefs = index.cssselect('.topiclist a.forumtitle')

        for href in hrefs:
            url = urljoin(self.index_url, href.get('href'))
            yield href.text, self.getdoc(url)
    
    def _scrape_unit(self, thread):
        fipo = True # First post
        thread.doc = self.getdoc(thread.props.url)
        for page in self.get_pages(thread.doc):
            for post in page.cssselect('.post'):
                ca = thread if fipo else thread.copy(parent=thread)
                ca.props.date = toolkit.readDate(post.cssselect('.author')[0].text_content()[-22:])
                ca.props.text = post.cssselect('.content')
                
                title = post.cssselect('.postbody h3 a')[0].text
                if fipo:
                    optitle = title
                if title:
                    ca.props.headline = title
                else:
                    ca.props.headline = 're: {}'.format( optitle )

                try:
                    ca.props.author = post.cssselect('.author strong')[0].text_content()
                except:
                    try:
                        ca.props.author = post.cssselect('.author a')[0].text_content()
                    except:
                        # Least reliable method
                        ca.props.author = post.cssselect('.author')[0].text_content().split()[0]

                yield ca

                fipo = False
