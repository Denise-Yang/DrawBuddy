import socket
import threading
import string
from queue import Queue

HOST = "" # put your IP address here if playing on multiple computers
PORT = 48714
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
        msg += client.recv(10).decode("UTF-8")
        command = msg.split("\n")
        while (len(command) > 1):
          print(command)
          readyMsg = command[0]
          msg = "\n".join(command[1:])
          serverChannel.put(str(cID) + "\t" + readyMsg)
          command = msg.split("\n")
      except:
        # we failed
        return

def serverThread(clientele, serverChannel):
  while True:
      msg = serverChannel.get(True, None)
      print("msg recv")
      print(msg)
      msgNew = msg.split('\t')
      senderID = msgNew[0]
      msgNew = "send\t" + msgNew[1] + '\t' + msgNew[3] + '\t' + msgNew[2] + '\n'
      if (msg != ""):
        for cID in clientele:
          if cID != senderID:
            clientele[cID].send(msgNew.encode())
            print("> sent to %s:" % cID)
      print()
      serverChannel.task_done()

clientele = dict()
userNum = 0

serverChannel = Queue(100)
threading.Thread(target = serverThread, args = (clientele, serverChannel)).start()

names = ["user1", "user2", "user3", "user4", "user5"]

while True:
  client, address = server.accept()
  # myID is the key to the client in the clientele dictionary
  myID = names[userNum]
  print(myID, userNum)
  for cID in clientele:
      print (repr(cID), repr(userNum))
      clientele[cID].send(("newUser\t%s\n" % myID).encode())
      client.send(("newUser\t%s\n" % cID).encode())
  clientele[myID] = client
  client.send(("myIDis\t%s\n" % myID).encode())
  print("connection recieved from %s" % myID)
  threading.Thread(target = handleClient, args = 
                        (client ,serverChannel, myID, clientele)).start()
  userNum += 1
