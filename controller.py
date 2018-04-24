#!/usr/bin/python

from pymongo import MongoClient
from models import *
from mail_class import *
from Reply_Module import *
import configparser
import imaplib, smtplib, email
import os
import sys
import pymongo
import datetime
import logging






logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# create a file handler
handler = logging.FileHandler('Parser_Config.log')
handler.setLevel(logging.DEBUG)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

logger.info('\n\n################################ Starting Logs ########################################\n')
logger.info('Logging Strats, Date: ' + str(datetime.datetime.utcnow()) + '\n\n')

logger.info('Reading Resume_parser.ini file for credentials of db and mail...')
config = configparser.ConfigParser()
config.read("Parser_Config.ini")


## Getting mail connection detials and initailizing mail object ##

logger.info('Connecting to the Gmail Server of Coriolis.co.in...')
sectn = config['MAIL_DETAILS']
userName = sectn['mail_userName']
passwd = sectn['mail_pass']
org_domain = sectn['mail_orgDomain']

mail_obj = mail_class(org_domain,userName, passwd)

########################################

logger.info('Mail Connection Established....\n' + str(mail_obj))
logger.info('Selecting INBOX...')
mail_list,inst = mail_obj.connect_select('inbox')
########################################

## Getting DB Details for Connection  and Initializing DB onject ##

logger.info('Initiating Connection with DB with following details: ')
#remove_all()
sectn = config['DB_DETAILS']
host = sectn["db_host"]
db_user = sectn["db_userName"]
db_pass = sectn["db_pass"]
db_name = sectn["db_name"]

logger.info('host: ' + str(host) + '\n' + 'DataBase User: ' + str(db_user) + '\n' + 'Database Name: ' + str(db_name) + '\n' + 'Collection Name: ' + 'mail_resumes')

###########################################

db_inst = models(host, db_name, db_user, db_pass)

logger.info('Established Connection, DB Instance: ' + str(db_inst))

########################################

logger.info("\nInitiating reply object: \n")
reply_mail_obj = Reply_Module(inst, db_inst)

##########################################




"""
def to_Process(pending_att_mail_dict):
    ## Check the resume.txt with resp threshold value/passing value, true for send test and false for rejection ##

    logger.info('\nTraversing the list of attachments for getting the passing marks...\n')
       
    processor = resume_processor(<path of applications maybe>)

    for att in pending_att_mail_dict:
        is_Rejected, profile, exp = resume_processor.process_resume(post[str(att)])

        if not is_Rejected:
           ans = raw_input("\nResume shortlisted: \n" + str(att) + " Do you really want to send test? (y/n)")
           mail_id = pending_att_mail_dict[str(att)]

           if ans == 'y':
               reply_mail_obj.send_reply(mail_id,profile,exp)
        else:
           reply_mail_obj.send_reply(mail_id)

"""


## Asking for the task to perform ##

option = input('\nDo you want to parse new mails or reply to existing: 1. Parse Mails, 2. Reply, 3. Process the Unprocessed Resumes: \n')



if option == 1:

    if (len(mail_list) < 1):
        logger.info('No unparsed mails found....Terminating')
        sys.exit()

    logger.info('Found some list of UNREAD mails related to the requirements...Traversing Through...')

    #----getting the first and latest mail id
    f_mail = int(mail_list[0]) - 1
    l_mail = int(mail_list[-1]) 


    ## List containing the attachment names of this parse run in all mails

    pending_att_mail_dict = {}

    for mail in range(l_mail,f_mail,-1):
        logger.info('Parsing the Mail list, one by one...')
        post = mail_obj.parse_mail(mail,inst)
        pending_att_mail_dict[str(post["Resume_File_Name"])] = post["Mail_ID"]        

        logger.info('The post which is to be updated in DB after parsing the mail is: \n' + str(post))
        logger.info('Initiating Update...')
        db_inst.update_db(post)



    #op = raw_input("\nGot the list of resumes in this run, Do you want to process and perform rejection or accept actions: (y/n)\n")
    
    #if op == 'y':
        #self.to_Process(pending_att_mail_dict)
    #else:
        #logger.info('\nResumes are left unprocessed, saved in DB with status URR and the list is : \n ' + att_list)
        #print("\nThe Resumes are un processed, saved in DB with status 'URR'\n")



#logger.info('Folder updated, Please find all the applications in the /home/<Username>/Applications/...')


elif option == 2: 

    mail_id = raw_input("\nEnter Mail_id to be replied: \n")
    op = raw_input("\nDo you want to send the test: (y/n)\n")
    send_test = True if op == 'y' else False
    
    if send_test == True:
        profile = raw_input("\nEnter the Profile: \n")
        exp = raw_input("\nEnter the Experience in years: \n")
        logger.info("\ncalling send_reply() from reply_module...\n")
        reply_mail_obj.send_reply(mail_id,profile,exp)
    else:
        op = raw_input("\nDo you want to send the F2F interview invitation or Rejection Mail or Final Selection: (1/2/3/n)\n")
        if op == '1':
            date = raw_input("\nEnter the date and time exactly in format: (dd month'yy hh:mm am/pm) \n")
            reply_mail_obj.send_Custom_Reply(mail_id, True, date)
        elif op == '2':
            reply_mail_obj.send_reply(mail_id)
        elif op == '3':
            date = raw_input("\nAre you sure sending the selection mail, if yes, Enter the date and time exactly in format: (dd month'yy hh:mm am/pm) \n")
            if date is not 'n' :
            	reply_mail_obj.send_Custom_Reply(mail_id, False, date)
            else:
                sys.exit()
        else:
            text = raw_input("\nEnter the custom text and '(\n)' for new line: \n")
            reply_mail_obj.send_Custom_Reply(mail_id, False,text)




#elif option == 3: 

    #pending_att_mail_dict = {}
    
    #if raw_input("\nWant to process all or till date (1/2): \n") == '1':
        #rec = db_inst.get_Unprocessed_Resumes(
    #else:
        #date = raw_input("\nThen enter date: \n")
        #rec = db_inst.get_Unprocessed_Resumes(date)
    
    #for r in rec:
        #pending_att_mail_dict[r['Resume_File_Name']] = r['Mail_ID']
    
    #self.to_Process(pending_att_mail_dict)



else:
    logger.error('\nInvalid Option selected...\n') 
    print "\nInvalid Option \n"

   


#logger.info('##### Printing all the data in DB #####\n\n\n\n\n')
#db_inst.print_db()

logger.info('###############The End################')



