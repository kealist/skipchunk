import json
import pysolr
from . import solr

## -------------------------------------------
## Indexing!

def indexableGroups(groups,contenttype='concept'):
    """ Generates concept records for Solr, similar to how ES Bulk indexing
        uses a generator to generate bulk index/update actions """
    createtime = solr.timestamp()
    for group in groups:
        key = group.key
        for label in group.labels:
            snippetid = str(label.docid) + '_' + str(label.sentenceid)
            labelid = group.key + '_' + snippetid
            #print("Indexing %s" % labelid)

            record = {
                'id' : labelid,
                'key' : key,
                'idiom' : label.idiom,
                'label' : label.label,
                'length' : label.length,
                'start' : label.start,
                'end' : label.end,
                'docid' : label.docid,
                'sentenceid' : snippetid,
                'sentencenum_s' : label.sentenceid,
                'objectof' : label.objectOf,
                'subjectof' : label.subjectOf,
                'contenttype' : contenttype,
                'createtime': createtime,
                #Group-level values
                'preflabel' : group.preflabel,
                'prefcount' : group.prefcount,
                'total' : group.total
            }

            #For separate concept/predict behavior (such as autosuggest)
            if contenttype == 'concept':
                record['conceptlabel'] = label.label
            else:
                record['predicatelabel'] = label.label

            ##Generator for the record
            yield record

## -------------------------------------------

def indexableLabels(labels,contenttype='concept'):
    """ Generates labels for indexing, similar to how ES Bulk indexing
        uses a generator to generate bulk index/update actions """

    createtime = solr.timestamp()
    for key in labels.keys():
        for label in labels[key]:
            labelid = key + '_' + str(label.docid) + '_' + str(label.sentenceid)

            #print("Indexing %s" % labelid)

            record = {
                'id' : labelid,
                'key' : key,
                'idiom' : label.idiom,
                'label' : label.label,
                'length' : label.length,
                'start' : label.start,
                'end' : label.end,
                'docid' : label.docid,
                'sentenceid' : label.sentenceid,
                'objectof' : label.objectOf,
                'subjectof' : label.subjectOf,
                'contentType' : contenttype,
                'createtime': creattime
            }

            if contenttype == 'concept':
                record['conceptlabel'] = label.label
            else:
                record['predicatelabel'] = label.label

            ##Generator for the record
            yield record

##==========================================================
# MAIN API ENTRY POINT! USE THIS!

class GraphQuery():

    ## -------------------------------------------
    # Accepts a skipchunk object to index the required data in Solr

    def index(self,skipchunk,timeout=10000):
        predicatedocs = list(indexableGroups(skipchunk.predicategroups,contenttype="predicate"))
        conceptdocs = list(indexableGroups(skipchunk.conceptgroups,contenttype="concept"))
        return self.engine.index(conceptdocs+predicatedocs,timeout=timeout)

    def indexes(self):
        return self.engine.indexes(self.kind)

    ## -------------------------------------------
    # Calculates preflabels in the index for new concepts
    def makePrefLabels(self):
        # TODO: Write this
        return 0

    ## -------------------------------------------
    # Accepts a verb to find the concepts appearing in the same context

    def conceptVerbConcepts(self,concept,verb,mincount=1,limit=100):
        return self.engine.conceptVerbConcepts(concept,verb,mincount=mincount,limit=limit)

    ## -------------------------------------------
    # Accepts a verb to find the concepts appearing in the same context

    def conceptsNearVerb(self,verb,mincount=1,limit=100):
        return self.engine.conceptsNearVerb(verb,mincount=mincount,limit=limit)

    ## -------------------------------------------
    # Accepts a concept to find the verbs appearing in the same context

    def verbsNearConcept(self,concept,mincount=1,limit=100):
        return self.engine.verbsNearConcept(concept,mincount=mincount,limit=limit)

    ## -------------------------------------------
    # Suggests a list of concepts given a prefix

    def suggestConcepts(self,prefix,build=False):
        return self.engine.suggestConcepts(prefix,build=build)

    ## -------------------------------------------
    # Suggests a list of predicates given a prefix

    def suggestPredicates(self,prefix,build=False):
        return self.engine.suggestPredicates(prefix,build=build)

    ## -------------------------------------------
    # Summarizes a core

    def summarize(self,mincount=1,limit=100):
        concepts,predicates = self.engine.summarize(mincount=mincount,limit=limit)
        return concepts,predicates

    ## -------------------------------------------
    # Gets the subject-predicate-object graph for a subject

    def graph(self,subject,objects=5,branches=10):
        return self.engine.graph(subject,objects=objects,branches=branches)

    ## -------------------------------------------
    # Pretty-prints a graph walk of all suggested concepts and their verbs given a starting term prefix

    def explore(self,term,contenttype="concept",build=False,quiet=False,branches=10):
        return self.engine.explore(term,contenttype=concepttype,build=build,quiet=quiet,branches=branches)

    ## -------------------------------------------
    # host:: the url of the solr server
    # name:: the name of the solr core
    def __init__(self,config):
        self.kind = "graph"
        self.host = config["host"]
        self.name = config["name"]
        self.engine_name = config["engine_name"].lower()
        self.path = config["path"]

        #Setup the search engine
        if self.engine_name in ["solr"]:
            self.engine = solr.Solr(self.host,self.name,self.kind,self.path)

        elif self.engine_name in ["elasticsearch","elastic","es"]:
            raise ValueError("Sorry! Elastic isn't ready yet")
        
        else:
            raise ValueError("Sorry! Only Solr or Elastic are currently supported")

        if '-graph' not in self.name:
            self.name += '-graph'
        self.solr_uri = self.host + self.name
        self.select_handler = pysolr.Solr(self.solr_uri)
        self.suggest_handler = pysolr.Solr(self.solr_uri, search_handler='/suggest')


##==========================================================
# Command line explorer!

"""
if __name__ == "__main__":
    import sys
    import jsonpickle

    def pretty(obj):
        print(jsonpickle.encode(obj,indent=2))

    if len(sys.argv)<3:
        print('python sq.py <solr_core_name> <concept|predicate> <term>')

    else:
        i=1
        if sys.argv[0]=='python':
            i=2

        if len(sys.argv)<i+3:
            print('python sq.py <solr_core_name> <concept|predicate> <term>')
        else:
            core = sys.argv[i]
            kind = sys.argv[i+1]
            term = sys.argv[i+2]

            if solr.indexExists('http://localhost:8983/solr/',core):
                sq = GraphQuery('http://localhost:8983/solr/',core)
                #sq.explore(term,contenttype=kind,build=False)
                sq.graph(term)
            else:
                print('Core "',core,'" does not exists on localhost')
"""