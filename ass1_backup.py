#!/usr/bin/python
#From Aarkham Knight with Love

from urllib import quote_plus
import pymongo
from pymongo import MongoClient
import imaplib
import smtplib
import time
import email
import os
import errno
import sys
import stat
import textract
import shutil
import getpass
import datetime
import json

#---Initialization------
ORG_EMAIL ="@coriolis.co.in"
FROM_EMAIL = "ayush.rangwala" + ORG_EMAIL #--Value will be "careers"
FROM_PASS = "A@yush17" #--will be edited by the admin or later will define for asking on the fly
MAIL_SERVER = "imap.gmail.com"
SERVER_PORT = 993
curr_dir = '.'

try:
    #--collecting and selecting inbox
    mail = imaplib.IMAP4_SSL(MAIL_SERVER)
    if(mail):
	print "\n\nMail Connection Established... \n";
    mail.login(FROM_EMAIL,FROM_PWD)
    print "Logged in, Searching Inbox ...."
    mail.select('inbox')
        
    #---selecting list of mails with specific subject
    type,data = mail.search(None,'(SUBJECT "resume" FROM "ayush.rangwala@coriolis.co.in")')
    mail_ids = data[0]
    id_list = mail_ids.split()
    if (len(id_list) < 1):
	print "\n\nNo Unparsed mails available\n\nTerminating...\n"
	sys.exit()
     
    #----getting the first and latest mail id
    first_mail = int(id_list[0]) - 1
    latest_mail = int(id_list[-1]) 
	    
    count = 0		     
    #---iterate through the list of email IDs if list size is greater than 1
    for m in range(latest_mail,first_mail,-1):
	type,data = mail.fetch(m,'(RFC822)')
	count += 1
	final_message = ""

	for response in data:
	    #-- to check if each entity from data list is a type of "Tuple" class
	    if(isinstance(response,tuple)):
	        msg = email.message_from_string(response[1])                 #---Fetching the details from the Message------
	        subject = msg['subject']
	        mail_from = msg['from']
		final_message += subject + "\n\n" + mail_from + "\n\n\n" + "Message: \n\n"
		user_name = getpass.getuser()
		#print user_name
		os.chmod("/home/" + user_name,stat.S_IRWXU)
		curr_dir = "/home/" + user_name + "/Applications/"
		directory = os.path.dirname(curr_dir)
		
		try:
		    os.makedirs(directory)
		except OSError as e:
		    if e.errno != errno.EEXIST:
			raise

		#f = open(curr_dir + "/message.txt", "w+")
		#f.write("Subject : " + subject + "\n" + "From : " + mail_from +  "\n\n")

		#This is for only one attachment, try to look for multiple later
	        # and also consider the case for "No attachment found"
	        for part in msg.walk():
	            if part.get_content_type() == 'text/plain':
	    	        #f.write(str(part.get_payload()))
			final_message += part.get_payload()
		    if (part.get('Content-Disposition') is not None):
		    	att_name = part.get_filename()
			#print filename + " reached"
		        final_path = os.path.join(curr_dir + att_name)    
			if not os.path.isfile(final_path):
			    #print "\n" + final_message
			    fp = open(curr_dir + "/" + att_name, 'wb')
			    fp.write(part.get_payload(decode=True))
		            fp.close()

		#f.close()	
	
   		try:
		    text = textract.process(curr_dir + "/" + att_name)
		    fp1 = open(curr_dir + "/" +  att_name + ".txt", 'w+')
		    fp1.write(text)
		    fp1.close()
		    os.remove(curr_dir + "/" + att_name)

   	            print "\n\n\n\nAttachment processed, Updating DB.......\n\n\n\n"

		    db_client = MongoClient()
		    db = db_client.applications
		    print "##### Connected to DB #####"
		    collection = db.app_collection

		    post = {"Mail_id": str(mail_from), "Message": str(final_message), "Resume_File_Name": str(att_name) + ".txt", "date": datetime.datetime.utcnow()}

		    collection_id = collection.insert_one(post).inserted_id
		    #collection.remove()
		    print "\n\n\n\n#### DB Updated Successfully, with collection_id: " + str(collection_id) + " #####\n\n"

		except Exception, e:
		    print "Exception Occurred: " + str(e)




    print "\n\n\n\nFolder updated, Please find all the applications in the " + curr_dir + "...\n\n\n\n#####printing all the data in db#####\n\n\n\n\n"
    
    for msgs in collection.find({}):
	print "\n\n#######Record Starts#########\n\n\n\n" + "Dated: " + str(msgs['date'])+ "\n\n" + str(msgs['Message']) + "\n\nResume File Name: " + str(msgs['Resume_File_Name']) + "\n\n\n##########Record Ends#############\n"

    

	
                    
        
except Exception, e:
    print str(e)
    
    
    

