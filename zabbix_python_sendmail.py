[monitor@zabbix alertscripts]$ cat sendmail.py
#!/usr/bin/python3
# _*_ coding:utf-8 _*_

import smtplib, sys
from email.mime.text import MIMEText
from email.utils import formataddr
import time

def send_mail(to_email, subject, message):
    my_sender = 'oneuser@aliyun.com'
    my_pass = 'passwd'
    my_user = to_email
    time_str = time.strftime('%Y-%m-%d %X', time.localtime(time.time()))
    message = message.replace('\n','<p>')
    msg_html = '<html><body>' + message + "<br><br><span style='color:#999;font-size:"\
        + "10px;font-family:Verdana;'>" \
        + time_str + " by " + my_sender + "</span>"+'</body></html>'

    send_msg = MIMEText(msg_html, 'html', 'utf-8')

    # 发送邮件的信息主体，发件人，收件人，内容
    #msg = MIMEText(message, 'plain', 'utf-8')
    send_msg['From'] = formataddr(["oneuser@aliyun.com", my_sender])
    #msg['To'] = formataddr(["Ops", my_user])
    send_msg['To'] = my_user
    send_msg['Subject'] = subject
    send_msg['X-Mailer'] = 'Foxmail 7.2.15.80[cn]'

    server = smtplib.SMTP_SSL("smtp.aliyun.com", 465)
    server.login(my_sender, my_pass)
    server.sendmail(my_sender, [my_user, ], send_msg.as_string())
    server.quit()

if __name__ == '__main__':
    send_mail(sys.argv[1], sys.argv[2], sys.argv[3])





monitor@zabbix alertscripts]$ cat sendmail.py
#!/usr/bin/python
# _*_ coding:utf-8 _*_

import smtplib, sys
from email.mime.text import MIMEText
from email.utils import formataddr


def send_mail(to_email, subject, message):
    my_sender = 'oneuser@aliyun.com'
    my_pass = 'passwd'
    my_user = to_email

    # 发送邮件的信息主体，发件人，收件人，内容
    msg = MIMEText(message, 'plain', 'utf-8')
    msg['From'] = formataddr(["oneuser@aliyun.com", my_sender])
    msg['To'] = formataddr(["Ops", my_user])
    msg['Subject'] = subject
    server = smtplib.SMTP_SSL("smtp.aliyun.com", 465)
    server.login(my_sender, my_pass)
    server.sendmail(my_sender, [my_user, ], msg.as_string())
    server.quit()

if __name__ == '__main__':
    send_mail(sys.argv[1], sys.argv[2], sys.argv[3])



[monitor@zabbix etc]$ cat mail.rc
# 改用python脚本，用户mm已直接写作原代码，无需此问题。
# This is the configuration file for Heirloom mailx (formerly
# known under the name "nail".
# See mailx(1) for further options.
# This file is not overwritten when 'make install' is run in
# the mailx build process again.

# Sccsid @(#)nail.rc	2.11 (gritter) 8/2/08

# Do not forward to mbox by default since this is likely to be
# irritating for most users today.
set hold

# Append rather than prepend when writing to mbox automatically.
# This has no effect unless 'hold' is unset again.
set append

# Ask for a message subject.
set ask

# Assume a CRT-like terminal and invoke a pager.
set crt

# Messages may be terminated by a dot.
set dot

# Do not remove empty mail folders in the spool directory.
# This may be relevant for privacy since other users could
# otherwise create them with different permissions.
set keep

# Do not remove empty private mail folders.
set emptybox

# Quote the original message in replies by "> " as usual on the Internet.
set indentprefix="> "

# Automatically quote the text of the message that is responded to.
set quote

# Outgoing messages are sent in ISO-8859-1 if all their characters are
# representable in it, otherwise in UTF-8.
set sendcharsets=iso-8859-1,utf-8

# Display sender's real names in header summaries.
set showname

# Display the recipients of messages sent by the user himself in
# header summaries.
set showto

# Automatically check for new messages at each prompt, but avoid polling
# of IMAP servers or maildir folders.
set newmail=nopoll

# If threaded mode is activated, automatically collapse thread.
set autocollapse

# Mark messages that have been answered.
set markanswered

# Hide some header fields which are uninteresting for most human readers.
ignore received in-reply-to message-id references
ignore mime-version content-transfer-encoding

# Only include selected header fields when forwarding messages.
fwdretain subject date from to

# For Linux and BSD, this should be set.
set bsdcompat
#set mail configure
set from=oneuser@aliyun.com
set smtp="smtps://smtp.aliyun.com:465"
set smtp-auth-user=oneuser@aliyun.com
set smtp-auth-password=passwd
set smtp-auth=login
set ssl-verify=ignore
set nss-config-dir=/etc/pki/nssdb
