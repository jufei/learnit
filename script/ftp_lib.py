from miniftp import MiniFTP
from urlparse import urlparse
import os


def download_from_ftp_to_local(ftp_url, local_file, mode='bin', user='anonymous', password='anonymous@'):
    """ This keyword download a file from Ftp server to local of test case running.

    | Input Parameters | Man. | Description |
    | ftp_url        | yes  | the URL of download file. |
    | local_file    | yes   | the file path for save the downloaded file |
    | mode          | NO   | the translate mode of FTP. default is BIN (values:BIN, TEXT) |
    | user          | NO   | the username to login in ftp server, default is anonymous |
    | password      | NO   | the password to login in ftp server, default is anonymous  |


    example usage:
    | Download From Ftp To Local | ftp://10.56.117.112/etc/ipsec_configuration.xml | c:${/}ipsec_configuration.xml | BIN |

    | Return value | the output of command |
    """
    url = urlparse(ftp_url)

    ftp_obj = MiniFTP(url.hostname, url.port or 21, user, password, "", 'trace')

    if os.path.isdir(local_file):
        ftp_obj.download_dirs(local_file, url.path)
    else:
        ftp_obj.download(local_file, url.path, mode)


def _download_from_ftp_to_remote(url, local, mode, user=None, password=None):
    pass


def upload_to_ftp_from_local(ftp_url, local_file, mode='bin', user='anonymous', password='anonymous@'):
    """ This keyword upload a file to Ftp server from local of test case running.

    | Input Parameters | Man. | Description |
    | ftp_url        | yes  | the URL of upload file. |
    | local_file    | yes   | the local file path for upload |
    | mode          | NO   | the translate mode of FTP. default is BIN (values:BIN, TEXT) |
    | user          | NO   | the username to login in ftp server, default is anonymous |
    | password      | NO   | the password to login in ftp server, default is anonymous  |


    example usage:
    | Upload to Ftp From Local | ftp://10.56.117.112/etc/ipsec_configuration.xml | c:${/}ipsec_configuration.xml | BIN |

    | Return value | the output of command |
    """

    url = urlparse(ftp_url)

    ftp_obj = MiniFTP(url.hostname, url.port or 21, user, password, "", 'trace')

    if os.path.isdir(local_file):
        ftp_obj.upload_dirs(local_file, url.path)
    else:
        ftp_obj.upload(local_file, url.path, mode)


def _upload_to_ftp_from_remote(url, local, mode, user=None, password=None):
    pass


def sftp_download_file(host, port, username, password, remote_filename, remote_path, local_filename):
    import paramiko
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    print remote_path + '/' + remote_filename
    sftp.get(remote_path + '/' + remote_filename, local_filename)
    sftp.close()
    transport.close()


def sftp_download_files(host, port, username, password, remote_file_filter, remote_path, local_path):
    import paramiko
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    ret = []
    filelist = sftp.listdir(remote_path)  # list files in sftp server, return a list type of filename
    for filename in filelist:
        if remote_file_filter in filename:
            remotefile = remote_path + '/' + filename
            localfile = os.sep.join([local_path, filename])
            print remotefile
            sftp.get(remotefile, localfile)
            ret.append(filename)
    sftp.close()
    transport.close()
    return ret


def sftp_upload_file(host, port, username, password, remote_filename, remote_path, local_filename):
    import paramiko
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    print remote_path + '/' + remote_filename
    sftp.put(local_filename, remote_path + '/' + remote_filename)
    sftp.close()
    transport.close()


def download_files_from_remote_dire(host, port, username, password, remote_dire, local_dire):
    ftp_obj = MiniFTP(host, port, username, password, "", 'trace')
    output = ftp_obj.list(remote_dire)
    print output

    for filename in output:
        print filename.split(' ')[-1]


def ftp_download_files(host, port, username, password, remote_file_filter, remote_path, local_path):
    print remote_path
    ftp_obj = MiniFTP(host, port, username, password, "", 'trace')
    output = []
    output = ftp_obj.ftp.nlst(remote_path)
    for filename in output:
        if remote_file_filter in filename:
            lfilename = os.sep.join([local_path, filename.split('/')[-1]])
            print 'Download: %s --- %s ' % (filename, lfilename)
            ftp_obj.download(lfilename, filename, 'bin')


if __name__ == '__main__':
    ftp_download_files('10.69.66.180', '21', 'TA_LOG', 'TA_LOG', '.csv',
                       '/TM500_LOG/170519_105006_SESSION/170519_112333', '/home/work/Jenkins2/workspace')
    print 'Done'
