#!/usr/bin/python2.7

import epics
import commands

movlist = ['manphi','mantet','manz','many','manx',			
		'int','detlin','mirrot','mirtilt','thzpol','att',		
		'msc_motor']
		
mov_namelist = ['manphi','mantet','manz','many','manx',			
		'int','detlin','mirrot','mirtilt','thzpol','fstb att',		
		'msc_motor'] 

buncherlist = ['thz:buncher:m1:pos', 'thz:buncher:m2:pos', 'thz:buncher:m3:pos', 'thz:buncher:m4:pos']

maglist = ['SOL_I_SET_r','QF1_I_MON','QD1_I_MON','QF2_I_MON','QD2_I_MON','QF3_I_SET_r','QD3_I_SET_r','QF4_I_MON','QD4_I_MON','QF5_I_MON',
		'QD5_I_MON','BH1_I_MON','BH2_I_MON','BA1_I_MON','ZH1_I_MON','ZV1_I_MON','ZH2_I_MON','ZV2_I_MON','ZH3_I_MON','ZV3_I_MON']

phaselist = ['GLSR_MON','KLY0_MON','KLY1_MON','ACC_MON']		

rfinlist = ['KLY0:RFIN_MON','KLY1:RFIN_MON']
		
uvmirlist = ['X_MON','Y_MON']

def LUCXsnapshot():
	global snapshot
	snapshot = ""
	for var in range(len(movlist)):
		line = str(commands.getoutput("caget -t "+"thz:"+movlist[var]+":pos"))
		snapshot += (mov_namelist[var]+': '+"\t"+line+"\n")
	
	snapshot += ('UV_attenuator: '+"\t"+str(commands.getoutput("caget -t "+'GLSR:POWER:UV:TOGUN_ANG_MON'))+"\n"+"\n") 
	
	snapshot += (('\t'.join(map(str,buncherlist)))+"\n")		
	for var in range(len(buncherlist)):
		line = str(commands.getoutput("caget -t "+buncherlist[var]))
		snapshot += (line+"\t")	
	
	snapshot += ("\n"+"\n")
	
	snapshot += (('\t'.join(map(str,maglist)))+"\n")
	for var in range(len(maglist)):
		line = str(commands.getoutput("caget -t "+"MAGNET:MON:"+maglist[var]))
		snapshot += (line+"\t")

	snapshot += ("\n"+"\n")

	snapshot += (('\t'.join(map(str,phaselist)))+"\n")
	for var in range(len(phaselist)):
		line = str(commands.getoutput("caget -t "+"LLRF:PHASE:"+phaselist[var]))
		snapshot += (line+"\t")

	snapshot += ("\n"+"\n")

	snapshot += (('\t'.join(map(str,rfinlist)))+"\n")		
	for var in range(len(rfinlist)):
		line = str(commands.getoutput("caget -t "+"LLRF:"+rfinlist[var]))
		snapshot += (line+"\t")

	snapshot += ("\n"+"\n")

	snapshot += (('\t'.join(map(str,uvmirlist)))+"\n")		
	for var in range(len(uvmirlist)):
		line = str(commands.getoutput("caget -t "+"GLSR:MIRROR:UV:"+uvmirlist[var]))
		snapshot += (line+"\t")		
	return snapshot
	
	

