

Een scraper zorgt voor de extractie van artikelen en metadata uit verschillende media. Op het moment wordt er vooral gefocust op online media zoals websites en kranten.

<br>
<h1>Modules</h1>
<h2>scraping.objects</h2>
Objecten representeren gescrapete artikelen. Elk object van deze soort bevat een property <code>props</code>, die gevuld moet worden met eigenschappen van Article-objects (zie <code>amcat.model.article.Article</code>). Deze objecten worden geretourneerd door de scrape-methoden hieronder beschreven.<br>
<br>
<br>
<h2>scraping.processors</h2>
Een processor legt de basis voor een scraper. Op het moment zijn er een aantal processors met als voornaamsten <code>Scraper</code> en <code>HTTPScraper</code>. Deze zullen behandeld worden; de overige processors behoeven (dan) geen uitleg.<br>
<br>
De eerste methode die uitgevoerd wordt door een startende scraper is <code>init</code>. Deze methode dient een index-pagina op te halen en een iterable te retourneren met daarin een <code>scraping.objects.*</code>-objecten. Elk object wordt in een work-queue gezet, om later opgepikt te worden door een <code>Worker</code>. Deze roept vervolgens de <code>get</code> methode aan, met het object als enige argument.<br>
<br>
<code>get</code> zorgt ervoor dat het artikel uiteindelijk gevuld wordt met de informatie die nodig is voor de AmCAT-database. Omdat er meerdere workers zijn, wordt <code>get</code> parallel aangeroepen - wat bij webscrapers zorgt dat ze veel sneller draaien.<br>
<br>
<h2>scraping.toolkit</h2>
Bevat tools die door meerdere scrapers handig kunnen zijn, maar niet passen in de amcat-lib.<br>
<br>
<br>
<br>
<h1>Voorbeeld (Sp!tsnieuws)</h1>
Omdat <code>amcat.scripts.script.Script</code> onze front-end verzorgt, is het zaak dat we eerst een Django Form defineren met daarin de opties die we willen aannemen, in dit geval 'date'. Ook defineren we direct met welk (amcat-)medium met deze scraper correspondeert.<br>
<br>
<pre><code>from scraping.processors import HTTPScraper, CommentScraper, Form<br>
<br>
from amcat.model.medium import Medium<br>
<br>
from django import forms<br>
<br>
class SpitsnieuwsForm(Form):<br>
    date = forms.DateField()<br>
<br>
class SpitsnieuwsScraper(HTTPScraper, CommentScraper):<br>
    options_form = SpitsnieuwsForm<br>
    medium = Medium.objects.get(name="Spits - website")<br>
<br>
    def init(self):<br>
        return []<br>
<br>
    def main(self, doc):<br>
        return []<br>
<br>
    def comments(self, doc):<br>
        return []<br>
<br>
# Zorg ervoor dat de commandline interface gestart wordt,<br>
# zodra de scraper los wordt aangeroepen.<br>
if __name__ == '__main__':<br>
    from amcat.scripts import cli<br>
    cli.run_cli(SpitsnieuwsScraper)<br>
<br>
</code></pre>

Het eerste dat opvalt is dat deze scraper geen <code>get</code> methode heeft - deze is door CommentScraper opgesplitst in <code>main</code> en <code>comments</code>. De volledige implementatie van de scraper is dan als volgt:<br>
<br>
<pre><code><br>
INDEX_URL = "http://www.spitsnieuws.nl/archives/%(year)s%(month)02d/"<br>
<br>
from scraping.objects import HTMLDocument<br>
from scraping import toolkit as stoolkit<br>
<br>
from amcat.tools import toolkit<br>
<br>
from lxml.html import tostring<br>
from urlparse import urljoin<br>
<br>
[.......]<br>
<br>
    def init(self):<br>
        date = self.options['date']<br>
        url = INDEX_URL % dict(year=date.year, month=date.month)<br>
        <br>
        for li in self.getdoc(url).cssselect('.ltMainContainer ul li.views-row'):<br>
            docdate = toolkit.readDate(li.text.strip('\n\r •:')).date()<br>
            if docdate == stoolkit.todate(date):<br>
                href = li.cssselect('a')[0].get('href')<br>
                href = urljoin(INDEX_URL, href)<br>
<br>
                yield HTMLDocument(url=href)<br>
<br>
    def main(self, doc):<br>
        doc.props.headline = doc.doc.cssselect('h2.title')[0].text<br>
        doc.props.text = doc.doc.cssselect('div.main-article-container &gt; p')<br>
<br>
        footer = doc.doc.cssselect('.article-options &gt; div')[0].text.split('|')<br>
        doc.props.author = footer[0].strip()<br>
        doc.props.date = toolkit.readDate(" ".join(footer[1:3]))<br>
<br>
        yield doc<br>
<br>
    def comments(self, doc):<br>
        divs = doc.doc.cssselect('#comments .reactiesList')<br>
<br>
        for div in divs:<br>
            comm = doc.copy()<br>
<br>
            comm.props.text = div.cssselect('p')[0]<br>
            comm.props.author = div.cssselect('strong')[0].text<br>
<br>
            dt = [t.strip() for t in div.itertext() if t.strip()][-3]<br>
            comm.props.date = toolkit.toDate(dt)<br>
<br>
            yield comm<br>
</code></pre>

Er vallen een aantal dingen op:<br>
<ul><li>HTMLDocument heeft automatisch de gedefineerde url opgehaald en in de property <code>doc</code> gezet. Deze property is een lxml.html object.<br>
</li><li>In de methode <code>comments</code> heeft <code>doc</code> automatisch een parent-waarde die verwijst naar de artikelen geyield in <code>main</code>.<br>
</li><li><code>self.getdoc()</code> wordt gebruikt om een url op te halen. <code>getdoc</code> zet de url om naar een lxml-object en probeert op verschillende wijze de encoding van een document goed te zetten.</li></ul>


<br>
<h1>Richtlijnen</h1>
<ul><li>Gebruik <code>lxml</code> in plaats van <code>BeautifulSoup</code>
</li><li>Gebruik alleen reguliere expressies als het echt nodig is.