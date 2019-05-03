# Code reads in sample input and modifies Q20 and Q30 constraint, saved file names, input file name
# Basic configuration needs to be set up first.
# Creates corresponding job.qsub file (tentative)
# Create tableLog.dat file to keep track file name vs deformation
import os

def CreateInput(sample_input, sample_qsub):
 os.system("shopt -s extglob\n"+"cd qsubs \n rm !(job*|*py)\n")
 os.system("shopt -s extglob\n"+"cd reviews \n rm *\n") 
 os.system("shopt -s extglob\n"+"cd outputs \n rm !(*.py)\n")
 os.system("shopt -s extglob\n"+"cd inputs \n rm !(hfodd*)\n")
 fileH = "ra225_sly4_69-_eps1e5_"  # File name header:
 edfAbbr = "69-_" # edfAbbreviation for qsub
 # Define stiffness:
 stfn_q2 = 0.10
 stfn_q3 = 0.10
 stfn_q1 = 0.10
 # If both Q20_active & Q30_active is not 1, there's no point using this code
 Q20_start = 15.0; Q20_end = 25.0; Q20_step = 1.0; Q20_active = 1
 Q30_start = 2.5; Q30_end = 7.0; Q30_step = 0.5; Q30_active = 1
 # sample file for input and qsub, everything except multipole constraint and save file names #
 # will be kept the same in this version #
 f1 = open(str(sample_input)); f2 = open(str(sample_qsub))
 # Save logfile for file# vs constraint
 logFile = open(str("./inputs/tableLog.dat"),"w")
 # Path for executable
 exePath = "../hf273y"
 # Choose Constraint range, each configuration will result in a unique input file and a unique qsub file #
 # Constraint is only accurate to "decm" digits after decimal
 decm = 1
 Q20_len = int((Q20_end - Q20_start)/Q20_step + 0.0001)+1
 Q30_len = int((Q30_end - Q30_start)/Q30_step + 0.0001)+1
 Q20 = 0.0; Q30 = 0.0
 if (Q20_active != 1):
  Q20_len = 0
 if (Q30_active != 1):
  Q30_len = 0
 # We don't save .rec and .cou file for blocking calculations, this takes up a lot of storage (0.5GB per configuration) #
 orgStr1 = ""; orgStr2 = ""; orgStr3 = ""
 qsubStr1 = ""; qsubStr2 = ""; qsubStr3 = ""
 constStr1 = ""; constStr2 = ""
 reviewFileName = ""; outStr = ""
 switch = 0
 # Read file and copy strings before multipole constraint and after multipole constraint
 # Later we could just insert line for constraint and file name
 ##################################################################################################
 #######   CREATES STRINGS OF SECTIONS THAT DO NOT NEED TO BE ALTERED IN THE .INPUT. FILES  #######
 ##################################################################################################
 l1 = f1.readlines(); l2 = f2.readlines()
 for line in l1:
  ss = line.split()
  orgStr1 = orgStr1 + line
  try:
   if (ss[0] == "MULTCONSTR"):
    orgStr1 = orgStr1 + "               -1       0     "+str(stfn_q1)+"     0.0      1\n"
    break
  except (ValueError, IndexError):
   continue
 
 switch = 0
 for line in l1:
  ss = line.split()
  try:
   if (ss[0] == "MAX_SCHIFF"):
    switch = 1
   if (ss[0] == "REVIEWFILE"):
    orgStr2 = orgStr2 + line
    break
   if (switch == 1):
    orgStr2 = orgStr2 + line
  except (ValueError, IndexError):
   continue

 switch = 0
 for line in l1:
  ss = line.split()
  try:
   if (ss[0] == "REPLAYFILE"):
    switch = 1
   if (switch == 1):
    orgStr3 = orgStr3 + line
  except (ValueError, IndexError):
   continue
 ##################################################################################################
 #######    CREATES STRINGS OF SECTIONS THAT DO NOT NEED TO BE ALTERED IN THE .QSUB. FILE   #######
 ##################################################################################################

 for line in l2:
  ss = line.split()
  qsubStr1 = qsubStr1 + line
  try:
   if (ss[1] == "-j"):
    qsubStr1 = qsubStr1 + "#PBS -N "
    break
  except (ValueError, IndexError):
   continue
 switch = 0
 for line in l2:
  ss = line.split()
  try:
   if (ss[0] == "cd"):
    switch = 1
   if (switch == 1):
    qsubStr2 = qsubStr2 + line
   if (ss[0] == "ulimit"):
    break
  except (ValueError, IndexError):
   continue


 logFile.write(fileH + "\n")
 logFile.write("File#".ljust(10)+"Q20".ljust(10)+"Q30".ljust(10))

 ##################################################################################################
 ####### THIS SECTION CREATES .INPUT/QSUB. FILES FOR CONSTRAINED HFODD BLOCKING CALCULATION #######
 ##################################################################################################
 if (Q20_active == 1 and Q30_active == 1):
  count = 0
  for i in xrange(0,Q20_len):
   constStr1 = ""
   #Q20 for this file
   Q20 = round(Q20_start + i * Q20_step,decm)
   constStr1 = constStr1 + "               -2       0     "+str(stfn_q2)+"     " + str(Q20) +"      1 \n"
   for j in xrange(0,Q30_len):
    outStr = ""
    constStr2 = ""
    fileName = fileH + str(int(count))
    output = open("./inputs/"+fileName+".dat", "w")
    outQsub = open("./qsubs/"+fileName+".qsub", "w")
    reviewFileName = fileName + ".rev\n"
    #Q30 for this file
    Q30 = round(Q30_start + j * Q30_step,decm)
    constStr2 = constStr1 + "                3       0     "+str(stfn_q3)+"     " + str(Q30) +"      1 \n"
    outStr = orgStr1 + constStr2 + orgStr2 + "            ../reviews/" + reviewFileName + orgStr3
    logFile.write( "\n" + str(count).ljust(10) + str(Q20).ljust(10) + str(Q30).ljust(10) )
    output.write(outStr)
    output.close()
    qsubStr3 = qsubStr1 + "hfodd_" + edfAbbr + str(count) + "\n\n" + qsubStr2 + "date\n" + \
     exePath + " <../inputs/" + fileName + ".dat " + \
     ">../outputs/" + fileName + ".out" + "\ndate"
    outQsub.write(qsubStr3)
    outQsub.close()
    count = count + 1
 elif (Q20_active == 1 and Q30_active != 1):
  count = 0
  for i in xrange(0,Q20_len):
   outStr = ""
   constStr1 = ""
   Q30 = "n/a"
   fileName = fileH + str(int(count))
   output = open("./inputs/"+fileName+".dat", "w")
   outQsub = open("./qsubs/"+fileName+".qsub", "w")
   reviewFileName = fileName + ".rev\n"
   Q20 = round(Q20_start + i * Q20_step,decm)
   constStr1 = constStr1 + "                2       0     "+str(stfn_q2)+"     " + str(Q20) +"      1 \n"
   outStr = orgStr1 + constStr1 + orgStr2 + "            ../reviews/" + reviewFileName + orgStr3
   logFile.write( "\n" + str(count).ljust(10) + str(Q20).ljust(10) + str(Q30).ljust(10) )
   output.write(outStr)
   output.close()
   qsubStr3 = qsubStr1 + "hfodd_" + edfAbbr + str(count) + "\n\n" + qsubStr2 + "date\n" + \
     exePath + " <../inputs/" + fileName + ".dat " + \
     ">../outputs/" + fileName + ".out" + "\ndate"
   outQsub.write(qsubStr3)
   outQsub.close()
   count = count + 1
 elif (Q20_active != 1 and Q30_active == 1):
  count = 0
  for j in xrange(0,Q30_len):
   outStr = ""
   constStr1 = ""
   Q20 = "n/a"
   fileName = fileH + str(int(count))
   output = open("./inputs/"+fileName+".dat", "w")
   outQsub = open("./qsubs/"+fileName+".qsub", "w")
   reviewFileName = fileName + ".rev\n"
   Q30 = round(Q30_start + j * Q30_step,decm)
   constStr1 = constStr1 + "                3       0     "+str(stfn_q3)+"     " + str(Q30) +"      1 \n"
   outStr = orgStr1 + constStr1 + orgStr2 + "            ../reviews/" + reviewFileName + orgStr3
   logFile.write( "\n" + str(count).ljust(10) + str(Q20).ljust(10) + str(Q30).ljust(10) )
   output.write(outStr)
   output.close()
   qsubStr3 = qsubStr1 + "hfodd_" + edfAbbr + str(count) + "\n\n" + qsubStr2 + "date\n" + \
     exePath + " <../inputs/" + fileName + ".dat " + \
     ">../outputs/" + fileName + ".out" + "\ndate"
   outQsub.write(qsubStr3)
   outQsub.close()
   count = count + 1


 logFile.close()
 f1.close()

sampleInput = "./inputs/hfodd.dat"
sampleQsub = "./qsubs/job.qsub"
CreateInput(sampleInput, sampleQsub)

