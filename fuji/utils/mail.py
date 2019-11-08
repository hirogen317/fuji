import re
import base64
import smtplib
import mimetypes

from email.mime.text import MIMEText
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from os.path import basename


class MailSender(object):

    CONFIG_SMTP_SERVER = 'SMTP_server'
    CONFIG_SMTP_PORT = 'SMTP_port'
    CONFIG_MAIL_ACCOUNT = 'account'
    CONFIG_MAIL_PASSWORD = 'password'
    CONFIG_DISPLAY_NAME = 'display_name'

    def __init__(self, account_config):
        for mail_account_field in [MailSender.CONFIG_SMTP_SERVER, MailSender.CONFIG_SMTP_PORT,
                                   MailSender.CONFIG_MAIL_ACCOUNT, MailSender.CONFIG_MAIL_PASSWORD]:
            if mail_account_field not in account_config:
                raise Exception("{} field missing in Mail account config file.".format(mail_account_field))

        self.smtp_server = account_config[MailSender.CONFIG_SMTP_SERVER]
        self.smtp_port = account_config[MailSender.CONFIG_SMTP_PORT]
        self.mail_account = account_config[MailSender.CONFIG_MAIL_ACCOUNT]
        self.mail_password = account_config[MailSender.CONFIG_MAIL_PASSWORD]

        self.display_name = account_config.get(MailSender.CONFIG_DISPLAY_NAME, self.mail_account)

    @staticmethod
    def _parse_address(address):
        mail_full_pattern = '[^,<]+\<([^,>]+)\>'
        mail_simple_pattern = '[^,<@]+@[^,<@]+'

        send_address_list = []
        if type(address) is str:
            address_list = address.split(',')
        elif type(address) is list:
            address_list = address
        else:
            return []
        for single_address in address_list:
            full_match_result = re.match(mail_full_pattern, single_address)
            if full_match_result:
                send_address_list.append(full_match_result.group(1))
            else:
                simple_pattern_match_result = re.match(mail_simple_pattern, single_address)
                if simple_pattern_match_result:
                    send_address_list.append(simple_pattern_match_result.group(0))
                else:
                    raise Exception("Invalidate mail address: {}".format(single_address))

        return send_address_list

    @staticmethod
    def encode_mail_address(mail_addresses):
        formatted_mail_addresses = []
        for index, mail_address in enumerate(mail_addresses):
            match = re.search('([^<]+) <(.+)>', mail_address)
            if match is None:
                formatted_mail_addresses.append(mail_address)
            else:
                formatted_mail_addresses.append('{} <{}>'.format(Header(match.group(1), 'utf-8').encode(), match.group(2)))

        return formatted_mail_addresses

    def send_email(self, address_to=None, address_cc=None, address_bcc=None,
                   subject='', body='', attachements=None, display_name=None):
        smtpobj = self.connect_and_login_account()
        if address_to is None and address_cc is None and address_bcc is None:
            raise Exception('No place to send the Email')

        # Display Names
        if display_name is None:
            display_name = self.display_name
        display_name = "{} <{}>".format(display_name, self.mail_account)

        if address_to is not None:
            address_to_list = address_to.split(',')
            encoded_address_to_list = MailSender.encode_mail_address(address_to_list)
            encoded_address_to = ','.join(encoded_address_to_list)
        else:
            encoded_address_to = None

        if address_cc is not None:
            address_cc_list = address_cc.split(',')
            encoded_address_cc_list = MailSender.encode_mail_address(address_cc_list)
            encoded_address_cc = ','.join(encoded_address_cc_list)
        else:
            encoded_address_cc = None

        if address_bcc is not None:
            address_bcc_list = address_bcc.split(',')
            encoded_address_bcc_list = MailSender.encode_mail_address(address_bcc_list)
            encoded_address_bcc = ','.join(encoded_address_bcc_list)
        else:
            encoded_address_bcc = None

        msg = MailSender.create_mail_object(display_name, mail_to=encoded_address_to,
                                            mail_cc=encoded_address_cc, mail_bcc=encoded_address_bcc, mail_subject=subject,
                                            mail_body_html=body, attachements=attachements)

        smtpobj.send_message(msg)
        smtpobj.close()

    def connect_and_login_account(self):
        smtpobj = smtplib.SMTP(self.smtp_server, self.smtp_port)
        smtpobj.ehlo()
        smtpobj.starttls()
        smtpobj.ehlo()
        smtpobj.login(self.mail_account, self.mail_password)
        return smtpobj

    @staticmethod
    def create_mail_object(mail_from, mail_to=None, mail_cc=None, mail_bcc=None, mail_subject='', mail_body_html='', attachements=None):
        mail = MIMEMultipart()
        mail['Subject'] = mail_subject
        mail['From'] = mail_from
        if mail_to is not None:
            mail['To'] = mail_to
        if mail_cc is not None:
            mail['Cc'] = mail_cc
        if mail_bcc is not None:
            mail['Bcc'] = mail_bcc

        mail['Date'] = formatdate()
        mail.attach(MIMEText(mail_body_html))

        if type(attachements) == list:
            for f in attachements:
                mimetype, _ = mimetypes.guess_type(f)
                if mimetype is None:
                    mimetype = 'application/octet-stream'
                _, subtype = mimetype.split('/')

                with open(f, 'rb') as file:
                    part = MIMEApplication(
                        file.read(),
                        _subtype=subtype
                    )
                file_name_format = base64.b64encode(basename(f).encode('UTF-8')).decode()
                part.add_header('Content-Disposition', 'attachment', filename='=?utf-8?b?' + file_name_format + '?=')

                mail.attach(part)
        elif type(attachements) == dict:
            for filename, fileobj in attachements.items():
                mimetype, _ = mimetypes.guess_type(filename)
                if mimetype is None:
                    mimetype = 'application/octet-stream'
                _, subtype = mimetype.split('/')

                fileobj.seek(0)
                part = MIMEApplication(
                    fileobj.getvalue(),
                    _subtype=subtype
                )
                file_name_format = base64.b64encode(filename.encode('UTF-8')).decode()
                part.add_header('Content-Disposition', 'attachment', filename='=?utf-8?b?' + file_name_format + '?=')

                mail.attach(part)
        return mail
