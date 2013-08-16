#! /usr/bin/python

import smtplib

from optparse import OptionParser
import argparse
import configparser

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication

CONFIG_FILE = "send_mail.conf"

parser = argparse.ArgumentParser()

parser.add_argument('-f', '--from', dest='sender', action='store', default='netman.gor@gmail.com')
parser.add_argument('-t', '--to', dest='recipients', metavar='RECIPIENT', action='append', nargs='+', required=True)
parser.add_argument('-s', '--subject', dest='subject', action='store', required=True)

parser.add_argument('-m', '--html', dest='html', action='store', help="html content file")
parser.add_argument('-x', '--text', dest='text', action='store', help="text content file")
parser.add_argument('-i', '--image', dest='images', metavar='IMAGE', action='append', nargs='+')

args = parser.parse_args()
args.recipients = [item for sublist in args.recipients for item in sublist]
args.images = [item for sublist in args.images for item in sublist]

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

SMTP_SERVER   = config.get("Mail", "smtp_server")
SMTP_PORT     = config.getint("Mail", "smtp_port")
SMTP_USERNAME = config.get("Mail", "username")
SMTP_PASSWORD = config.get("Mail", "password")

msgRoot = MIMEMultipart('related')
msgRoot['Subject'] = args.subject
msgRoot['From'] = args.sender
msgRoot['To'] = ','.join(args.recipients)
msgRoot.preamble = 'This is a multi-part message in MIME format.'

if args.html:
    html = open(args.html, 'r').read()
    msgHtml = MIMEText(html, 'html')

if args.text:
    text = open(args.text, 'r').read()
    msgText = MIMEText(text)

if args.html and args.text:
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)
    msgAlternative.attach(msgText)
    msgAlternative.attach(msgHtml)

else:
    if args.html:
        msgRoot.attach(msgHtml)

    if args.text:
        msgRoot.attach(msgText)    

for imageName in args.images:
    img = open(imageName, 'rb').read()
    msgImg = MIMEImage(img, 'png')
    msgImg.add_header('Content-ID', '<%s>' % imageName)
    msgImg.add_header('Content-Disposition', 'inline', filename=imageName)
    msgRoot.attach(msgImg)

session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)

session.ehlo()
session.starttls()
session.ehlo()
session.login(SMTP_USERNAME, SMTP_PASSWORD)

session.sendmail(args.sender, args.recipients, msgRoot.as_string())
session.quit()
