# My project's README

###########
# Purpose #
###########
CSV export for large databases (any size).
Other CSV export tools are avialable elsewhere, the advantages of this repo:
(1) Kibana integration (this is work in progress)
(2) Support any size of file, using ElasticSearch built in scrool
(3) When download process is complete, csv file is uplaoded to S3 and
    notification email is sent to user.

Notice: This is work in progress.
What's working: The Python scirpt with JSON query as input thatcan be used
for any size, with an option to upload to S3.

What's work in progress: The tools is triggered by kibana, but I haven't found
a proper way as of now to send the query. So I'm using a hack (descibed below)
which could work OK if you have a small number of users and also you are writing
the Kibana dashboard for them (or for yourself) so you can embed the specific
query in the Dashboard.

TODO: If you're a good JS developer and can give me a hand here, please contact
leofer@gmail.com. What I need is a proper way to send the query JSON text
from the browser to the node server. This would improve my tool significantly for
me, my custmers and the community.

###########
# Install #
###########
0. Requirement
tested on: EC2 m3.medium / m3.2xlarge with Ubuntu 16 using

1. Prerequisite:
   python 3.6.0
   ElasticSearch - I've used docker version
   Kibana
   AWS:
     * account and write credentials for S3 bucket (for csv file to be uploaded)
     * aws configure (need AWSAccessKeyId and AWSSecretKey) on the server
     
   clone elk_scv the project into ELK_CSV_HOME
      $ git clone https://github.com/brakot35/elk_csv.git
   
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

5. Kibana integration, disclaimer here
   This part is work in progress and implemented as a work around for a problem I have.
   Let's take it in a few steps (I there is a demand, I'll make this a plugin).

   CODE_HOME shoud be the place where the git repo was cloned to.
   KIBANA_HOME should be where Kibana is installed

   5.1 Plugin
   I base my code on the example my-new-plugin, which sets up a server listen for the http requests to
   get the csv.
   *** create the new_plugin

   cd $CODE_HOME
   cp index.html $KIBANA_HOME/plugins/my-new-plugin/public/templates/index.html # text
   cp index.js   $KIBANA_HOME/plugins/my-new-plugin
   cp app.js     $KIBANA_HOME/plugins/my-new-plugin/public/app.js #client (test_1 is called by index.js)
   cp example.js $KIBANA_HOME/plugins/my-new-plugin/server/routes/example.js # Line BELOW:
   cp invoke_get_list.py $KIBANA_HOME/plugins/my-new-plugin/server/routes/

   5.2 Add the hook to call the get_csv
   This is the tricky part, I had to decide on GUI to click the CSV button and also somehow to 

I attach it to agg_table , but I wasn't able to find the query itself from client side.
   I have opened an issue about it - but no resolution yet.
   See here:
   
   cp CODE_HOME/example.js plugins/my-new-plugin/server/routes/

   $ npm install underscore

5.3
   $ cd KIBANA_HOME
   $ cp CODE_HOME/invoke_get_csv.py plugins/my-new-plugin/server/routes/
   $ cp CODE_HOME/agg_table.html src/ui/public/agg_table/
   $ cp CODE_HOME/agg_table.js src/ui/public/agg_table/
   

5.4 Getting the query from tshark
   $ sudo apt-get install tshark
   
   cd /home/ubuntu/cap&&nohup sudo tcpdump -l -i docker0 -w dump  -W 2 -C 1 dst port 9200
