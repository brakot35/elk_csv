# My project's README

###########
# Install #
###########
1. Requirement
tested on OS X and EC2 with Ubuntu using python 3.6.0

2. creating python environment
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirement.txt

3. Configuration
$ emacs config_env.yml
  edit the following:
  * under elk
        url - elasticsearch URL, can leave 'localhost' if installed on the same machine as elasticsearch
	user, pw - these are the username and password of elasticsearch. 
	index, type - current version support only a predefined index/type
  * under aws
        csv - name of AWS S3 bucket to write the csv to
$ emacs config.yml
  * under log
    notify_to - comma separated list of email addresses to notify of a a new file
                e.g. ["x@gmail.com","b@ai.co"]
  * under general
    get_s3_csv_files - edit <bucket> (same as config_env.yml aws.csv)

4. (Optional) Test your configuration
  $ ipython
    >>> quert = """ somethihg """
        (any valied ES query, can be takned e.g. ftom Kibana spy mode request
	 see https://www.elastic.co/guide/en/kibana/master/vis-spy.html)
    >>> from test_es_driver import get_data
    >>> data = get_data(query)
    now test your data integrity

  If this step doesn't work, tweak with timeouts/thresholds or ask for my specific help

