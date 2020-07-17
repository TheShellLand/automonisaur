import elasticsearch

from elasticsearch import Elasticsearch, RequestsHttpConnection

from automon.log.logger import Logging
from automon.integrations.elasticsearch.config import ElasticsearchConfig

log = Logging(__name__, Logging.ERROR)


class Cleanup:

    def __init__(self):

        self.ES = ElasticsearchConfig()
        self.ES_connect = self.ES.Elasticsearch()

        self.cache = []
        self.indices = []

    def ping(self):
        if not self.ES_connect:
            return False
        return self.ES.Elasticsearch().ping()

    def search_indices(self, index_pattern):
        if not self.ES_connect:
            return False

        try:
            retrieved_indices = self.ES.Elasticsearch().indices.get(index_pattern)
            num_indices = len(retrieved_indices)

            msg = 'Search found {} indices'
            msg = msg.format(num_indices)
            log.info(msg)
            return retrieved_indices
        except elasticsearch.exceptions.NotFoundError:
            msg = '''You provided the index pattern '{}', but searches returned fruitless'''
            msg = msg.format(index_pattern)
            log.error(msg)

    def delete_indices(self, index_pattern):
        if not self.ES_connect:
            return False

        retrieved_indices = [x for x in self.search_indices(index_pattern).keys()]
        num_indices = len(retrieved_indices)

        msg = 'Search found {} indices'
        msg = msg.format(num_indices)
        log.info(msg)

        if not num_indices:
            msg = '''No indices found. exiting'''
            print(msg)
            return False

        for index in retrieved_indices:
            print(index)

        # TODO: Find a way to undo index deletions
        #       One way could be to rename the indices and store a link to the new
        #       indices in a node of deleted indices
        if num_indices < 2:
            msg = '''\nYOU'RE ABOUT TO DELETE {} INDEX! ARE YOU SURE YOU WANT TO CONTINUE? '''
        elif num_indices > 1:
            msg = '''\nYOU'RE ABOUT TO DELETE {} INDICES! ARE YOU SURE YOU WANT TO CONTINUE? '''
        msg += '''THIS CANNOT BE UNDONE! DECIDED WISELY [y/N]'''
        msg = msg.format(num_indices)
        print(msg)

        answer = str(input()).lower()

        if not answer:
            answer = 'N'

        if answer == 'y':
            for index in retrieved_indices:
                msg = '''Deleting {}...'''
                msg = msg.format(index)
                print(msg, end='')
                # Delete the index
                self.ES.Elasticsearch().indices.delete(index=index)
                print('done')
        else:
            msg = '''Whew, you might have just blew it, if you had said yes'''
            print(msg)

    def get_indices(self):
        if not self.ES_connect:
            return False
        retrieved_indices = self.ES.Elasticsearch().indices.get('*')
        num_indices = len(retrieved_indices)

        self.indices = retrieved_indices
        msg = 'Retrieved {} indices'
        msg = msg.format(num_indices)
        log.info(msg)
