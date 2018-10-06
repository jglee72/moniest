# coding: utf-8
# 
#todo: due date intervals other than monthly
#todo: 'delete' account or 'cancel out'
#todo: accounts that won't be paid off;
# how to indicate paymet plan within balance

# TIG version. Edit in pythonista from external files-->open, choose from TIG. Use apple 'file' to enable/see TIG files first. 

import ui
from time import sleep
from datetime import *
import console
import csv
import dialogs

# Globals:
#__________#
done_pushed=False
cancel_pushed=False

########### Class Definitions ############
##########################################
class account (object):
	'''Class for handling data for each account
	Currently all data is handled directly -i.e. there is no class modules to handle data security at the moment. 
	'''
	def __init__(self,idx_val=None,name_val='',bal_val='',due_day_val='Due Date',repeat_val=True,dep_val=0.0, dep_date_val=datetime.today()):
		self.idx=idx_val
		self.name=name_val
		self.balance=bal_val
		self.due_day=due_day_val
		self.repeat=repeat_val
		self.bank_balance=dep_val
		self.bank_date = dep_date_val

#############===============#############
class accountField (ui.View):
	'''Each account's display of current balance,name,due date, and recurrence setting.  Editable fields for balance and name update. Datepicker for Due Day update, toggle for recurring. 
	todo: dialog for recurring weekly,bi-monthly, etc
	'''	
	# datepicker needs background running or 
	# didn't return or wouldn't go away?	- can't remember
	@ui.in_background
	def due_button_tapped(self,sender):
		global done_pushed
		global cancel_pushed
		v=sender
		s_y_pos=v.frame[1]+50
		w=sender.superview
		v.due_button_pressed=True

		#get due day in datetime format to pre-fill datepicker with current due date
		due_day_picker = datetime.strptime(sender.superview.superview.acc_list[self.idx].due_day,'%Y,%m,%d')
		
		#datepicker below account info for upper positions, and above for lower poitions. aleviated keyboard cover-up. 
		ext_date= ui.DatePicker(action=None,frame=(0,(s_y_pos if s_y_pos<300 else s_y_pos-150) ,300,100),mode=ui.DATE_PICKER_MODE_DATE,background_color='white',date=due_day_picker)
		
		w.add_subview(ext_date)
		
		while (not(done_pushed) and not(cancel_pushed)):
			sleep(0.5)
		w.remove_subview(ext_date)
		done_pushed = False
		if cancel_pushed==True:
			cancel_pushed=False
			return 
		#'Done' was pushed
		v.title=(str(ext_date.date))[:10]
		#save to acc_list
		acc_list= sender.superview.superview.acc_list
		acc_list[self.idx].due_day= datetime.strftime(ext_date.date,'%Y,%m,%d')
	
	# Delegate functions within class definition.  Generic names need checks as they are called by any associate (i.e. textfield) ui object	
	def repeat_changed(self,sender):
		acc_list= sender.superview.superview.acc_list
		acc_list[self.idx].repeat=sender.value
	
	def textfield_did_end_editing(self, textfield):
		if(textfield.placeholder=='Balance'):
			textfield.superview.superview.acc_list[self.idx].balance=float(textfield.text)
		
		elif(textfield.placeholder=='Account'):
			textfield.superview.superview.acc_list[self.idx].name=textfield.text
	
	def __init__(self, frame_loc=(0,100),acc=account()):
		
		self.frame_location=()
		self.frame_wh=(100,45)
		self.frame_wh_=(140,45)
		self.frame_gw=self.frame_wh[0]+10
		self.frame_gw_=self.frame_wh_[0]+10
		self.due_button_pressed=False
		
		self.idx=acc.idx
		
		self.acc_field= ui.TextField(frame=frame_loc+(self.frame_wh_),bg_color=(.36, .54, .67),text_color=('#060606'),font=('Rockwell',17), placeholder='Account', text=acc.name, border_color=(.0, .0, .0),border_width=2,border_radius=20,alignment=ui.ALIGN_LEFT,alpha=0.5,selected=(False),editable=True,delegate=self)
		
		self.frame_location = (frame_loc[0]+self.frame_gw_,frame_loc[1])
		
		self.bal_field= ui.TextField(frame=self.frame_location+(self.frame_wh),bg_color=(.36, .54, .67), text_color=('#000000'),font=('Rockwell',17), border_color='black', placeholder='Balance',text=str(acc.balance),border_width=2, border_radius=20,alignment=ui.ALIGN_LEFT,alpha=0.5,selected=(True),editable=True,keyboard_type=ui.KEYBOARD_NUMBERS)
		self.bal_field.delegate=self
		
		self.frame_location = (self.frame_location[0]+self.frame_gw-5,frame_loc[1]-15)
		
		self.due_button = ui.Button(title=(acc.due_day[:10]), font=('AmericanTypewriter',17),action=self.due_button_tapped)
		self.due_button.frame = self.frame_location+(self.frame_wh)
		
		self.switch= ui.Switch(frame= (self.frame_location[0],(self.frame_location[1]+30),51,31),action=self.repeat_changed,border_width=0, border_radius=15, value= True if acc.repeat=='True' else False, bg_color='#c1c1c1',delegate=self)
		
#===================================#		
#++++++++++ MAIN CLASS++++++++++++++#
#___________________________________#
		
class moniest (ui.View):
	''' Overall Class 
	'''
	global done_pushed
	
	@ui.in_background
	def textfield_did_begin_editing(self,textfield):
		if(textfield.placeholder=='Bank Bal'):
			field1={'type':'number','key':'balance','title':'Current Balance:  ','tint_color':'#346511','value':textfield.text}
			field2={'type':'number','key':'deposit1','title':'Deposit Amount:  ','value':self.acc_list[1].bank_balance}
			field3={'type':'date','key':'dep1_date','title':'Deposit Date:  ','tint_color':'#000000',
			'value':(datetime.strptime(self.acc_list[1].bank_date,'%Y,%m,%d'))}
			field4={'type':'number','key':'deposit2','title':'Deposit Amount:  ','value':self.acc_list[2].bank_balance}
			field5={'type':'date','key':'dep2_date','title':'Deposit Date:  ' ,'tint_color':'#000000',
			'value':(datetime.strptime(self.acc_list[2].bank_date,'%Y,%m,%d'))}
			
			t1=[field1]
			t2=[field2,field3]
			t3=[field4,field5]
			s1='Current Balance',t1
			s2='Recurring Deposit 1',t2
			s3='Recurring Deposit 2',t3
		
			sect=(s1,s2,s3)
			
			answer=dialogs.form_dialog(title='Bank Balance Settings',sections=sect,done_button_title='Finished')
			
			d_bal=answer['balance']
			d_dep1=answer['deposit1']
			d_dep1_date=answer['dep1_date']
			d_dep2=answer['deposit2']
			d_dep2_date=answer['dep2_date']
			print('dbal=:',d_bal)
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
	
	def add_a_subview(self,acc_list):
		x_pos= 10
		y_start =10
		y_delta = 50

		for idx,a in enumerate(acc_list):
			self.acc_fld= accountField(frame_loc=(x_pos,(idx*50+y_start)),acc=a)
			self.sv.add_subview (self.acc_fld.acc_field)
			self.sv.add_subview (self.acc_fld.bal_field)
			self.sv.add_subview (self.acc_fld.due_button)
			self.sv.add_subview (self.acc_fld.switch)
	def save_button_(self,sender):
		print('writing')
		write_acc_list(self.acc_list)
		console.hud_alert('Saved')
	def __init__(self):
		w,h = ui.get_screen_size()
		# main View frame	attributes
		self.name='Moniest'
		self.background_color='#cacaca'
		self.ext_date=datetime.today()
		self.slide_date=datetime.today()
		self.flex=''
		
		# application buttons
		self.right_button_items = (ui.ButtonItem(title='Done',action=done_button),ui.ButtonItem(title='Cancel',action=cancel_button))
		
		self.left_button_items = (ui.ButtonItem(title='Save',action=self.save_button_),)		
				
		
		# retreive the database: f() returns a  list of accounts incl bank balance
		self.acc_list=read_acc_list()
		
		#Scrollview for all accounts: increases
		#total on iphone; keyboard non-blocking
		self.sv = ui.ScrollView(frame = (0,0,w,h-245),bg_color='#e2e2e2',shows_vertical_scroll_indicator=False,scroll_enabled=True,indicator_style='#ade4ed',flex='')
	
		#important content size must be bigger than scrollview to allow for scrolling
		self.sv.content_size = (w, h*2) 
		self.add_subview(self.sv)

		# add accounts list to GUI
		self.add_a_subview(self.acc_list)
		
		# maintain y pos for next item
		self.next_y_pos= (len(self.acc_list)*50+10)
		
		# button to add new account
		self.add_account = ui.Button(title='Add Account',font=('Copperplate',17),frame=(10,440,0,0),action=add_account_tapped,border_width=0,border_color='#676767')

		self.add_subview(self.add_account)
		
		#Extended date picker
		self.ext_date_seg = ui.SegmentedControl (segments=('10D','20D','30D'), frame=(170,445,180,35),selected_index=-1 , action=ext_date_tapped)
		
		self.add_subview(self.ext_date_seg)
		
		# slider to calculate slide date balance
		self.date_slider= ui.Slider(frame=(10,500,350,10),action=slider_changed)
		self.add_subview(self.date_slider)
		
		# Bank balances
		# todo: should this be a class of 'accounts'
		self.b_real_balance = ui.TextField(frame=(10,530,110,45), placeholder = 'Bank Bal' , text=str(self.acc_list[0].bank_balance) , keyboard_type=ui.KEYBOARD_NUMBERS , border_width=0,border_radius=5 , bordered=True, delegate=self)

		self.add_subview(self.b_real_balance)
		
		self.real_label= ui.Label(frame=(10,565,110,45),text='Bank Bal')
		self.add_subview(self.real_label)
		
		self.b_ext_balance = ui.TextField(frame=(130,530,110,45),text='678.65',editable=False,selected=False,border_width=0)
		self.b_ext_balance.bordered=True
		self.add_subview(self.b_ext_balance)
		
		self.ext_label= ui.Label(frame=(130,565,110,45),text='ext Bal')
		self.add_subview(self.ext_label)
		
		self.b_slide_balance = ui.TextField(frame=(250,530,110,45),text='-86.76',border_radius=20,border_color='black',border_width=0,editable=False)
		self.add_subview(self.b_slide_balance)
		
		self.slide_label= ui.Label(frame=(250,565,110,45),text='slide Bal')
		self.add_subview(self.slide_label)
					
	def draw(self): 
		print('+++++++++++++++++++++++++++++++')
		self.b_real_balance.text= self.acc_list[0].bank_balance
		
		sum=sum_slide=0.0	
		# date conversions for date math
		dep1_date = datetime.strptime(self.acc_list[1].bank_date,'%Y,%m,%d')
		dep2_date = datetime.strptime(self.acc_list[2].bank_date,'%Y,%m,%d')
		
		for i in (self.acc_list):
			#string conversion to datetime.datetime
			due_day_= datetime.strptime(i.due_day,'%Y,%m,%d')
			
			# Need 1,2,3 month advance due day for recurring accounts
			#todo: can this be passed as reference on a per button active
			# only do if repeat is True
			due_day_next=due_day_ + timedelta(days=30)
			due_day_next_next= due_day_ + timedelta(days=60)
			due_day_next_next_next= due_day_ + timedelta(days=90)
#			print(due_day_,due_day_next,due_day_next_next,due_day_next_next_next)
			#todo: only process if ext_date changes
			if (due_day_next > self.ext_date > due_day_):
				print('orig', i.name, self.ext_date)
			# sum += 1x recurring balance
			elif (due_day_next_next > self.ext_date > due_day_next):
				print('30 day',i.name)
			# sum += 2x recurring balance
			elif (due_day_next_next_next > self.ext_date > due_day_next_next):
				print('60 day',i.name)
			elif (self.ext_date > due_day_next_next_next):
				print('90 day',i.name)
				
			#todo: only process on slide_date change
			if (due_day_next > self.slide_date > due_day_):
				print('s_orig', i.name)
			# sum += 1x recurring balance
			elif (due_day_next_next > self.slide_date > due_day_next):
				print('s_30 day',i.name)
			# sum += 2x recurring balance
			elif (due_day_next_next_next > self.slide_date > due_day_next_next):
				print('s_60 day',i.name)
			elif (self.slide_date > due_day_next_next_next):
				print('s_90 day',i.name)
			
			#todo need to use recurring above
			#calculations for General extend date	
			if due_day_ < self.ext_date:
				sum+=float(i.balance)
				
			#calculations for slider extend date
			if due_day_ < self.slide_date:
				sum_slide+=float(i.balance)
				
		#now add deposits
		#todo: need to calculate and check against recurring bank deposits beyond their init deposit date
		# Extend update
		if self.ext_date > dep1_date:
			sum-= float(self.acc_list[1].bank_balance)
		if self.ext_date > dep2_date:
			sum-=			float(self.acc_list[2].bank_balance)
		# Slider update	
		if self.slide_date > dep1_date:
			sum_slide-= float(self.acc_list[1].bank_balance)
		if self.slide_date > dep2_date:
			sum_slide-= float(self.acc_list[2].bank_balance)
			
			# example of how to store mulitple data in a single csv cell and then extract it (painstakenly); date somehow has extra quotes so ([][2:-2]) needed
			
#			l=(2450.00,'2018,6,7') # dep,date tuple
#			s=str(l)					# csv turns to str()
#			t=s.split(",",1)	#aftr read turn back to tuple, stop after 1 x ','
#			float(t[0][1:])			#dep back to float
#			time=datetime.strptime(t[1][2:-2],'%Y,%m,%d') #date tuple back to datetime
		
		# update balance GUIs
		self.b_ext_balance.text= str(round((float(self.b_real_balance.text)-sum),2))
		
		self.b_slide_balance.text= str(round((float(self.b_real_balance.text)-sum_slide),2))
		self.slide_label.text=str(self.slide_date)[:10]
		
	def will_close(self):
		''' Called when app is closed via the 'X' left-button only. 
		'''
		write_acc_list(self.acc_list)
		
########### CSV DB Functions ##############
###########################################	
# When adding new column need to write before reading (because the coulumn is not there yet, and read is first operation and will fail). All data can be overwritten so make copies, git, or dropbox csv prior. 
# 1. add new column to 'fields'
# 2. add new column to write()
# 3. add new column to account class as needed, incl initialization
# 4. run program once, exit, and 
# 5. verify csv has new column and all old and new data
# 6. finally, add new column to read()
# todo: self detect new column?
fields= ['idx','name','balance','due_day','repeat','bank_bal','bank_date']

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
			#new
			dep_date_val=row['bank_date'] )
			acc_list.append(ac)
	return acc_list

def write_acc_list(acc_list):
	with open('moniest.csv', 'w') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=fields)
		writer.writeheader()
		for i in range(len(acc_list)):
			writer.writerow ({ 'idx':i , 'name':acc_list[i].name , 'balance':acc_list[i].balance, 'due_day': acc_list[i].due_day, 'repeat':acc_list[i].repeat, 'bank_bal':acc_list[i].bank_balance,
			'bank_date':acc_list[i].bank_date })
			
########### Button Actions ##################
#############################################

# Application buttons {Done,Cancel,Save} have a quirk (bug): they do not have a superview. therefore a global trigger is polled elsewhere. 'Save' required access to account list acc_list so a 'self' method was used
def done_button(sender):
	global done_pushed
	done_pushed=True
	
def cancel_button(sender):
	global cancel_pushed
	cancel_pushed=True
	
def add_account_tapped(sender):
	add=sender
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

	adda.next_y_pos+=50
	
def ext_date_tapped(sender):
	s=sender
	#returns set{0,2}
	sv=sender.superview
	idx=s.selected_index
	sleep(0.5)
	
	today_date=datetime.today()

	sv.ext_date=today_date + (idx+1)*timedelta(days=10)
	sv.set_needs_display()
		
def slider_changed(sender):
	s=sender
	sv=sender.superview
	idx=sender.value
	
	today_date=datetime.today()
	
	sv.slide_date=today_date + (idx)*timedelta(days=90)
	sv.set_needs_display()
	
def main():	
	console.clear()
	view=moniest()
	view.present('sheet')

if __name__=='__main__':
	main()
