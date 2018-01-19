import os, sys, time
from thread import *
import threading
from PetShell.connections.telnet_connection import TelnetConnection

class tm500_manager():
    def __init__(self, host, port=5003):
        self.host = host
        self.port = port
        self.conn = None
        self.exit = True

    def connect(self):
        self.conn = TelnetConnection(self.host, self.port, '', 30, "CR")

    def disconnect(self):
        if self.conn:
            self.conn.close_connection()
            self.conn = None

    def working_thread(self):
        while 1:
            if not self.conn:
                return 0
            ret = self.conn.read_very_eager()
            if ret:
                print ret

    def run(self):
        if not self.conn:
            self.connect()
        self.exit = False
        start_new_thread(self.working_thread , ())
        count = 0
        while 1:
            if self.exit:
                self.stop()
                break
            else:
                count += 1
                if count == 100:
                    self.execute_command('HELP')
                time.sleep(0.01)

    def stop(self):
        self.exit = True

    def execute_command(self, command):
        self.conn.write('%s\n\r' %(command))
        pass



def main():
    tm500 = tm500_manager('10.69.64.88')
    try:
        tm500.run()
    finally:
        tm500.stop()
        # time.sleep(0.1)
    pass

if __name__ == '__main__':
    main()

