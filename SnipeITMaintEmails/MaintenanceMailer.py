import logging
import smtplib, ssl
from email.encoders import encode_base64
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)
logger.debug('Importing Module : '+__name__)

class MaintenanceMailer(object):
    """Class to manage Mail"""
    def __init__(self,server,server_name,port,sender=None,receiver,message_body_html=None,message_body_text=None,message_body_logo=None,use_tls=None,username=None,password=None):
        self.server=server
        self.server_name=server_name
        self.port=port
        self.use_tls=True if ssl else False
        self.username=username if username else sender
        self.password=password
        self.ssl_context=ssl.create_default_context()
        self.sender=sender
        self.receiver=receiver
        self.message_body_html='message.html' if not message_body_html else message_body_html
        self.message_body_text='message.txt' if not message_body_text else message_body_text
        self.message_body_logo='logo.png' if not message_body_logo else message_body_logo



    def create_text_table(self,results):
        """Creates a text table based of list of dicts"""
        headers={}
        #Set the minimum padding for the table
        for key,value in results[0].items():
            #Make padding length of the key
            headers[key]=len(key)
        #Iterate over all key/values update padding if the value len is greater than padding
        for result in results:
            for key,value in result.items():
                length=len(str(value))
                headers[key]=length if length > headers[key] else headers[key]
        #Empty Lists
        formating_rows=[]
        formating_headers=[]
        #Create the formatting based on the header dict
        for key,value in headers.items():
            #Row formating based on keywords
            formating_rows.append(F"{{{key}:{value}}} ")
            #Header formating based on postion
            formating_headers.append(F"{{:{value}}} ")
        #Join all the formating together into one string
        formating_rows=''.join(formating_rows)
        formating_headers=''.join(formating_headers)
        #List to store output
        rows_output=[]
        #Iterate over inputted data
        for index,result in enumerate(results):
            #If its the first row append the header
            if index == 0:
                rows_output.append((formating_headers+'\n').format(*result))
                spacer=[]
                for key,value in headers.items():
                    spacer.append('-'*value)
                rows_output.append((formating_headers+'\n').format(*spacer))
            #Append a row to the list
            rows_output.append((formating_rows+'\n').format(**result))
        #Join all the rows and headers into one string
        output=''.join(rows_output)
        return output

    def create_html_table(self,results,href_key=None,href_target=None):
        """Creates a html table based of list of dicts"""

        table_header_format='<th style="font-family: Avenir, Helvetica, sans-serif; box-sizing: border-box; border-bottom: 1px solid #EDEFF2; padding-bottom: 8px; text-align: left;">{header_name}</th>'
        table_row_format ='<td style="font-family: Avenir, Helvetica, sans-serif; box-sizing: border-box; color: #74787E; font-size: 15px; line-height: 18px; padding: 10px 0; text-align: left;">{row_value}</td>'
        table_row_href_format ='<td style="font-family: Avenir, Helvetica, sans-serif; box-sizing: border-box; color: #74787E; font-size: 15px; line-height: 18px; padding: 10px 0; text-align: left;"><a href="{row_href}" style="font-family: Avenir, Helvetica, sans-serif; box-sizing: border-box; color: #3869D4;">{row_value}</a></td>'
        table_headers=[]
        table_rows=[]
        #Iterate over inputted data
        for index,result in enumerate(results):
            #Iterate over key value pairs
            table_rows.append('<tr>\n')
            for row_index,(key,value) in enumerate(result.items(),1):
                #Setup headers
                if index == 0:
                    #Don't add a header for href key
                    if not key == href_key:
                        #Append out header to a row
                        if len(result.keys()) > row_index:
                            table_headers.append((table_header_format+'\n').format(header_name=key))
                        else:
                            table_headers.append(table_header_format.format(header_name=key))
                
                if key == href_target:
                    table_rows.append((table_row_href_format+'\n').format(row_href=result[href_key],row_value=value))
                elif not key == href_key:
                    table_rows.append((table_row_format+'\n').format(row_value=value))
                else:
                    pass
            if len(results) > index+1:
                table_rows.append('</tr>\n')
            else:
                table_rows.append('</tr>')

        rows=''.join(table_rows)    
        headers=''.join(table_headers)
        return headers, rows;

    def create(self,html,text,subject,receiver,data,href_key=None,Href_target=None):
        """creates the email object
            Arguments:
                html {string} -- html content template
                text {string} -- text content template
                subject {string} -- subject of email
                receiver {string} -- email address of the receiver
                data {list} -- contains a list of dicts with data to populate email template with

            returns:
                MimeMultipart Object
        """
        #sets the headers of the message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.sender
        message["To"] = receiver

        html_headers, html_rows = self.create_html_table(data,href_key,Href_target)
        #Read the Html File
        with open(html,'r',encoding='UTF-8') as f:
            html_data=f.read()
        html_formatted=html_data.format(
            table_headers=html_headers,
            table_rows=html_rows,
            snipeit_server_name=self.server_name,
            snipeit_maintenance_items=len(data)
        )
        #Read the text File
        with open(text,'r',encoding='UTF-8') as f:
            text_data=f.read()         
        text_table=self.create_text_table(data)
        text_formatted=text_data.format(text_table=text_table,snipeit_server_name=self.server_name,snipeit_maintenance_items=len(data))
        #attatches the plain text and html content to the message
        message.attach(MIMEText(text_formatted,'plain'))
        message.attach(MIMEText(html_formatted,'html',))
        #creates a content ID for the logo and adds it to the message

        with open(self.message_body_logo,'rb') as f:
            mime = MIMEBase('image','png',filename=self.message_body_logo)
            mime.add_header('Content-Disposition', 'attachment', filename=self.message_body_logo)
            mime.add_header('X-Attachment-Id', '0')
            mime.add_header('Content-ID', '<0>')
            mime.set_payload(f.read())
            encode_base64(mime)
            message.attach(mime)
        #returns the message object
        return message

    def send(self,receiver,message):
        """Send SMTP Mail"""
        with smtplib.SMTP(self.server,self.port) as server:
            if self.use_tls:
                if server.starttls(context=self.ssl_context)[0] != 220:
                    logging.error("Failed to Start TLS")
                    return False
                server.login(self.username,self.password)
            server.sendmail(
                self.sender,
                receiver,
                message.as_string()
            )

