#!/usr/bin/python


from urllib import quote_plus
import imaplib, smtplib, email
import time, datetime
import os, errno, sys
import stat
import textract
import shutil
import getpass
import json
import logging






logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



class mail_class(object):
    #---Initialization------
    def __init__(self, ORG_DOMAIN, FROM_USER, FROM_PASS, MAIL_SERVER = "imap.gmail.com", SERVER_PORT = 993, CURR_DIR = '.'):
    	self.FROM_EMAIL = str(FROM_USER) + str(ORG_DOMAIN) #--Value will be "careers"
    	self.FROM_PASS = str(FROM_PASS)
    	self.MAIL_SERVER = MAIL_SERVER
    	self.SERVER_PORT = SERVER_PORT
    	self.curr_dir = CURR_DIR


    def connect_select(self, section):
        #--collecting inbox
        imapSession = imaplib.IMAP4_SSL(str(self.MAIL_SERVER))
        typ, accountDetails = imapSession.login(self.FROM_EMAIL, self.FROM_PASS)
        if typ != 'OK':
            logger.error('Not able to sign in...')
            print 'Not able to sign in!'
            raise
        logger.info('Successfully logged in....')
        imapSession.select(section)
        
        #---selecting list of mails with specific subject
        typ, data = imapSession.search(None,'(UNSEEN FROM "rangwalaas@rknec.edu")')
        if typ != 'OK':
            logger.info('Error searching inbox....')
            print 'Error searching Inbox.'
            raise
        logger.info('Successfully Searched for Unread Mails....')
        mail_ids = data[0]
        id_list = mail_ids.split()
        return (id_list,imapSession)



    
    def parse_mail(self, mail, mail_inst):
	type,data = mail_inst.fetch(mail,'(RFC822)')
        logger.info('Fetched Data from Mail...parsing Now....')
	final_message = ""
        post = ""
  	for response in data:
	    #-- To check if each entity from data list is a type of "Tuple" class, nevertheless it will be
	    if(isinstance(response,tuple)):
	        msg = email.message_from_string(response[1])                 #---Fetching the details from the Message------
	        subject = msg['subject']
	        mail_from = msg['from']
		final_message += "Message: \n\n"
		user_name = getpass.getuser()
		os.chmod("/home/" + user_name,stat.S_IRWXU)
		curr_dir = "/home/" + user_name + "/Applications"
		directory = os.path.dirname(curr_dir)
		
		try:
		    os.makedirs(directory)
		except OSError as e:
		    if e.errno != errno.EEXIST:
                        logger.info('Exception Occured: ' + str(e))
			raise
                logger.info('Saving Attachments in /home/<Username>/Applications/ directory...')
		att_name = self.save_attachments(msg,curr_dir)

                logger.info('Getting Text Message from the mail...')
                final_message = self.get_Text_Message_From_Mail(msg,final_message)

		if(att_name == ""):
                    logger.error('Attachment Not found.........')
		    continue
                    
                logger.info('Attachments found...extracting Text...')

                logger.info('\nAppending the list of attachments as: \n' + att_name)

                logger.info('Initiating Extraction of text....')            
	        self.extract(curr_dir,att_name)	

                logger.info('Updating DB...........')

                post = {"Date": datetime.datetime.utcnow(), "Mail_ID": str(mail_from),"Subject": str(subject), "Message": str(final_message), "Resume_File_Name": str(att_name) + ".txt", "Status": "URR", "Status_Desc": "UNDER_REVIEW_RESUME", "Test_Link": "NA"}

	return (post)




    def save_attachments(self,msg,curr_dir):
        #This is for only one attachment, try to look for multiple later
	# and also consider the case for "No attachment found"
	for part in msg.walk():
	    if (part.get('Content-Disposition') is not None):
                logger.info('Fetching Attachment....')
	        a_name = part.get_filename()
	        final_path = os.path.join(curr_dir + "/" + a_name)    
	        if not os.path.isfile(final_path):
	    	    fp = open(curr_dir + "/" + a_name, 'wb')
		    fp.write(part.get_payload(decode=True))
	            fp.close()
	    else:
		a_name = ""
	return a_name


    def get_Text_Message_From_Mail(self,msg,f_msg):
        for part in msg.walk():
	    if part.get_content_type() == 'text/plain':
		f_msg += part.get_payload()
        return f_msg



    def extract(self,curr_dir, a_name):
	text = textract.process(curr_dir + "/" + a_name)
	fp1 = open(curr_dir + "/" +  a_name + ".txt", 'w+')
	fp1.write(text)
	fp1.close()
	os.remove(curr_dir + "/" + a_name)
        logger.info('Attchment Processed.....')






'''

final constant threshold = <Some_Integer>
    def isRejected(file_name):
        res_threshhold = process_resume(file_name)
	if threshhold <= res_threshhold:
            return false
        return true


    def process_resume(resume):
        ## using ML Algo
        return threshhold_marks

'''




############################## BACKUP ############################



'''
def parse_mail(self, mail, mail_inst):
	type,data = mail_inst.fetch(mail,'(RFC822)')
        logger.info('Fetched Data from Mail...parsing Now....')
	final_message = ""
        post = ""
  	for response in data:
	    #-- To check if each entity from data list is a type of "Tuple" class, nevertheless it will be
	    if(isinstance(response,tuple)):
	        msg = email.message_from_string(response[1])                 #---Fetching the details from the Message------
	        subject = msg['subject']
	        mail_from = msg['from']
		final_message += subject + "\n\n\n" + "Message: \n\n"
		user_name = getpass.getuser()
		os.chmod("/home/" + user_name,stat.S_IRWXU)
		curr_dir = "/home/" + user_name + "/Applications"
		directory = os.path.dirname(curr_dir)
		
		try:
		    os.makedirs(directory)
		except OSError as e:
		    if e.errno != errno.EEXIST:
                        logger.info('Exception Occured: ' + str(e))
			raise
            
		att_name, final_message = self.save_attachments(msg,curr_dir,final_message)
                logger.info('Got the Final Message and Attachment.......')
		if(att_name == ""):
                    logger.warn('Attachment Not found.........')
		    continue    
                logger.info('Attachments found...extracting Text...')
		#print "\n\n\nAttachments found...extracting Text...\n\n"
                logger.info('Initiating Extraction of text....')            
	        self.extract(curr_dir,att_name)	
                logger.info('Updating DB...........')
                #print "\n\n\n\nUpdating DB.....\n\n\n\n"
                post = {"Date": datetime.datetime.utcnow(), "Mail_ID": str(mail_from),"Message": str(final_message), "Resume_File_Name": str(att_name) + ".txt"}

	return (post)

    def save_attachments(self,msg,curr_dir,f_msg):
        #This is for only one attachment, try to look for multiple later
	# and also consider the case for "No attachment found"
	for part in msg.walk():
	    if part.get_content_type() == 'text/plain':
		f_msg += part.get_payload()
	    if (part.get('Content-Disposition') is not None):
                logger.info('Fetching Attachment....')
	        a_name = part.get_filename()
	        final_path = os.path.join(curr_dir + "/" + a_name)    
	        if not os.path.isfile(final_path):
	    	    fp = open(curr_dir + "/" + a_name, 'wb')
		    fp.write(part.get_payload(decode=True))
	            fp.close()
	    else:
		a_name = ""
	return (a_name,f_msg)
    def __init__(self, ORG_DOMAIN, FROM_USER, FROM_PASS, MAIL_SERVER = "imap.gmail.com", SERVER_PORT = 993, CURR_DIR = '.'):
    	self.FROM_EMAIL = str(FROM_USER) + str(ORG_DOMAIN) #--Value will be "careers"
    	self.FROM_PASS = str(FROM_PASS)
    	self.MAIL_SERVER = MAIL_SERVER
    	self.SERVER_PORT = SERVER_PORT
    	self.curr_dir = CURR_DIR 

'''








































    
    
    

