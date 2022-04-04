import socket
import threading
import string
from queue import Queue
import sys
PORT = int(sys.argv[1])

HOST = "172.26.93.96" # put your IP address here if playing on multiple computers
BACKLOG = 2
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind((HOST,PORT))
server.listen(BACKLOG)
print("looking for connection")
def handleClient(client, serverChannel, cID, clientele):
  client.setblocking(1)
  msg = ""
  while True:
      try:
        msg += client.recv(30).decode("UTF-8")
        command = msg.split("\t")
        while (len(command) > 1):
          readyMsg = command[0]
          msg = "\t".join(command[1:])
          serverChannel.put(str(cID) + "\t" + readyMsg + '\t' + msg)
          command = msg.split("\t")
      except:
        # we failed
        return
def serverThread(clientele, serverChannel):
  global names
  while True:
      msg = serverChannel.get(True, None)
      print("msg recv")
      print(msg)
      msgSplit = msg.split('\t')
      senderID = msgSplit[0]
      msgNew = msgSplit[1] + '\t' + senderID + '\t' + msgSplit[2] + '\n'
      if msgSplit[1] == 'dname':
        names[senderID] = msgSplit[2]
      if (msg != ""):
        for cID in clientele:
          if cID != senderID:
            clientele[cID].send(msgNew.encode())
            print("> sent to %s:" % cID)
      print()
      serverChannel.task_done()
clientele = dict()
userNum = 1
u = 'user'
serverChannel = Queue(100)
threading.Thread(target = serverThread, args = (clientele, serverChannel)).start()
names = {"user1":'user1', "user2":'user2', "user3":'user3', "user4":'user4', "user5":'user5'}

def getUsers():
  global names
  res = '\t'
  for name in names:
    if names[name] != name:
      res += name + '\t' + names[name] + '\t'
  return res[:-1]

while True:
  client, address = server.accept()
  # myID is the key to the client in the clientele dictionary
  myID = names['user' + str(userNum)]
  print(myID, userNum)
  for cID in clientele:
      print (repr(cID), repr(userNum))
      clientele[cID].send(("newUser\t%s\n" % myID).encode())
      client.send(("newUser\t%s\n" % cID).encode())
  clientele[myID] = client
  client.send(("myIDis\t%s%s\n" % (myID, getUsers())).encode())
  print("connection recieved from %s" % myID)
  threading.Thread(target = handleClient, args = 
                        (client ,serverChannel, myID, clientele)).start()
  userNum += 1