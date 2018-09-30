# moniest
Pythonista Financial App
# **WHAT THE F$!?&@**
Quite simply it’s a running total of how much cash you have in the bank now, upcoming, and any point in time in the future.

# **ASSUMPTIONS **
   - All bills are paid on time (due date)
   - All bills will be paid in full 
   - Even bills with zero balance to be included in various reports 
   - Diligent spending entry is not expected, casual updates to balances only needed

# **BALANCES**
These are the three balances 

**Real**
>Actual Bank balance 
> - Can be a rough estimation 
> - Updateable whenever to match online balance 

**Theoretical Extended**
>Bank Balance minus all bills 
> - Variable 1-3 months advance bills 
> - Good for quick glance of upcoming bills

**Sliding**
>Bank Balance minus bills (Paid or Due) prior to sliding date
> - Theoretical net value on slider date 
> - Slider will show date
> -  All balances shown if possible 
> - Income added to bank balance prior to slide date


# **REMINDERS**
- All bills alert at bill issuing date 
- All bills alert 7 business days prior to Due Date
- Reminders have no effect on balace, just that the bill is due
- Reminder can be anything from the category 
Bills

# **BILLS**
## *Bills Categories:*
   - Government medical or tax payment
   - Car/Life/Medical/House/etc Insurance
   - Mortgae/Loan/Tax/etc payment 
   - Credit Cards
   - Gas/Electric/Phone/Water/cable/Internet/etc
   - Editable/Create/destroy

## *Bills Types*

### One Time
- A Bill for a service rendered

### Recurring
- Most Bills will be of this type by default 
- Including credit cards with zero balance 

## *Bill Status*

### *Paid*
   - Actual transfer of funds from bank (or any other financial account)

### *Due*
   - Bill has been issued from organization
   - Bill due date (for running/instant total)

# Account Class

**Title**        | **Description**
------------ | -------------
Name            |  String
Balance        |  float
Ext Bal 1.       |  float 
Ext Bal 2.      |  float
Due date.     |  datetime.date
Save data     |  class method (create/edit csv)
Retrv data    |  class method (read csv)
Retrv bal      |  class method
Retrv ext bal      |  class method
Retrv sld bal      |  class method
