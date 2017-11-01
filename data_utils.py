import yaml,logging,traceback,json,smtplib
from logging.handlers import RotatingFileHandler
from subprocess import check_output,STDOUT
from email.mime.text import MIMEText

cfg={}
for config_file in ["config.yml" , "config_env.yml"]:
    with open(config_file, 'r') as ymlfile:
        cfg.update( yaml.load(ymlfile))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def email_notify(to_email, subject, body="test"):
    from_email = "deamon@circadialabs.com"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    s = smtplib.SMTP('localhost')
    s.sendmail(from_email, to_email, msg.as_string())
    s.quit()

def get_s3_csv_files():
    return(check_output(cfg['general']['get_s3_csv_files'],
                        shell=True, stderr=STDOUT).rstrip().decode('utf-8`'))
