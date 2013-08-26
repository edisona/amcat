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

import collections, csv
from amcat.scripts.script import Script
from amcat.tools.amcatsolr import Solr, filters_from_form
from amcat.tools.table.table3 import Table
from amcat.models import ArticleSet

from amcat.tools.featurestream import featureStream

class Features(Script):
    """
    Get features from articlesets. Written to be called from R.
    
    If use_index == True, this action has a very silly output. First the table is filled with the features per unit, and after that it is filled with the featureindex, containing the labels for each word and pos. The reason is that this allows the data to be uploaded to R in a single table.

    Note that if use_index == True and offset/batchsize are used to get data per batch, the index can only be used with the batch for which it was made. 
    """

    class options_form(forms.Form):
        articleset = forms.ModelChoiceField(queryset=ArticleSet.objects.all())
        unit_level = forms.CharField()
        offset = forms.IntegerField()
        batchsize = forms.IntegerField()
        use_index = forms.BooleanField(initial=True)
    output_type = Table
    
    def run(self, _input=None):
        use_index = self.options['use_index']
        articleset_id = self.options['articleset'].id
        unit_level = self.options['unit_level']
        offset = self.options['offset']
        batchsize = self.options['batchsize']
        
        featurestream_parameters = {'delete_stopwords':True, 'posfilter':['noun','NN']}
        f = featureStream(**featurestream_parameters)

        rows = []
        index, index_counter = {}, 1
        for a,parnr,sentnr,features in f.streamFeaturesPerUnit(articleset_id=articleset_id, unit_level=unit_level, offset=offset, batchsize=batchsize, verbose=True):
            for feature, count in features.iteritems():
                word, pos = feature[0], feature[1]
                if use_index == True: word, pos, index, index_counter = self.index(word, pos, index, index_counter)
                rows.append({'id':a.id,'paragraph':parnr,'sentence':sentnr,'word':word,'pos':pos, 'hits':count, 'label':None})
               
        if unit_level == 'article': columns = ['id','word','pos','hits']
        else: columns = ['id',unit_level,'word','pos','hits']
        if use_index == True: columns.append('label')

        if use_index == True:
            for label, id_nr in index.iteritems():
                row = {'id':None,'paragraph':None,'sentence':None, 'word':id_nr,'pos':None, 'hits': None, 'label':label}
                rows.append(row)
        t = Table(rows=rows, columns = columns, cellfunc=dict.get)
        return t

    def index(self, word, pos, index, index_counter):
        if not word in index:
            index[word] = index_counter
            index_counter += 1
        if not pos in index:
            index[pos] = index_counter
            index_counter += 1
        word = index[word]
        pos = index[pos]
        return (word, pos, index, index_counter)
                    
if __name__ == '__main__':
    from amcat.scripts.tools import cli
    result = cli.run_cli()
    #print result.output()
    
