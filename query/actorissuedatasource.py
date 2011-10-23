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

import datasource 
import article
import ont2
import idlabel
import categorise
import lucenelib
import dbtoolkit
from ontologydatasource import *

from amcatmetadatasource import ConceptMapper, MappedField

def getActor(db, obj):
    lbl = obj.labels.get(15)
    if not lbl: lbl = str(obj)
    return idlabel.IDLabel(obj.id, lbl)

class ActorIssueDataSource(OntologyDataSource):
    def __init__(self, dm, db, index):
        artfield = MappedField(self, dm.getConcept("article"), ConceptMapper(db, article.Article))
        issue = SetOntologyField(self, dm.getConcept("issue"), 5002, 5000, 1, languageid=13)
        actor = SetOntologyField(self,dm.getConcept("actor"), 5003, 5000, 1, conceptmapper=ConceptMapper(db, getActor), languageid=13)
        issuearticle = OntArtField(self, dm.getConcept("issuearticle"), issue)
        coocissue = datasource.Field(self, dm.getConcept("coocissue"))
        issuecooc = datasource.Field(self, dm.getConcept("issuecooc"))


        set = SetField(self, dm.getConcept("set"))

        mappings = [
            ObjectArticleMapping(issue, artfield, db),
            ObjectArticleMapping(actor, artfield, db),
            ArticleOntArtMapping(artfield, issuearticle),
            OntArtObjectMapping(issuearticle, coocissue),
            OntArtCoocMapping(issuearticle, issuecooc),
            SetObjectsMapping(set, issue),
            SetObjectsMapping(set, actor),
            ]
        OntologyDataSource.__init__(self, dm, db, index, mappings)
        
if __name__ == '__main__':
    import dbtoolkit, ont2
    db = dbtoolkit.amcatDB()
    ont = ont2.fromDB(db)

    class Y(object): pass
    x = Y()
    x.ont = ont

    f = HierarchyOntologyField(x, None, 16104, 10002, depth=2)
    for o in f.getObjects():
        print o, f.getQuery(o)
