import re
from amcat.models.article import Article

def run():
    articles = Article.objects.filter(articlesetarticle__articleset = 124)
    p = re.compile("/xda-teletekst/index.jsp\?page=TTARTICLE_PAGE_([0-9]{3})_[0-9]{2}.htm")
    for a in articles:
        match = p.search(a.url)
        if match:
            a.pagenr = match.group(1)
            print(a.pagenr)
            a.save()
        

if __name__ == "__main__":
    run()
