from ElasticSearchDriver import ElasticSearchDriver
from data_utils import cfg,logger

esd    = ElasticSearchDriver(logger, cfg)
fields = ['dreamId', 'body']
def get_data(query):
    return(esd.read_all_data(query, 'dream_clean_v123', 'clean',1000, fields))
