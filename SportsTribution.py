#!/usr/bin/env python
#Parts
#MyFrame: gives you the main app frame. If you click on dataButtonClick you can select the data file. filterButtonclick the filter file. And so on...
#ListWindow: After selecting a data file, a second window opens that gives you a list of all the selectable attributes
#DoScatterPlot: Does the scatter plot (duh)
#isfloatTry: Checks if the user set manual maximum and minumum values
#useFilter: If a filter file is selected, this performs all the filtering steps
#inplace_change: Mac and PC have this stupid problem that they write brakes differently. This is an app intern fix.

import os
import sys
import re
import wx
import wx.lib.intctrl
import numpy as np
import matplotlib.pyplot as plt
import platform
#from mpl_toolkits.axes_grid1 import make_axes_locatable
plt.rcParams['pdf.fonttype'] = 42

class MyFrame(wx.Frame):
	def __init__(self):
		# create a frame, no parent, default to wxID_ANY
		wx.Frame.__init__(self, None, wx.ID_ANY, 'SportsTribution',
						  pos=(550, 40), size=(600, 335))
		self.num_cols=0
		
		self.dataButton = wx.Button(self, id=-1, label='Select Data File',
								 pos=(8, 2), size=(175, 20))
		self.dataButton.Bind(wx.EVT_BUTTON, self.dataButtonClick)
		self.dataInput = wx.TextCtrl(self, style=wx.TE_MULTILINE,
								 pos=(8, 38), size=(290, 40))		

		self.filterButton = wx.Button(self, id=-1, label='Select Filter File',
								 pos=(308, 2), size=(175, 20))
		self.filterButton.Bind(wx.EVT_BUTTON, self.filterButtonClick)
		self.filterInput = wx.TextCtrl(self, style=wx.TE_MULTILINE,
								 pos=(308, 38), size=(290, 40))
		self.filterText = wx.StaticText(self, pos=(308, 85), label='No filter selected')
		
		wx.StaticText(self, -1, 'X axis data, column:', pos=(8, 85))
		self.xAxisInput = wx.lib.intctrl.IntCtrl(self, pos=(145, 82), size=(22, 22),value=1)
		self.xAxisInput.Bind(wx.EVT_TEXT,self.updateXaxisLabel)
		self.xAxis36 = wx.CheckBox( self, -1, "Per 36", pos=(190, 85) )
		self.xAxisLabelName = wx.StaticText(self, -1, 'Please load Player Data', pos=(8, 102))

		wx.StaticText(self, -1, 'Y axis data, column:', pos=(8, 130))
		self.yAxisInput = wx.lib.intctrl.IntCtrl(self, pos=(145, 127), size=(22, 22),value=2)
		self.yAxisInput.Bind(wx.EVT_TEXT,self.updateYaxisLabel)
		self.yAxis36 = wx.CheckBox( self, -1, "Per 36", pos=(190, 130) )
		self.yAxisLabelName = wx.StaticText(self, -1, 'Please load Player Data', pos=(8, 147))
		
		self.button1 = wx.Button(self, id=-1, label='Visualize this!',
								 pos=(8, 170), size=(175, 28))
		self.button1.SetFont(wx.Font(14, wx.FONTFAMILY_MODERN,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD, faceName="Courier New"))
		self.button1.Bind(wx.EVT_BUTTON, self.button1Click)
		self.LogInfo = wx.StaticText(self, -1, 'You need to select at least a file containing player information', pos=(8, 200))
		
		
		wx.StaticText(self, -1, 'Data provided by:', pos=(8, 225))
		self.dataSource = wx.TextCtrl(self, -1, 'nba.com', pos=(125, 222), size=(150, 22))
		wx.StaticText(self, -1, 'Font Size:', pos=(290, 225))
		self.fontSize = wx.lib.intctrl.IntCtrl(self, pos=(357, 222), size=(22, 22),value=10)
		self.shortName = wx.CheckBox( self, -1, "Shorten player names", pos=(395, 225) )
		self.shortName.SetValue(1)
		
		wx.StaticText(self, -1, 'Highlight names:', pos=(8, 255))
		self.highlightName = wx.TextCtrl(self, -1, '', pos=(125, 252), size=(150, 22))
		
		wx.StaticText(self, -1, 'Figure Size X:', pos=(290, 255))
		self.figSizeX = wx.lib.intctrl.IntCtrl(self, pos=(380, 252), size=(22, 22),value=8)
		wx.StaticText(self, -1, 'Figure Size Y:', pos=(410, 255))
		self.figSizeY = wx.lib.intctrl.IntCtrl(self, pos=(500, 252), size=(22, 22),value=6)

		wx.StaticText(self, -1, 'x Axis Limits (Min,Max):', pos=(8, 285))
		self.xAxisMin = wx.TextCtrl(self, -1, '', pos=(170, 282), size=(22, 22))
		self.xAxisMax = wx.TextCtrl(self, -1, '', pos=(195, 282), size=(22, 22))
		wx.StaticText(self, -1, 'y Axis Limits (Min,Max):', pos=(290, 285))
		self.yAxisMin = wx.TextCtrl(self, -1, '', pos=(452, 282), size=(22, 22))
		self.yAxisMax = wx.TextCtrl(self, -1, '', pos=(477, 282), size=(22, 22))		

		
		# show the frame
		self.Show(True)
		
	def dataButtonClick(self,event):
		frozen = getattr(sys, 'frozen', None)
		if not frozen:
			file_path = os.getcwd()
		elif os.name=='posix':
			file_path = os.path.dirname(os.getcwd())
			file_path = os.path.dirname(file_path)
			file_path = os.path.dirname(file_path)
		else:
			file_path = os.path.abspath(os.path.dirname(__file__))
			file_path = os.path.dirname(file_path)
		dlg = wx.FileDialog(
			self, message="Choose file containing the data",
			defaultDir=file_path,
			defaultFile="",
			style=wx.OPEN | wx.CHANGE_DIR
			)
		
		# Show the dialog and retrieve the user response. If it is the OK response,
		# process the data.
		if dlg.ShowModal() == wx.ID_OK:
			# This returns a Python list of files that were selected.
			paths = dlg.GetPaths()
			self.dataInput.SetValue(dlg.GetPath())
			filename=self.dataInput.GetValue()
			inplace_change(filename,'\r','\n')
			
			with open(filename, 'r') as f:
				num_cols = len(f.readline().split('\t'))
				f.seek(0)
				self.playerData = np.genfromtxt(f, delimiter="\t", skip_header=0, usecols = range(1,num_cols), missing='', missing_values=None,
						   filling_values=None, names=True, case_sensitive=True )
				self.num_cols=num_cols-1
			#print playerData[playerData.dtype.names[0]]
			#print playerData.dtype.names[0]
			self.playerNames = np.genfromtxt(filename, dtype='|S50', delimiter="\t", skip_header=1, usecols = (0), missing='',
							 case_sensitive=True )
			self.LogInfo.SetLabel('Data file selected - Please select the stats you are interested in')
			self.LogInfo.SetForegroundColour((0,0,0))
			if hasattr(self, 'listWindow'):
				if isinstance(self.listWindow, wx.Frame):
					self.listWindow.Destroy()
			self.listWindow = ListWindow(self, id=-1)
			self.listWindow.Show()
			self.updateXaxisLabel(0)
			self.updateYaxisLabel(0)
			
	def filterButtonClick(self,event):
		frozen = getattr(sys, 'frozen', None)
		if not frozen:
			file_path = os.getcwd()
		elif os.name=='posix':
			file_path = os.path.dirname(os.getcwd())
			file_path = os.path.dirname(file_path)
			file_path = os.path.dirname(file_path)
		else:
			file_path = os.path.abspath(os.path.dirname(__file__))
			file_path = os.path.dirname(file_path)
			
		dlg = wx.FileDialog(
			self, message="Choose file containing filter information",
			defaultDir=file_path,
			defaultFile="",
			style=wx.OPEN | wx.CHANGE_DIR
			)
		
		# Show the dialog and retrieve the user response. If it is the OK response,
		# process the data.
		if dlg.ShowModal() == wx.ID_OK:
			# This returns a Python list of files that were selected.
			paths = dlg.GetPath()
			self.filterInput.SetValue(dlg.GetPath())
			self.filterInfo = np.loadtxt(paths, dtype={'names': ('column', 'comp', 'value'),'formats': ('i2', 'S2', 'f4')},delimiter=",")
			UseFilter(self)
			self.LogInfo.SetLabel('No Data file selected - Please select the stats you are interested in')

		    
	def button1Click(self,event):
		DoScatterPlot(self)
		
	def updateXaxisLabel(self,event):
		if hasattr(self, 'playerData'):
			xCol=self.xAxisInput.GetValue()
			if xCol>0 and xCol<=self.num_cols:
				xAxisLabel=re.sub('_',' ',self.playerData.dtype.names[xCol-1])
				self.xAxisLabelName.SetLabel(xAxisLabel)
			else:
				self.xAxisLabelName.SetLabel('Please insert a valid data column')
		else:
			self.xAxisLabelName.SetLabel('Please select valid player Data')
		
		
	def updateYaxisLabel(self,event):
		if hasattr(self, 'playerData'):
			yCol=self.yAxisInput.GetValue()
			if yCol>0 and yCol<=self.num_cols:
				yAxisLabel=re.sub('_',' ',self.playerData.dtype.names[yCol-1])
				self.yAxisLabelName.SetLabel(yAxisLabel)
			else:
				self.yAxisLabelName.SetLabel('Please insert a valid data column')
		else:
			self.yAxisLabelName.SetLabel('Please select valid player Data')


class ListWindow(wx.Frame):
	def __init__(self,parent,id):
		num_data= parent.num_cols
		playerData=parent.playerData
		wx.Frame.__init__(self, parent, id, 'Available Data', pos = (8,40), size=(10,10))
		#wx.Frame.CenterOnScreen(self)
		pos_w=8
		max_h=0
		points_per_row=40
		max_col=int(np.ceil(float(num_data)/points_per_row))
		self.dataText=[]
		for j in range(0, max_col):
			self.dataText.append(j)
			self.dataText[j] = wx.StaticText(self, pos=(pos_w, 8), label='')
			textTemp=''
			for i in range(0, min(points_per_row,num_data-j*points_per_row)):
				textTemp+=str(j*points_per_row+i+1)
				textTemp+='. '
				textTemp+= re.sub('_',' ',playerData.dtype.names[j*points_per_row+i])
				textTemp+='\n'
				
			self.dataText[j].SetLabel(textTemp)
			(w,h)= self.dataText[j].Size
			max_h=max(max_h,h)
			pos_w+=w+8
		self.SetSize((pos_w,max_h+28))
		self.SetPosition((8,40))

def DoScatterPlot(self):
	if not hasattr(self, 'playerData'):
		self.LogInfo.SetLabel('No existing data file selected - Please select valid player Data')
		self.LogInfo.SetForegroundColour((255,0,0))
		return
	
	
	filename=self.filterInput.GetValue()
	if filename:
		self.filterInfo = np.loadtxt(filename, dtype={'names': ('column', 'comp', 'value'),
			'formats': ('i2', 'S2', 'f4')},delimiter=",")
		
		dataFilter=UseFilter(self)
	else:
		(num_players,) = self.playerData.shape
		dataFilter=np.ones(num_players)
		self.LogInfo.SetLabel('No filter selected - Data plot can look very crowdy')

	
	xCol = max(self.xAxisInput.GetValue(),1)-1
	yCol = max(self.yAxisInput.GetValue(),1)-1
	

	xData=self.playerData[self.playerData.dtype.names[xCol]]
	yData=self.playerData[self.playerData.dtype.names[yCol]]
	dataFilter=dataFilter*(1-np.isnan(yData))*(1-np.isnan(xData))
	xLabel=re.sub('_',' ',self.playerData.dtype.names[xCol])
	yLabel=re.sub('_',' ',self.playerData.dtype.names[yCol])
	xData=xData[dataFilter==1]
	yData=yData[dataFilter==1]
	
	minuteData=self.playerData[self.playerData.dtype.names[1]]
	minuteData=minuteData[dataFilter==1]
	if self.xAxis36.GetValue():
		xData=xData/minuteData*36
		xLabel+=' Per 36 Min'
		
	if self.yAxis36.GetValue():
		yData=yData/minuteData*36
		yLabel+=' Per 36 Min'
	
		
	
	playerNames=self.playerNames[dataFilter==1]
	playerLong=self.playerNames[dataFilter==1]
	
	if self.shortName.GetValue():
		for i, txt in enumerate(playerNames):
			txtMatch=re.finditer(" ", txt)
			temp = list(txtMatch)
			if len(temp)>1:
				txtPos=txt.find(" ")
				nameTemp=playerNames[i][0].upper()
				nameTemp+="."
				nameTemp+=playerNames[i][txtPos+1:]
				playerNames[i]=nameTemp
		
	
	fontSize=self.fontSize.GetValue()
	if fontSize<1:
		fontSize=10
		
	namePattern=self.highlightName.GetValue()
	namePattern = namePattern.split(',')
	for i, iname in enumerate(namePattern):
		namePattern[i]=iname.lstrip()
	
	figSizeX=self.figSizeX.GetValue()
	if figSizeX<=0:
		figSizeX=6
	figSizeY=self.figSizeY.GetValue()
	if figSizeY<=0:
		figSizeY=6
	
	fig, axScatter = plt.subplots(figsize=(figSizeX,figSizeY))
	for i, txt in enumerate(playerNames):
		nameFound = 0
		for iname in namePattern:
			if playerLong[i].find(iname) > -1 and iname != "":
				axScatter.annotate(txt, (xData[i],yData[i]), ha='center', va = 'center', size = fontSize ,color='red')
				nameFound=1
				break
		if nameFound==0:
			axScatter.annotate(txt, (xData[i],yData[i]), ha='center', va = 'center', size = fontSize)	
			#axScatter.annotate(txt, (xData[i],yData[i]), ha='center', va = 'center', size = 10, family='Arial Narrow' )
	
	xdist=(xData.max()-xData.min()+0.00000001)/10
	ydist=(yData.max()-yData.min()+0.00000001)/40

	if is_float_try(self.xAxisMin.GetValue()):
		xMin=float(self.xAxisMin.GetValue())
	else:
		xMin=xData.min()-xdist
		
	if is_float_try(self.xAxisMax.GetValue()):
		xMax=float(self.xAxisMax.GetValue())
	else:
		xMax=xData.max()+xdist
	
	if is_float_try(self.yAxisMin.GetValue()):
		yMin=float(self.yAxisMin.GetValue())
	else:
		yMin=yData.min()-ydist
		
	if is_float_try(self.yAxisMax.GetValue()):
		yMax=float(self.yAxisMax.GetValue())
	else:
		yMax=yData.max()+ydist
	
	axScatter.set_xlim((xMin, xMax))
	axScatter.set_ylim((yMin, yMax))
	
	axScatter.set_xlabel(xLabel, size = fontSize+2)
	axScatter.set_ylabel(yLabel, size = fontSize+2)
	plt.setp(axScatter.get_xticklabels(), fontsize=fontSize+2)
	plt.setp(axScatter.get_yticklabels(), fontsize=fontSize+2)
	
	dataCorr=np.corrcoef(xData,yData)
	
	tempTitle=''
	if not self.dataSource.IsEmpty():
		tempTitle+='Data by: '
		tempTitle+=self.dataSource.GetValue()
		tempTitle+=' - '
	tempTitle+='Visualization by @SportsTribution'
	tempTitle+=' - CorrCoeff r:'
	tempTitle+=str(round(dataCorr[1][0],2))
	axScatter.set_title(tempTitle, size= fontSize+2)
	
#	mngr = plt.get_current_fig_manager()
#	mngr.frame.SetPosition((550, 320))
	fig1 = plt.gcf()
	plt.draw()
	plt.show()
	fig1.savefig('test.png')
	

def is_float_try(str):
	try:
		float(str)
		return True
	except ValueError:
		return False

def UseFilter(self):
	if not hasattr(self, 'playerData'):
		self.LogInfo.SetLabel('No existing data file selected - Please select valid player Data')
		self.LogInfo.SetForegroundColour((255,0,0))
		return
	
	else:
		filterInfo=self.filterInfo
		playerData=self.playerData	
		num_filters = filterInfo.size
		if num_filters == 1:
			filterInfo=np.array([filterInfo])
		(num_players,) = playerData.shape
		dataFilter=np.ones(num_players)
		filterString='Selected Filter are:\n'
		for i in range(0, num_filters):
			filterTemp=np.zeros(num_players)
			if re.match('>', filterInfo[i][1]):
				filterTemp=filterTemp + playerData[playerData.dtype.names[filterInfo[i][0]-1]]>filterInfo[i][2]
			if re.match('<', filterInfo[i][1]):
				filterTemp=filterTemp + playerData[playerData.dtype.names[filterInfo[i][0]-1]]<filterInfo[i][2]
			if re.match('=', filterInfo[i][1]):
				filterTemp=filterTemp + playerData[playerData.dtype.names[filterInfo[i][0]-1]]==filterInfo[i][2]
			dataFilter = dataFilter * filterTemp
			filterString+=playerData.dtype.names[filterInfo[i][0]-1]
			filterString+=filterInfo[i][1]
			threshFilter='%.2f' % filterInfo[i][2]
			filterString+=threshFilter
			filterString+='\n'
		
		self.filterText.SetLabel(filterString)
		return dataFilter
	
def inplace_change(filename, old_string, new_string):
	s=open(filename).read()
	if old_string in s:
		s=s.replace(old_string, new_string)
		f=open(filename, 'w')
		f.write(s)
		f.flush()
		f.close()
		





		
application = wx.App()
# call class MyFrame
window = MyFrame()
# start the event loop
application.MainLoop()






