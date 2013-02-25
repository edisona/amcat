from amcat.models import Project, ArticleSet
from amcat.tools import amcattest

def setup_test():
    p = amcattest.create_test_project()
    us1, us2, is1, is2, cs1, cs2 = [amcattest.create_test_set(project=p, articles=5+i) for i in range(6)]
    return locals()


if __name__ == '__main__':
    setup_test()
