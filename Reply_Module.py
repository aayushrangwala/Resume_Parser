#!/usr/bin/python


from pymongo import MongoClient
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.message import MIMEMessage
from models import *
from mail_class import *
import configparser
import imaplib, smtplib, email
import os
import sys
import pymongo
import datetime
import logging


'''

The test link will be containing in some different prop file

Also the status(s) of the candidate will be in coded format 
ex: 
"UNDER_REVIEW_RESUME" : "URR"
"UNDER_REVIEW_TEST": "URT"
"UNDER_REVIEW_INTERVIEW": "URF", 
"REJECTION_BEFORE_TEST": "REJBT"
"REJECION_AFTER_TEST": "REJAT"
"REJECION_AFTER_INTERVIEW": "REJAF", 
"SELECTED_TEST": "SELT"
"SELECTED_RESUME": "SELR"
"SELECTED": "SEL" 


SLAB_1: Freshers (0-1)
SLAB_2: (2-3)
SLAB_3: (3-5)
SLAB_4: (5-8)

'''



R_config = configparser.ConfigParser()
R_config.read("Reply_Config.ini")

P_config = configparser.ConfigParser()
P_config.read("Parser_Config.ini")


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



class Reply_Module(object):
    
    def __init__(self, MAIL_SESSION, DB_INSTANCE, MAIL_SERVER = "smtp.gmail.com", SERVER_PORT = 993, C_MAIL = 'ayush.rangwala@coriolis.co.in'):
    	self.SESSION_INST = MAIL_SESSION
    	self.MAIL_SERVER = MAIL_SERVER
    	self.SERVER_PORT = SERVER_PORT
        self.COMPANY_MAIL = C_MAIL
        self.DB_INSTANCE = DB_INSTANCE
        self.PRO_DIC = {"JAVA": "JAVA_TEST_LINK", "PYTHON": "PYTHON_TEST_LINK", "LINUX_KERNEL": "LK_TEST_LINK"}


    def set_Reply_Properties(self, mail_id):
        logger.info('\nInitiating the starting properties for ML processed resume reply or custom reply: \n')    
        
        try: 
            REPLY_TO_ADDR = mail_id
    	    record = self.DB_INSTANCE.COLLECTION.find_one({"Mail_ID": mail_id})
            REPLY_SUBJECT = record['Subject']
                
            REPLY_FROM_ADDR = self.COMPANY_MAIL
            r_msg = MIMEMultipart("mixed")
            r_msg["Message-ID"] = email.utils.make_msgid()
            r_msg['to'] = REPLY_TO_ADDR
            r_msg['from'] = REPLY_FROM_ADDR
            r_msg['subject'] = 'RE: ' + REPLY_SUBJECT
            logger.info('\nHeaders are set, \nReply To : ' + str(REPLY_TO_ADDR) + ' with subject: ' + str(REPLY_SUBJECT) + ' Message-ID: ' + str(r_msg["Message-ID"]) + '\n')
        
        except Exception as e:
            logger.error("\nException setting the peoperties for mail, maybe mail_id is not given\n")
            logger.error(e)

        return r_msg


    def get_Test_Link(self, profile, exp):
        logger.info('Deciding the Experience Slab, the candidate fits in. ')
        profile_test_link, slab = self.get_Slab_and_Profile_Util(profile,exp)
        logger.info('\nRefering to Rely_Config.ini file for test links \n')
        sectn = R_config[profile_test_link]
        link = sectn[slab]
        logger.info('Found: ' + str(link) + '\n')
        return str(link)



    def get_Slab_and_Profile_Util(self, profile, exp):
        slab = ""
        profile_TL = ""

        if exp > 0 and exp <= 1:
            slab = "SLAB_1"
        elif exp > 1 and exp <= 2:
            slab = "SLAB_2"
        elif exp > 2 and exp <= 3:
            slab = "SLAB_3"
        elif exp > 3 and exp <= 5:
            slab = "SLAB_4"
        else:
            slab = "SLAB_5"
        
        profile_TL = self.PRO_DIC[profile] 

        return (str(profile_TL), slab)



    def get_Test_Mail_Template(self):
        logger.info('\nRefering to Rely_Config.ini file for test mail Template: \n')
        sectn = R_config['MESSAGE_TEMPLATE']
        templ = sectn["TL_msg"]
        logger.info('Found: ' + str(templ) + '\n')
        return templ


    def get_Interview_Mail_Template(self):
        logger.info('\nRefering to Rely_Config.ini file for Interview mail Template: \n')
        sectn = R_config['MESSAGE_TEMPLATE']
        templ = sectn["I_msg"]
        logger.info('Found: ' + str(templ) + '\n')
        return templ


    def get_Rejection_Template(self):
        logger.info('\nRefering to Rely_Config.ini file for Rejection mail Template: \n')
        sectn = R_config['MESSAGE_TEMPLATE']
        templ = sectn["R_msg"]
        logger.info('Found: ' + str(templ) + '\n')
        return templ         

    
    def get_selection_Mail_Template(self):
        ogger.info('\nRefering to Rely_Config.ini file for Final Selection mail Template: \n')
        sectn = R_config['MESSAGE_TEMPLATE']
        templ = sectn["S_msg"]
        logger.info('Found: ' + str(templ) + '\n')
        return templ    
    	




    def send_Custom_Reply(self,MAIL_ID, f2f, date=None, text=None):
        logger.info('\nInitiating Custom Reply: \nFirst setting properties: \n')
        reply_msg = self.set_Reply_Properties(MAIL_ID)

        #if send_test:
            #logger.info('\nSending Mail with Test message getting template from Reply_Config.ini file \n')
            #test_link_msg_template = self.get_Test_Mail_Template()
            #test_link_msg = test_link_msg_template.replace("XXXXXX", str(test_link))
            #reply_text = test_link_msg
        if f2f: ## for f2f need mail_id, true, date
            logger.info('\nSending Mail with interview message getting template from Reply_Config.ini file \n')
            interview_msg_template = self.get_Interview_Mail_Template()
            interview_msg = interview_msg_template.replace("XXXXXX", str(date))
            reply_text = interview_msg
            self.DB_INSTANCE.update_status(reply_msg['to'],False,None,True)
        
        elif date is not None: ## for selection need only mail_id and date
            logger.info('\nSending Mail with final selection message getting template from Reply_Config.ini file \n')
            selection_msg_template = self.get_selection_Mail_Template()
            selection_msg = selection_msg_template.replace("XXXXXX", str(date))
            reply_text = selection_msg
            self.DB_INSTANCE.update_status(reply_msg['to'],False,None,False,False)

        else: ## Text: need only text
            logger.info('\npreparing custom message... \n')
            reply_text = text

        logger.info('\nPreparing and attaching the content to the reply instance \n')
        reply_msg = self.attach_mail_body(reply_text,reply_msg)
        logger.info('\nGot the final mail: \n' + str(reply_msg) + ' \nSending mail: ')
        self.send_now(reply_msg)




    def attach_mail_body(self, msg, reply_msg):
        logger.info('\nAttaching mesage to reply mail instance: \nMessage: ' + str(msg) + '\n')
        body = MIMEMultipart("alternative")
        body.attach( MIMEText(msg, "plain") )
        #body.attach( MIMEText("<html>reply body text</html>", "html") )
        reply_msg.attach(body)
        return reply_msg



    def send_now(self, reply_msg):
        logger.info('\nConnecting to SMTP mail server: \n')
        server = smtplib.SMTP(self.MAIL_SERVER)
        server.starttls()
        logger.info('\nLogging to mail: \n')
        server.login(self.COMPANY_MAIL,P_config['MAIL_DETAILS']['MAIL_PASS'])
        logger.info('\nSending....\n')
        server.sendmail(reply_msg['from'], [reply_msg['to']], reply_msg.as_string())
        server.quit()
        logger.info('\nMail Sent.....\n' + str(reply_msg['from']) + ' ' + str([reply_msg['to']]) + ' '  + str(reply_msg.as_string()))


'''

## Uncomment me when your ML Algo is ready and then comment send_reply() and also the provision of asking the option to parse or reply from user ##

    def send_reply(self, MAIL_ID, profile=None, exp=None):
        reply_msg = self.set_Reply_Properties(MAIL_ID)

        if (profile is not None) and (exp is not None):
            logger.info("\nSending Mail with Test message getting template from Reply_Config.ini file \n")
            test_link = self.get_Test_Link(profile,exp)
            test_link_msg_template = self.get_Test_Mail_Template()
            test_link_msg = string.replace(test_link_msg_template, 'XXXXXX', test_link)
            reply_msg = self.attach_mail_body(test_link_msg, reply_msg)
            self.DB_INSTANCE.update_status(reply_msg['to'],True,test_link)
        else:
            logger.info("\nSending Rejection mail, getting template message \n")
            rej_msg = get_Rejection_Template()
            reply_msg = self.attach_mail_body(rej_msg, reply_msg)
            self.DB_INSTANCE.update_status(reply_msg['to'],false,None,False,True)  

        self.send_now(reply_msg)
           


'''

    

    

    




    
        
    
    
