from __future__ import print_function
import httplib2
import os
import sys

import base64
import email
from apiclient import errors

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
"""
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
"""
# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = '../client_secret.json'
APPLICATION_NAME = 'Gmail Email Addresses From Label'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials



def ListMessagesWithLabels(service, user_id, label_ids=[]):
  """List all Messages of the user's mailbox with label_ids applied.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    label_ids: Only return Messages with these labelIds applied.

  Returns:
    List of Messages that have all required Labels applied. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate id to get the details of a Message.
  """
  try:
    response = service.users().messages().list(userId=user_id,
                                               labelIds=label_ids).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id,
                                                 labelIds=label_ids,
                                                 pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages
  except errors.HttpError as error:
    print('An error occurred: {}'.format(error))


def GetMessage(service, user_id, msg_id):
  """Get a Message with given ID.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A Message.
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
    
    return message
  except errors.HttpError as error:
    print('An error occurred: {}'.format(error))


def GetEmailFromMessage(service, user_id, msg_id):
  """Get a 'From' Email From Message with given ID.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    An email address.
  """
  try:
    message = GetMessage(service, user_id, msg_id)
    
    payload = message['payload']
    headers = payload['headers']
    address = ""
    for thing in headers:
        if thing['name'] == 'From':
            address = thing['value']
    
    
    return address
  except errors.HttpError as error:
    print('An error occurred: {}'.format(error))

def main():

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    
    labelName = 'IMPORTANT'
    if len(sys.argv)>1:
       labelName = sys.argv[1]

    addresses = []
    foundlabel = False
    
    if not labels:
        print('No labels found.')
    else:
      for label in labels:
        if label['name'] == labelName:
            print(label['id'])
            foundlabel = True
            emails = ListMessagesWithLabels(service,'me',[label['id']])
   
            for email in emails:
                address = GetEmailFromMessage(service,'me',email['id'])
                if not 'crodave' in address:
                    if not 'no-reply' in address:
                        
                        if "<" in address:
                            #we have "joe blogs <joeblogs@hotmail.com>
                            #we want a comma seperated list, frist name, second name , email
                            #first remove "<" and ">"  and seprate the email with ","
                            address = address.replace("<",",")
                            address = address.replace(">","")
                            #now try and coma seperate first and second name
                            if " " in address:
                                address = address.replace(" ",",",1)
                            else:
                            #leave the first name blank
                                address = "," + address
                        
                        else:
                            address = ",," + address
                            
                        addresses.append(address)
                        print(address)
        
    
    if foundlabel == True:
        
        if len(addresses)>0:
            print("Saving csv...")
            csvString  = "\n".join(addresses)
            fileName = "../" + labelName + "EmailAdresses.csv"       
            f = open(fileName, 'w')      
            f.write(csvString)
            print("Done.")
        else:
            print("No emails found with label: '" +  labelName + "'")
    else:
        print("Label: '" + labelName + "' not found.")
    """
    for address in addresses:
        csvString  += address
        csvString  += "\n"
    """
    

if __name__ == '__main__':
    main()