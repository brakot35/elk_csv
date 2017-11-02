from ElasticSearchDrive import ElasticSearchDriver
from data_utils import cfg,logger,email_notify
import time,boto,sys,json,logging,csv,io,subprocess,glob,re,os
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    filename=str(cfg['log']['get_csv_fn']), 
    maxBytes=int(cfg['log']['maxBytes']), 
    backupCount=int(cfg['log']['backupCount']))
logger.addHandler(handler)

formatter = logging.Formatter('{"location":"%(module)s:%(lineno)d:%(funcName)s","server_time":"%(asctime)s","level":"%(levelname)s","msg":%(message)s}')
handler.setFormatter(formatter)
# TODO: add process number
logger.info("CSV Starting...")
logger.info(cfg)

#http://docs.ceph.com/docs/master/radosgw/s3/python/
def upload(bucket_name, key_name, dreams_str):
    conn = boto.connect_s3()
    bucket = conn.get_bucket(bucket_name)
    key = bucket.new_key(key_name)
    key.set_contents_from_string(dreams_str)
    
def get_names(hits):
    names = []
    for h in hits:
        names.extend(list(h["_source"].keys()))
        names = list(set(names))
    return (names)

    
def to_csv(hits):
    output = io.StringIO()
    fieldnames = get_names(hits)
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for cur_hit in hits:
        try:
            h = cur_hit
            writer.writerow(dict(h['_source'].items()))
        except Exception as e:
            logger.error({"e":str(e),"hit":h})

    return(output)


def get_query(fn):
    query = "ERR"
    try:
        cmd = """tshark -r INPUT -Y 'http && (tcp.dstport == 9200) && !(http.connection == "keep-alive")'  -T fields -e http.file_data|grep csv"""
        results = subprocess.check_output(cmd.replace("INPUT", fn),shell=True)
        result = [x for x in re.split('\n',results.decode("utf-8")) if x!=''][-1]
        query = json.loads(result)
        return query
    except Exception as e:
        return query

def read_data(q):
    logger.debug(q)

    es_query = {"query":q["query"]}
    logger.info({"es_query":es_query})
        
    hits = esd.read_all_data(es_query, cfg['elk']['index'], cfg['elk']['type'], 5000)
        
    logger.info({"first hit":hits[0]})
    return(hits)


try:
    before = time.time()
    esd    = ElasticSearchDriver(logger, cfg)

    os.chdir(cfg['general']['cap_lib'])
    files = glob.glob("dump*")
    logger.info({"files":files})
    files.sort(key=os.path.getmtime,reverse=True)
    last_query = get_query(files[0])
    if 'query' not in last_query:
        last_query = get_query(files[1])
    logger.info({"query":last_query})

    if 'query' in last_query:
        hits_json = read_data(last_query)

        time_str = time.ctime().replace(' ','_').replace(':','_')
        hits_csv = to_csv(hits_json).getvalue()
        
        logger.info({"first2k chars":hits_csv[0:2000]})
        bucket = cfg['aws']['csv']
        fn = f'data_{time_str}.csv'
        upload(bucket, fn, hits_csv)

        aws_pref = cfg['general']['aws_pref']
        body = f'{aws_pref}/{bucket}/{fn}'
        logger.info({"hits-keys":len(hits), "duration":(time.time()-before), "s3":body})

        email_notify(cfg['log']['notify_to'], "New csv is ready for download from S3", body)

except Exception as e:
    logger.error("Error:"+str(e))
    print ("Error:"+str(e))
