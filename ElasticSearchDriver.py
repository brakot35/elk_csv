from elasticsearch import Elasticsearch
from data_utils import cfg,logger

class ElasticSearchDriver:
    def __init__(self,logger,cfg):
        self.es = Elasticsearch([cfg['elk']['url']],
            verify_certs=True,
            ca_certs = '/usr/local/etc/openssl/cert.pem',
            http_auth = (cfg['elk']['user'], cfg['elk']['pw'] ))

        self.logger=logger
        self.cfg = cfg

    def write(self, doc, index, doc_id, doc_type='list'):
        logger.debug({"About to write":str(doc)})
        res = self.es.index(index, id=doc_id, doc_type=doc_type, body=doc )
        logger.info({"wrote, results":str(res)})
        return(res)
        
    def update(self, doc, index, doc_id, doc_type='list'):
        logger.debug({"about to update":str(doc)})
        res = self.es.update(index, id=doc_id, doc_type=doc_type, body=doc )
        logger.info({"updated. results":str(res)})
        return(res)

    def reduce_data(self, data, reduce):
        if reduce == []:
            return(data)
        data_reduced = []
        for d in data:
            d_reduced = { "_source": {} }
            for f in reduce:
                d_reduced["_source"][f] = d["_source"][f]
            data_reduced += [d_reduced]
            
        return(data_reduced)

    def read_all_data(self, query, index, query_type, scroll_size=500, reduce = [], to=30000):
        page = self.es.search(index=index, size = scroll_size,
                scroll = '5m', # Keep the scroll window open for 5 minutes
                body=query, doc_type=query_type, request_timeout=to)

        sid = page['_scroll_id']
        scroll_size = page['hits']['total']
        data = self.reduce_data(page['hits']['hits'], reduce)

        # Start scrolling
        while (scroll_size > 0):
            logger.info("Scrolling...")
            page = self.es.scroll(scroll_id = sid, scroll = '2m')
            # Update the scroll ID
            sid = page['_scroll_id']
            # Get the number of results that we returned in the last scroll
            data += self.reduce_data(page['hits']['hits'], reduce)
            scroll_size = len(page['hits']['hits'])
            logger.info({"scroll size:": str(scroll_size)})

        return(data)

    def read_data(self, query, index, max_size, query_type):
        if self.es.indices.exists(index=index):
            res = self.es.search(index=index, size = max_size,
                scroll = '5m', # Keep the scroll window open for 5 minutes
                body=query, doc_type=query_type)

            logger.info({"hits":res['hits']['total']})
            return res['hits']['hits']
        else:
            return([])
