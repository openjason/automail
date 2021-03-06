# -*- coding: UTF-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import logging
import os
import configparser
import re
import time
from filecmp import dircmp

SMTP_SERVER = ""
WORK_DIR = ""
SMTP_USER = ""
SMTP_PWD = "none"

long_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
folder_prefix = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

cf = configparser.ConfigParser()
try:
    cf.read('conf.ini', encoding="utf-8-sig")
    customer_total = int (cf.get("Common", "total"))
    from_email_addr = cf.get("Common", "from_email_addr")
    SMTP_SERVER = cf.get("Common", "SMTP_SERVER")
    WORK_DIR = cf.get("Common", "WORK_DIR")
    SMTP_USER = cf.get("Common", "SMTP_USER")
    SMTP_PWD = cf.get("Common", "SMTP_PWD")

except:
    logging.warning('无法打开文件 file d:\\automail\\conf.ini 或设置错误.')
    exit(2)
customer_name = []
customer_folder = []
customer_wildcard = []
customer_toaddr = []
customer_ccaddr = []
customer_subject = []
for i in range(1,customer_total+1):
    try:
        cfstr = 'Customer' + str(i)
        customer_name.append(cf.get(cfstr,'name'))
        customer_folder.append(cf.get(cfstr,'folder'))
        customer_wildcard.append(cf.get(cfstr,'wildcard'))
        customer_toaddr.append(cf.get(cfstr,'to_email_addr'))
        customer_ccaddr.append(cf.get(cfstr,'cc_email_addr'))
        customer_subject.append(cf.get(cfstr,'subject'))
    except:
        logging.warning("conf.ini 配置有误，位置:"+cfstr)
#    print (customer_name)
#    print (customer_toaddr)


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename = os.path.join(WORK_DIR,'automail.log'),
                    filemode='a')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

def send_email(dir_path,files,toaddr,ccaddr,c_name,c_subject):

    c_subject = c_subject.replace("YYYY-MM-DD",long_date)
    logging.info("Subject:"+c_subject)
    msg = MIMEMultipart()
    msg['To'] = ";".join(toaddr)
    msg['CC'] = ";".join(ccaddr)
    msg['From'] = SMTP_USER
    msg['Subject'] = c_subject
    html = ""
    template_file_name = WORK_DIR+"template\\"+c_name+".template"
    try:
        with open(template_file_name,"r",encoding="utf-8") as t_f:
            for temp_line in t_f:
                html = html + temp_line
    except:
        html = '无正文内容'

    html = html.replace("YYYY-MM-DD",long_date)
    html = html.replace("ATTACHMENT","、".join(files))

    print(html)


    body = MIMEText(html, 'plain')
    #    body = MIMEText(text_body, 'plain')
    msg.attach(body)  # add message body (text or html)

    for f in files:  # add files to the message
        file_path = os.path.join(dir_path, f)
        attachment = MIMEApplication(open(file_path, "rb").read())
        attachment.add_header('Content-Disposition','attachment', filename=f)
        msg.attach(attachment)

    server = smtplib.SMTP(SMTP_SERVER, 25)
    #    server.starttls()
    server.login(SMTP_USER, SMTP_PWD)
    mailbody = msg.as_string()

    server.sendmail(SMTP_USER, toaddr + ccaddr, mailbody) #send mail to & cc email address
    logging.info(c_name + ":发送邮件："+"to:"+";".join(toaddr)+" ;附件："+";".join(files))
    server.quit()

def get_customer_file_list(folder,wildard):
    _filelist = []
    source_dir = folder
    have_file = False
    _wildcard = wildard.split('|')
    if not os.path.exists(folder):
        logging.warning("文件夹不存在："+ folder)
        return _filelist
    for i in range(len(_wildcard)):
        _wcard = _wildcard[i]
        _wcard = _wcard.replace('*','')
        for j in os.listdir(source_dir):
            if j.find(_wcard) > 0 :
                have_file = True
                if not(j in _filelist):
                    _filelist.append(j)
    if not have_file :
        logging.info("没有匹配文件_folder:"+source_dir+"  "+wildard)
    return _filelist

def get_customer_mail_list(toaddr):
    _mail_list =[]
    _to_addr = toaddr.split("|")
    for i in range(len(_to_addr)):
        if len(_to_addr[i]) > 7:
            if re.match('^[\w\d]+[\d\w\_\.]+@([\d\w]+)\.([\d\w]+)(?:\.[\d\w]+)?$|^(?:\+86)?(\d{3})\d{8}$|^(?:\+86)?(0\d{2,3})\d{7,8}$', _to_addr[i]) != None:
                _mail_list.append(_to_addr[i])
            else:
                logging.info("邮件地址有误："+_to_addr[i])
    return _mail_list

def prepare_files(source_dir,  target_dir):
    copy_ok = True
    for file in os.listdir(source_dir):
        sourceFile = os.path.join(source_dir,  file)
        targetFile = os.path.join(target_dir,  file)
        try:
            open(targetFile, "wb").write(open(sourceFile, "rb").read())
            logging.info("复制文件:"+str(sourceFile) + " to " + str(targetFile))
        except:
            logging.info('copy file error.')
            copy_ok = False
    return copy_ok
def check_diff_n_leftonly_files(dir1,dir2):
    dcmp = dircmp(dir1, dir2)
    is_diff = False
    if len(dcmp.diff_files)>0:
        is_diff = True
        logging.info ("diff_file:" + ";".join(dcmp.diff_files))
    if len(dcmp.left_only)>0:
        is_diff = True
        logging.info ("source_only:" + ";".join(dcmp.left_only))
    return is_diff

if __name__ == '__main__':


    for i in range(customer_total):
        folder_list = customer_folder[i]
        c_name = customer_name[i]
        file_list = get_customer_file_list(folder_list,customer_wildcard[i])

        if len(file_list) > 0:
            limit_times = 1
            while limit_times < 9:
                folder_prefix = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                prepare_folder = WORK_DIR+"sent\\" + folder_prefix+customer_name[i]
                os.mkdir(prepare_folder)
                if prepare_files(customer_folder[i],prepare_folder) == False:
                    logging.warning("拷贝文件夹出错...")
                    continue
                if check_diff_n_leftonly_files(customer_folder[i],prepare_folder) == False:
                    logging.info("拷贝文件夹与原文件夹一致,已比对次数:" + str(limit_times))
                    time.sleep(limit_times * limit_times)
                    break
                else:
                    logging.warning("拷贝文件夹与原文件夹不一致次数:" + str(limit_times))
                limit_times +=1

            file_list = get_customer_file_list(prepare_folder,customer_wildcard[i])

            tomail_list = get_customer_mail_list(customer_toaddr[i])
            ccmail_list = get_customer_mail_list(customer_ccaddr[i])
            c_subject = customer_subject[i]
            print(tomail_list,ccmail_list)
            print (prepare_folder,file_list,tomail_list,ccmail_list,c_name,c_subject)

            send_email(prepare_folder,file_list,tomail_list,ccmail_list,c_name,c_subject)
            logging.info("sending mail....."+c_name)
            time.sleep(3)