# coding: utf-8
# 
#DONE: due date intervals other than 
# monthly
#DONE: 'delete' account or 'cancel out'

# TIG version. Edit in pythonista from external files-->open, choose from TIG. Use apple 'file' to enable/see TIG files first. 
#
# 2018-10-05 
# Paid button: when a bill is known to be paid: automatically txfr money out of bank balance, change due date to next interval (if a recurring bill)?  Does this effect slide ext balances with regards to todays date?
# Added cancel and done logic to bill balance and bill name
#
# 2018-10-07
# Implement recurring deposits
#  	option a) increase bank balace menu to 
#							include future deposits
#		option b)	extrapolate deposits out 3 mo
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
#		todo: redraw screen to update
import ui
from time import sleep
from datetime import *
import console
import csv
import dialogs
import operator
# Globals:
#__________#
done_pushed=False
cancel_pushed=False
bi_weekly=15
bi_monthly=60
monthly=30
yearly=365
none=0

########### Class Definitions ############
##########################################
class account (object):
	'''Class for handling data for each account+
	Currently all data is handled directly -i.e. there is no class modules to handle data security at the moment. 
	'''
	def __init__(self,idx_val=None,name_val='',bal_val='0.0',due_day_val= datetime.strftime(date.today(),'%Y,%m,%d'), repeat_val=True,dep_val=0.0, dep_date_val= date.today(), paid_val=0.00,cycle_val=monthly):
		self.idx=idx_val
		self.name=name_val
		self.balance=bal_val
		self.due_day=due_day_val
		self.repeat=repeat_val
		self.bank_balance=dep_val
		self.bank_date = dep_date_val
		self.paid = paid_val
		self.cycle = cycle_val

#############===============#############
class accountField (ui.View):
	'''Each account's display of current balance,name,due date, and recurrence setting.  Editable fields for balance and name update. Datepicker for Due Day update, toggle for recurring. 
	todo: dialog for recurring weekly,bi-monthly, etc
	'''	
	global done_pushed
	global cancel_pushed
	# datepicker needs background running or 
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
		due_pick_str=datetime.strftime(due_date_picker.date,'%Y,%m,%d')
		v.title=(due_pick_str)
	
		#save to acc_list
		acc_list= sender.superview.superview.acc_list
		acc_list[self.idx].due_day= due_pick_str
	
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
		field1={'type':'number','key':'balance','title':'Current Balance:  ','value':'{:0.2f}'.format(float(balance_new))}
		field1_2={'type':'number','key':'sched_payment','title':'Scheduled Payment:  ','value':'{:0.2f}'.format(float(amt_pay))}
		field2={'type':'switch','key':'bi_weekly','title':'Bi Weekly','value':True if float(cycle) == bi_weekly else False}
		field3={'type':'switch','key':'bi_monthly','title':'Bi-Monthly',
		'value':True if float(cycle) == bi_monthly else False}
		field4={'type':'switch','key':'monthly','title':'Monthly','value':True if float(cycle) == monthly else False}
		field5={'type':'switch','key':'yearly','title':'Yearly','value':True if float(cycle) == yearly else False}
		field6={'type':'switch','key':'none','title':'None','value':True if float(cycle) == none else False}	
			
		t1=[field1,field1_2]
		t2=[field2,field3,field4,field5,field6]
		s1='Withdrawl Amount',t1
		s2='Bill Cycle',t2
		sect=(s1,s2)
		
		answer=dialogs.form_dialog(title= (name + ' Menu'), sections=sect,done_button_title='Finished')
		if(not answer == None):
			d_balance=answer['balance']
			d_weekly=answer['bi_weekly']
			d_bi_monthly=answer['bi_monthly']
			d_monthly=answer['monthly']
			d_yearly=answer['yearly']
			d_none = answer['none']
			d_paid = answer['sched_payment']
			
			if (d_weekly):
				acc_list[self.idx].cycle=bi_weekly
				recur_str='bi-week'
			if  (d_monthly):
				acc_list[self.idx].cycle=monthly
				recur_str='monthly'
			if  (d_bi_monthly):
				acc_list[self.idx].cycle=bi_monthly
				recur_str='bi-month'
			if  (d_yearly):
				acc_list[self.idx].cycle=yearly
				recur_str='yearly'
			if  (d_none):
				acc_list[self.idx].cycle=none
				recur_str='one-time'
			#update account list
			acc_list[self.idx].balance=d_balance
			self.bal_field.text=d_balance
			self.recur_status.text = recur_str
			acc_list[self.idx].paid=d_paid
		
	def textfield_did_end_editing(self, textfield):
		global done_pushed
		done_pushed=True
		if(textfield.placeholder=='Balance'):
			textfield.text_color='black'
			textfield.superview.superview.acc_list[self.idx].balance=float(textfield.text)
			
			# limit to, or add, 2 decimal places as needed
			textfield.text='{:.2f}'.format(float(textfield.text))
		elif(textfield.placeholder=='Account'):
			textfield.superview.superview.acc_list[self.idx].name=textfield.text
		textfield.end_editing()
		return(True)
		
	@ui.in_background	
	def textfield_did_begin_editing (self, textfield):
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
		#'Done' was pushed
		else:
			done_pushed = False

	def __init__(self, frame_loc=(0,100),acc=account()):
		
		self.frame_location=()
		self.frame_wh=(100,45)
		self.frame_wh_=(140,45)
		self.frame_gw=self.frame_wh[0]+10
		self.frame_gw_=self.frame_wh_[0]+10
		self.due_button_pressed=False
		
		self.idx=acc.idx
		
		#account name field
		self.acc_field= ui.TextField(frame=frame_loc+(self.frame_wh_),bg_color=(.36, .54, .67),text_color=('#060606'),font=('Rockwell',17), placeholder='Account', text=acc.name, border_color=(.0, .0, .0),border_width=2,border_radius=20,alignment=ui.ALIGN_LEFT,alpha=0.5,selected=(False),editable=True,delegate=self)
		
		self.frame_location = (frame_loc[0]+self.frame_gw_,frame_loc[1])
		
		#bill balance field
		self.bal_field= ui.TextField(frame=self.frame_location+(self.frame_wh),bg_color=(.36, .54, .67), font=('Rockwell',17), text_color= 'grey' if acc.paid == 'True' else 'black', border_color='black', placeholder='Balance',text='{:.2f}'.format(float(acc.balance)),border_width=2, border_radius=20,alignment=ui.ALIGN_LEFT,alpha=0.5,selected=(False),editable=False,keyboard_type=ui.KEYBOARD_NUMBERS, delegate=self)
		
		self.frame_location = (self.frame_location[0]+self.frame_gw-5,frame_loc[1]-15)

		#bill due date button
		self.due_button = ui.Button(title=str(acc.due_day), font=('AmericanTypewriter',17),action=self.bt_due_day)
		self.due_button.frame = self.frame_location+(self.frame_wh)
		
		# fill initial recur status in field
		recur_str = 'default'
		if (float(acc.cycle) == bi_weekly):
			recur_str='bi-week'
		if  (float(acc.cycle) == monthly):
			recur_str='monthly'
		if  (float(acc.cycle) == bi_monthly):
			recur_str='bi-month'
		if  (float(acc.cycle) == yearly):
			recur_str='yearly'
		if  (float(acc.cycle) == none):
			recur_str='one-time'
		
		#bill frequency field
		self.recur_status= ui.TextView(frame= (self.frame_location[0],(self.frame_location[1]+30),90,30),font=('AmericanTypewriter',16),border_width=0, border_radius=15, text= recur_str, bg_color='#c1c1c1',editable=False)
		
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
			field2={'type':'number','key':'deposit1','title':'Deposit Amount:  ','value':'{:.2f}'.format( float(self.acc_list[1].bank_balance))}
			field3={'type':'date','key':'dep1_date','title':'Deposit Date:  ','tint_color':'#000000',
			'value': (datetime.strptime(self.acc_list[1].bank_date,'%Y,%m,%d'))}
			field4={'type':'number','key':'deposit2','title':'Deposit Amount:  ','value':'{:.2f}'.format(float(self.acc_list[2].bank_balance))}
			field5={'type':'date','key':'dep2_date','title':'Deposit Date:  ' ,'tint_color':'#000000',
			'value': (datetime.strptime(self.acc_list[2].bank_date,'%Y,%m,%d'))}
			
			t1=[field1]
			t2=[field2,field3]
			t3=[field4,field5]
			s1='Current Balance',t1
			s2='Recurring Deposit 1',t2
			s3='Recurring Deposit 2',t3
		
			sect=(s1,s2,s3)
			answer=dialogs.form_dialog(title='Bank Balance Settings',sections=sect,done_button_title='Finished')
			if (not(answer==None)):
				d_bal = answer['balance']
				d_dep1 = answer['deposit1']
				d_dep1_date = answer['dep1_date']
				d_dep2 = answer['deposit2']
				d_dep2_date = answer['dep2_date']

				# fill account list bank balaces
				# dates require conversion to string 
				# prior to csv write
				self.acc_list[0].bank_balance= d_bal
				self.acc_list[1].bank_balance= d_dep1
				self.acc_list[1].bank_date= datetime.strftime(d_dep1_date,'%Y,%m,%d')
				self.acc_list[2].bank_balance=d_dep2
				self.acc_list[2].bank_date= datetime.strftime(d_dep2_date,'%Y,%m,%d')
			# update balance on gui
			self.set_needs_display()

	def textfield_did_end_editing(self, textfield):
		textfield.end_editing()
		return(True)
	def add_a_subview(self,acc_list):
		x_pos= 10
		y_start =10
#		y_delta = 50

		for idx,a in enumerate(acc_list):
			self.acc_fld= accountField(frame_loc=(x_pos,(idx*50+y_start)),acc=a)
			self.sv.add_subview (self.acc_fld.acc_field)
			self.sv.add_subview (self.acc_fld.bal_field)
			self.sv.add_subview (self.acc_fld.due_button)
			self.sv.add_subview (self.acc_fld.recur_status)

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
		
		# application buttons
		self.right_button_items = (ui.ButtonItem(title='Done',action= self.done_button),ui.ButtonItem(title='Cancel',action=self.cancel_button))
		
		self.left_button_items = (ui.ButtonItem(title='Save',action=self.save_button_),)		
				
		# retreive the database: f() returns a  list of accounts incl bank balance
		self.acc_list=read_acc_list()
		
		#Scrollview for all accounts: increases
		#total on iphone; keyboard non-blocking
		self.sv = ui.ScrollView(frame = (0,0,w,h-280),bg_color='#e2e2e2',shows_vertical_scroll_indicator=False,scroll_enabled=True,indicator_style='#ade4ed',flex='')
	
		#important content size must be bigger than scrollview to allow for scrolling
		self.sv.content_size = (w, h*2) 
		self.add_subview(self.sv)

		# add accounts list to GUI
		self.add_a_subview(self.acc_list)
		
		# maintain y pos for next item
		self.next_y_pos= (len(self.acc_list)*50+10)
		
		# button to add new account
		self.add_account = ui.Button(title='Add Account',font=('Copperplate',17),frame=(10,h-275,0,0),action=add_account_tapped,border_width=0,border_color='#676767')

		self.add_subview(self.add_account)
		
		# button to delete last account
		self.rem_account = ui.Button(title='Rem Account',font=('Copperplate',17),frame=(10,h-245,0,0),action=rem_account_tapped,border_width=0,border_color='#676767')

		self.add_subview(self.rem_account)
		
		#Extended date picker
		self.ext_date_seg = ui.SegmentedControl (segments=('10D','20D','30D'), frame=(170,h-255,180,35),selected_index=-1 , action=ext_date_tapped)
		
		self.add_subview(self.ext_date_seg)
		
		# slider to calculate slide date balance
		self.date_slider= ui.Slider(frame=(10,h-205,350,10),action=slider_changed, continuous=False)
		self.add_subview(self.date_slider)
		
		# Bank balances
		# todo: should this be a class of 'accounts'
		self.b_real_balance = ui.TextView(frame=(10,h-180,110,45), placeholder = 'Bank Bal' , text='{:.2f}'.format(float(self.acc_list[0].bank_balance)) ,  border_width=0,border_radius=5 , bordered=True, delegate=self,font=('Verdana',17))

		self.add_subview(self.b_real_balance)
		
		self.real_label= ui.Label(frame=(10,h-140,110,45),text='Bank Bal')
		self.add_subview(self.real_label)
		
		self.b_ext_balance = ui.TextView(frame=(130,h-180,110,45),text='678.65',font=('Verdana',17),editable=False,selectable=False,border_width=0)
		self.b_ext_balance.bordered=True
		self.add_subview(self.b_ext_balance)
		
		self.ext_label= ui.Label(frame=(130,h-140,110,45),text='ext Bal')
		self.add_subview(self.ext_label)
		
		self.b_slide_balance = ui.TextView(frame=(250,h-180,110,45),text='-86.76',font=('Verdana',17),border_radius=20,border_color='black',border_width=0,editable=False,selectable=False)
		self.add_subview(self.b_slide_balance)
		
		self.slide_label= ui.Label(frame=(250,h-140,110,45),text='slide Bal')
		self.add_subview(self.slide_label)
					
	def draw(self): 
#		print('+++++++++++++++++++++++++++++')
		self.b_real_balance.text= '{:.2f}'.format(float(self.acc_list[0].bank_balance))
		#reset summations for date calcs
		sum=sum_slide=0.0	
		

		# date conversions for deposit date math
		dep1_date = datetime.strptime(self.acc_list[1].bank_date,'%Y,%m,%d')
		dep2_date = datetime.strptime(self.acc_list[2].bank_date,'%Y,%m,%d')
		
		today = date.today()
		
		for i in (self.acc_list):
			#string conversion to datetime.date 
			# Inial due day for future due dates 
			due_day_0= datetime.strptime(i.due_day,'%Y,%m,%d').date()
			
			# get cycle info from account
			cycle = int(i.cycle)

			if (cycle):
				due_day_future = next_bill_due_date(due_day_0,cycle)

				# Need advance dates for accounts based on cycle settings
				due_day_1 = due_day_future[0]
				due_day_2 = due_day_future[1]
				due_day_3 = due_day_future[2]
				due_day_4 = due_day_future[3]
				if cycle == bi_weekly:
					due_day_5 = due_day_future[4]			
					due_day_6 = due_day_future[5]
					due_day_7 = due_day_future[6]		
					due_day_8 = due_day_future[7]			
					
			# Extend update covers 30 days
			ii=0
			if self.ext_date >= due_day_1 and due_day_1 >= today:
				ii+=1
			if self.ext_date >= due_day_2 and due_day_2 >= today:
				ii+=1

			if self.ext_date >= due_day_3:
				ii+=1
				if self.ext_date >= due_day_4:
					ii+=1
			sum+= ii * (float(i.paid))
			
			ii=0
			if self.slide_date >= due_day_1 and due_day_1 >= today:
				ii+=1
			if self.slide_date >= due_day_2 and due_day_2 >= today:
				ii+=1
			if self.slide_date >= due_day_3:
				ii+=1
				if self.slide_date >= due_day_4:
					ii+=1
					if (cycle == bi_weekly):
						if self.slide_date >= due_day_5:
							ii+=1
							if self.slide_date >= due_day_6:
								ii+=1
							if self.slide_date >= due_day_7:
								ii+= 1
			sum_slide+= ii * (float(i.paid))
				
		###########now add deposits###########
		# deduce first valid deposit day using datetime.day math and extrapolation
		deposit_1_dates = next_bill_due_date(dep1_date, monthly)
		deposit_2_dates = next_bill_due_date(dep2_date, monthly)

		dep1_0= deposit_1_dates[0].date()
		dep1_1= deposit_1_dates[1].date()
		dep1_2= deposit_1_dates[2].date()
		dep1_3= deposit_1_dates[3].date()
		dep2_0= deposit_2_dates[0].date()
		dep2_1= deposit_2_dates[1].date()
		dep2_2= deposit_2_dates[2].date()
		dep2_3= deposit_2_dates[3].date()
		
		# Extend update
		ii=0
		if self.ext_date >= dep1_0 and dep1_0 >= today:
			ii+=1
		if self.ext_date >= dep1_1:
			ii+=1
			if self.ext_date >= dep1_2:
				ii+=1
				if self.ext_date >= dep1_3:
					ii+=1
		sum-= ii * (float(self.acc_list[1].bank_balance))
		ii=0
		if self.ext_date >= dep2_0 and dep2_0 >= today:
			ii+=1
		if self.ext_date >= dep2_1:
			ii+=1
			if self.ext_date >= dep2_2:
				ii+=1
				if self.ext_date >= dep2_3:
					ii+=1
		sum-= ii * (float(self.acc_list[2].bank_balance))
			
		# slide update
		ii=0
		if self.slide_date >= dep1_0 and dep1_0 >= today:
			ii+=1
		if self.slide_date >= dep1_1:
			ii+=1
			if self.slide_date >= dep1_2:
				ii+=1
				if self.slide_date >= dep1_3:
					ii+=1
		sum_slide-= ii * (float(self.acc_list[1].bank_balance))	
		
		ii=0
		if self.slide_date >= dep2_0 and dep2_0 >= today:
			ii+=1
		if self.slide_date >= dep2_1:
			ii+=1
			if self.slide_date >= dep2_2:
				ii+=1
				if self.slide_date >= dep2_3:
					ii+=1
		sum_slide-= ii * (float(self.acc_list[2].bank_balance))
		
		# update balance GUIs
		self.b_ext_balance.text= '{:.2f}'.format(float(self.b_real_balance.text)-sum)
		
		self.b_slide_balance.text= '{:.2f}'.format(float(self.b_real_balance.text)-sum_slide)
		self.slide_label.text=str(self.slide_date)[:10]

	def will_close(self):
		''' Called when app is closed via the 'X' left-button only. 
		'''
		write_acc_list(self.acc_list)
		
##############Date Functions##############
##########################################
def next_bill_due_date( bill_date, cycle):
	''' given an initial due date, and cycle, return 3-6 future dates from today. eg: for (bi-)monthly, keep day static and increase month only. For bi-weekly, use 14 days delta and month increases
	'''
	#test for monthly,bi-monthly to use date math instead of +timedeta(days)

	t_day= date.today().day
	t_mo= date.today().month
	t_yr= date.today().year
	
	b_day= bill_date.day
	b_mo= bill_date.month
	b_yr= bill_date.year
	dates=[]
	if (cycle==bi_weekly):
		# this month bill date:
		this_bill = bill_date
		this_mo = t_mo
		this_yr = t_yr
		for i in range(4):
			if this_mo > 12:
				this_mo -= 12
				this_yr += 1
			#use time.replace(month=x+i)
			this_bill = this_bill.replace(month=this_mo,day=b_day,year=this_yr)
			dates.append(this_bill)
			this_bill = this_bill.replace(month=this_mo,day=b_day+14, year=this_yr)
			this_mo+=1
			dates.append(this_bill)

	elif (cycle==monthly):
		this_bill = bill_date
		this_mo = t_mo
		this_yr = t_yr
		for i in range(4):
			if this_mo > 12:
				this_mo -= 12
				this_yr += 1
			this_bill= this_bill.replace(month=this_mo,year=this_yr)
			dates.append(this_bill)
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
			this_mo = t_mo+1
		else:
			this_mo = t_mo
			
		this_bill = bill_date
		this_yr = t_yr
		for i in range(4):
			if this_mo > 12:
				this_mo -= 12
				this_yr += 1
			this_bill=this_bill.replace(month=this_mo,year=this_yr)
			dates.append(this_bill)
			this_mo+=2
			
	elif (cycle == yearly):
		this_bill = bill_date
		for i in range(4):
			this_bill = this_bill.replace(year=t_yr+i)
			dates.append(this_bill)
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
# todo: self detect new column?
fields= ['idx','name','balance','due_day','repeat','bank_bal','bank_date','paid','cycle']

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
			ac= account(idx_val=idx, name_val=row['name'], bal_val=row['balance'], due_day_val=row['due_day'], repeat_val=row['repeat'],
			dep_val=row['bank_bal'],
			dep_date_val=row['bank_date'], paid_val=row['paid'], cycle_val=row['cycle'] )
			acc_list.append(ac)
	return acc_list

def write_acc_list(acc_list):
	with open('moniest.csv', 'w') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=fields)
		writer.writeheader()
		for i in range(len(acc_list)):
			writer.writerow ({ 'idx':i , 'name':acc_list[i].name , 'balance':acc_list[i].balance, 'due_day': acc_list[i].due_day, 'repeat':acc_list[i].repeat, 'bank_bal':acc_list[i].bank_balance,
			'bank_date':acc_list[i].bank_date, 'paid':acc_list[i].paid, 'cycle':acc_list[i].cycle })
			
########### Button Actions ##############
##########################################

# Application buttons {Done,Cancel,Save} have a quirk (bug): they do not have a superview. therefore a global trigger is polled elsewhere. 'Save' required access to account list acc_list so a 'self' method was used
#where cancel and donewere 
	
# Other button actions
	
def add_account_tapped(sender):
	adda=sender.superview
	#add an account
	ac_new=account(idx_val=len(adda.acc_list))
	#append account list
	adda.acc_list.append(ac_new)
	
	# update database
	acc_fld=accountField(frame_loc=(10,(adda.next_y_pos)),acc=ac_new)
	adda.sv.add_subview (acc_fld.acc_field)
	adda.sv.add_subview (acc_fld.bal_field)
	adda.sv.add_subview (acc_fld.due_button)
	adda.sv.add_subview (acc_fld.recur_status)
#	adda.sv.add_subview (acc_fld.paid_button)

	adda.next_y_pos+=50

def rem_account_tapped(sender):
	'''Remove last account added. eventually allow for any account to be deleted. maybe simple to remove from acc list, then write/read 
	'''
	verify = console.alert('Delete Last Account?','Restart Application after Deletions','Cancel','Continue',hide_cancel_button=True)
	if verify == 2: #Contine chosen
		sv=sender.superview
		# Remove last account from list. Use i=n for different account in future 
		sv.acc_list.pop()
		#Only rem last account when opened: 
		#todo: needs to remove this session's new additions as well: how?
		sv.remove_subview(sv.acc_fld.due_button)
		sv.remove_subview(sv.acc_fld.recur_status)
		sv.remove_subview(sv.acc_fld.bal_field)	
		sv.remove_subview(sv.acc_fld.acc_field)			
		sv.next_y_pos-=50
		
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
