# coding: utf-8
#!python3.7 
# DONE: due date intervals other than 
# monthly
# DONE: 'delete' account or 'cancel out'
#
# TIG version. Edit in pythonista from 
# external files-->open, choose from TIG. 
# Use apple 'file' to enable/see TIG files 
# first. 
#
# 2018-10-05 
# Paid button: when a bill is known to be 
# paid: automatically txfr money out of 
# bank balance, change due date to next # 
# interval (if a recurring bill)?  Does 
# this effect slide ext balances with 
# regards to todays date?
# Added cancel and done logic to bill 
# balance and bill name
#
# 2018-10-07
# Implement recurring deposits
#  	option a) increase bank balace menu to 
#							include future deposits
#		option b)	extrapolate deposit out 3 mo
#
# 2018-10-09
# Further implement recurring bills; 
# 	option a) extended bal menu. needs new
#		storage; could implement new tuple csv
#		method
# 	option b) extend switch menu to have
#		bi_monthly, monthly. fine for equal 
#		payments; new column 
#
# 2018-11-22
#   Change bill balance to a popup window 
#   and include all date functions as well
#   recurring bill settings.
#
# 2019-03-28
#		Remove paid button references as it
#		not used anymore, change bill balance
#		to open window; change some names
#		for clarity. 
#	2019-04-23
#		overhaul of date manipulation using 
#		more datetime methods. bills and slide
#		and extend dates use correct day
# 2019-04-25
#		Optimization and cleanup
#		Additon of 'delete account' method
#		Change all dates to datetime.date
#		todo: how to choose account to delete
#		todo: how to remove specific subview
#		todo: bill paid day option overides 
#		due date
#		todo: change color of ? near due date
# 2019-10-03
#		added 2 deposit dates, made 
#		independent. Added weekly billing cat
#		Major change to future date's function
#		Addeds DEBUG constant for all prints
# 2019-10-05 
#		fix 'one time' bills not included
#		remove redundant DEBUG info 
# 2019-10-12
#		Hardcode 'Dep_3' to every two weeks 
#		Add 2 wk category to date method
# 2019-10-16
#		streamlined weekly bill due dates
#		Added bank balance date
#		Change next due date math to return 
#		dates beyond bank balance date. was 
#		today date. 
#		Added dates to all balances in GUI
#########################################
import ui
from time import sleep
from datetime import *
import console
import csv
import dialogs
import operator

import threading

# Globals:
#__________#
done_pushed=False
cancel_pushed=False
weekly=7
two_weeks = 14
bi_weekly=15
bi_monthly=60
monthly=30
yearly=365
none=0
DEBUG = True

########### Class Definitions ###########
##########################################
class account (object):
	'''Class for handling data for each account+
	Currently all data is handled directly -i.e. there is no class modules to handle data security at the moment. 
	'''
	def __init__(self,idx_val=None,name_val='',bal_val='0.0',due_day_val= date.strftime(date.today(),'%Y,%m,%d'), repeat_val=True,dep_val=0.0, dep_date_val= date.strftime(date.today(),'%Y,%m,%d'), paid_val=0.00, paid_date_val=date.strftime(date.today(),'%Y-%m-%d'), cycle_val=monthly):
		self.idx=idx_val
		self.name=name_val
		self.balance=bal_val
		self.due_day=due_day_val
		self.repeat=repeat_val
		self.bank_balance=dep_val
		self.bank_date = dep_date_val
		self.paid = paid_val
		self.paid_date = paid_date_val
		self.cycle = cycle_val

#############===============#############

class accountField (object):
	'''Each account's display of current balance,name,due date, and recurrence setting.  Editable fields for balance and name update. Datepicker for Due Day update, toggle for recurring. 
	todo: dialog for recurring weekly,bi-monthly, etc
	Change to object subclass no ill effects to date (2019-10-25)
	'''	
	global done_pushed
	global cancel_pushed
	global switch_on
	# experiment for XOR of bill recur switches
	switch_on=False

	# datepicker needs background running 
	@ui.in_background
	def bt_due_day(self,sender):
		global done_pushed
		global cancel_pushed
		v=sender
		s_y_pos=v.frame[1]+50
		w=sender.superview
		v.due_button_pressed=True

		#get due day in datetime format to pre-fill datepicker with current due date
		due_day_datetime = datetime.strptime(sender.superview.superview.acc_list[self.idx].due_day,'%Y,%m,%d')
		
		#datepicker below account info for upper positions, and above for lower positions. aleviated keyboard cover-up. 
		due_date_picker= ui.DatePicker(action=None,frame=(0,(s_y_pos if s_y_pos<300 else s_y_pos-150) ,300,100),mode=ui.DATE_PICKER_MODE_DATE,background_color='white',date=due_day_datetime)
		w.add_subview(due_date_picker)
		
		while (not(done_pushed) and not(cancel_pushed)):
			sleep(0.5)
		w.remove_subview(due_date_picker)
		done_pushed = False
		if cancel_pushed==True:
			cancel_pushed=False
			return 
		#'Done' was pushed: update gui
		due_pick_str= date.strftime(due_date_picker.date,'%Y,%m,%d')
		v.title=(due_pick_str)
	
		#save to acc_list
		acc_list= sender.superview.superview.acc_list
		acc_list[self.idx].due_day= due_pick_str
		
	def test_func(sender):
		''' sender is __main__ accounfield not switch object. Global switch_on not reflective of switch position. __getitem__ returns None. how to use?
		'''
		global switch_on
		switch_on=not switch_on
#		print(switch_on)
		
	# Delegate functions within class definition.  Generic names need checks as they are called by any associated (i.e. textfield) ui object	
	
	#Bill Balance Field Action
#	@ui.in_background
	def bill_balance_action(self, sender):
		acc_list= sender.superview.superview.acc_list
		sv=sender.superview
		# get current balance
		balance_new = sender.text
		#get cycle value for default
		cycle = acc_list[self.idx].cycle
		# get name
		name = acc_list[self.idx].name
		if(float(acc_list[self.idx].paid) == 0.00):
			amt_pay = balance_new			
		else:
			amt_pay = acc_list[self.idx].paid
			
		# Fields for balance dialog popup
		field1={'type':'number','key':'balance','title':'Current Balance:  ','value':'{:0.2f}'.format(float(balance_new))}
		field1_2={'type':'number','key':'sched_payment','title':'Scheduled Payment:  ','value':'{:0.2f}'.format(float(amt_pay))}
		
		field1_3={'type':'date',' key':'sched_pay_date','title':'Scheduled Payment Date','value':datetime.strptime(acc_list[self.idx].paid_date,'%Y-%m-%d')}
		field1_4={'type':'switch','key':'weekly','title':'Weekly','value':True if float(cycle) == weekly else False}
		field1_5={'type':'switch','key':'2weekly','title':'Every 2 Weeks','value':True if float(cycle) == two_weeks else False}		
		field2={'type':'switch','key':'bi_weekly','title':'Bi Weekly','value':True if float(cycle) == bi_weekly else False}
		field3={'type':'switch','key':'bi_monthly','title':'Bi-Monthly',
		'value':True if float(cycle) == bi_monthly else False}
		field4={'type':'switch','key':'monthly','title':'Monthly','value':True if float(cycle) == monthly else False}
		field5={'type':'switch','key':'yearly','title':'Yearly','value':True if float(cycle) == yearly else False}
		
		# Can we XOR switches? Action is not even documented to work in a dialogs switch. 
		field6={'type':'switch','key':'none','title':'None','value':True if float(cycle) == none else False, 'action':self.test_func()} 
			
		t1=[field1,field1_2,field1_3]
		t2=[field1_4,field1_5,field2,field3,field4,field5,field6]
		s1='Withdrawl Amount',t1
		s2='Bill Cycle',t2
		sect=(s1,s2)
		# Balance dialog popup
		answer=dialogs.form_dialog(title= (name + ' Menu'), sections=sect,done_button_title='Finished')

		if(not answer == None):
			d_balance=answer['balance']
			d_weekly=answer['weekly']
			d_2weekly=answer['2weekly']
			d_bi_weekly=answer['bi_weekly']
			d_bi_monthly=answer['bi_monthly']
			d_monthly=answer['monthly']
			d_yearly=answer['yearly']
			d_none = answer['none']
			d_paid = answer['sched_payment']
			d_paid_date = answer['Scheduled Payment Date']
			
			if (d_weekly):
				acc_list[self.idx].cycle=weekly
				recur_str='weekly'
			elif (d_2weekly):
				acc_list[self.idx].cycle=two_weeks
				recur_str='2-weeks'			
			elif (d_bi_weekly):
				acc_list[self.idx].cycle=bi_weekly
				recur_str='bi-week'
			elif  (d_monthly):
				acc_list[self.idx].cycle=monthly
				recur_str='monthly'
			elif  (d_bi_monthly):
				acc_list[self.idx].cycle=bi_monthly
				recur_str='bi-month'
			elif  (d_yearly):
				acc_list[self.idx].cycle=yearly
				recur_str='yearly'
			else:
				acc_list[self.idx].cycle=none
				recur_str='one-time'
			#update account list
			acc_list[self.idx].balance=d_balance
			self.bal_field.text=d_balance
			self.recur_status.text = recur_str
			acc_list[self.idx].paid=d_paid
			acc_list[self.idx].paid_date=date.strftime(d_paid_date,'%Y-%m-%d')

	def textfield_did_end_editing(self, textfield):
		print('end')
		global done_pushed
		done_pushed=True
		if(textfield.placeholder=='Balance'):
#			textfield.text_color='black'
			textfield.superview.superview.acc_list[self.idx].balance=float(textfield.text)
			
			# limit to, or add, 2 decimal places as needed
			textfield.text='{:.2f}'.format(float(textfield.text))
		elif(textfield.placeholder=='Account'):
			textfield.superview.superview.acc_list[self.idx].name=textfield.text
		textfield.end_editing()
		return(True)
		
	@ui.in_background	
	def textfield_did_begin_editing (self, textfield):
		print('begin')
		# setup and record previous vals
		old_text=textfield.text
		global cancel_pushed
		global done_pushed
		# clear done from previous end editing
		done_pushed= False
		# open balance/due_day view
		if(textfield.placeholder=="Balance"):
			self.bill_balance_action(textfield)

		while (not(done_pushed) and not(cancel_pushed)):
			sleep(0.5)
		#'Cancel' was pushed
		if cancel_pushed==True:
			cancel_pushed=False
			#temp data needs to be redrawn
			textfield.text=old_text
			textfield.end_editing()
		#'Done' was pushed
		else:
			done_pushed = False
			textfield.end_editing()

	def __init__(self, frame_loc=(0,100),acc=account()):
		
		self.frame_location=()
		self.frame_wh=(100,45)
		self.frame_wh_=(140,45)
		self.frame_gw=self.frame_wh[0]+10
		self.frame_gw_=self.frame_wh_[0]+10
		self.due_button_pressed=False
		# no worky here:
#		self.update_interval = 1
		
		self.idx=acc.idx
		
		#account name field
		self.acc_field= ui.TextField(frame=frame_loc+(self.frame_wh_),bg_color=(.36, .54, .67),text_color=('#060606'),font=('Rockwell',17), placeholder='Account', text=acc.name, border_color=(.0, .0, .0),border_width=2,border_radius=20,alignment=ui.ALIGN_LEFT,alpha=0.5,selected=(False),editable=True,delegate=self)
		
		self.frame_location = (frame_loc[0]+self.frame_gw_,frame_loc[1])
		
		#bill balance field
		self.bal_field= ui.TextField(frame=self.frame_location+(self.frame_wh),bg_color=(.36, .54, .67), font=('Rockwell',17), text_color= 'red' if acc.paid_date == '2019-09-26' else 'black', border_color='black', placeholder='Balance',text='{:.2f}'.format(float(acc.balance)),border_width=2, border_radius=20,alignment=ui.ALIGN_LEFT,alpha=0.5,selected=(False),editable=False,keyboard_type=ui.KEYBOARD_NUMBERS, delegate=self)
		
		self.frame_location = (self.frame_location[0]+self.frame_gw-5,frame_loc[1]-15)

		#bill due date button
		self.due_button = ui.Button(title=str(acc.due_day), font=('AmericanTypewriter',17),action=self.bt_due_day)
		self.due_button.frame = self.frame_location+(self.frame_wh)
		
		# fill initial recur status in field
		recur_str = 'default'
		if (float(acc.cycle) == weekly):
			recur_str='weekly'		
		elif (float(acc.cycle) == two_weeks):
			recur_str='2 weeks'				
		elif (float(acc.cycle) == bi_weekly):
			recur_str='bi-week'
		elif (float(acc.cycle) == monthly):
			recur_str='monthly'
		elif (float(acc.cycle) == bi_monthly):
			recur_str='bi-month'
		elif (float(acc.cycle) == yearly):
			recur_str='yearly'
		elif (float(acc.cycle) == none):
			recur_str='one-time'
		else:
			recur_str='none'		
		#bill frequency field
		self.recur_status= ui.TextView(frame= (self.frame_location[0],(self.frame_location[1]+30),90,30),font=('AmericanTypewriter',16),border_width=0, border_radius=15, text= recur_str, bg_color='#c1c1c1',editable=False)

	# no worky here:
	'''		
	def update(self):
		print('xxxxxx')
		self.bal_field.txt_color = 'red' if acc.paid_date == '2019-09-26' else 'black'
	
	def draw(self):
		print('yes')
	'''
		
#===================================#		
#++++++++++ MAIN CLASS++++++++++++++#
#___________________________________#
		
class moniest (ui.View):
	''' Overall Class 
	'''
	global done_pushed
	
	#bank balance field (action)
	@ui.in_background
	def textview_did_begin_editing(self,textfield):
		if(textfield.placeholder=='Bank Bal'):
			field1={'type':'number','key':'balance','title':'Current Balance:  ','tint_color':'#346511','value':'{:.2f}'.format(float(textfield.text))}
			field1_1={'type':'date','key':'bal_date','title':'Deposit Date:  ','tint_color':'#000000',
			'value': (datetime.strptime(self.acc_list[0].bank_date,'%Y-%m-%d'))}
			field2={'type':'number','key':'deposit1','title':'Deposit Amount:  ','value':'{:.2f}'.format( float(self.acc_list[1].bank_balance))}
			field3={'type':'date','key':'dep1_date','title':'Deposit Date:  ','tint_color':'#000000',
			'value': (datetime.strptime(self.acc_list[1].bank_date,'%Y,%m,%d'))}
			field4={'type':'number','key':'deposit2','title':'Deposit Amount:  ','value':'{:.2f}'.format(float(self.acc_list[2].bank_balance))}
			field5={'type':'date','key':'dep2_date','title':'Deposit Date:  ' ,'tint_color':'#000000',
			'value': (datetime.strptime(self.acc_list[2].bank_date,'%Y,%m,%d'))}			
			field6={'type':'number','key':'deposit3','title':'Deposit Amount:  ','value':'{:.2f}'.format(float(self.acc_list[3].bank_balance))}
			field7={'type':'date','key':'dep3_date','title':'Deposit Date:  ' ,'tint_color':'#000000',
			'value': (datetime.strptime(self.acc_list[3].bank_date,'%Y,%m,%d'))}
			field8={'type':'number','key':'deposit4','title':'Deposit Amount:  ','value':'{:.2f}'.format(float(self.acc_list[4].bank_balance))}
			field9={'type':'date','key':'dep4_date','title':'Deposit Date:  ' ,'tint_color':'#000000',
			'value': (datetime.strptime(self.acc_list[4].bank_date,'%Y,%m,%d'))}
			
			t1=[field1,field1_1]
			t2=[field2,field3]
			t3=[field4,field5]
			t4=[field6,field7]
			t5=[field8,field9]		
			s1='Current Balance',t1
			s2='Recurring Deposit 1: (Monthly)',t2
			s3='Recurring Deposit 2: (monthly)',t3
			s4='Recurring Deposit 3: (every 2 weeks)',t4			
			s5='Recurring Deposit 4: (monthly)',t5
			sect=(s1,s2,s3,s4,s5)
			answer=dialogs.form_dialog(title='Bank Balance Settings',sections=sect,done_button_title='Finished')
			if (not(answer==None)):
				d_bal = answer['balance']
				d_bal_date = answer['bal_date']
				d_dep1 = answer['deposit1']
				d_dep1_date = answer['dep1_date']
				d_dep2 = answer['deposit2']
				d_dep2_date = answer['dep2_date']
				d_dep3 = answer['deposit3']
				d_dep3_date = answer['dep3_date']
				d_dep4 = answer['deposit4']
				d_dep4_date = answer['dep4_date']				
				# fill account list bank balaces
				# dates require conversion to string 
				# prior to csv write
				self.acc_list[0].bank_balance= d_bal
				self.acc_list[0].bank_date= date.strftime(d_bal_date,'%Y-%m-%d')
				self.acc_list[1].bank_balance= d_dep1
				self.acc_list[1].bank_date= date.strftime(d_dep1_date,'%Y,%m,%d')
				self.acc_list[2].bank_balance=d_dep2
				self.acc_list[2].bank_date= date.strftime(d_dep2_date,'%Y,%m,%d')
				self.acc_list[3].bank_balance=d_dep3
				self.acc_list[3].bank_date= date.strftime(d_dep3_date,'%Y,%m,%d')
				self.acc_list[4].bank_balance=d_dep4
				self.acc_list[4].bank_date= date.strftime(d_dep4_date,'%Y,%m,%d')
			# update balance on gui
			self.set_needs_display()

	def textfield_did_end_editing(self, textfield):
		textfield.end_editing()
		return(True)
	def add_all_subview(self,acc_list):
		x_pos= 10
		y_start =10
#		y_delta = 50

		for idx,a in enumerate(acc_list):
			self.acc_fld[idx]= accountField(frame_loc=(x_pos,(idx*50+y_start)),acc=a)
			
			# add subviews
			self.sv.add_subview (self.acc_fld[idx].acc_field)
			self.sv.add_subview (self.acc_fld[idx].bal_field)
			self.sv.add_subview (self.acc_fld[idx].due_button)
			self.sv.add_subview (self.acc_fld[idx].recur_status)

	def save_button_(self,sender):
		write_acc_list(self.acc_list)
		console.hud_alert('Saved')
		
	def done_button(self,sender):
		global done_pushed
		done_pushed=True

	def cancel_button(self,sender):
		global cancel_pushed
		cancel_pushed=True

	def __init__(self):
		w,h = ui.get_screen_size()
		# main View frame	attributes
		self.name='Moniest'
		self.background_color='#cacaca'
		self.ext_date=date.today()
		self.slide_date=date.today()
		self.flex=''
		# make a list to have index color control
		self.acc_fld=[]
		
		# update attempt
		self.update_interval = 1
	
		# application buttons
		self.right_button_items = (ui.ButtonItem(title='Done',action= self.done_button),ui.ButtonItem(title='Cancel',action=self.cancel_button))
		
		self.left_button_items = (ui.ButtonItem(title='Save',action=self.save_button_),)		
				
		# retreive the database: f() returns a  list of accounts incl bank balance
		self.acc_list=read_acc_list()
		
		# attempt list for acc gui
		print('acc_list len',range(len(self.acc_list)))
		for x in range(len(self.acc_list)):
			self.acc_fld.append(0)
		
		#Scrollview for all accounts: increases
		#total on iphone; keyboard non-blocking
		self.sv = ui.ScrollView(frame = (0,0,w,h-320),bg_color='#e2e2e2',shows_vertical_scroll_indicator=False,scroll_enabled=True,indicator_style='#ade4ed',flex='')
	
		#important content size must be bigger than scrollview to allow for scrolling
		self.sv.content_size = (w, h*2.5) 
		self.add_subview(self.sv)

		# add accounts list to GUI
		self.add_all_subview(self.acc_list)
		
		# maintain y pos for next item
		self.next_y_pos= (len(self.acc_list)*50+10)
		
		# button to add new account
		self.add_account = ui.Button(title='Add Account',font=('Copperplate',17),frame=(10,h-310,0,0),action=add_account_tapped,border_width=0,border_color='#676767')

		self.add_subview(self.add_account)
		
		# button to delete last account
		self.rem_account = ui.Button(title='Rem Account',font=('Copperplate',17),frame=(10,h-280,0,0),action=rem_account_tapped,border_width=0,border_color='#676767')

		self.add_subview(self.rem_account)
		
		#Extended date picker
		self.ext_date_seg = ui.SegmentedControl (segments=('10D','20D','30D'), frame=(170,h-300,180,35),selected_index=-1 , action=ext_date_tapped)
		
		self.add_subview(self.ext_date_seg)
		
		# slider to calculate slide date balance
		self.date_slider= ui.Slider(frame=(10,h-235,350,10),action=slider_changed, continuous=False)
		self.add_subview(self.date_slider)
		
		# Bank balances
		# Real bank balance and date recorded
		self.b_real_balance = ui.TextView(frame=(10,h-180,110,45), placeholder = 'Bank Bal' , text='{:.2f}'.format(float(self.acc_list[0].bank_balance)) ,  border_width=0,border_radius=5 , bordered=True, delegate=self,font=('Verdana',17))

		self.add_subview(self.b_real_balance)
		
		self.real_label= ui.Label(frame=(15,h-140,110,45),text='Bank Bal')
		self.add_subview(self.real_label)
		
		self.real_date_label= ui.Label(frame=(15,h-215,110,45),text='slide Bal')
		self.add_subview(self.real_date_label)		
		# 10/20/30 Day Extended Bank
		#  Balance extrapolation
		self.b_ext_balance = ui.TextView(frame=(130,h-180,110,45),text='678.65',font=('Verdana',17),editable=False,selectable=False,border_width=0)
		self.b_ext_balance.bordered=True
		self.add_subview(self.b_ext_balance)
		
		self.ext_label= ui.Label(frame=(135,h-140,110,45),text='Ext Bal')
		self.add_subview(self.ext_label)

		self.ext_date_label= ui.Label(frame=(135,h-215,110,45),text=date.strftime(self.ext_date,'%Y-%m-%d'))
		self.add_subview(self.ext_date_label)				
		# Slider Bank Balance extrapolation
		self.b_slide_balance = ui.TextView(frame=(250,h-180,110,45),text='-86.76',font=('Verdana',17),border_radius=20,border_color='black',border_width=0,editable=False,selectable=False)
		self.add_subview(self.b_slide_balance)
		
		self.slide_date_label= ui.Label(frame=(255,h-215,110,45),text='slide Bal')
		self.add_subview(self.slide_date_label)

		self.slide_label= ui.Label(frame=(255,h-140,110,45),text='Slide Bal')
		self.add_subview(self.slide_label)		
					
	def draw(self): 
#		print('+++++++++++++++++++++++++++++')
		self.b_real_balance.text= '{:.2f}'.format(float(self.acc_list[0].bank_balance))
		# reset summations for date calcs
		sum=sum_slide=0.0	
	
		# Conversion math for deposit dates
		dep1_date = datetime.strptime(self.acc_list[1].bank_date,'%Y,%m,%d')
		dep1_date = datetime.date(dep1_date)
		dep2_date = datetime.strptime(self.acc_list[2].bank_date,'%Y,%m,%d')
		dep2_date = datetime.date(dep2_date)
		dep3_date = datetime.strptime(self.acc_list[3].bank_date,'%Y,%m,%d')
		dep3_date = datetime.date(dep3_date)
		dep4_date = datetime.strptime(self.acc_list[4].bank_date,'%Y,%m,%d')		
		dep4_date = datetime.date(dep4_date)
		
		today = date.today()
		bal_date=datetime.strptime(self.acc_list[0].bank_date,'%Y-%m-%d')
		bal_date = datetime.date(bal_date)
		
		for i in (self.acc_list):
			# string conversion to datetime.date 
			# Inital due day for future due dates 
			i.paid_date = '2019-09-27'
			due_day_0= datetime.strptime(i.due_day,'%Y,%m,%d').date()
			if DEBUG:
				print('\nipaid:',i.paid)
			# get cycle info from account
			cycle = int(i.cycle)
			if DEBUG:
				print('Withdrawls....')
			due_day_future = next_bill_due_date(bal_date, due_day_0,cycle)
			if DEBUG:
				print('1st billdate:',due_day_0,cycle)
				print('future bill dates:',end='')
			for bill_date in due_day_future:
				if DEBUG:
					print(bill_date,end=',')
				if self.ext_date >= bill_date:
					sum+=float(i.paid)
					i.paid_date='2019-09-26'
				else:
#					i.paid_date='2019-09-27'			
					pass
				if self.slide_date >= bill_date:
					sum_slide+=float(i.paid)
					i.paid_date='2019-09-26'	
				else:
					pass
#					i.paid_date='2019-09-27'			
			if DEBUG:
				print('\nsum,slide:',sum,sum_slide)
				print('ext,slide_date',self.ext_date,self.slide_date)
		#end for loop
		
		###########now add deposits###########
		# deduce first valid deposit day using datetime.day math and extrapolation
		if DEBUG:
			print('deposits...')
		deposit_1_dates = next_bill_due_date(bal_date,dep1_date, monthly)
		deposit_2_dates = next_bill_due_date(bal_date,dep2_date, monthly)
		deposit_3_dates = next_bill_due_date(bal_date,dep3_date, two_weeks)
		deposit_4_dates = next_bill_due_date(bal_date,dep4_date, monthly)
		if DEBUG:
				print(deposit_1_dates)
				print(deposit_2_dates)
				print('dep3:',deposit_3_dates)				
				print(deposit_4_dates)											
		for dep_date in deposit_1_dates:
			if self.ext_date >= dep_date:
				sum-= (float(self.acc_list[1].bank_balance))
			if self.slide_date >= dep_date:
				sum_slide-= (float(self.acc_list[1].bank_balance))
				
		for dep_date in deposit_2_dates:
			if self.ext_date >= dep_date:
				sum-= (float(self.acc_list[2].bank_balance))
			if self.slide_date >= dep_date:
				sum_slide-= (float(self.acc_list[2].bank_balance))
				
		for dep_date in deposit_3_dates:
			if self.ext_date >= dep_date:
				sum-= (float(self.acc_list[3].bank_balance))
			if self.slide_date >= dep_date:
				sum_slide-= (float(self.acc_list[3].bank_balance))
				
		for dep_date in deposit_4_dates:
			if self.ext_date >= dep_date:
				sum-= (float(self.acc_list[4].bank_balance))
			if self.slide_date >= dep_date:
				sum_slide-= (float(self.acc_list[4].bank_balance))
		
		# update balance GUIs
		self.b_ext_balance.text= '{:.2f}'.format(float(self.b_real_balance.text)-sum)
		
		self.b_slide_balance.text= '{:.2f}'.format(float(self.b_real_balance.text)-sum_slide)
		self.slide_date_label.text=str(self.slide_date)[:10]		
		self.real_date_label.text=self.acc_list[0].bank_date
		self.ext_date_label.text=date.strftime(self.ext_date,'%Y-%m-%d')
		write_acc_list(self.acc_list)		

	def will_close(self):
		''' Called when app is closed via the 'X' left-button only. 
		'''
	# Update called every interval
	def update(self):
		for idx,a in enumerate(self.acc_list):
			self.acc_fld[idx].bal_field.text_color = 'red' if a.paid_date == '2019-09-26' else 'black'

		
##############Date Functions##############
##########################################

def last_day_of_month(date):
		if date.month == 12:
			return date.replace(day=31)
		return date.replace(month=date.month+1, day=1) - dt.timedelta(days=1)
		
def next_bill_due_date( bal_date, bill_date, cycle):
	''' given an initial due date, and cycle, return 3-6 future dates from dayof bank balance input. eg: for (bi-)monthly, keep day static and increase month only. For bi-weekly, use 14 days delta and month increases
	'''
	t_day= date.today().day
	t_mo= date.today().month
	t_yr= date.today().year
	
	b_day= bill_date.day
	b_mo= bill_date.month
	b_yr= bill_date.year
	dates=[]
	
	if (cycle==weekly):
		#every week, dates change
		this_bill=bill_date
		# Extrapolate date beyond today		
		while this_bill <= bal_date:
			this_bill+=timedelta(7)
		for i in range(20):
			if this_bill >= bill_date:
				dates.append(this_bill)
			this_bill+= timedelta(days=7)		
		
	elif cycle==two_weeks:
		#every 2 weeks dates change
		this_bill=bill_date
		# Extrapolate date beyond today		
		while this_bill <= bal_date:	
			this_bill+=timedelta(14)
		for i in range(6):
			if this_bill >= bill_date:
				dates.append(this_bill)
			this_bill+= timedelta(days=14)
				
	elif (cycle==bi_weekly):
		# twice month occuring on same dates
		# this month bill date:
		this_bill = bill_date
		this_mo = b_mo
		this_yr = b_yr
		b_day_corrected=b_day+14
		for i in range(10):
			#use time.replace(month=x+i)
			this_bill = this_bill.replace(month=this_mo,day=b_day,year=this_yr)
			if this_bill > bal_date and this_bill >= bill_date:				
				dates.append(this_bill)
			# Feb 28 check 
			if(this_mo==2 and b_day_corrected>28):
				b_day_corrected=28
			this_bill = this_bill.replace(month=this_mo,day=b_day_corrected, year=this_yr)
			if this_bill > bal_date and this_bill >= bill_date:
				dates.append(this_bill)
			this_mo+=1
			if this_mo > 12:
				this_mo -= 12
				this_yr += 1
			# always reset for Feb 28 
			b_day_corrected=b_day+14
			
	elif (cycle==monthly):
		# monthly needs check for Feb 28 
		this_bill = bill_date
		this_mo = b_mo
		this_yr = b_yr
		this_day = b_day
		for i in range(6):
			if this_mo > 12:
				this_mo -= 12
				this_yr += 1
			# Feb 28 check 
			if(this_mo==2 and this_day>28):
				this_day=28
			if this_day == 31:
				this_day=30
			this_bill= this_bill.replace(month=this_mo,day=this_day,year=this_yr)
			if this_bill > bal_date and this_bill >= bill_date:
				dates.append(this_bill)
			# always reset for Feb 28 
			this_day=b_day
			this_mo+=1						

	elif (cycle==bi_monthly):#needs to know which month to start. maybe even odd?
	#if true month is odd
		odd_bill_month= b_mo%2
		odd_this_month= t_mo%2
		# bill odd today even = add mo
		# bill even today odd = add mo
		# both even do nothing
		# both odd do nothing
		if (operator.xor(odd_bill_month,  odd_this_month)):
			this_mo = b_mo+1
		else:
			this_mo = b_mo
		this_day=b_day
		this_bill = bill_date
		this_yr = b_yr
		for i in range(6):
			if this_mo > 12:
				this_mo -= 12
				this_yr += 1
			# Feb 28 check 
			if(this_mo==2 and this_day>28):
				this_day=28
			this_bill=this_bill.replace (month=this_mo,day=this_day,year=this_yr)
			# always rest for Feb
			this_day=b_day
#			if this_bill >= date.today():
			if this_bill > bal_date and this_bill >= bill_date:		
				dates.append(this_bill)
			this_mo+=2			

	elif (cycle == yearly):
		this_bill = bill_date
		for i in range(4):
			this_bill = this_bill.replace(year=t_yr+i)

			if this_bill > bal_date and this_bill >= bill_date:	
				dates.append(this_bill)
	else: 
		if bill_date > bal_date: 	
				dates.append(bill_date)
		
	return dates
		
########### CSV DB Functions ############
##########################################
# When adding new column need to write before reading (because the coulumn is not there yet, and read is first operation and will fail). All data can be overwritten so make copies, git, or dropbox csv prior. 
# 1. add new column to 'fields'
# 2. add new column to write()
# 3. add new column to account class as needed, incl initialization
# 4. run program once, exit, and 
# 5. verify csv has new column and all old and new data
# 6. finally, add new column to read()
fields= ['idx','name','balance','due_day','repeat','bank_bal','bank_date','paid','paid_date','cycle']

def read_acc_list():
	# initial check to see if csv is empty
	# is this accidentally wiping data when adding new column?! Disable until new empty csv is created
	if 0:
		with open('moniest.csv', 'r') as csvfile:
			csv_dict = [row for row in csv.DictReader(csvfile)]
		if (csv_dict) == 0:
			print('csv file is empty')
			with open('moniest.csv', 'w') as csvfile:
				writer = csv.DictWriter(csvfile, fieldnames=fields)
				writer.writeheader()
				writer.writerow({ 'idx': None, 'name': '', 'balance': 0.0, 'due_day': '', 'repeat': True})
			
	acc_list=[]		
	#Open CSV, parse into type: account list
	with open('moniest.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for idx,row in enumerate(reader):
			ac= account( idx_val=idx, name_val=row['name'], bal_val=row['balance'], due_day_val=row['due_day'], repeat_val=row['repeat'],
			dep_val=row['bank_bal'],
			dep_date_val=row['bank_date'], paid_val=row['paid'], paid_date_val=row['paid_date'], cycle_val=row['cycle'] )
			acc_list.append(ac)
	return acc_list

def write_acc_list(acc_list):
	with open('moniest.csv', 'w') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=fields)
		writer.writeheader()
		for i in range(len(acc_list)):
			writer.writerow ({ 'idx':i , 'name':acc_list[i].name , 'balance':acc_list[i].balance, 'due_day': acc_list[i].due_day, 'repeat':acc_list[i].repeat, 'bank_bal':acc_list[i].bank_balance,
			'bank_date':acc_list[i].bank_date, 'paid':acc_list[i].paid, 'paid_date':acc_list[i].paid_date, 'cycle':acc_list[i].cycle })
			
########### Button Actions ##############
##########################################

# Application buttons {Done,Cancel,Save} have a quirk (bug): they do not have a superview. therefore a global trigger is polled elsewhere. 'Save' required access to account list acc_list so a 'self' method was used
#where cancel and done were...? 
	
# Other button actions
	
def add_account_tapped(sender):
	# todo: new accounts init on 31st mo fail non 31 day months
	# todo: new month fails moniest update. 	
	adda=sender.superview

	# scroll to end of account	
	adda.sv.content_offset = (0,adda.next_y_pos-300)
	# add an account
	ac_new= account(idx_val=len(adda.acc_list))
	#append account list
	adda.acc_list.append(ac_new)
	
	# add GUI 
	account_fld=accountField(frame_loc=(10,(adda.next_y_pos)),acc=ac_new)
	adda.sv.add_subview (account_fld.acc_field)
	adda.sv.add_subview (account_fld.bal_field)
	adda.sv.add_subview (account_fld.due_button)
	adda.sv.add_subview (account_fld.recur_status)

	adda.acc_fld.append(account_fld)
	
	# update database
	adda.next_y_pos+=50
	write_acc_list(adda.acc_list)

def rem_account_tapped(sender):
	'''Remove last account added. eventually allow for any account to be deleted. maybe simple to remove from acc list, then write/read 
	'''
	sv=sender.superview	
	# scroll to end of account
	sv.sv.content_offset = (0,sv.next_y_pos-300)
	verify = console.alert('Delete Last Account?','Restart Application after each Deletion', 'Cancel','Continue', hide_cancel_button=True)
	if verify == 2: #Contine chosen
		
		last_acc = len(sv.acc_list)-1

		# Remove last account from list. Use i=n for different account in future 
		sv.acc_list.pop()

		# remove_subview() only removes last
		# account (when opened) from GUI. 
		# Succesive calls do not effect GUI. 
		# todo: needs to remove this session's new additions as well: how?
		sv.remove_subview(sv.acc_fld[last_acc].due_button)
		sv.remove_subview(sv.acc_fld[last_acc].recur_status)
		sv.remove_subview(sv.acc_fld[last_acc].bal_field)	
		sv.remove_subview(sv.acc_fld[last_acc].acc_field)			
		sv.acc_fld.pop()
		sv.next_y_pos-=50
		sv.set_needs_display()
		
def ext_date_tapped(sender):
	s=sender
	sv=sender.superview
	#returns set{0,2}
	idx=s.selected_index
	
	today_date=date.today()

	sv.ext_date=today_date + (idx+1)*timedelta(days=10)
	sv.set_needs_display()
		
def slider_changed(sender):
	''' Continuous mode had to be false to aleviate pythonista dropping out. 
	'''
	s=sender
	sv=sender.superview
	idx=sender.value
	today_date=date.today()
	
	sv.slide_date=today_date + (idx)*timedelta(days=90)

	sv.set_needs_display()
	
def main():	
	console.clear()
	view=moniest()
	view.present('sheet')

if __name__=='__main__':
	main()
