import sys, os
from  optparse import *

sys.path.append('/data/utelib/src')

def main(args = sys.argv[1:]):
    parser = OptionParser()
    parser.add_option("-a",  "--address", dest="address", default=None)
    parser.add_option("-p",  "--port", dest=3600, default=None)
    (options, args) = parser.parse_args()

    import ute_admin
    admin = ute_admin.ute_admin()
    try:
        admin.setup_admin(  enb_address=options.address,
                            enb_port=options.port,
                            username="developer",
                            password="$developer#",
                            use_ssl=True)
        print 'Admin API Setup completed!'
    finally:
        admin.teardown_admin()
        print 'Admin API Teardown completed!'

