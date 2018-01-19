#! /usr/bin/env python
# -*- coding: UTF-8 -*-
# Filename  : hbte_pam.py  
# Author    : simon
# Date      : 2015/12/14
# Tel       : 18916101893 
# 适用于PAM
# Python version 2.7.9

#                     port configuration   example for 8*8
#
#          OUT1 OUT2    OUT3     OUT4    OUT5    OUT6   OUT7    OUT8
#        _____________________________________________________________
#   IN1 |   1   |   9  |   17  |  25  |   33  |   41  |  49  |   57  |
#       |------------------------------------------------------------|
#   IN2 |   2   |  10  |   18  |  26  |   34  |   42  |  50  |   58  |
#       |------------------------------------------------------------|
#   IN3 |   3   |  11  |   19  |  27  |   35  |   43  |  51  |   59  |
#       |------------------------------------------------------------|
#   IN4 |   4   |  12  |   20  |  28  |   36  |   44  |  52  |   60  |
#       |------------------------------------------------------------|
#   IN5 |   5   |  13  |   21  |  29  |   37  |   45  |  53  |   61  |
#       |------------------------------------------------------------|
#   IN6 |   6   |  14  |   22  |  30  |   38  |   46  |  54  |   62  |
#       | -----------------------------------------------------------|
#   IN7 |   7   |  15  |   23  |  31  |   39  |   47  |  55  |   63  |
#       | -----------------------------------------------------------|
#   IN8 |   8   |  16  |   24  |  32  |   40  |   48  |  56  |   64  |
#       |------------------------------------------------------------|
#
#                                                       port configuration   example for 16*16
#
#            OUT1   OUT2    OUT3   OUT4    OUT5    OUT6   OUT7       OUT8    OUT9   OUT10    OUT11  OUT12   OUT13   OUT14   OUT15   OUT16
#          ________________________________________________________________________________________________________________________________
#   IN1   |   1   |  17  |   33  |  49  |   65  |   81  |  97    |   113  |  129  |  145  |  161  |  177  |  193  |  209  |  225  |  241   |
#         |--------------------------------------------------------------------------------------------------------------------------------|
#   IN2   |   2   |  18  |   34  |  50  |   66  |   82  |  98    |   114  |  130  |  146  |  162  |  178  |  194  |  210  |  226  |  242   |
#         |--------------------------------------------------------------------------------------------------------------------------------|
#   IN3   |   3   |  19  |   35  |  51  |   69  |   83  |  99    |   115  |  131  |  147  |  163  |  179  |  195  |  211  |  227  |  243   |
#         |--------------------------------------------------------------------------------------------------------------------------------|
#   IN4   |   4   |  20  |   36  |  52  |   68  |   84  |  100   |   116  |  132  |  148  |  164  |  180  |  196  |  212  |  228  |  244   |
#         |--------------------------------------------------------------------------------------------------------------------------------|
#   IN5   |   5   |  21  |   37  |  53  |   69  |   85  |  101   |   117  |  133  |  149  |  165  |  181  |  197  |  213  |  229  |  245   |
#         |--------------------------------------------------------------------------------------------------------------------------------|
#   IN6   |   6   |  22  |   38  |  54  |   70  |   86  |  102   |   118  |  134  |  150  |  166  |  182  |  198  |  214  |  230  |  246   |
#         | -------------------------------------------------------------------------------------------------------------------------------|
#   IN7   |   7   |  23  |   39  |  55  |   71  |   87  |  103   |   119  |  135  |  151  |  167  |  183  |  199  |  215  |  231  |  247   |
#         | -------------------------------------------------------------------------------------------------------------------------------|
#   IN8   |   8   |  24  |   40  |  56  |   72  |   88  |  104   |   120  |  136  |  152  |  168  |  184  |  200  |  216  |  232  |  248   |
#         | -------------------------------------------------------------------------------------------------------------------------------|
#   IN9   |   9   |  25  |   41  |  57  |   73  |   89  |  105   |   121  |  137  |  153  |  169  |  185  |  201  |  217  |  233  |  249   |
#         |--------------------------------------------------------------------------------------------------------------------------------|
#   IN10  |  10   |  26  |   42  |  58  |   74  |   90  |  106   |   122  |  138  |  154  |  170  |  186  |  202  |  218  |  234  |  250   |
#         |--------------------------------------------------------------------------------------------------------------------------------|
#   IN11  |  11   |  27  |   43  |  59  |   75  |   91  |  107   |   123  |  139  |  155  |  171  |  187  |  203  |  219  |  235  |  251   |
#         |--------------------------------------------------------------------------------------------------------------------------------|
#   IN12  |  12   |  28  |   44  |  60  |   76  |   92  |  108   |   124  |  140  |  156  |  172  |  188  |  204  |  220  |  236  |  252   |
#         |--------------------------------------------------------------------------------------------------------------------------------|
#   IN13  |  13   |  29  |   45  |  61  |   77  |   93  |  109   |   125  |  141  |  157  |  173  |  189  |  205  |  221  |  237  |  253   |
#         |--------------------------------------------------------------------------------------------------------------------------------|
#   IN14  |  14   |  30  |   46  |  62  |   78  |   94  |  110   |   126  |  142  |  158  |  174  |  190  |  206  |  222  |  238  |  254   |
#         | -------------------------------------------------------------------------------------------------------------------------------|
#   IN15  |  15   |  31  |   47  |  63  |   79  |   95  |  111   |   127  |  143  |  159  |  175  |  191  |  207  |  223  |  239  |  255   |
#         | -------------------------------------------------------------------------------------------------------------------------------|
#   IN16  |  16   |  32  |   48  |  64  |   80  |   96  |  112   |   128  |  144  |  160  |  176  |  192  |  208  |  224  |  240  |  256   |
#         |--------------------------------------------------------------------------------------------------------------------------------|
#



#$TA,Z*\r\n                 查询设备配置
#$TA,F*\r\n                 查询所有通道
#$TA,E,00*\r\n              设置所有通道,快捷方式
#$TA,G,000102...7879*\r\n   设置所有通道


import socket
import time

function   = lambda x:hex(x)[2:].zfill(2)
transint   = lambda y:int(y)
transfloat = lambda z:float(z)


def OnePortOperate(ip, port, db):
    """
    FunctionName:   OnePortOperate
    FunctionParam:  ip    - as "192.168.1.254"
                    port  - "1"
                    dB    - "0.5" [all port set to 0.5dB]                                          
    FunctionReturn:  0      ok
                    -1      fail
                    -2      param error
    """
    clientsocket = None
    
    try:
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        clientsocket.settimeout(500)
        clientsocket.connect((ip, 5000))

        clientsocket.sendall("$TA,Z*\r\n")
        recvcmd = clientsocket.recv(512)
        
        if recvcmd == "FF\r\n":
            if clientsocket != None:
                clientsocket.close()
            return -1
        
        if recvcmd[8] != "*":  #index=8=* means the dev is pam
            if clientsocket != None:
                clientsocket.close()
            return -1

        if len(db) == 0 or len(port) == 0:
            if clientsocket != None:
                clientsocket.close()
            return -2

        #$TA,Z,08*08-90*\r\n
        inputport  = int(recvcmd[6:8])   
        outputport = int(recvcmd[9:11])

        if int(port)<1 or int(port)>(inputport*outputport):
            if clientsocket != None:
                clientsocket.close()
            return -2
                           
        sendcmd = "$TA,A,"  #set
        inport  = (int(port)-1)%inputport+1
        outport = (int(port)-1)/inputport+1
        sendcmd += (str(inport)).zfill(2)
        sendcmd += (str(outport)).zfill(2)
        sendcmd += function(int(float(db)*2)).upper()
        sendcmd += "*\r\n"
     
        clientsocket.sendall(sendcmd)
        recvcmd = clientsocket.recv(512)

        #马上发送查询指令
        sendcmd = "$TA,B,"  #read
        sendcmd += (str(inport)).zfill(2)
        sendcmd += (str(outport)).zfill(2)
        sendcmd += "*\r\n"

        clientsocket.sendall(sendcmd)
        recvcmd = clientsocket.recv(512)
        clientsocket.close()
          
        if recvcmd == "FF\r\n":
            if clientsocket != None:
                clientsocket.close()
            return -1
        
        if (recvcmd[10 : 12] == function(int(float(db)*2)).upper()) or (recvcmd[10 : 12] == 'FE'):
            return 0
        else:
            return -1
    except Exception,e:
        if clientsocket != None:
            clientsocket.close()
        print "Connect to %s failed, error is %s" % (ip, e)

    
def AllPortOperate(ip, db):
    """
    FunctionName:   AllPortOperate
    FunctionParam:  ip    - as "192.168.1.254"              
                    dB    - "0.5" [all port set to 0.5dB]                                          
    FunctionReturn:  0      ok
                    -1      fail
                    -2      param error
    """
    statuslist = []
    clientsocket = None
    
    try:
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        clientsocket.settimeout(500)
        clientsocket.connect((ip, 5000))

        clientsocket.sendall("$TA,Z*\r\n")
        recvcmd = clientsocket.recv(512)
        
        if recvcmd == "FF\r\n":
            if clientsocket != None:
                clientsocket.close()
            return -1
        
        if recvcmd[8] != "*":  #index=8=* means the dev is pam
            if clientsocket != None:
                clientsocket.close()
            return -1

        if len(db) == 0:
            if clientsocket != None:
                clientsocket.close()
            return -2

        #$TA,Z,08*08-90*\r\n
        inputport  = int(recvcmd[6:8])   
        outputport = int(recvcmd[9:11])
                           
        sendcmd = "$TA,E,"                 
        sendcmd += function(int(float(db)*2)).upper()
        sendcmd += "*\r\n"
            
        clientsocket.sendall(sendcmd)
        recvcmd = clientsocket.recv(512)

        clientsocket.sendall("$TA,F*\r\n")  #马上发送查询指令
        recvcmd = clientsocket.recv(4096)
        clientsocket.close()
        
        if recvcmd == "FF\r\n":
            if clientsocket != None:
                clientsocket.close()
            return -1

        for i in range(outputport):          #控制总循环次数
            for j in recvcmd[(9+inputport*2)*i+6: (9+inputport*2)*i+((6+inputport*2))]:   
                statuslist.append(j)
                
        recvcmd = "".join(statuslist)
        for i in range(inputport*outputport):
            if (function(int(float(db)*2)).upper() == recvcmd[i*2 : i*2+2]) or (recvcmd[i*2 : i*2+2]=='FE'):
                pass
            else:
                return -1
        return 0
    except Exception,e:
        if clientsocket != None:
            clientsocket.close()
        print "Connect to %s failed, error is %s" % (ip, e)
    
def PortOperate(ip, port, db):
    """
    FunctionName:   PortOperate
    FunctionParam:  ip    - as "192.168.1.254"
                    port  - "1,2,  33, 44"
                    db    - "0,1.5,10, 25.5"
    FunctionReturn: 0       ok
                    -1      fail
                    -2      param error
    """ 
    clientsocket = None
    statuslist = []
    sendcmd = "$TA,G,"
    
    try:
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        clientsocket.settimeout(500)
        clientsocket.connect((ip, 5000))

        clientsocket.sendall("$TA,Z*\r\n")
        recvcmd = clientsocket.recv(512)
        
        if recvcmd == "FF\r\n":
            if clientsocket != None:
                clientsocket.close()
            return -1
        
        if recvcmd[8] != "*":  #index=8=* means the dev is pam
            if clientsocket != None:
                clientsocket.close()
            return -1
             
        if len(port)==0 or len(db)==0:
            if clientsocket != None:
                clientsocket.close()
            return -2
        #$TA,Z,08*08-90*\r\n
        inputport  = int(recvcmd[6:8])   
        outputport = int(recvcmd[9:11])
        
        for i in range(outputport):         #控制总循环次数
            for j in range(inputport*2):      
                statuslist.append('F')      #填充F
        
        portlist = map(lambda x:x.strip(), port.split(","))#"1,2, 14, 15"  str  -->['1', '2', '14', '15']
        dblist   = map(lambda x:x.strip(), db.split(","))  #"1,2, 14, 15"  str  -->['1', '2', '14', '15']

        port_list = map(lambda x:transint(x), portlist)    #1,2,14,15      int  -->[1, 2, 14, 15]     
        db_list   = map(lambda x:transfloat(x), dblist)    #1,2,14,15      float-->[1, 2, 14, 15]
	
        db = map(lambda x: int(x*2), db_list)              #2,A,58,5B
        setdb_para = map(lambda c:function(c).upper(), db) #02,0A,58,5B
     
        if len(port_list) == len(db):
            for i in range(len(port_list)):
                if port_list[i]<1 or port_list[i]>(inputport*outputport):
                    if clientsocket != None:
                        clientsocket.close()
                    return -2
                
                statuslist[ 2*(port_list[i]-1)]   = setdb_para[i][0]
                statuslist[ 2*(port_list[i]-1)+1] = setdb_para[i][1]           
           
            statuslist.append("*\r\n")              
            sendcmd += "".join(statuslist)

            clientsocket.sendall(sendcmd)
            recvcmd = clientsocket.recv(4096)

            if recvcmd =="FF\r\n":
                return -1
            
            clientsocket.sendall("$TA,F*\r\n")  #马上发送查询指令
            recvcmd = clientsocket.recv(4096)
            clientsocket.close()
            
            if recvcmd == "FF\r\n":
                if clientsocket != None:
                    clientsocket.close()
                return -1
            
            statuslist = []
            for i in range(outputport):          #控制总循环次数
                for j in recvcmd[(9+inputport*2)*i+6: (9+inputport*2)*i+((6+inputport*2))]:   
                    statuslist.append(j)
                
            recvcmd = "".join(statuslist)
             
            for i in range(len(setdb_para)):
                if (setdb_para[i] == recvcmd[(port_list[i]-1)*2 : port_list[i]*2]) or (recvcmd[(port_list[i]-1)*2 : port_list[i]*2]=='FE'):
                    pass
                else:
                    return -1
            return 0
    
        else:   #len(port)!=len(db)
            if clientsocket != None:
                clientsocket.close()
            return -2        
    except Exception,e:
        if clientsocket != None:
            clientsocket.close()
        print "Connect to %s failed, error is %s" % (ip, e)

def MulPortOperate(ip, startport, endport, db):
    """
    FunctionName:   MulPortOperate
    FunctionParam:  ip        - as "192.168.1.254"
                    startport - as "1"
                    endport   - as "5" 
                    db        - "1.5"
    FunctionReturn:  0          ok
                    -1          fail
                    -2          param error
    """
    clientsocket = None
    statuslist = []
    sendcmd = "$TA,G,"
    
    try:
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.settimeout(500)
        clientsocket.connect((ip, 5000))

        clientsocket.sendall("$TA,Z*\r\n")
        recvcmd = clientsocket.recv(512)
        
        if recvcmd == "FF\r\n":
            if clientsocket != None:
                clientsocket.close()
            return -1
        
        if recvcmd[8] != "*":       #index=8=* means the dev is pam
            if clientsocket != None:
                clientsocket.close()
            return -1      
     
        try:            
            inputport  = int(recvcmd[6:8])
            outputport = int(recvcmd[9:11])
            
            db = db.strip()
            if float(db)<0:
                if clientsocket != None:
                    clientsocket.close()
                return -2        
            if int(startport) >= int(endport) or int(startport)==0 or int(endport)==0 or int(endport)>(inputport*outputport):                 
                if clientsocket != None:
                    clientsocket.close()
                return -2
        except Exception,e:
            if clientsocket != None:
                clientsocket.close()
            print"Parameter error is %s" % (e)
        
        for i in range(outputport):         #控制总循环次数
            for j in range(inputport*2):      
                statuslist.append('F')      #填充F
     
        dbhex = function(int(float(db)*2)).upper()
        for i in range(int(startport), int(endport)+1):
            statuslist[ 2*(i-1)]   = dbhex[0]
            statuslist[ 2*(i-1)+1] = dbhex[1]
                
        statuslist.append("*\r\n")              
        sendcmd += "".join(statuslist)
                
        clientsocket.sendall(sendcmd)
        recvcmd = clientsocket.recv(4096)

        clientsocket.sendall("$TA,F*\r\n")  #马上发送查询指令
        recvcmd = clientsocket.recv(4096)
        clientsocket.close()
        
        if recvcmd =="FF\r\n":
            return -1
        
        statuslist = []
        for i in range(outputport):          #控制总循环次数
            for j in recvcmd[(9+inputport*2)*i+6: (9+inputport*2)*i+((6+inputport*2))]:   
                statuslist.append(j)
                
        recvcmd = "".join(statuslist)
            
        for i in range(int(startport), int(endport)+1):           
            if (dbhex == recvcmd[(i-1)*2 : i*2]) or (recvcmd[(i-1)*2 : i*2]=='FE'):
                pass
            else:
                return -1
        return 0
    except Exception,e:
        if clientsocket != None:
            clientsocket.close()
        print "Connect to %s failed, error is %s" % (ip, e)

def RowOperate(ip, row, db):
    """
    FunctionName:   RowOperate
    FunctionParam:  ip  - as "192.168.1.254"
                    row - as "1" or "1,3,5"
                    db  - "5.5" 
    FunctionReturn:  0    ok
                    -1    fail
                    -2    param error
    """
    clientsocket = None
    statuslist = []
    sendcmd = "$TA,G,"
    
    try:
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        clientsocket.settimeout(500)
        clientsocket.connect((ip, 5000))

        clientsocket.sendall("$TA,Z*\r\n")
        recvcmd = clientsocket.recv(512)
        
        if recvcmd == "FF\r\n":
            if clientsocket != None:
                clientsocket.close()
            return -1
        
        if recvcmd[8] != "*":
            if clientsocket != None:
                clientsocket.close()
            return -1
             
        if len(row)==0 or len(db)==0:
            if clientsocket != None:
                clientsocket.close()
            return -2
        
        try:
            db = db.strip()
            if float(db)<0:
                if clientsocket != None:
                    clientsocket.close()
                return -2
            
            inputport  = int(recvcmd[6:8])
            outputport = int(recvcmd[9:11])
            
            rowlist = map(lambda x:x.strip(), row.split(",")) #['1', '3', '5']
            for i in range(len(rowlist)):
                if(int(rowlist[i])<1 or int(rowlist[i])>inputport):
                    if clientsocket != None:
                        clientsocket.close()
                    return -2                       
        except Exception,e:
            if clientsocket != None:
                clientsocket.close()
            print"Parameter error is %s" % (e)

        
        for i in range(outputport):         #控制总循环次数
            for j in range(inputport*2):      
                statuslist.append('F')      #填充F
                
        dbhex = function(int(float(db)*2)).upper()
        
        for i in range(len(rowlist)):       #行数范围
            for j in range(1, outputport+1):#列宽范围        
                statuslist[(inputport*2)*(j-1) + 2*int(rowlist[i]) -2] = dbhex[0]
                statuslist[(inputport*2)*(j-1) + 2*int(rowlist[i]) -1] = dbhex[1]
                
        statuslist.append("*\r\n")             
        sendcmd += "".join(statuslist)
                
        clientsocket.sendall(sendcmd)
        recvcmd = clientsocket.recv(4096)
        
        clientsocket.sendall("$TA,F*\r\n")  #马上发送查询指令
        recvcmd = clientsocket.recv(4096)
        clientsocket.close()
     
        if recvcmd =="FF\r\n":
            return -1

        statuslist = []
        for i in range(outputport):          #控制总循环次数
            for j in recvcmd[(9+inputport*2)*i+6 : (9+inputport*2)*i+((6+inputport*2))]:   
                statuslist.append(j)
                
        recvcmd = "".join(statuslist)
        
        for i in range(len(rowlist)):       #行数范围     
            for j in range(outputport):#列宽范围               
                #双倍间隔           偏移量
                startindex = (inputport*2)*(j) + 2*(int(rowlist[i])-1) #间隔inputport*2个距离取值                              
                if(dbhex==recvcmd[startindex : startindex+2]) or (recvcmd[startindex : startindex+2]=='FE'):
                    pass
                else:
                    return -1
        return 0
    except Exception,e:
        if clientsocket != None:
            clientsocket.close()
        print "Connect to %s failed, error is %s" % (ip, e)
    
def ColumnOperate(ip, column, db):
    """
    FunctionName:   ColumnOperate
    FunctionParam:  ip       - as "192.168.1.254"
                    column   - as "1" or "1,3,5"
                    db       - "5.5" 
    FunctionReturn:  0         ok
                    -1         fail
                    -2         param error
    """
    clientsocket = None
    statuslist = []
    sendcmd = "$TA,G,"
    
    try:
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        clientsocket.settimeout(500)
        clientsocket.connect((ip, 5000))

        clientsocket.sendall("$TA,Z*\r\n")
        recvcmd = clientsocket.recv(512)
        
        if recvcmd == "FF\r\n":
            if clientsocket != None:
                clientsocket.close()
            return -1
        if recvcmd[8] != "*":
            if clientsocket != None:
                clientsocket.close()
            return -1
             
        if len(column)==0 or len(db)==0:
            if clientsocket != None:
                clientsocket.close()
            return -2
        
        try:
            inputport  = int(recvcmd[6:8])
            outputport = int(recvcmd[9:11])
            
            db = db.strip()
            if float(db)<0:
                if clientsocket != None:
                    clientsocket.close()
                return -2
        
            columnlist = map(lambda x:x.strip(), column.split(","))
            for i in range(len(columnlist)):
                if(int(columnlist[i])<1 or int(columnlist[i])>outputport):
                    if clientsocket != None:
                        clientsocket.close()
                    return -2                       
        except Exception,e:
            if clientsocket != None:
                clientsocket.close()
            print"Parameter error is %s" % (e)
        
        for i in range(outputport):         #控制总循环次数
            for j in range(inputport*2):      
                statuslist.append('F')      #填充F
                
        dbhex = function(int(float(db)*2)).upper()
                
        for i in range(len(columnlist)):
            for j in range(1, inputport+1):  
                statuslist[(int(columnlist[i])-1)*(inputport*2) + 2*(j-1)]   = dbhex[0]
                statuslist[(int(columnlist[i])-1)*(inputport*2) + 2*(j-1)+1] = dbhex[1]
                
        statuslist.append("*\r\n")              
        sendcmd += "".join(statuslist)
           
        clientsocket.sendall(sendcmd)
        recvcmd = clientsocket.recv(4096)
        
        clientsocket.sendall("$TA,F*\r\n")  #马上发送查询指令
        recvcmd = clientsocket.recv(4096)
        clientsocket.close()
        
        if recvcmd =="FF\r\n":
            return -1
        
        statuslist = []
        for i in range(outputport):          #控制总循环次数
            for j in recvcmd[(9+inputport*2)*i+6 : (9+inputport*2)*i+((6+inputport*2))]:   
                statuslist.append(j)
                
        recvcmd = "".join(statuslist)
            
        for i in range(len(columnlist)):
            for j in range(inputport):
                startindex = (int(columnlist[i])-1)*(inputport*2) + 2*j #间隔inputport*2个距离取值
                if(dbhex==recvcmd[startindex : startindex+2]) or (recvcmd[startindex : startindex+2]=='FE'):
                    pass
                else:
                    return -1
        return 0
    except Exception,e:
        if clientsocket != None:
            clientsocket.close()
        print "Connect to %s failed, error is %s" % (ip, e)

def ReBoot(ip):
    clientsocket = None
      
    try:
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        clientsocket.settimeout(500)
        clientsocket.connect((ip, 5000))

        clientsocket.sendall("$TA,R*\r\n")
        clientsocket.close()
        
        time.sleep(1)
        
    except Exception,e:
        if clientsocket != None:
            clientsocket.close()
        print "Connect to %s failed, error is %s" % (ip, e)
             
	
#End of hbte_pam.py 
