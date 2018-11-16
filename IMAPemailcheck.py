########
# NOTE : This program deletes all emails in the IMAP INBOX. Only use on a service mailbox for this purpose
########

from __future__ import unicode_literals

from imapclient import IMAPClient
import email
import smtplib
import sys

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#Your incoming email server information
imaphost = 'mailserver.yourdomainhere.com'
imapusername = 'user'
imappassword = 'userpass'

#The Email address that we will search for when looking for an email
TargetEmailAddress = 'user@yourdomainhere.com'
#Subject of this email
TargetEmailSubject = "These are not the droids you are looking for"

#Your smtp information for sending an email
smtpport = 25
smtphost = 'mailserver.yourdomainhere.com'
smtpfromemail = 'user@yourdomainhere.com'
smtpusername = 'user'
smtppassword = 'userpass'

#if the email isn't found, send to these people
emaillist = ['user@yourdomainhere.com','5555555555@vtext.com']


#if we can't check emails on the server, then you probably want to send and email to IT
checkfaillist = ['user@yourdomainhere.com']


#Backup SMTP server, in case email server is down, which is useful if you fail retrieving emails from the server
redundancy = True
backuphost = 'mailserver2.yourdomainhere.com'
backupport = 25
backupfromemail = 'user@yourdomainhere.com'
backupusername = 'user'
backuppassword = 'userpass'

ssl = True
EmailWasFound = False


#If we couldn't check the mailbox, we are going to let someone know this script isn't working
def sendcheckfailemail():
	print('We couldnt check for emails. We must ALERT the IT Dept!')
	emailsucceeded = False
	
	#This is built to use two email accounts/servers for redundancy. If one fails, you can try another.
	#We first attempt the primary server
	try:
		s = smtplib.SMTP(smtphost, smtpport)		
		s.ehlo()
		
		#Attempt TLS
		try:
			s.starttls()
			
		except BaseException as e:
			print(e)
			
		#Attempt to login	
		try:
			s.login(smtpusername, smtppassword)
			
		except BaseException as e:
			print(e)
	
		#We send an email for each recipient in the list
		for email in checkfaillist:
			msg = MIMEMultipart()  
			msg['From']=smtpfromemail
			msg['To']=email
			msg['Subject']="CHECK FAILED - EMAIL INACCESSIBLE"
			messagetext = "We could not check for the specified email. Please check your IMAP settings"
			msg.attach(MIMEText(messagetext, 'plain'))
			s.send_message(msg)
			del msg
			emailsucceeded = True
			print('Email 1 succeeded')
			
		s.quit()
		
	except BaseException as e:
			print(e)	
	
	#If our first attempt fails, we will try a different account/server	
	if not emailsucceeded and redundancy:
		try:
				s = smtplib.SMTP(backuphost, backupport)
				s.ehlo()
				
				#Attempt TLS
				try:
					s.starttls()
				
				except BaseException as e:
					print(e)
					
				#Attempt to login	
				try:
					s.login(smtpusername, smtppassword)
				
				except BaseException as e:
					print(e)
					
			
				for email in checkfaillist:
					msg = MIMEMultipart()
					msg['From']=backupfromemail
					msg['To']=email
					msg['Subject']="CHECK FAILED - EMAIL INACCESSIBLE"
					messagetext = "We could not check for the specified email. Please check your IMAP settings"
					msg.attach(MIMEText(messagetext, 'plain'))
					s.send_message(msg)
					del msg
					print('Email 2 succeeded')
					
				s.quit()
					
				
		except BaseException as e:
			print(e)	
	
		

#The email check was completed, and an email was not received.  We must send an email	
def SendEmailNotFound():
	print('The email was not found')
	emailsucceeded = False

	#This is built to use two email accounts/servers for redundancy. If one fails, you can try another.
	#We first attempt the primary server
	try:
		s = smtplib.SMTP(smtphost, smtpport)		
		s.ehlo()
		
		#Attempt TLS
		try:
			s.starttls()
		
		except BaseException as e:
			print(e)
		
		#Attempt to login
		try:
			s.login(smtpusername, smtppassword)
			
		except BaseException as e:
			print(e)
		
		
		#We send an email for each recipient in the list
		for email in emaillist:
			msg = MIMEMultipart()  
			msg['From']=smtpfromemail
			msg['To']=email
			msg['Subject']="EMAIL WAS NOT DELIVERED"
			messagetext = "The EMAIL WAS NOT DELIVERED. Please take appropriate action"
			msg.attach(MIMEText(messagetext, 'plain'))
			s.send_message(msg)
			del msg
			emailsucceeded = True
			print('Email A succeeded')
			
		s.quit()
	
	
	except BaseException as e:
		print(e)	
	
	#If our first attempt fails, we will try a different account/server
	if not emailsucceeded and redundancy:
		try:
			s = smtplib.SMTP(backuphost, backupport)
			s.ehlo()
			
			#Attempt TLS
			try:
				s.starttls()
				
			except BaseException as e:
				print(e)
				
			#Attempt login
			try:
				s.login(backupusername, backuppassword)
				
			except BaseException as e:
				print(e)
			
			
			#We send an email for each recipient in the list
			for email in emaillist:
				msg = MIMEMultipart()
				msg['From']=backupfromemail
				msg['To']=email
				msg['Subject']="EMAIL WAS NOT DELIVERED"
				messagetext = "The EMAIL WAS NOT DELIVERED. Please take appropriate action."
				msg.attach(MIMEText(messagetext, 'plain'))
				s.send_message(msg)
				del msg
				print('Email B succeeded')
				
			s.quit()
						
		except BaseException as e:
			print(e)	
	


try: 
	#Establish an IMAP connection to check for the NJ email
	server = IMAPClient(imaphost, use_uid=True, ssl=ssl)
	server.login(imapusername, imappassword)

	#We look in the INBOX
	select_info = server.select_folder('INBOX')
	print('%d messages in INBOX' % select_info[b'EXISTS'])

	#We search all the messages and fetch them
	messages = server.search()
	response = server.fetch(messages, ['RFC822', 'BODY[TEXT]'])

	#We go email by email until we find what we want
	for uid, message_data in server.fetch(messages, 'RFC822').items():
		email_message = email.message_from_bytes(message_data[b'RFC822'])	
		sender = email_message.get('From')
		subject = email_message.get('Subject')
		print(sender, ' ',subject)
	
		#If we find the email, we stop looking and mark NJ as being completed
		if sender.find(TargetEmailAddress) != -1 and subject.find(TargetEmailSubject) != -1:
			print('Found the specified email', subject)
			EmailWasFound = True
			break
	
		else:
			print('Not a Match')
	

	#NOW WE DELETE ALL EMAILS - we do this so the next time we search, the email alert will not already be in there.
	server.delete_messages(messages)
	server.expunge()

	#We close the connection and disconnect from the IMAP server
	server.logout()

#We've failed checking for emails
except BaseException as e:
	print(e)
	#Send an email saying this failed and then exit
	sendcheckfailemail()
	sys.exit(1)


#If we received the email, we exit and do nothing
if EmailWasFound:
	print('Yay, Night Jobs didnt crash!')
	
#If there is no email found, we must send an alert	
else:
	print('The email was not received, sending an email saying it was not found')
	#send an email saying we did not receive the expected email
	SendEmailNotFound()
