#!/usr/bin/python

from pymongo import MongoClient
from urllib import quote_plus
import datetime
import time
import pymongo
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class models(object):
    def __init__(self,host, db_name, db_user, db_pass):
        self.DB_CLIENT = MongoClient('mongodb://%s:%s@%s/%s?authMechanism=SCRAM-SHA-1' % (quote_plus(db_user), quote_plus(db_pass), quote_plus(host), quote_plus(db_name)))     
        self.DB = getattr(self.DB_CLIENT,db_name)
        self.COLLECTION = self.DB.mail_resumes


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



    def remove_all(self):
        logger.warn('Removing all the Data.....')
        self.COLLECTION.remove()
