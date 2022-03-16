import socket
import threading
import base64
import os
from queue import Queue
import time


HOST = "" # put your IP address here if playing on multiple computers
PORT = 48714

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.connect((HOST,PORT))
print("connected to server")

global myID
global userList

def handleServerMsg(server, serverMsg):
  server.setblocking(1)
  msg = ""
  command = ""
  while True:
    msg += server.recv(10).decode("UTF-8")
    command = msg.split("\n")
    while (len(command) > 1):
      readyMsg = command[0]
      msg = "\n".join(command[1:])
      serverMsg.put(readyMsg)
      command = msg.split("\n")

def mainloop():
    while(True):
        while (serverMsg.qsize() > 0):
            msg = serverMsg.get(False)
            #print("received: ", msg, "\n")
            msg = msg.split("\t")
            command = msg[0]
            try:
                if(command == "myIDis"):
                    myID = msg[1]
                elif(command == "newUser"):
                    userList.append(msg[1])
                elif(command == "send"):
                    recTime = time.time()
                    timeDif = recTime - float(msg[1])
                    print(timeDif)
                    (open(os.getcwd() + '/' + msg[3], "w")).write(base64.b64decode(msg[2]).decode())
            except:
                print("failed")
            serverMsg.task_done()
        while(len(userList) != 0):
            inp = input("Do you wish to send or receive an image?: (s/r) ")
            if (inp == 's'):
                imageName = input("what would you like their image to be named?: ")
                x = (open(input("what image would you like to send?: "), 'r')).read()
                curTime = time.time()
                senMes = str(curTime) + '\t' + imageName + '\t' + base64.b64encode(x.encode()).decode() + '\n'
                server.send(senMes.encode())
                break
            else:
                break

serverMsg = Queue(100)
threading.Thread(target = handleServerMsg, args = (server, serverMsg)).start()

myID = ""
userList = []
mainloop()

