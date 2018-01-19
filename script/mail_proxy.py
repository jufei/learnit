import os, time

import smtplib

mailfile = '/tmp/petmail.txt'
smtp_server = 'mail.emea.nsn-intra.net'
logfile = '/data/jufei/petmail.log'

def loginfo(info):
    with open(logfile, 'a') as f:
        info = time.ctime() + '  '+ info
        print info
        f.write(info)



def sendmail():
    if not os.path.exists(mailfile):
        return 0
    lines = [x for x in open(mailfile).readlines()]

    from email.mime.text import MIMEText
    from email.utils import COMMASPACE, formatdate

    from_ = 'I_PET1_TA_GROUP@internal.nsn.com'
    to_   = 'fei.ju@nokia.com'
    for i in range(len(lines)):
        line = lines[i]
        if 'mailto:' in line:
            to_ = line.splitlines()[0].split(':')[-1]
        if 'Subject:' in line:
            subject_ = ':'.join(line.splitlines()[0].split(':')[1:])
            break

    try:
        smtp = smtplib.SMTP(smtp_server)
        loginfo('To mail list: ' + to_)
        for to in to_.replace(',', ';').split(';'):
            if to.strip():
                msg = MIMEText(''.join(lines[i+1:]))
                msg['From'] = from_
                msg['To'] = to
                msg['Subject'] = subject_
                msg['Date'] = formatdate(localtime=True)
                smtp.sendmail(from_, to, msg.as_string())
                loginfo('Send mail to %s successful, please check it.\n' %(to))
        os.remove(mailfile)
    except:
        loginfo('Send mail failed, please check it.')
    finally:
        smtp.close()
if __name__ == '__main__':
    while True:
        sendmail()
        time.sleep(5)
