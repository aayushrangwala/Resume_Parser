#!/usr/bin/python

import configparser
#from jproperties import Properties

#p = Properties()
#p["db_server"] = "192.168.12.244"
#p["mail_userName"] = "ayush.rangwala"
#p["mail_pass"] = "R@ngwala17"
#p["db_name"] = "Applications"
#p["db_userName"] = "hiring"
#p["db_pass"] = "Coriolis#!123"
#p["mail_orgDomain"] = "@coriolis.co.in"

#with open("Parser_Config.properties","wb") as prop_file:
#    p.store(prop_file,encoding="utf-8")

config = configparser.ConfigParser()


test_link_temp = "Hi,\n\nThank you for applying to Coriolis.  We found your profile interesting and would like to invite you to start our interview process. As a first step I would like you to go through the following online pre-interview preparation. \nWe will be using your answers to these questions during the interview. \nClick on the following link to start:\n\n XXXXXX\n\nWe expect this to take about 1.5 to 2 hours of your time. \nYou can do this at any time at your convenience within 4 days after you received this mail .However, once you start, please try to finish the whole activity in one session, since the system is tracking how long you take to finish it. \n\n\n\n\nThanks and Regards\nTrupti Dongare\nHR-Coriolis Technologies Pvt Ltd"

rej_temp = "Hi, \n\n We regret to say that your profile is not selected at this point. \n\n We will still be keeping your resume and let you know when suitable pofile opening comes up.\n\n\n\n\nThanks and Regards\n\nTrupti Dongare\nHR-Coriolis Technologies Pvt Ltd"

config['MESSAGE_TEMPLATE'] = {
                               'TL_msg': str(test_link_temp), 'R_msg': str(rej_temp)
                             }


config['STATUS_CODE'] = {
                          "UNDER_REVIEW_RESUME" : "URR", "UNDER_REVIEW_TEST": "URT", "UNDER_REVIEW_INTERVIEW": "URF", 
                          "REJECTION_BEFORE_TEST": "REJBT", "REJECION_AFTER_TEST": "REJAT", "REJECION_AFTER_INTERVIEW": "REJAF", 
                          "SELECTED_TEST": "SELT", "SELECTED_RESUME": "SELR", "SELECTED": "SEL" 
		        }


config['JAVA_TEST_LINK'] = {'SLAB_1': "www.google.com", 'SLAB_2': "www.google.com", 'SLAB_3': "www.google.com", "SLAB_4": "www.google.com"}

config['PYTHON_TEST_LINK'] = {'SLAB_1': "www.google.com", 'SLAB_2': "www.google.com", 'SLAB_3': "www.google.com", "SLAB_4": "www.google.com"}

config['LK_TEST_LINK'] = {'SLAB_1': "www.google.com", 'SLAB_2': "www.google.com", 'SLAB_3': "www.google.com", "SLAB_4": "www.google.com"}



with open("Reply_Config.ini", "w") as fp:
    config.write(fp)