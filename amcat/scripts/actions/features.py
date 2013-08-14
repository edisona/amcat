#!/usr/bin/python

##########################################################################
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

import logging; log = logging.getLogger(__name__)
from functools import partial

from django import forms

import collections
from amcat.scripts.script import Script
from amcat.tools.amcatsolr import Solr, filters_from_form
from amcat.tools.table.table3 import Table
from amcat.models import ArticleSet

from amcat.tools.featurestream import featureStream

class Features(Script):
    """
    Get features from articlesets
    """

    class options_form(forms.Form):
        articleset = forms.ModelChoiceField(queryset=ArticleSet.objects.all())
        unit_level = forms.CharField()
        min_freq = forms.IntegerField()
        #source = forms.ModelChoiceField(queryset=['parsed','rawtext'], empty_label="parsed")
        #query = forms.CharField()
    output_type = Table
    
    def run(self, _input=None):
        articleset_id = self.options['articleset'].id
        unit_level = self.options['unit_level']
        min_freq = self.options['min_freq']
        rows = []
        #f = featureStream(source=self.options['source'])
        f = featureStream()
        countfeatures = collections.defaultdict(lambda:0)
        for a,parnr,sentnr,features in f.streamFeaturesPerUnit(articleset_id=articleset_id, unit_level=unit_level, verbose=True):
            for feature, count in features.iteritems():
                if min_freq > 0: countfeatures[feature] += count
                rows.append({'id':a.id,'paragraph':parnr,'sentence':sentnr,'feature':feature[0],'pos':feature[1], 'hits':count})
        
        if min_freq > 0:
            relevantfeatures = [feature for feature, n in countfeatures.iteritems() if n > min_freq]
            rows = [row for row in rows if (row['feature'],row['pos']) in relevantfeatures]
                
        if unit_level == 'article': columns = ['id','feature','pos','hits']
        else: columns = ['id',unit_level,'feature','pos','hits']

        t = Table(rows=rows, columns = columns, cellfunc=dict.get)
        return t
    
if __name__ == '__main__':
    from amcat.scripts.tools import cli
    result = cli.run_cli()
    print result.output()
        
