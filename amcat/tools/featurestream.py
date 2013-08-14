#!/usr/bin/python
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

from __future__ import unicode_literals, print_function, absolute_import

from amcat.models import Article, Coding, Token, Lemma, Word, AnalysedArticle
from amcat.tools.toolkit import clean, stripAccents
from django import db

import nltk
import re, math, collections, itertools, random, pickle
from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist

from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_selection import SelectKBest, SelectPercentile, chi2

class featureStream():
    """
    A class to iterate through features of articles. Features can be organized on three levels: article, paragraph and sentence. Parsed data can be used (source='parsed'), or raw text (source='rawtext'). For raw text low cost tokenization and stemming options are implemented. Ngrams can be used as well.
    At __init__ the arguments are passed for what features should be used (i.e. words or lemma, strings or id's, ngrams). The 'featurestream' function can then be used to yield these features for a given aricleset and unit level.
    """
    
    def __init__(self, source='rawtext', language='dutch', use_lemma=True, use_id=True, use_stemming=True, delete_stopwords=True, usepos=True, posfilter=None, ngrams=1, lowercase=True, headlinefilter=None):
        self.source = source
        self.posfilter = posfilter
        self.ngrams = ngrams
        self.usepos = usepos
        self.headlinefilter = headlinefilter
        if delete_stopwords == True: self.stopwords = nltk.corpus.stopwords.words(language)
        else: self.stopwords = None

        if source == 'parsed':
            self.use_lemma = use_lemma
            self.use_id = use_id
            self.lowercase = lowercase and not use_id
            if self.stopwords:
                if use_id and not use_lemma == True: self.stopwords = set(w.id for w in Word.objects.filter(word = stopwords))
                if use_id and use_lemma == True: self.stopwords = set(w.id for w in Lemma.objects.filter(lemma = stopwords))
       
        if source == 'rawtext':
            self.lowercase = lowercase
            self.tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+|[^\w\s]+')
            if posfilter or (usepos == True):
                if language == 'dutch': self.tagger = nltk.UnigramTagger(nltk.corpus.alpino.tagged_sents())
                if language == 'english': self.tagger = nltk.UnigramTagger(nltk.corpus.brown.tagged_sents())
            if use_stemming == True: self.stemmer = nltk.SnowballStemmer(language)
            else: self.stemmer = None

    def toNgrams(self, features, ngrams):
        ngram_features = []
        for i in range(0,len(features)):
            feature = features[i]
            if (i+ngrams) > len(features) : break
            for n in range(1,ngrams): feature = "%s_%s" % (feature,features[i+n])
            ngram_features.append(feature)
        return ngram_features

    def getTokensFromDatabase(self, a):
        for t in Token.objects.select_related('sentence__sentence','word__lemma').filter(sentence__analysed_article__id = a.analysedarticle_set.get().id):
            paragraph = t.sentence.sentence.parnr
            sentence = t.sentence.sentence.sentnr

            if self.use_id == True:
                if self.use_lemma == True: word = t.word.lemma_id
                else: word = t.word_id
            else:
                if self.use_lemma == True: word = str(t.word.lemma)
                else: word = str(t.word)

            if self.stopwords and word in self.stopwords: continue
                
            if self.posfilter or (self.usepos == True):
                pos = t.word.lemma.pos
                if not pos in self.posfilter: continue
                yield (paragraph, sentence, word, t.word.lemma.pos)
            else: yield (paragraph, sentence, word, None)

    def getTokensFromRawText(self, a):
        for s in a.sentences.all():
            paragraph = s.parnr
            sentence = s.sentnr
            for word, pos in self.prepareRawText(s.sentence):
                yield (paragraph, sentence, word, pos)

    def prepareRawText(self, text):
            sent = stripAccents(text)
            #sent = clean(text,25)
            sent = self.tokenizer.tokenize(sent)
            if self.posfilter or (self.usepos == True):
                for word, pos in self.tagger.tag(sent):
                    if self.posfilter and not pos in self.posfilter: continue
                    if self.stopwords and word in self.stopwords: continue
                    if self.stemmer: word = self.stemmer.stem(word)
                    yield (word, pos)
            else:
                for word in sent:
                    if self.stopwords and word in self.stopwords: continue
                    if self.stemmer: word = self.stemmer.stem(word) 
                    yield (word, None)
        
    def getFeatures(self, a, unit_level):
        if self.source == 'parsed': words = self.getTokensFromDatabase(a)
        if self.source == 'rawtext': words = self.getTokensFromRawText(a)

        for paragraph, sentence, word, pos in words:
            if self.headlinefilter:
                if self.headlinefilter == 'exclude' and paragraph == 1: continue
                if self.headlinefilter == 'only' and not paragraph == 1: continue
            if self.lowercase == True: word = word.lower()
            if unit_level == 'article': paragraph, sentence = None, None
            if unit_level == 'paragraph': sentence = None
           
            yield (paragraph, sentence, word, pos)

    def getFeaturesPerUnit(self, a, unit_level):
        features_unit_dict = collections.defaultdict(lambda:[])
        for par, sent, word, pos in self.getFeatures(a, unit_level):
            if self.usepos == True: word = "%s (%s)" % (word,pos)
            features_unit_dict[(par,sent)].append(word)
        for par, sent in features_unit_dict:
            features = features_unit_dict[(par,sent)]
            if self.ngrams > 1: features = self.toNgrams(features, self.ngrams)
            yield (par, sent, features)

    def streamFeaturesPerUnit(self, articleset_id=None, article_ids=None, unit_level='sentence', as_dict=True, verbose=True):
        if article_ids: # article_list overrides articleset_id
            articles = Article.objects.select_related('sentences','analysedarticle_set').filter(pk__in=article_ids)
        else: 
            articles = Article.objects.select_related('sentences','analysedarticle_set').filter(articlesets_set=articleset_id)
        N = len(articles)
        for i, a in enumerate(articles):
            if verbose == True:
                if i % 2500 == 0: print('%s / %s' % (i,N))
            for paragraph, sentence, features in self.getFeaturesPerUnit(a, unit_level):
                if as_dict == True: features = collections.Counter(features)
                yield (a, paragraph, sentence, features)

class codedFeatureStream():
    """
    featureStream for codingjobs, where the values of an assigned coding field can be attached to each unit. Meant as a convenience for machinelearning purposes. 
    Use the function streamCodedFeaturesPerUnit:
        Parameters:
            - featureStream: an instance of the featureStream class.
            - codingjob_ids
            - fieldnr: the nr of the field in the codingschema
            - unit_level: the level at which features are streamed. Can be article, paragraph or sentence. Codings are also gathered from codingjobs at this level, so that at the article level codings from the articleschema are used, and at sentence level the codings from the unitschema. At paragraph level a list of the coded values of sentences is given.
            - recode_dict: a dictionary to replace coded values (keys) with recoded values (values).
    """

    def getSentenceCodings(self, c, sentence_codings, fieldnrs):
        article_id, parnr, sentnr = c.article_id, c.sentence.parnr, c.sentence.sentnr
        if (article_id, parnr, sentnr) in sentence_codings: return sentence_codings
        values = [(v.field, v.value) for v in (c.values.select_related('field__fieldnr','value').filter(field__fieldnr__in=fieldnrs))]
        if len(values) == 0: return sentence_codings
        for v in values:
            fieldnr = v[0].fieldnr
            if fieldnr in fieldnrs:
                value = v[1]
                sentence_codings[(article_id, parnr, sentnr)][fieldnr] = value
        return sentence_codings

    def getArticleCodings(self, c, article_codings, fieldnrs):
        article_id = c.article_id
        if article_id in article_codings: return article_codings
        values = [(v.field, v.value) for v in (c.values.select_related('field__fieldnr','value').filter(field__fieldnr__in=fieldnrs))]
        #print('Queries used: %s' % len(db.connection.queries)) ### how to reduce db hits in this case?
        if len(values) == 0: return article_codings
        for v in values:
            fieldnr = v[0].fieldnr
            if fieldnr in fieldnrs:
                value = v[1]
                article_codings[(article_id,None,None)][fieldnr] = value
        return article_codings

    def getParagraphCodings(self, fieldnrs, paragraph_codings, sentence_codings):
        for k,v in sentence_codings.iteritems():
            aid, parnr, sentnr = k
            for fnr, value in v.iteritems():
                if not fnr in fieldnrs: continue
                paragraph_codings[(aid,parnr,None)][fnr].append(value)
        return paragraph_codings 
            
    def getCodedFields(self, codingjob_ids, fieldnrs):
        if not type(codingjob_ids) in [type(set()), type([])]: codingjob_ids = [codingjob_ids]
        article_codings = collections.defaultdict(lambda:{})
        paragraph_codings = collections.defaultdict(lambda:collections.defaultdict(lambda:[])) # codings are listed, for aggregation purposes (e.g., sum, mean or mode
        sentence_codings = collections.defaultdict(lambda:{})

        for codingjob_id in codingjob_ids:
            print("Codingjob: %s" % codingjob_id)
            for c in Coding.objects.select_related('codingjob','article','values').filter(codingjob_id = codingjob_id):
                if c.sentence_id: sentence_codings = self.getSentenceCodings(c, sentence_codings, fieldnrs)
                else: article_codings = self.getArticleCodings(c, article_codings, fieldnrs)
            paragraph_codings = self.getParagraphCodings(fieldnrs, paragraph_codings, sentence_codings)
        #print('Queries used: %s' % len(db.connection.queries))
        return {'article':article_codings, 'paragraph':paragraph_codings, 'sentence':sentence_codings}

    def streamCodedFeaturesPerUnit(self, featurestream, codingjob_ids, fieldnr, unit_level, recode_dict):
        print('GETTING UNIT CODINGS')
        uc = self.getCodedFields(codingjob_ids=codingjob_ids, fieldnrs=[fieldnr])
        article_ids = set([aid for aid,parnr,sentnr in uc[unit_level]])

        print('\nGETTING FEATURES')
        codedfeaturesperunit = []
        if len(article_ids) == 0: return None
        for a, parnr, sentnr, features in featurestream.streamFeaturesPerUnit(article_ids=article_ids, unit_level=unit_level):
            if not (a.id,parnr,sentnr) in uc[unit_level]: continue
            label = uc[unit_level][(a.id,parnr,sentnr)][fieldnr]
            if recode_dict: label = recode_dict[label]
            
            codedfeaturesperunit.append((a, parnr, sentnr, features, label))                       
        return codedfeaturesperunit

class prepareFeatures_oud(): ## overbodig indien de nieuwe op sklearn gebaseerde prepareFeatures werkt
    """
    Class for feature extraction and feature selection functions
    """
    def selectFeatures(self, codedfeatures, features_pct, min_freq):
        fd = FreqDist()
        cfd = collections.defaultdict(lambda:FreqDist())
        for a, parnr, sentnr, features, label in codedfeatures:
            for feature, score in features.iteritems():
                for i in range(0,score):
                    fd.inc(feature)
                    cfd[label].inc(feature)
            
        feature_scores = collections.defaultdict(lambda:0)
        for v in cfd:
            for feature, freq in fd.iteritems():
                 if freq < min_freq: continue
                 feature_score = BigramAssocMeasures.chi_sq(cfd[v][feature], (freq, cfd[v].N()), fd.N())
                 feature_scores[(feature)] += feature_score

        n_topfeatures = int(len(feature_scores) * (features_pct/100.0))
        topfeatures = sorted([(score,feature) for feature,score in feature_scores.iteritems()],reverse=True)[:n_topfeatures]
        print('Using top %s of %s features (%s percent)' % (len(topfeatures), len(feature_scores), features_pct))
        return [feature for score,feature in topfeatures]
          
    def prepareFeatures(self, codedfeatures, features_pct=0.50, min_freq=0, only_true=True, binominal=False):
        prepared_features = []
        usefeatures = self.selectFeatures(codedfeatures, features_pct, min_freq)
        for a, parnr, sentnr, features, label in codedfeatures:
            newfeatures = {}
            for use_f in usefeatures:
                if not use_f in features:
                    if only_true == True: continue
                    else: features[use_f] = 0
                hits = features[use_f]
                if binominal == True: hits = hits > 0
                newfeatures[use_f] = hits
            #newfeatures = extractFeatures(newfeatures)
            prepared_features.append((a, parnr, sentnr, newfeatures, label))
        return prepared_features


class prepareFeatures():
    """
    Class for feature extraction and feature selection functions. Use the prepareFeatures function to run.
    Takes a list of dictionaries (representing units), in which keys are words and values its occurence within the unit. Two types of transformations can be issued. Vectortransformation changes the representation of the vector, for instance using tfidf. Featureselection select a percentage of the featurelist (features_pct) based on a score for the relevance of the feature (e.g., chi2). The transformations are performed using the sklearn package.
    The resulting data can be returned as a list of dictionaries, or as a sparse matrix.
    """
    def prepareFeatures(self, featureslist, featuresclass=None, vectortransformation='tfidf', featureselection='chi2', features_pct=50, returnasmatrix=False):
        dv = DictVectorizer()
        fmatrix = dv.fit_transform(featureslist)
        print('- Selecting features')
        if featureselection:
            fnames = dv.feature_names_ # featurenames (required for inverse_transform) are stored in dv
            fmatrix, fnames = self.selectFeatures(fmatrix, fnames, featureselection, featuresclass, features_pct)
            dv.feature_names_ = fnames # store new index of featurenames for dv.inverse_transform
        print('- Extracting features')
        if vectortransformation: fmatrix = self.transformVectors(fmatrix, vectortransformation)
        if returnasmatrix == False: featureslist = dv.inverse_transform(fmatrix)
        return featureslist

    def selectFeatures(self, fmatrix, fnames, method, featuresclass, features_pct):
        if method == 'chi2': sk = SelectPercentile(chi2, features_pct)
        fmatrix = sk.fit_transform(fmatrix, featuresclass)
        selectedfeatures = zip(sk.get_support(), fnames)
        fnames = [feature for selected, feature in selectedfeatures if selected == True]
        return (fmatrix, fnames)
  
    def transformVectors(self, fmatrix, method):
        if method == 'tfidf':
            transformer = TfidfTransformer()
            idf = transformer.fit(fmatrix)
            fmatrix = transformer.transform(fmatrix)
        if method == 'binomial':
            fmatrix.data = fmatrix.data > 0
        if method == 'count':
            fmatrix = fmatrix
        return fmatrix

   
