import os
from ftplib import FTP

class MiniFTP(object):
    def __init__(self, host, port, username='anonymous', password='anonymous', root_path='', log_level = 'info'):
        ftp = FTP()
        ftp.connect(host, port)
        ftp.login(username, password)
        self.ftp = ftp

        for dir_name in root_path.split("/"):
            self.cdw(dir_name)

    def cdw(self, path):
        if not path:
            return

        for dir_name in path.split("/"):
            try:
                self.ftp.cwd(dir_name)
            except:
                self.ftp.mkd(dir_name)
                self.ftp.cwd(dir_name)


    def upload(self, local_path, ftp_path, mode='bin'):

        mode = mode and mode.lower() or 'bin'
        if(mode not in ('bin', 'text')):
            raise RuntimeError, "Invalid Ftp mode (%s)" % mode

        file_mode = (mode == 'bin') and 'rb' or 'r'
        file = open(local_path, file_mode)
        try:
            if(mode == 'bin'):
                ret = self.ftp.storbinary('STOR %s' % ftp_path, file)
            else:
                ret = self.ftp.storlines('STOR %s' % ftp_path, file)

            return True
        finally:
            file.close()

        return False

    def upload_dirs(self, local_dir, ftp_dir):
        if not os.path.isdir(local_dir):
            raise RuntimeError, "'%s' not a directory!" % local_dir

        file_count = 0
        dir_count = 0
        path_list = [ [ e for e in os.listdir(local_dir) if e != '.svn' ], ]
        path = [ local_dir ]

        self.cdw(ftp_dir)

        while path_list:
            while path_list[-1]:
                file = path_list[-1].pop()
                cur_path = os.path.join(*path + [ file ])

                if os.path.isdir(os.path.join(*path + [ file ])):
                    self.cdw(file)
                    path.append(file)
                    cur_list = [ e for e in os.listdir(cur_path) if e != '.svn' ]
                    path_list.append(cur_list)
                    dir_count += 1
                else:
                    if self.upload(cur_path, file):
                        file_count += 1

            if len(path) > 1:
                self.cdw("..")
                path.pop()
            path_list.pop()

        return (True, file_count, dir_count)

    def download(self, local_path, ftp_path, mode='bin'):

        mode = mode and mode.lower() or 'bin'
        if(mode not in ('bin', 'text')):
            raise RuntimeError, "Invalid Ftp mode (%s)" % mode

        file_mode = (mode == 'bin') and 'w+b' or 'w'
        file = open(local_path, file_mode)
        try:
            if(mode == 'bin'):
                ret = self.ftp.retrbinary('RETR %s' % ftp_path, file.write)
            else:
                ret = self.ftp.retrlines('RETR %s' % ftp_path, file.writelines)

            file.close()

            return True
        except Exception, e:
            file.close()
            os.remove(local_path)
            raise e

        return False

    def download_dirs(self, local_dir, ftp_dir):
        raise RuntimeError, "not supported operation!"


    def list(self, path=""):
        print path
        dirs = self.ftp.dir(path)
        print dirs
        return dirs
