# -*- coding: utf-8 -*-
from vimenv import env
import os
import re
import io 
import saveable

RESULT_FORMAT="%s|%s|%s"
RESULT_FORMAT_FILE="%s|f|%s"
FILE_ENCODE_LIST=("gbk","utf-8","cp1252",None)
FILE_PATH_CNCODE="gbk"

class CCacheSearch(saveable.CSave):
	"""
	struct
	{
		py:{
			root:(
				[dir1,dir2]
				{
					f1:{
						"t":iMT,
						"l":{
								1:line1
								2:line2
							}
					}
					f2:...
				}
				)
		}
		txt:...
	}
	"""
	m_Observe=1
	def __init__(self,sFile):
		saveable.CSave.__init__(self,sFile)
		self.m_Data={}
		self.m_ProPaths=env.var("g:g_ProPaths")
		self.m_ProExts=env.var("g:g_ProExts")
		self.m_IgnoreSearch=set(env.var("g:g_IgnoreSearch"))
		self.m_DefaultExt=[".py"]
		self.m_LastRoot="*"
		self.ReadData()
		self.m_NeedUpdateFile=set()
		self.m_AllObserveDir=set()
		self.m_HasObserveDir=set()
		for sPro,lstDir in self.m_ProPaths.iteritems():
			for sDir in lstDir:
				self.m_AllObserveDir.add(sDir)
	
	def Load(self,dData):
		if self.m_Observe:
			return
		if not dData:
			return
		self.m_Data=dData

	def Save(self):
		if self.m_Observe:
			return {}
		return self.m_Data

	def GetAllRoot(self):
		dResult={}
		lstRet=[]
		for sExt,dRoot in self.m_Data.iteritems():
			rootset=set()
			dResult[sExt]=rootset
			for sRoot in dRoot:
				iFind=0
				for sTmp in rootset.copy():
					if sRoot in sTmp:
						iFind=1
						rootset.remove(sTmp)
					elif sTmp in sRoot:
						iFind=2
				if iFind!=2:
					rootset.add(sRoot)

		for sExt,rootset in dResult.iteritems():
			for sRoot in rootset:
				lstRet.append([sExt,sRoot])
		return lstRet

	def DelRoot(self,sExt,sRoot):
		dRoot=self.m_Data[sExt]
		lstDir,_=dRoot[sRoot]
		del dRoot[sRoot]
		for sDir in lstDir:
			sSubRoot="%s\\%s"%(sRoot,sDir)
			self.DelRoot(sExt,sSubRoot)

	def UpdateRoot(self,sRoot,sExt):
		if self.m_Observe:
			iReturn=1
			for sTmp in sExt:
				if sRoot not in self.m_Data.get(sTmp,{}):
					iReturn=0
			if iReturn:
				return
		setExt=set(sExt)
		dNewRoot={}
		for sExt in setExt:
			if not sExt in self.m_Data:
				self.m_Data[sExt]={}
			dNewRoot[sExt]={}

		for sTmpR,lstDir,lstFile in os.walk(sRoot):
			if sTmpR.split("\\")[-1] in self.m_IgnoreSearch:
				continue
			lstDir=list(set(lstDir)-self.m_IgnoreSearch)
			dNewFile={}
			dOldFile={}
			for sExt in setExt:
				dOldFile[sExt]=self.m_Data[sExt].get(sTmpR,([],{}))[1]
				dNewFile[sExt]={}
			for sFile in lstFile:
				sPath="%s\\%s"%(sTmpR,sFile)
				_,sExt=os.path.splitext(sPath)
				if not sExt in setExt:
					continue
				dOldF=dOldFile[sExt].get(sFile,{})
				iMTime=os.path.getmtime(sPath)
				if iMTime==dOldF.get("t"):
					dNewFile[sExt][sFile]=dOldF
					continue
				dNewL={}
				dNewF={"t":iMTime,"l":dNewL}
				self.ReadLines(sPath,dNewL)
				dNewFile[sExt][sFile]=dNewF
			for sExt in setExt:
				dNewRoot[sExt][sTmpR]=(lstDir,dNewFile[sExt])

		for sExt in setExt:
			dOld=self.m_Data[sExt]
			dNew=dNewRoot[sExt]
			for sOldRoot in dOld.keys():
				if sRoot in sOldRoot and not sOldRoot in dNew:
					del dOld[sOldRoot]
			for sNewRoot,dData in dNew.iteritems():
				dOld[sNewRoot]=dData

	def ReadLines(self,sFile,dLine):
		for sEncode in FILE_ENCODE_LIST:
			try:
				iLine=0
				oFile=io.open(sFile,encoding=sEncode)
				for sLine in oFile:
					iLine+=1
					dLine[iLine]=sLine.encode("utf-8")
				return
			except:
				oFile.close()
		raise Exception("ReadLines decode fail: %s"%sFile)

	def UpdatedFile(self):
		for sPath in self.m_NeedUpdateFile:
			sPath=sPath.encode(FILE_PATH_CNCODE)
			if os.path.isfile(sPath):
				iDel=0
			else:
				iDel=1
			sExt=os.path.splitext(sPath)[-1]
			if not sExt in self.m_Data:
				continue
			sDir=os.path.dirname(sPath)
			sFile=os.path.basename(sPath)
			if not sDir in self.m_Data[sExt]:
				self.m_Data[sExt][sDir]=([],{})
			if not sFile in self.m_Data[sExt][sDir][1]:
				self.m_Data[sExt][sDir][1][sFile]={}
			if iDel:
				del self.m_Data[sExt][sDir][1][sFile]
				continue
			dOldF=self.m_Data[sExt][sDir][1][sFile]
			iMTime=os.path.getmtime(sPath)
			dNewL={}
			dNewF={"t":iMTime,"l":dNewL}
			self.ReadLines(sPath,dNewL)
			self.m_Data[sExt][sDir][1][sFile]=dNewF
		self.m_NeedUpdateFile=set()

	def ObserveCB(self,fileset):
		for sFile in fileset:
			self.m_NeedUpdateFile.add(sFile)

	def CheckObserve(self,lstRoot):
		import dirobserver
		if not self.m_Observe:
			return
		observeset=(set(lstRoot)&self.m_AllObserveDir)-self.m_HasObserveDir
		if not observeset:
			return
		for sDir in observeset:
			dirobserver.ObserveDir(sDir,self.ObserveCB)
			self.m_HasObserveDir.add(sDir)
		print "start observe",observeset

	def Search(self,sText,sMode="n",sAllExt="",sRoot="",sFilter=""):
		self.UpdatedFile()
		if "f" in sMode and ";" in sText:
				if not "r" in sMode:
					sMode="%sr"%(sMode)
				sText=sText.replace(";",".*\\\\")

		if not sRoot:
			sRoot=env.curdir
			for sPro in sorted(self.m_ProPaths.keys(),reverse=True):
				if sPro in sRoot:
					sRoot=sPro
					break
			#eg gamepublic
			if not sRoot in self.m_ProPaths:
				for sPath in self.m_ProPaths.get(self.m_LastRoot,[]):
					if sPath in sRoot:
						sRoot=self.m_LastRoot
						break
			if int(env.var("InSysBuf()")):
				sRoot=self.m_LastRoot
		self.m_LastRoot=sRoot

		if not sAllExt:
			if sPro in self.m_ProExts:
				lstExt=self.m_ProExts[sPro]
			else:
				lstExt=self.m_DefaultExt
		else:
			lstExt=[]
			for sExt in sAllExt.split(","):
				if not sExt:
					continue
				if not "." in sExt:
					sExt=".%s"%sExt
				lstExt.append(sExt)

		lstRoot=[sRoot]
		if sRoot in self.m_ProPaths:
			lstRoot=self.m_ProPaths[sRoot]
		print sRoot,sText,sMode,lstExt,lstRoot,sFilter

		if "r" in sMode:
			oPat=re.compile(sText)
		else:
			oPat=sText

		dFunc={
			"n" :self.SearchRoot,
			"r" :self.SearchRRoot,
			"f" :self.SearchFile,
			"fr":self.SearchRFile,
			"o":self.SearchOne,
			"or":self.SearchROne,
		}
		oFunc=dFunc[sMode]
		lstRet=[]
		for sRoot in lstRoot:
			self.UpdateRoot(sRoot,lstExt)
			for sExt in lstExt:
				dData=self.m_Data[sExt]
				oFunc(dData,sRoot,oPat,lstRet)
		lstRet=self.Filter(lstRet,sFilter)
		env.effqf("".join(lstRet))
		self.CheckObserve(lstRoot)

	def Filter(self,lstRet,sFilter):
		if not sFilter:
			return lstRet
		oPat=re.compile(sFilter)
		lstNew=[]
		for sLine in lstRet:
			sReal=sLine.split("|")[-1]
			if oPat.search(sReal):
				lstNew.append(sLine)
		return lstNew

	def SearchRoot(self,dData,sRoot,oPat,lstRet):
		lstDir,dRoot=dData[sRoot]
		for sFile,dFile in dRoot.iteritems():
			for iLine,sLine in dFile["l"].iteritems():
				if oPat in sLine:
					lstRet.append(RESULT_FORMAT%(sRoot+"\\"+sFile,iLine,sLine))
		for sDir in lstDir:
			sDeepR="%s\\%s"%(sRoot,sDir)
			self.SearchRoot(dData,sDeepR,oPat,lstRet)

	def SearchRRoot(self,dData,sRoot,oPat,lstRet):
		lstDir,dRoot=dData[sRoot]
		for sFile,dFile in dRoot.iteritems():
			for iLine,sLine in dFile["l"].iteritems():
				if oPat.search(sLine):
					lstRet.append(RESULT_FORMAT%(sRoot+"\\"+sFile,iLine,sLine))
		for sDir in lstDir:
			sDeepR="%s\\%s"%(sRoot,sDir)
			self.SearchRRoot(dData,sDeepR,oPat,lstRet)

	def SearchOne(self,dData,sRoot,oPat,lstRet):
		sFile=env.var('expand("%:t")')
		lstDir,dRoot=dData[sRoot]
		for iLine,sLine in dRoot[sFile]["l"].iteritems():
			if oPat in sLine:
				lstRet.append(RESULT_FORMAT%(sRoot+"\\"+sFile,iLine,sLine))

	def SearchROne(self,dData,sRoot,oPat,lstRet):
		sFile=env.var('expand("%:t")')
		lstDir,dRoot=dData[sRoot]
		for iLine,sLine in dRoot[sFile]["l"].iteritems():
			if oPat.search(sLine):
				lstRet.append(RESULT_FORMAT%(sRoot+"\\"+sFile,iLine,sLine))

	def SearchFile(self,dData,sRoot,oPat,lstRet):
		lstDir,dRoot=dData[sRoot]
		for sFile,dFile in dRoot.iteritems():
			sPath="%s\\%s"%(sRoot,sFile)
			#only \\ in oPat,we search fullfile
			if "\\" in oPat and oPat in sPath:
				lstRet.append(RESULT_FORMAT_FILE%(sPath,"file\n"))
			elif oPat in sFile:
				lstRet.append(RESULT_FORMAT_FILE%(sPath,"file\n"))
		for sDir in lstDir:
			sDeepR="%s\\%s"%(sRoot,sDir)
			self.SearchFile(dData,sDeepR,oPat,lstRet)

	def SearchRFile(self,dData,sRoot,oPat,lstRet):
		lstDir,dRoot=dData[sRoot]
		for sFile,dFile in dRoot.iteritems():
			sPath="%s\\%s"%(sRoot,sFile)
			if oPat.search(sPath):
				lstRet.append(RESULT_FORMAT_FILE%(sPath,"file\n"))
		for sDir in lstDir:
			sDeepR="%s\\%s"%(sRoot,sDir)
			self.SearchRFile(dData,sDeepR,oPat,lstRet)

