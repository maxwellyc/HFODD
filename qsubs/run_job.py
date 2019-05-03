import os
import time

def main(logFile):
 f1 = open(str(logFile))
 l1 = f1.readlines()
 fileH = ""
 for line in l1:
  fileH = line.strip('\n')
  break
 switch = 0
 for line in l1:
  ss = line.split()
  try:
   endNum = int(ss[0])
  except (ValueError, IndexError):
   continue

 # Auto qsub with optional time delay to avoid system failure
 lsLoc = ""
 lsLoc = os.listdir("./")
 for i in xrange(0,endNum+1):
  fileName = fileH + str(i) + ".qsub"
  #os.system ("date")
  if fileName in lsLoc:
   print("qsub "+ fileH + str(i) + ".qsub")
   os.system ("qsub "+ fileName)
   #time.sleep(3) #delay for 3 seconds
 f1.close()
main("../inputs/tableLog.dat")



