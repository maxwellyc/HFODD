# Make sure tableLog.dat is in the "inputs" directory
# Make sure first row of tableLog.dat is the file header, such as "ra225_une0_blocking_",
# basically the string before the file #
# Make sure this file, extract_output.py, is in the "outputs" directory
# This code relies on the output file of hfodd being in a specific ordering
# because the same variables are used repeatedly,
# it's important that, for eg. the Q20 following the statement
# "MULTIPOLE MOMENTS [UNITS:  (10 FERMI)^LAMBDA]                    NEUTRONS"
# means Q20 for neutrons, so we need this line to occur right before saving this Q20
# value to the corresponding location in python lists. Same goes for other quantities.

import os
import time
from operator import itemgetter

def is_num(s):
 try:
  float(s)
  return True
 except ValueError:
  return False

def main(logFile):
 f1 = open(logFile)
 l1 = f1.readlines()
 fileH = ""     # read file header from tableLog.dat
 # last iteration, binding energy, number of lists in outputLs
 iter = 0; bindE = 0.0; outLen = 0
 #Q20_n = 0.0; Q20_p = 0.0; Q20_t = 0.0        # Neutron/ Proton/ Total Q20
 #Q30_n = 0.0; Q30_p = 0.0; Q30_t = 0.0        # Neutron/ Proton/ Total Q30
 SchiffDict = {}  # Key is file #, stores Schiff Moment neutron Q10, followed by proton, total
 Q2Dict = {}    # Key is file #, list ordering: Neutron Q20,Q21,Q22 followed by proton, total
 Q3Dict = {}    # Key is file #, list ordering: Neutron Q30,Q31,Q32 Q33 followed by proton, total
 a1 = ""; a2 = ""; a3 = ""; a4 = "";  # temporary string holder
 overLs = []    # Reached time limit (or currently running) file #
 convLs = []    # Converged calculation file #
 chaoLs = []    # Chaotic divergence file #
 quabLs = []    # Error QUABCS file #
 zheeLs = []    # Error ZHEEVR file #
 pingLs = []    # ping-pong divergence file #
 lostLs = []    # unrecored file #, not in the above categories, check manually
 memoLs = []    # memory failure 
# Lists of lists containing prerun info from tableLog.dat and combine calculated result
 # from all outputs, the default ordering of sublist is:
 # [File #, initial Q20 constraint, initial Q30 constraint,
 # converged binding energy, total Schiff/Q20/Q30, neutron Schiff/Q20/Q30,
 # proton Schiff/Q20/Q30
 outputLs = []
 # Dictionary records each row of tableLog.dat, (file #, Q20, Q30)
 tbLog = {}
 # l1 is from tableLog.dat, this line records file header for this set, defined in create_hfodd_input.py
 for line in l1:
  fileH = line.strip('\n')
  break
 for line in l1:
  ss = line.split()
  try:
   if ( is_num(ss[0]) ):
    tbLog[ss[0]] = (ss[1],ss[2])
    endNum = int(ss[0])+1
  except (ValueError, IndexError):
   continue
 saveSum = open( "./Summary_" + fileH  + ".out" , "w")
 f1.close()
 lsLoc = os.listdir("./")
 # switch for recording calculated deformation, schiff moment etc.
 # value is 0: inactive, 1:Q2_N, Q3_N, 2:Schiff_N, 3: Q2_P, Q3_P, 4: Schiff_P
 # 5:Q2_total, Q3_total, 6: Schiff_total
 recordS = 0
 # this loop iterates through all possible file #
 for i in xrange(0,endNum):
  recordS = 0
  fileOut = fileH + str(i) +".out"
  # check if current file is in the directory
  if fileOut in lsLoc:
      f0 = open(fileOut)
      l0 = f0.readlines()
      switch = -1
      for line in l0:
       if "CONVERGENCE REPORT" in line:
        switch = 1
       if (switch == 1):
        # ############# switch == 0 is for converged results #############
        if "NEUTRONS" in line:
         switch = 0
         #break
        elif "CHAOTIC  DIVERGENCE DETECTED" in line:
         switch = 2
         break
        elif "EXCEEDED IN QUABCS" in line:
         switch = 3
         break
        elif "ERROR IN ZHEEVR" in line:
         switch = 4
         break
        elif "PING-PONG CONDITION DETECTED" in line:
         switch = 5
         break
       if "ALLOCATION OF MEMORY" in line:
        switch = 6
        break
       if ( switch == 1 ) :
        ss = line.split()
        try:
         if ( is_num(ss[1]) ):
          iter = int(ss[1])
          bindE = float(ss[2])
        except (ValueError, IndexError):
         continue
       # convergence reached, now sift through file to find location of deformation etc.
       if ( switch == 0 ) :
        ####################################################################################
        # Reading calculated results related to ###### NEUTRONS ######
        ####################################################################################
        if ("MULTIPOLE MOMENTS" in line) and ("NEUTRONS" in line):
         recordS = 1
        if ( recordS == 1 ):
         if "Q20" in line:
          a1 = line[8:17]       #Q20
          a2 = line[23:32]      #Q21
          a3 = line[38:47]      #Q22
          if "ZERO" in a1:
           a1 = "0.0"
          if "ZERO" in a2:
           a2 = "0.0"
          if "ZERO" in a3:
           a3 = "0.0"
          Q2Dict[str(i)] = [ a1,a2,a3 ]
         if "Q30" in line:
          a1 = line[8:17]       #Q30
          a2 = line[23:32]      #Q31
          a3 = line[38:47]      #Q32
          a4 = line[53:62]      #Q33
          if "ZERO" in a1:
           a1 = "0.0"
          if "ZERO" in a2:
           a2 = "0.0"
          if "ZERO" in a3:
           a3 = "0.0"
          if "ZERO" in a4:
           a4 = "0.0"
          Q3Dict[str(i)] = [ a1,a2,a3,a4 ]
         if ("SCHIFF" in line) and ("NEUTRONS" in line):
          recordS = 2
        if ( recordS == 2 ) and ("Q10" in line):
         a1 = line[8:17]       #Schiff Q10
         if "ZERO" in a1:
           a1 = "0.0"
         SchiffDict[str(i)] = [ a1 ]
         recordS = 0
        ####################################################################################
        # Reading calculated results related to ###### PROTONS ######
        ####################################################################################
        if ("MULTIPOLE MOMENTS" in line) and ("PROTONS" in line):
         recordS = 3
        if ( recordS == 3 ):
         if "Q20" in line:
          a1 = line[8:17]       #Q20
          a2 = line[23:32]      #Q21
          a3 = line[38:47]      #Q22
          if "ZERO" in a1:
           a1 = "0.0"
          if "ZERO" in a2:
           a2 = "0.0"
          if "ZERO" in a3:
           a3 = "0.0"
          Q2Dict[str(i)] = Q2Dict[str(i)] + [ a1,a2,a3 ]
         if "Q30" in line:
          a1 = line[8:17]       #Q30
          a2 = line[23:32]      #Q31
          a3 = line[38:47]      #Q32
          a4 = line[53:62]      #Q33
          if "ZERO" in a1:
           a1 = "0.0"
          if "ZERO" in a2:
           a2 = "0.0"
          if "ZERO" in a3:
           a3 = "0.0"
          if "ZERO" in a4:
           a4 = "0.0"
          Q3Dict[str(i)] = Q3Dict[str(i)] + [ a1,a2,a3,a4 ]
         if ("SCHIFF" in line) and ("PROTONS" in line):
          recordS = 4
        if ( recordS == 4 ) and ("Q10" in line):
         a1 = line[8:17]       #Schiff Q10
         if "ZERO" in a1:
           a1 = "0.0"
         SchiffDict[str(i)] = SchiffDict[str(i)] + [ a1 ]
         recordS = 0
        ####################################################################################
        # Reading calculated results related to ###### TOTAL ######
        ####################################################################################
        if ("MULTIPOLE MOMENTS" in line) and ("TOTAL" in line):
         recordS = 5
        if ( recordS == 5 ):
         if "Q20" in line:
          a1 = line[8:17]       #Q20
          a2 = line[23:32]      #Q21
          a3 = line[38:47]      #Q22
          if "ZERO" in a1:
           a1 = "0.0"
          if "ZERO" in a2:
           a2 = "0.0"
          if "ZERO" in a3:
           a3 = "0.0"
          Q2Dict[str(i)] = Q2Dict[str(i)] + [ a1,a2,a3 ]
         if "Q30" in line:
          a1 = line[8:17]       #Q30
          a2 = line[23:32]      #Q31
          a3 = line[38:47]      #Q32
          a4 = line[53:62]      #Q33
          if "ZERO" in a1:
           a1 = "0.0"
          if "ZERO" in a2:
           a2 = "0.0"
          if "ZERO" in a3:
           a3 = "0.0"
          if "ZERO" in a4:
           a4 = "0.0"
          Q3Dict[str(i)] = Q3Dict[str(i)] + [ a1,a2,a3,a4 ]
         if ("SCHIFF" in line) and ("TOTAL" in line):
          recordS = 6
        if ( recordS == 6 ) and ("Q10" in line):
         a1 = line[8:17]       #Schiff Q10
         if "ZERO" in a1:
           a1 = "0.0"
         SchiffDict[str(i)] = SchiffDict[str(i)] + [ a1 ]
         break
      #  ############# switch == 0 is for converged results #############
      if switch == 0:
       convLs.append(i)
       # [File #, initial Q20 constraint, initial Q30 constraint,
       # converged binding energy, total Schiff/Q20/Q30, neutron Schiff/Q20/Q30,
       # proton Schiff/Q20/Q30
       outputLs.append( [i, tbLog[str(i)][0], tbLog[str(i)][1], bindE, SchiffDict[str(i)][2], \
        Q2Dict[str(i)][6], Q3Dict[str(i)][8], SchiffDict[str(i)][0], Q2Dict[str(i)][0],\
        Q3Dict[str(i)][0], SchiffDict[str(i)][1],  Q2Dict[str(i)][3],  Q3Dict[str(i)][4] ] )     
      elif switch == 1:
       overLs.append(i)
       #print "File " +str(i)+ " Calculation incomplete, walltime exceeded \t##### FAILED TO CONVERGE"
      elif switch == 2:
       chaoLs.append(i)
       #print "Chaotic Divergence\t\t\t\t##### FAILED TO CONVERGE"
      elif switch == 3:
       quabLs.append(i)
       #print "Max iterations in QUABCS\t\t\t##### FAILED TO CONVERGE"
      elif switch == 4:
       zheeLs.append(i)
       #print "Error in ZHEEVR\t\t\t\t\t##### FAILED TO CONVERGE"
      elif switch == 5:
       pingLs.append(i)
      elif switch == 6:
       memoLs.append(i)
 for i in xrange(0, endNum):
  if ( (i not in convLs) and (i not in overLs) and (i not in chaoLs) and (i not in quabLs) and (i not in zheeLs) and (i not in pingLs) and (i not in memoLs)):
     lostLs.append(i)

 saveSum.write(fileH+"\n")
 saveSum.write("Units:\n")
 saveSum.write("Energy: MeV, Schiff Moment: 100 fm^3, Q2j: (10fm)^2, Q3j: (10fm)^3\n")
 # [File #, initial Q20 constraint, initial Q30 constraint,
 # converged binding energy, total Schiff/Q20/Q30, neutron Schiff/Q20/Q30,
 # proton Schiff/Q20/Q30
 gap = 15
 saveSum.write( \
 "File#".ljust(gap) + "Q20_initial".ljust(gap) + "Q30_initial".ljust(gap) + "HFB_Energy".ljust(gap)\
  + "Schiff_tot".ljust(gap) + "Q20_tot".ljust(gap) + "Q30_tot".ljust(gap) \
  + "Schiff_N".ljust(gap) + "Q20_N".ljust(gap) + "Q30_N".ljust(gap) \
  + "Schiff_P".ljust(gap) + "Q20_P".ljust(gap) + "Q30_P".ljust(gap)  )
 outputLs.sort( key=lambda x:x[3])      #x[6] for Q30 ascending, x[3] for binding energy ascending
 outLen = len(outputLs)
 outStr = ""
 for i in xrange(0, outLen):
  outStr = "\n"
  for j in xrange(0,13):
   outStr = outStr + str(outputLs[i][j]).ljust(gap)
  saveSum.write(outStr)
 print "##########################################################################"
 print "Incomplete due to time limit (or currently running): " + str(len(overLs)) + "/" + str(endNum)
 print overLs
 saveSum.write("\n##########################################################################\n"+\
 "Incomplete due to time limit (or currently running): " + str(len(overLs)) + "/" + str(endNum) + "\n")
 saveSum.write(",".join(str(e) for e in overLs))
 print "##########################################################################"
 print "Incomplete due to maximum iteration reached in QUABCS: " + str(len(quabLs)) + "/" + str(endNum)
 print quabLs
 saveSum.write("\n##########################################################################\n"+\
 "Incomplete due to maximum iteration reached in QUABCS: "  + str(len(quabLs)) + "/" + str(endNum) + "\n")
 saveSum.write(",".join(str(e) for e in quabLs))
 print "##########################################################################"
 print "Incomplete due to chaotic divergence: " + str(len(chaoLs)) + "/" + str(endNum)
 print chaoLs
 saveSum.write("\n##########################################################################\n"+\
 "Incomplete due to chaotic divergence: " + str(len(chaoLs)) + "/" + str(endNum) + "\n")
 saveSum.write(",".join(str(e) for e in chaoLs))
 print "##########################################################################"
 print "Incomplete due to error in ZHEEVR: " + str(len(zheeLs)) + "/" + str(endNum)
 print zheeLs
 saveSum.write("\n##########################################################################\n"+\
 "Incomplete due to error in ZHEEVR: " + str(len(zheeLs)) + "/" + str(endNum) + "\n")
 saveSum.write(",".join(str(e) for e in zheeLs))
 print "##########################################################################"
 print "Incomplete due to ping-pong condition: " + str(len(pingLs)) + "/" + str(endNum)
 print pingLs
 saveSum.write("\n##########################################################################\n"+\
 "Incomplete due to ping-pong condition: " + str(len(pingLs)) + "/" + str(endNum) + "\n")
 saveSum.write(",".join(str(e) for e in pingLs))
 print "##########################################################################"
 print "Incomplete due to memory failure: " + str(len(memoLs)) + "/" + str(endNum)
 print memoLs
 saveSum.write("\n##########################################################################\n"+\
 "Incomplete due to memory failure: " + str(len(memoLs)) + "/" + str(endNum) + "\n")
 saveSum.write(",".join(str(e) for e in memoLs))
 print "##########################################################################"
 print "Files unaccounted for, please check manually: " + str(len(lostLs)) + "/" + str(endNum)
 print lostLs
 saveSum.write("\n##########################################################################\n"+\
 "Files unaccounted for, please check manually: " + str(len(lostLs)) + "/" + str(endNum) + "\n")
 saveSum.write(",".join(str(e) for e in lostLs))
 print "##########################################################################"
 print "Converged calculations: " + str(len(convLs)) + "/" + str(endNum)
 print convLs
 saveSum.write("\n##########################################################################\n"+\
 "Converged calculations: " + str(len(convLs)) + "/" + str(endNum) + "\n")
 saveSum.write(",".join(str(e) for e in convLs))


 saveSum.close()
 f0.close()


main("../inputs/tableLog.dat")



