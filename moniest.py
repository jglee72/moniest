# coding: utf-8
# 
#todo: due date intervals other than monthly
#todo: 'delete' account or 'cancel out'
#todo: accounts that won't be paid off;
# how to indicate paymet plan within balance

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
bi_weekly=15
bi_monthly=60
monthly=30
yearly=365

########### Class Definitions ############
##########################################
class account (object):
	'''Class for handling data for each account
	Currently all data is handled directly -i.e. there is no class modules to handle data security at the moment. 
	'''
	def __init__(self,idx_val=None,name_val='',bal_val='0.0',due_day_val= datetime.strftime(datetime.today(),'%Y,%m,%d'),repeat_val=True,dep_val=0.0, dep_date_val= datetime.today(), paid_val=False,cycle_val=monthly):
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
	
	# Delegate functions within class definition.  Generic names need checks as they are called by any associated (i.e. textfield) ui object	
	@ui.in_background
	def repeat_changed(self,sender):
		acc_list= sender.superview.superview.acc_list
		sv=sender.superview
		#save recur enable/disable
		acc_list[self.idx].repeat=sender.value
		#get cycle value for default
		cycle = acc_list[self.idx].cycle
		
		if (sender.value):
			field1={'type':'number','key':'balance','title':'Current Bill Amount:  ','value':'{:0.2f}'.format(float(acc_list[self.idx].balance))}
			field2={'type':'switch','key':'bi_weekly','title':'Bi Weekly','value':True if float(cycle) == bi_weekly else False}
			
			field3={'type':'switch','key':'bi_monthly','title':'Bi-Monthly',
			'value':True if float(cycle) == bi_monthly else False}
			field4={'type':'switch','key':'monthly','title':'Monthly','value':True if float(cycle) == monthly else False}
			field5={'type':'switch','key':'yearly','title':'Yearly','value':True if float(cycle) == yearly else False}
			
			t1=[field1]
			t2=[field2,field3,field4,field5]
			s1='Withdrawl Amount',t1
			s2='Cycle',t2
		
			sect=(s1,s2)
			answer=dialogs.form_dialog(title='Recurring accounts', sections=sect, done_button_title='Finished')
			
			d_balance=answer['balance']
			d_weekly=answer['bi_weekly']
			d_bi_monthly=answer['bi_monthly']
			d_monthly=answer['monthly']
			d_yearly=answer['yearly']
			
			if (d_weekly):
				acc_list[self.idx].cycle=bi_weekly
			if  (d_monthly):
				acc_list[self.idx].cycle=monthly
			if  (d_bi_monthly):
				acc_list[self.idx].cycle=bi_monthly
			if  (d_yearly):
				acc_list[self.idx].cycle=yearly
			
			acc_list[self.idx].balance=d_balance
			self.bal_field.text=d_balance
	
	def textfield_did_end_editing(self, textfield):
		global done_pushed
		done_pushed=True
		if(textfield.placeholder=='Balance'):
			textfield.text_color='black'
			textfield.superview.superview.acc_list[self.idx].balance=float(textfield.text)
			textfield.superview.superview.acc_list[self.idx].paid=False
			
			# limit to, or add, 2 decimal places as needed
			textfield.text='{:.2f}'.format(float(textfield.text))
		
		elif(textfield.placeholder=='Account'):
			textfield.superview.superview.acc_list[self.idx].name=textfield.text
		
	@ui.in_background	
	def textfield_did_begin_editing (self, textfield):
		old_text=textfield.text
		global cancel_pushed
		global done_pushed
		# clear done from previous end editing
		done_pushed= False
		while (not(done_pushed) and not(cancel_pushed)):
			sleep(0.5)
		#'Cancel' was pushed
		if cancel_pushed==True:
			cancel_pushed=False
			textfield.end_editing()
			#temp data needs to be redrawn
			textfield.text=old_text

		#'Done' was pushed
		else:
			done_pushed = False
			textfield.end_editing()

	# Paid button will grey current bal: use when bill is actually setup or is paid in real life so we can ignore for now.
	#is it worth doing acount updates?
	def paid_button(self,sender):
		sv=sender.superview.superview
		if sv.acc_list[self.idx].paid == True: 		
			sv.acc_list[self.idx].paid=False
			self.bal_field.text_color='black'
		else:
			sv.acc_list[self.idx].paid=True
			self.bal_field.text_color='grey'
	
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
		
		self.bal_field= ui.TextField(frame=self.frame_location+(self.frame_wh),bg_color=(.36, .54, .67), font=('Rockwell',17), text_color= 'grey' if acc.paid == 'True' else 'black', border_color='black', placeholder='Balance',text='{:.2f}'.format(float(acc.balance)),border_width=2, border_radius=20,alignment=ui.ALIGN_LEFT,alpha=0.5,selected=(True),editable=True,keyboard_type=ui.KEYBOARD_NUMBERS,delegate=self)

		self.frame_location = (self.frame_location[0]+self.frame_gw-5,frame_loc[1]-15)
		
		self.due_button = ui.Button(title=(acc.due_day[:10]), font=('AmericanTypewriter',17),action=self.due_button_tapped)
		self.due_button.frame = self.frame_location+(self.frame_wh)
		
		self.switch= ui.Switch(frame= (self.frame_location[0],(self.frame_location[1]+30),51,31),action=self.repeat_changed,border_width=0, border_radius=15, value= True if acc.repeat=='True' else False, bg_color='#c1c1c1',delegate=self)
		
		self.paid_button = ui.Button(frame=(self.frame_location[0]+60,(self.frame_location[1]+30),70,31), title='$$', action=self.paid_button, border_color='black',border_width=2)
		
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
			field1={'type':'number','key':'balance','title':'Current Balance:  ','tint_color':'#346511','value':'{:.2f}'.format(float(textfield.text))}
			field2={'type':'number','key':'deposit1','title':'Deposit Amount:  ','value':'{:.2f}'.format( float(self.acc_list[1].bank_balance))}
			field3={'type':'date','key':'dep1_date','title':'Deposit Date:  ','tint_color':'#000000',
			'value':(datetime.strptime(self.acc_list[1].bank_date,'%Y,%m,%d'))}
			field4={'type':'number','key':'deposit2','title':'Deposit Amount:  ','value':'{:.2f}'.format(float(self.acc_list[2].bank_balance))}
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
			self.sv.add_subview (self.acc_fld.paid_button)
	def save_button_(self,sender):
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
		self.date_slider= ui.Slider(frame=(10,500,350,10),action=slider_changed, continuous=False)
		self.add_subview(self.date_slider)
		
		# Bank balances
		# todo: should this be a class of 'accounts'
		self.b_real_balance = ui.TextField(frame=(10,530,110,45), placeholder = 'Bank Bal' , text='{:.2f}'.format(float(self.acc_list[0].bank_balance)) , keyboard_type=ui.KEYBOARD_NUMBERS , border_width=0,border_radius=5 , bordered=True, delegate=self)

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
#		print('+++++++++++++++++++++++++++++++')
		self.b_real_balance.text= '{:.2f}'.format(float(self.acc_list[0].bank_balance))
		#reset summations for date calcs
		sum=sum_slide=0.0	
		
		t_day= datetime.today().day
		t_mo= datetime.today().month
		t_yr= datetime.today().year
		# date conversions for deposit date math
		dep1_date = datetime.strptime(self.acc_list[1].bank_date,'%Y,%m,%d')
		dep2_date = datetime.strptime(self.acc_list[2].bank_date,'%Y,%m,%d')
		
		today = datetime.today()
		
		for i in (self.acc_list):
			#string conversion to datetime.datetime 
			# Inial due day for future due dates 
			due_day_0= datetime.strptime(i.due_day,'%Y,%m,%d')

			due_day_1 = due_day_0
			
			# test for recurring bill enabled
			recur = i.repeat
			# get cycle info from account
			cycle = int(i.cycle)

			if (recur=='True'):
				# first case: today is less than bill 
				# due day - ie normal
				if (today < due_day_0):
					due_day_1 = due_day_0

				#today is greater; how much
				else:
					days_delta = (today-due_day_0)

					# Every 30 days is beyond next cycle
					cycle_cnt = (days_delta.days //cycle) + 1
					due_day_1 = due_day_0 + timedelta(days= cycle_cnt * cycle)
			
				# Need advance dates for accounts based on cycle settings
				#todo: can this be a method
				due_day_2= due_day_1 + timedelta(days=cycle)
				due_day_3= due_day_2 + timedelta(days=cycle)
				due_day_4= due_day_3 + timedelta(days=cycle)
				if (cycle == bi_weekly):
					due_day_5 = due_day_4 + timedelta(days=cycle)
					due_day_6 = due_day_5 + timedelta(days=cycle)
			#todo: only process if ext_date changes
			# Extend update
			ii=0
			if self.ext_date > due_day_1:
				ii+=1
				if self.ext_date > due_day_2:
					ii+=1
					if self.ext_date > due_day_3:
						ii+=1
						if self.ext_date > due_day_4:
							ii+=1
			sum+= ii * (float(i.balance))
#			if ii: print('ext',i.name,ii)
			
			ii=0
			if self.slide_date > due_day_1:
				ii+=1
				if self.slide_date > due_day_2:
					ii+=1
					if self.slide_date > due_day_3:
						ii+=1
						if self.slide_date > due_day_4:
							ii+=1
							if (cycle == bi_weekly):
								if self.slide_date > due_day_5:
									ii+=1
									if self.slide_date > due_day_6:
										ii+=1
			sum_slide+= ii * (float(i.balance))
#			if ii: print('slide',i.name,ii)
				
		###########now add deposits##############
		# deduce first valid deposit day using datetime.day math and extrapolation
		delta = dep1_date.day-datetime.today().day
		
		if delta > 0:
			dep1_date = datetime.today() + timedelta(days=abs(delta))
			dep2_date = dep1_date + timedelta(days=15)
		else:
			dep1_date = datetime.today() - timedelta(days=abs(delta)) + timedelta(days=30) 
			dep2_date = dep1_date - timedelta(days=15)
		
		#future date calculations:
		dep1_30= dep1_date + timedelta(days=30)
		dep1_60= dep1_date + timedelta(days=60)
		dep1_90= dep1_date + timedelta(days=90)
		dep2_30= dep2_date + timedelta(days=30)
		dep2_60= dep2_date + timedelta(days=60)
		dep2_90= dep2_date + timedelta(days=90)
		
		# Extend update
		ii=0
		if self.ext_date > dep1_date:
			ii+=1
			if self.ext_date > dep1_30:
				ii+=1
				if self.ext_date > dep1_60:
					ii+=1
					if self.ext_date > dep1_90:
						ii+=1
		sum-= ii * (float(self.acc_list[1].bank_balance))
#		if ii: print('ext_dep1',ii)
			
		ii=0
		if self.ext_date > dep2_date:
			ii+=1
			if self.ext_date > dep2_30:
				ii+=1
				if self.ext_date > dep2_60:
					ii+=1
					if self.ext_date > dep2_90:
						ii+=1
		sum-= ii * (float(self.acc_list[2].bank_balance))
#		if ii: print('ext_dep2',ii)
			
		# slide update
		ii=0
		if self.slide_date > dep1_date:
			ii+=1
			if self.slide_date > dep1_30:
				ii+=1
				if self.slide_date > dep1_60:
					ii+=1
					if self.slide_date > dep1_90:
						ii+=1
		sum_slide-= ii * (float(self.acc_list[1].bank_balance))
#		if ii: print('slide_dep1',ii)			
		
		ii=0
		if self.slide_date > dep2_date:
			ii+=1
			if self.slide_date > dep2_30:
				ii+=1
				if self.slide_date > dep2_60:
					ii+=1
					if self.slide_date > dep2_90:
						ii+=1
		sum_slide-= ii * (float(self.acc_list[2].bank_balance))
#		if ii: print('slide_dep2',ii)			
		
			# example of how to store mulitple data in a single csv cell and then extract it (painstakenly); date somehow has extra quotes so ([][2:-2]) needed
			
#			l=(2450.00,'2018,6,7') # dep,date tuple
#			s=str(l)					# csv turns to str()
#			t=s.split(",",1)	#aftr read turn back to tuple, stop after 1 x ','
#			float(t[0][1:])			#dep back to float
#			time=datetime.strptime(t[1][2:-2],'%Y,%m,%d') #date tuple back to datetime
		
		# update balance GUIs
		self.b_ext_balance.text= '{:.2f}'.format(float(self.b_real_balance.text)-sum)
		
		self.b_slide_balance.text= '{:.2f}'.format(float(self.b_real_balance.text)-sum_slide)
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
			
########### Button Actions ##################
#############################################

# Application buttons {Done,Cancel,Save} have a quirk (bug): they do not have a superview. therefore a global trigger is polled elsewhere. 'Save' required access to account list acc_list so a 'self' method was used
def done_button(sender):
	global done_pushed
	done_pushed=True
	
def cancel_button(sender):
	global cancel_pushed
	cancel_pushed=True
	
# Other button actions
	
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
	adda.sv.add_subview (acc_fld.switch)
	adda.sv.add_subview (acc_fld.paid_button)

	adda.next_y_pos+=50
	
def ext_date_tapped(sender):
	s=sender
	sv=sender.superview
	#returns set{0,2}
	idx=s.selected_index
	
	today_date=datetime.today()

	sv.ext_date=today_date + (idx+1)*timedelta(days=10)
	sv.set_needs_display()
		
def slider_changed(sender):
	''' Continuous mode had to be false to aleviate pythonista dropping out. 
	'''
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
