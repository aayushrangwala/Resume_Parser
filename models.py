#!/usr/bin/python

from pymongo import MongoClient
from urllib import quote_plus
import datetime
import time
import pymongo
import logging
import configparser


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

##### IN reply_config.ini reverse the dic of codes from "desc to code" to "code to desc"
config = configparser.ConfigParser()
config.read("Reply_Config.ini")

class models(object):
    def __init__(self,host, db_name, db_user, db_pass):
        self.DB_CLIENT = MongoClient('mongodb://%s:%s@%s/%s?authMechanism=SCRAM-SHA-1' % (quote_plus(db_user), quote_plus(db_pass), quote_plus(host), quote_plus(db_name)))     
        self.DB = getattr(self.DB_CLIENT,db_name)
        self.COLLECTION = self.DB.mail_resumes
        self.SEL_STATUS_DIC = {"URR": "SELR", "SELR": "URT", "URT": "SELT", "SELT": "URF", "URF": "SEL"}
        self.REJ_STATUS_DIC = {"URR": "REJBT", "URT": "REJAT", "URF": "REJAF"}
		
		

    def update_db(self,post):
        logger.info('Initiating Establishment for Connection ot DB.....')

        try:
     
            ## Considering Mail_ID as primary key and also assuming only one time is applied with one Mail_ID ##
     
            collection_id = self.COLLECTION.insert_one(post).inserted_id
	    logger.info("\n\n#######Record Starts#########\n\n\n\n" + "Date: " + str(post['Date']) + "\n\n" + str(post['Message']) + "\n\nMail_ID: " + str(post['Mail_ID']) + "\n\nResume File Name: " + str(post['Resume_File_Name']) + "\n\n\n##########Record Ends#############\n")
            logger.info('Records Printed on the Terminal screen just fine....')
            if collection_id is not None:
                logger.info('DB Updated successfully, with collection_id: ' + str(collection_id))      

        except Exception, e:
            logger.error('Exception Occurred in Update_db: ' + str(e))



    def print_db(self):
        for msgs in self.COLLECTION.find({}):
            logger.info('Recods Printing...')
	    print "\n\n#######Record Starts#########\n\n\n\n" + "Date: " + str(msgs['Date']) + "\n\n" + str(msgs['Message']) + "\n\nResume File Name: " + str(msgs['Resume_File_Name']) + "\n\n\n##########Record Ends#############\n"




    def update_status(mail_id, test=False, test_link=None, f2f=False, rej=False, selected=False):
        post = self.COLLECTION.find({"Mail_ID": mail_id})
	curr_status = post["Status"]
	sectn = config["STATUS"]
		
	if rej == False:
	    new_status = self.SEL_STATUS_DIC[curr_status]
	    if (test == True) and (test_link is not None):
		self.COLLECTION.update_one({"Mail_ID": mail_id},{"$set": {"Status":new_status, "Status_Desc": sectn[new_status], "Test_Link": test_link}})
	    elif f2f == True:
   	        self.COLLECTION.update_one({"Mail_ID": mail_id},{"$set": {"Status":new_status, "Status_Desc": sectn[new_status]}})
            elif selected == True:
   	        self.COLLECTION.update_one({"Mail_ID": mail_id},{"$set": {"Status":new_status, "Status_Desc": sectn[new_status]}})
	else:
	    new_status = self.REJ_STATUS_DIC[curr_status]
	    self.COLLECTION.update_one({"Mail_ID": mail_id},{"$set": {"Status":new_status, "Status_Desc": sectn[new_status]}})
			
			
			

    def remove_all(self):
        logger.warn('Removing all the Data.....')
        self.COLLECTION.remove()


    def get_Unprocessed_Resumes(date=None):
        if date is None:
            up_rec = self.COLLECTION.find({'Status': "URR", 'Date': str(date)})
        else:
            up_rec = self.COLLECTION.find({'Status': "URR"})
        return up_rec


    def get_Unreplied_to_Test(date=None):
        if date is None:
            ut_rec = self.COLLECTION.find({'Status': "URT", 'Date': str(date)})
        else:
            ut_rec = self.COLLECTION.find({'Status': "URT"})
        return ut_rec

