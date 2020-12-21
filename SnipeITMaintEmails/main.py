import os,pathlib, sys
import logging
import logging.handlers
import schedule
import time
import SnipeITAPI
import datetime
import json
from MaintenanceMailer import MaintenanceMailer

def main():
    snipeit_server =os.getenv('SNIPEIT_SERVER','')
    snipeit_server_name=os.getenv('SNIPEIT_SERVER_NAME','Snipe-IT')
    snipeit_token =os.getenv('SNIPEIT_TOKEN','')
    exchange_server=os.getenv('MAIL_SERVER','')
    exchange_server_port=os.getenv('MAIN_SERVER_PORT','25')
    exchange_sender_email=os.getenv('MAIL_SENDER_ADDRESS','')
    exchange_receiver_email=os.getenv('MAIL_RECEIVER_ADDRESS','')

    with SnipeITAPI.Sessions(snipeit_server,snipeit_token) as snipeit_session:
        maintenances=snipeit_session.maintenances_get({'limit':50}).json()
    time_now=datetime.datetime.now()
    results=[]
    logger.info('Got '+str(len(maintenances['rows']))+' records from: '+snipeit_server_name)
    for maintenance in maintenances['rows']:
        start_date=datetime.datetime.strptime(maintenance['start_date']['date'],"%Y-%m-%d")
        due_date=(start_date-time_now).days
        logger.debug('Start Date: '+str(start_date)+' minus Time now: '+str(time_now)+' = '+str(due_date)+' Day(s)')
        if due_date >= 30:
            results.append({
            'asset_url':'{snipeit_server}/hardware/{hardware_id}'.format(snipeit_server=snipeit_server,hardware_id=maintenance['asset']['id']),
            'Asset Name': maintenance['asset']['name'],
            'Maintenance Type':maintenance['asset_maintenance_type'],
            'Maintenance Title':maintenance['title'],
            'Start Date':maintenance['start_date']['date']})
    if results:
        MaintMail=MaintenanceMailer(
            exchange_server,
            snipeit_server_name,
            exchange_server_port,
            exchange_sender_email,
            exchange_receiver_email)
        message=MaintMail.create(
            MaintMail.message_body_html,
            MaintMail.message_body_text,
            '30 Days Maintenance Reminder',
            exchange_receiver_email,
            results,
            'asset_url',
            'Asset Name'
        )
        MaintMail.send(
            MaintMail.receiver,
            message
        )
        logger.info('Found Assets')
    else:
        logger.info('No Assets found')

if __name__ == "__main__":
    if getattr(sys,'frozen',False):
        #Change the current working directory to be the parent of the main.py
        working_dir=pathlib.Path(sys._MEIPASS)
        os.chdir(working_dir)
    else:
        #Change the current working directory to be the parent of the main.py
        working_dir=pathlib.Path(__file__).resolve().parent
        os.chdir(working_dir)
    if os.getenv('DEBUG') == "True":
        LoggingLevel=logging.DEBUG
    else:
        LoggingLevel=logging.INFO
    #Initialise logging
    log_name = os.getenv("LOG_SAVE_LOCATION",'snipeit_maint_emailer.log')
    logging_format='%(asctime)s - %(levelname)s - [%(module)s]::%(funcName)s() - %(message)s'
    rfh = logging.handlers.RotatingFileHandler(
    filename=log_name, 
    mode='a',
    maxBytes=5*1024*1024,
    backupCount=2,
    encoding='utf-8',
    delay=0
    )
    console=logging.StreamHandler()
    console.setLevel(LoggingLevel)
    logging.basicConfig(
        level=LoggingLevel,
        format=logging_format,
        handlers=[rfh,console]
    )
    logger = logging.getLogger(__name__)
    logger.info('Working Dir: '+str(working_dir))
    logger.info('Logging Level: '+str(LoggingLevel))
    def job():
        logger.info('started job')
        logger.info('------------- Starting Session -------------')
        start=time.time()   
        main()
        end=time.time()
        logger.info('Synced in:'+str(end-start)+' Second(s)')
        logger.info('------------- Finished Session -------------')
    #job()
    schedule.every().day.at('08:00').do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)