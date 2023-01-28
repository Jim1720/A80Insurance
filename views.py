 
from collections import defaultdict
from decimal import DefaultContext
from errno import ENOTEMPTY
import json
from operator import truediv
from urllib.response import addclosehook
from django.shortcuts import redirect, render
# regular expressions
import re 
# environment promotion code
import os

from datetime import datetime 

# Create your views here.

from django.http import HttpResponse
import requests


def hello(request):
    return HttpResponse("Hello, world. You're at the A80Insurance hello.")

 
from django.shortcuts import render 

from django.http import   HttpResponseRedirect

from django.urls import reverse  

from .models import Adm, Customer, Signin, Claim, Plan, Service

def setup(request):

    request.session["AdjustClaimId"] = ""
    request.session['CopyClaimId'] = ""
    request.session["NewClaimNumber"] = ""
    request.session["ClaimNumber"] = ""
    request.session["HistoryAction"] = ""

def index(request):  
    start(request)


def start(request):  
    request.session['signIn'] = "No" 
    setup(request)
    now = datetime.now() # current date and time
    timetobuy = now.strftime("%A %B %d %Y %H:%M %p")   
    # 

    request.session['entry1'] = ""
    request.session['entry2'] = ""
    return render(request, "A80Insurance/start.html", { 'timetobuy': timetobuy}) 
        

def classic(request):  
    return render(request, "A80Insurance/classic.html") 


def about(request):  
    return render(request, "A80Insurance/about.html") 


def register(request):     
    noErrorsAreFound = ""

    if request.method == "GET":    
       request.session['regPassword'] = ""  # for password edits
       request.session['signIn'] = "No"
       message = "Enter Customer Information"
       customer = Customer()
       return render(request, "A80Insurance/register.html",
              { 'message': message, 'customer': customer })  

    if request.method == "POST": 
       editMessage = RegisterEdits(request)
       if editMessage == noErrorsAreFound:
           output = AddCustomer(request)
           customer = output['customer']
           message = output['message']
           result = output['result']
           # TODO: add None check 
           if result != "good": 
              message = message
              screenCustomer = BuildScreen(request) 
              return render(request, "A80Insurance/register.html", 
                   { 'message': message , 'customer': screenCustomer })   
           #
           message = "Successful registration for customer"
           request.session['menuMessage'] = message
           request.session['signIn'] = "Yes"
           DispCustOnMainTop(request, customer)
           return render(request, "A80Insurance/menu.html")
       else:
         message = editMessage  
         screenCustomer = BuildScreen(request) 
         return render(request, "A80Insurance/register.html", 
             { 'message': message , 'customer': screenCustomer })   

def signin(request):   

    noErrorsAreFound = ""

    if request.method == "GET":   
       request.session['signIn'] = "No"
       signin = Signin()
       message = "Enter Signin Information" 
       return render(request, "A80Insurance/signin.html",
              { 'message': message, 'signin': signin })  

    if request.method == "POST": 
       editMessage = SigninEdits(request)
       #if editMessage == "Invalid Password.":
       #   message = "Warning: Invalid Password (dev bypass)."
       #   request.session['signIn'] = "Yes" 
       #   return render(request, "A80Insurance/menu.html", { 'message': message})
       # end of this if.
       if editMessage == "DupWarning":
          message = "Warning: duplicates found. Using first one (dev bypass)."
          request.session['signIn'] = "Yes" 
          return render(request, "A80Insurance/menu.html", { 'message': message})
       # end of this if.
       if editMessage == noErrorsAreFound: 
           message = "Successful signin for Customer"
           # set sign in status 
           # ref: http://www.learningaboutelectronics.com/Articles/How-to-create-a-session-variable-in-Django.php

           request.session['signIn'] = "Yes" 
           return render(request, "A80Insurance/menu.html", { 'message': message})
       else:
         message = editMessage   
         signin = Signin()
         return render(request, "A80Insurance/signin.html", 
             { 'message': message, 'singin': signin })    

def NotSignedIn(request):
    signIn = request.session['signIn'] 
    if signIn != "Yes":
        return True
    else:
        return False


def AdmNotSignedIn(request):

    try:

       admSignIn = request.session['admSignin'] 
       if admSignIn != "Yes":
           return True
       else:
          return True

    except:

       return False


def notauthorized(request):
    return render(request, "A80Insurance/notauthorized.html")
   
def update(request):     
    noErrorsAreFound = ""

    if request.method == "GET":   
 
       # check for valid url must be signed in.
       if NotSignedIn(request) == True:
          return render(request, "A80Insurance/notauthorized.html")
        
       message = "Enter Customer Update Information"
       custId = request.session['custId']
 

    
       urlPrefix = os.environ['A80UrlPrefix']
       apiSelect = "/cust?id=" + custId  
       apiString = urlPrefix + apiSelect
       response = requests.request("GET",apiString)
       response.encoding = "UTF-8" 

       if response == None:
           message = f". Can not read customer {custId}." 
           request.session['menuMessage'] = message
           return render(request, "A80Insurance/menu.html")

       if response.status_code != 200:
          message = f"2. customer not read status is: {response.status_code}" 
          return message
     

       j = response.json()
       status = j['Status']
       message = j['Message']
       cust = j['Customer'] 
 

         # not found and bad password will return message and Unsuccessful.
       if status == "Unsuccessful": 
           message = f"3. siginin fails: {message}"
           return message 
 
     
       
       customer = BuildCustomerFromDict(cust) 
       request.session['regPassword'] = customer.password # for password edits
       request.session['uplan'] = customer.plan # not on screen input so keep it if edits occur

       message = "Enter customer update information."
       
      # custQuerySet = Customer.objects.filter(customer_id=custId)   
      # found = False
      # for custObject in custQuerySet: 
       #   found = True
       #   customer = BuildCustomerFromObject(custObject) 
       #   request.session['regPassword'] = customer.password # for password edits
          # not on screen
          #  pull when edit occurs
          #  pull in final update step.
       #   request.session['uplan'] = customer.plan # not on screen input so keep it if edits occur

     
 
       return render(request, "A80Insurance/update.html",
              { 'message': message, 'customer': customer })  

    if request.method == "POST":  
       editMessage = UpdateEdits(request)
       if editMessage == noErrorsAreFound: 
           UpdateCustomer(request)
           message = "Successful update for customer" 
           request.session['menuMessage'] = message
           return render(request, "A80Insurance/menu.html")
       else:
         message = editMessage   
         customer = BuildCustomer(request)
         return render(request, "A80Insurance/update.html", 
             { 'message': message, 'customer': customer })
              

def menu(request):   

    # check for valid url must be signed in.
    if NotSignedIn(request) == True:
        return render(request, "A80Insurance/notauthorized.html") 

    message = request.session['menuMessage'] 
    request.session['menuMessage'] = ""
    return render(request, "A80Insurance/menu.html", {'message': message })

def info(request):  
    return render(request, "A80Insurance/info.html") 


def plan(request):   

    if request.method == "GET":
 

       # check for valid url must be signed in.
       if NotSignedIn(request) == True:
          return render(request, "A80Insurance/notauthorized.html") 
       
       urlPrefix = os.environ['A80UrlPrefix']
       apiSelect = "/readPlans"    
       url = urlPrefix + apiSelect
       response = requests.get(url)
       response.encoding = "UTF-8" 

       if response == None:
           message = f". Can not read plans." 
           request.session['menuMessage'] = message
           return render(request, "A80Insurance/menu.html")

       if response.status_code != 200:
          message = f"2. plans not read status is: {response.status_code}"  
          request.session['menuMessage'] = message
          return render(request, "A80Insurance/menu.html") 

       j = response.json()  

       screenData = []
       for planRow in j:
           # plug literal and name into a array of objects  
           # dictionary of database names.
           planname = planRow.get("PlanName").strip()
           lit = planRow.get("PlanLiteral").strip()  
           planData = { 'name' : planname, 'literal' : lit } 
           # add to screen array
           screenData.append(planData) 
       # end of loop
       return render(request, "A80Insurance/plan.html", { 'screenData' : screenData } ) 

    if request.method == "POST":

        selectedPlanName = request.POST['commit'] 
        custId = request.session['custId'] 
        plan = selectedPlanName.strip() 
        token = request.session['A45Token'] 

        urlPrefix = os.environ['A80UrlPrefix']
        apiSelect = "/updatePlan" 
        apiString = urlPrefix + apiSelect  

        updatePlanDictioinary = { 

            "CustId" : custId,
            "CustPlan" : plan,
            "_csrf" : token
        }
         
 
        response = requests.put(apiString, data=updatePlanDictioinary)
        response.encoding = "UTF-8"  
 
        status = response.status_code
        if status == 200: 
           message = "Customer Plan Updated Successfully"
        else:
           message = "Plan update error."
        #
        return render(request, "A80Insurance/menu.html", { 'message' : message})

def FormatBack(input):

    # date comes in as 2022-01-01 must be changed to 20220101 for successful
    # update in the stored procedure. 
    newDate  = input[0:4] + input[5:7] + input[8:] 
    return newDate


def GetDropDownData(claimType): 

       #get('/readPlans')
    
       urlPrefix = os.environ['A80UrlPrefix']
       apiSelect = "/readServices"    
       url = urlPrefix + apiSelect
       response = requests.get(url)
       response.encoding = "UTF-8" 

       if response == None:
           message = f". Can not read services."   
           print (message)

       if response.status_code != 200:
          message = f"2. services not read status is: {response.status_code}" 
          print (message)  
        
       
       j = response.json() 
 

       services = [] 
       #serviceObjects = Service.objects.filter(claimType=claimType)
       for service in j: 
           dbClaimType = service['ClaimType'].strip()
           if dbClaimType == claimType:
              str_serviceName = f"{ service['ServiceName'] }" 
              serviceName = str_serviceName.strip() 
              services.append(serviceName)
       #
       return services
       #

def GetClaimLiteral(claimType):
    literal = "setup"
    match claimType:
        case 'm' : literal = "Medical"
        case 'd' : literal = "Dental"
        case 'v' : literal = "Vision"
        case 'x' : literal = "Drug"
        case _ : literal = "Unknown"

    return literal

def GetClaimType(claimLiteral):
    match claimLiteral:
        case 'Medical' : literal = "m"
        case 'Dental' : literal = "d"
        case 'Vision' : literal = "v"
        case 'Drug' : literal = "x"
        case _ : literal = "u"

    return literal

def SetupScreenForNewType(request, typeLiteral): 
    currentClaimType = GetClaimType(typeLiteral) 
    message = f"Building a {typeLiteral} claim."
    claim = BuildClaim(request, "build")  
    services = GetDropDownData(currentClaimType) 
    serviceLiteral = GetClaimLiteral(currentClaimType)  
    request.session['ClaimType'] = currentClaimType
    return render(request, "A80Insurance/claim.html", 
            { 'message': message , 'claim': claim , 'services' : services,
            'serviceLiteral' : serviceLiteral })    

def claim(request):  
 

     if request.method == "GET": 
 
        if NotSignedIn(request) == True:
          return render(request, "A80Insurance/notauthorized.html") 

        message  = "" 
        #
        # build blank claim for claim entry
        # when no history action used.
        #
        claim = Claim()  
        #
        defaultClaimType = "m"   
        request.session["ClaimType"] = defaultClaimType
        services = GetDropDownData(defaultClaimType) 
        serviceLiteral = GetClaimLiteral(defaultClaimType)
        # set hidden field changed by type buttons and used for POST processing.
        request.session["ClaimType"] = defaultClaimType
        # avoid key error when not entered.
        claim.date_confine = ""
        claim.date_release = ""
        return render(request, "A80Insurance/claim.html", 
              { 'claim' : claim , 'services' : services, 'serviceLiteral' : serviceLiteral } ) 


     if request.method == "POST": 

        # check Adjust Copy request session values to
        # use predefined claimidentification number
        # and for adjustments set the adjusted,adjustment claim ids and adjustment date
        # plus logic to stamp adjusted claim. 

        # change claim type
        changeClaimType = request.POST['commit']
        if changeClaimType == "Medical" or changeClaimType == "Dental" or \
           changeClaimType == "Vision"  or changeClaimType == "Drug":
           # change dropdown, literal and show claim form with new type services listed.
           typeLiteral = changeClaimType 
           currentClaimType = GetClaimType(typeLiteral) 
           message = f"Building a {typeLiteral} claim."
           claim = BuildClaim(request, "build")  
           services = GetDropDownData(currentClaimType) 
           serviceLiteral = GetClaimLiteral(currentClaimType)  
           request.session['ClaimType'] = currentClaimType 
           return render(request, "A80Insurance/claim.html", 
            { 'message': message , 'claim': claim , 'services' : services,
            'serviceLiteral' : serviceLiteral })    

       
        # customer going to plan screen ...
        assignPlan = request.POST['commit']
        assignPlanRequest = "Assign Plan"
        #
        # go to plan screen
        #
        if assignPlan == assignPlanRequest:    
           return redirect('/plan')
          # end of plan button logic.

        #  
        # Process the claim add screen.
        #
        submitButtonAddClaimValue = "Add Claim"
        addClaimProcess = request.POST['commit']
        if addClaimProcess != submitButtonAddClaimValue: 
           return
         
        noErrorsAreFound = ""
        editMessage = ClaimEdits(request)
        if editMessage == noErrorsAreFound:
           resultObject = AddClaim(request)    
           if resultObject['status'] == "good":
              message = "Claim added successfully"
              message = resultObject['message']
              return render(request, "A80Insurance/menu.html", { 'message' : message})
           else:
              message = f"Claim Add error {editMessage}"
              return render(request, "A80Insurance/menu.html", { 'message' : message})
        else:
           message = editMessage  
           claim = BuildClaim(request, "edit")
           planNeeded = "assign a plan"
           showPlanButton = "No"
           if planNeeded in editMessage:
              showPlanButton = "Yes"
           # initial claim and type changs: post claim type in hidden
           # field so we can process that type of claim.
           currentClaimType = request.session["ClaimType"]  
           services = GetDropDownData(currentClaimType) 
           serviceLiteral = GetClaimLiteral(currentClaimType)
           selectedService = claim.service 
           return render(request, "A80Insurance/claim.html", 
                 { 'message': message , 'claim': claim , 'showPlanButton' : showPlanButton,
                   'services' : services,
                   'serviceLiteral' : serviceLiteral,
                   'selectedService' : selectedService })   

def FormatFromDBtoScreen(date):
    # 2011-01-01 
    value = str(date)
    work = value[0:11]
    m = work[5:7]
    d = work[8:]
    y = work[0:4]
    s = "/"
    result  = m + s + d + s +  y  
    if y == "1753":
       result = ""
    if y == "1900":
        result = ""
    # 
    return result


def history(request):  

    if request.method == "GET": 

        
       # check for valid url must be signed in.
       if NotSignedIn(request) == True:
          return render(request, "A80Insurance/notauthorized.html")

       # set up action buttons.
       #
       # use unused field payment_action 
       #
       none = "none"
       comma = ","
       showAct1 = ""
       showAct2 = ""
       claim1 = ""
       claim2 = ""
       act1 = ""
       act2 = ""
       showAct1 = ""
       showAct2 = "" 
       info1 = pullRecord(request, 0)
       if info1 != none:
            commaPosition = info1.find(comma)
            endActionStringPosition = commaPosition
            startClaimNumberPosition = commaPosition + 1 
            showAct1 = "Yes"
            act1 = info1[:endActionStringPosition] 
            claim1  = info1[startClaimNumberPosition:]   
       #
       info2 = pullRecord(request, 1)
       if info2 != none:
            commaPosition = info2.find(comma)
            endActionStringPosition = commaPosition 
            startClaimNumberPosition = commaPosition + 1 
            showAct2 = "Yes"
            act2 = info2[:endActionStringPosition]
            claim2  = info2[startClaimNumberPosition:]  
        # end action button setup logic. 
       
       custId = request.session['custId']
       # read claims into queryset
       #claimsQuerySet = Claim.objects.filter(customer_id=custId).values()

            
       urlPrefix = os.environ['A80UrlPrefix']
       apiSelect = "/history?id=" + custId
       apiString = urlPrefix + apiSelect 
       response = requests.request("GET",apiString)
       response.encoding = "UTF-8" 

       if response == None:
            message = "1. customer not found , response none."
            print (message)

       if response.status_code != 200:
            message = f"2. claim history not found status is: {response.status_code}" 
            print (message)
 
       claimHistory = response.json()

       claimsData = [] 
       count = 0
       # Procedure3 act1 act2
       # PaymentAction top mid bottom
    
       n = len(claimHistory) # dictionary length.
       mid = (n - (n % 2)) / 2

       for claim in claimHistory:
              # insert claim data for display on history screen.  
              # change to claim object   
              # this claim item is a dictionary - iterate and strip blanks at right
              # sql format:  
              for key in claim: 
                 field = claim[key] 
                 field2 = str(field).rstrip() # get rid of trailing blanks. 
               # set up position tags use payment_action field to hold 'top' ...
               
              claim['Procedure3'] = ""
              claim['PaymentAction'] = "" 

              # writes tag at beginning of claims
              if count == 0:
                claim['PaymentAction'] = "top" 
              if count == mid:
                claim['PaymentAction'] = "mid"
              if count == n - 1:
                claim['PaymentAction'] = "bot"

              ci = claim['ClaimIdNumber'].rstrip()

                  # writes buttons
              if ci == claim1:
                claim['PaymentAction'] += "act1"
                
              if ci == claim2:
                claim['PaymentAction'] += "act2" 
 
              

              claim['DateService']    = FormatToScreen(claim['DateService'])
              claim['DateConfine']    = FormatToScreen(claim['DateConfine'])
              claim['DateRelease']    = FormatToScreen(claim['DateRelease'])
              claim['DateAdded']      = FormatToScreen(claim['DateAdded'])
              claim['AdjustedDate']   = FormatToScreen(claim['AdjustedDate']) 
              claim['PaymentDate']    = FormatToScreen(claim['PaymentDate'])
              
              # use Procedure3 for the seq number on the screen.
              claim['Procedure3'] = str(count  + 1)

              # remove trail blank
              claim['ClaimStatus'] = claim['ClaimStatus'].rstrip()
              
              # display field ....
              claim[key] = field2  
            
              claimsData.append(claim) 
              count = count + 1
       # end of loop
       
      
     
       message = f"{n} claims displayed"
       if n == 0:
          message = "no claims found"
       #  
       return render(request, "A80Insurance/history.html",
              { 'claimsData' : claimsData, 'message' : message,
                 'showAct1' : showAct1, 'act1' : act1, 'claim1' : claim1, 
                 'showAct2' : showAct2, 'act2' : act2, 'claim2' : claim2
               } ) 

    if request.method == "POST":

        selectedAction = request.POST['commit']
        
        # action can be : menu, claim, adjust..., or copy... 
        #
        adjustRequest = selectedAction.find("Adjust")
        copyRequest = selectedAction.find("Copy")
        payRequest = selectedAction.find("Pay")
        claimNumber = ""
        action = selectedAction
        found = 0
        #
        if adjustRequest == found: 
            action = "Adjust"
            claimNumber = selectedAction[6:]
            claimNumber = claimNumber.rstrip()
        if copyRequest == found:
            action = "Copy"
            claimNumber = selectedAction[4:]
            claimNumber = claimNumber.rstrip()
        if payRequest == found:
            action = "Pay"
            claimNumber = selectedAction[3:]
            claimNumber = claimNumber.rstrip()
        # 

        request.session['ClaimNumber'] = claimNumber
        request.session['HistoryAction'] = action
        # 
        match action:
           case "Menu": 
              message = ""
              return render(request, "A80Insurance/menu.html", { 'message' : message})

           case "Claim" : 
              claim = Claim()  
              message = "Enter a new claim"
              claimType = "m"
              services = GetDropDownData(claimType) 
              serviceLiteral = GetClaimLiteral(claimType) 
              request.session["ClaimType"] = claimType
              return render(request, "A80Insurance/claim.html", 
                  { 'claim' : claim , 'services' : services, 'serviceLiteral' : serviceLiteral,
                    'message' : message } ) 


           case "Adjust" :  
               
                rows = getClaim(claimNumber)
                claim = rows[0]
                if claim == None:
                   print("warning no claim found")

                newClaimId = GetClaimId() 
                claim['ClaimIdNumber'] = newClaimId
                request.session["NewClaimNumber"] = newClaimId
                message = f"Enter Adjustment Data for {newClaimId} adjustng {claimNumber}" 
                services = GetDropDownData(claim['ClaimType']) 
                serviceLiteral = GetClaimLiteral(claim['ClaimType']) 
                request.session["ClaimType"] = claim['ClaimType'] 
                 # remove spaces at right 
                for key in claim:
                       work = str(claim[key])
                       work = work.rstrip()
                       claim[key] = work
                 # claim is in database name format i.e. using database names must convert
                 # to claim object internal for display.
                claimObject = ClaimDBfieldsToObject(claim)

                 # hidden field already set to claim.ClaimType
                return render(request, "A80Insurance/claim.html", 
                  { 'claim' : claimObject , 'services' : services, 'serviceLiteral' : serviceLiteral,
                    'message' : message } ) 

           case "Copy" : 
               
                rows = getClaim(claimNumber)
                claim = rows[0]
                if claim == None:
                   print("warning no claim found")
                # get the new adjusted id
                newClaimId = GetClaimId() 
                claim['ClaimIdNumber']= newClaimId
                request.session["NewClaimNumber"] = newClaimId
                message = f"Enter Data for {newClaimId} copying {claimNumber}" 
                services = GetDropDownData(claim['ClaimType']) 
                serviceLiteral = GetClaimLiteral(claim['ClaimType']) 
                a = serviceLiteral 
                request.session["ClaimType"] = claim['ClaimType']
                # format dates from db to screen 
                # remove spaces at right
                for key in claim:
                       work = str(claim[key])
                       work = work.rstrip()
                       claim[key] = work

                # convert dictionary with db field names to claim object names
                claimObject = ClaimDBfieldsToObject(claim)

                return render(request, "A80Insurance/claim.html", 
                  { 'claim' : claimObject , 'services' : services, 'serviceLiteral' : serviceLiteral,
                    'message' : message } ) 

           case "Pay" :  
                message = ""
                return render(request, "A80Insurance/payclaim.html", 
                    { 'claimNumber' : claimNumber, 
                      'message' : message } ) 

           case _ : 
              message = "No button action"
              return render(request, "A80Insurance/claim.html", { 'message' : message})
        # end of case 

def ClaimDBfieldsToObject(d):

    c = Claim()
    c.claim_id = d['ClaimIdNumber']
    c.first_name = d['PatientFirst']
    c.last_name = d['PatientLast']
    c.description = d['ClaimDescription']
    c.diagnosis1 = d['Diagnosis1']
    c.diagnosis2 = d['Diagnosis2']
    c.procedure1 = d['Procedure1']
    c.procedure2 = d['Procedure2']
    c.physican = d['Physician']
    c.clinic = d['Clinic']
    c.referral = d['Referral']
    c.location = d['Location']

    dateNotUsed = '010153' 
    c.date_service = FormatScreenDateFromDatabase(d['DateService']) 
    c.date_confine = FormatScreenDateFromDatabase(d['DateConfine'])

    if c.date_confine == dateNotUsed:
        c.date_confine = None

    c.date_release = FormatScreenDateFromDatabase(d['DateRelease'])
    if c.date_release == dateNotUsed:
        c.date_release = None

    c.tooth_number = d['ToothNumber']

    c.drug_name = d['DrugName']

    c.eye_ware = d['Eyeware']
    

    return c


def getClaim(claimIdNumber):

       urlPrefix = os.environ['A80UrlPrefix']
       apiSelect = "/claim?id=" + claimIdNumber 
       url = urlPrefix + apiSelect 
       response = requests.get(url)
       response.encoding = "UTF-8" 

       if response == None:
          print ('get claim resp none ')
          return None

       if response.status_code != 200:
          print (f'get claim status {response.status_code}')
          None

       claim = response.json() 
       return claim



def signout(request):  

    request.session['signIn'] = "No"
    request.session['custId'] = "" 
    setup(request)
    now = datetime.now() # current date and time
    timetobuy = now.strftime("%A %B %d %Y %H:%M %p")  

    return render(request, "A80Insurance/start.html", { 'timetobuy': timetobuy}) 
 
# ====================== Edits ================================
 
def RegisterEdits(request):

    # edit cust id here and emit msg if bad

    # call rest of editsf
    editMessage = CustomerEdits(request, "register")
    return editMessage

def UpdateEdits(request):

    # skip cust id edit here 
    # stow matching passwords or edit invalid syntax or mismatch pw = encrypted

    # call rest of edits
    editMessage = CustomerEdits(request, "update")
    return editMessage

def SigninEdits(request):
 
       
    message = ""
    
    custId = request.POST['custId']  
    custPassword = request.POST['custpassword']  

    if custId == "":
        message = "Please enter a Customer Id."
        return message 
    
    if custPassword == "":
        message = "Please enter Customer Password."
        return message 
 
    try:
       urlPrefix = os.environ['A80UrlPrefix']
    except:
    # env var not set ! first place to be checked. 
        message = "3. Alert: Please have the admin set the environment variables."
        return message 
     

    apiSelect = "/signin?id=" + custId + "&pw=" + custPassword
    apiString = urlPrefix + apiSelect
    response = requests.request("GET",apiString)
    response.encoding = "UTF-8" 

    if response == None:
        message = "1. customer not found"
        return message 
     

    j = response.json()
    status = j['Status']
    message = j['Message']
    cust = j['Customer']
    token = '45object stuff decodes' 
 
     
    # not found and bad password will return message and Unsuccessful.
    if status == "Unsuccessful": 
        message = f"3. siginin fails: {message}"
        return message
 
     
    tokenString = j['Token'] 
    a45object = json.loads(tokenString)   
    a45data = a45object.get('A45Object') 
    token = a45data.get('token') 
 
    request.session['A45Token'] = token
    request.session['custId'] = custId

    DispCustOnMainTopDict(request, cust) 
    
    goodResult = ""
    return goodResult 

def DispCustOnMainTop(request, cust):
    disp = cust.customer_id + " " + cust.first_name + " " + cust.last_name
    request.session["displaycustinfo"] = disp


def DispCustOnMainTopDict(request, cust):
    disp = cust.get('custId') + " " + cust.get('custFirst') + " " + cust.get('custLast')
    request.session["displaycustinfo"] = disp

def CustomerEdits(request, screen): 
    
    message = "" 

    # register screen when password and confirm match store them
    # in session so no rekeying necessary for other edit issues.

    # update screen similar logic: 
    # when password not keyed pull from existing customer password
    # when keyed , and match confirm, store them in session
    # subsequent no rekey pull from session

    # tremporary like date just accept any password for mow.
    
    # phone , email, gender, promo to be added later. 

    custId = request.POST['custId']  
    custpassword = request.POST['custpassword']
    custfirst = request.POST['custfirst']
    custlast = request.POST['custlast']
    custmiddle = request.POST['custmiddle']
    custbirthdate = request.POST['custbirthdate']
    custaddr1 = request.POST['custaddr1']
    custaddr2 = request.POST['custaddr2']
    custgender = request.POST['custgender']
    custphone = request.POST['custphone']
    custemail = request.POST['custemail']
    custcity = request.POST['custcity']
    custstate = request.POST['custstate']       
    custzip = request.POST['custzip'] 
    confirm = request.POST['encrypted'] # confirm password  

    onRegisterScreen = True if screen == "register" else False

    if custId == "" and onRegisterScreen == True: 
        message = "Please enter a Customer Id."
        return message 
 
     

    # note:
    # register screen must set request.session['regPassword'] = ''
    # update screen must set request.session['regPassword] = <customer password>
    # before these edits process the screen.

    # upate logic saves a password first, so missing password edit
    # is only used on register screen where the saved password is blank.

    noSavedPassword = True if request.session['regPassword'] == "" else False 
    passwordEntered = False if custpassword == "" else True  
 
     
    if screen == "register" and passwordEntered == False and noSavedPassword == True:
        message = "Please enter a Password."
        return message  

    standard = "^([0-9a-zA-Z\s])+$"
    standard_or_blank = "^([0-9a-zA-Z\s])*$"  
    emailpattern = "^([0-9a-zA-Z])+@([0-9a-zA-Z])+.([0-9a-zA-Z])+$" 
    phonepattern = "^([0-9]){10}$"
    zippattern = "^([0-9A-Z\s]){5,9}$"
    msg1 = " must be alphanumeric."
    msg2 = " must be alphanumeric or blank."  

    if passwordEntered == True:
 

        request.session['regPassword'] = ""
         
        if re.match(standard, custpassword) == None: 
           return "Password " + msg1 + "." + custpassword + "."  

        # pw appears after saving.
        if custpassword != confirm:
           message = "Confirm password does not match password."
           return message 
 

        request.session['regPassword'] = custpassword 
 

    # (dateMessage, flag, input , result)
    result = DateEdit(custbirthdate, "birth")  
    dateMessage = result[0]
    flag = result[1] 

    if flag == False:
        # soft edit return dateMessage 
        message = f"{dateMessage}"
        return message
 
 
    if onRegisterScreen == True:
       if  re.match(standard, custId) == None or custId.rstrip() == "":
        return "custId " + msg1 

    if re.match(standard, custfirst) == None or custfirst.rstrip() == "":
        return "First Name " + msg1 

    if re.match(standard_or_blank, custmiddle) == None:
        return "Middle Name " + msg2 
    
    if re.match(standard, custlast) == None or custlast.rstrip() == "":
        return "Last Name " + msg1 

    if re.match(standard, custaddr1) == None or custaddr1.rstrip() == "":
        return "Address 1 " + msg1  
    
    if re.match(standard_or_blank, custaddr2) == None:
        return "Address 2 " + msg2 

    if re.match(standard, custcity) == None or custcity.rstrip() == "":
        return "City " + msg1   
    
    if re.match(zippattern, custzip) == None or custzip .rstrip() == "":
        return "Zip Code " + msg1 + " and between five to nine characters."

    gen = custgender.upper()
    if gen != "M" and gen != "F":
        return "Invalid gender"

    state = custstate.upper()
    if state != "WA" and state != "CA":
        return "Invalid state"
 
    if onRegisterScreen == True:
        # put this in env variable 
       promo = request.POST['promotioncode']  
       environment_promotion_code = os.environ['A80PromotionCode']
       if promo != environment_promotion_code:   
          return message
 
    
    if re.match(emailpattern, custemail) == None or custemail.rstrip() == "":
        return "Invalid e-mail entered"

    if re.match(phonepattern, custphone) == None or custphone.rstrip() == "":
       return "Invalid Phone Number entered" 

    # customer duplicate check
    c = GetCustomer(request, custId)

    # avoid duplication use this session value...
    if request.session['customerFound'] == "Yes": 
       return "Duplicate Customer." 
      


    goodResult = ""
    return goodResult 

def ClaimEdits(request):
 
    
    
    service = request.POST["service"] 

    message = ""

    # refer to name = 'name'
    patientFirst = request.POST['first']  
    patientLast = request.POST['last']
    description = request.POST['desc']
    diagnosis1 = request.POST['diag1'] 
    diagnosis2 = request.POST['diag2']
    procedure1 = request.POST['proc1'] 
    procedure2 = request.POST['proc2']
    physician = request.POST['phys'] 
    clinic = request.POST['clinic'] 
    referral = request.POST['referral'] 
    location = request.POST['location'] 
    dateservice = request.POST['dateservice'] 
    # claim type kept in session variable
    
    # service id dropdown
    # dos needs to be coded 

    if patientFirst.rstrip() == "":
        message = "Please enter Patient First Name."
        return message 
    
    if patientLast.rstrip() == "":
        message = "Please enter Patient Last Name."
        return message 
    
    tooth_pattern = "^([0-9])+$"
    standard = "^([0-9a-zA-Z\s])+$"
    standard_or_blank = "^([0-9a-zA-Z\s])*$"
    msg1 = " must be alphanumeric."
    msg2 = " must be alphanumeric or blank."

    if  re.match(standard, patientFirst) == None:
        return "Patient First " + msg1 

    if  re.match(standard, patientLast) == None:
        return "Patient Last " + msg1  
    
    if re.match(standard_or_blank, description) == None:
        return "Decripton " + msg2

    if re.match(standard, diagnosis1) == None or diagnosis1.rstrip() == "":
        return "Diagnosis 1 " + msg1 
    
    if re.match(standard_or_blank, diagnosis2) == None:
        return "Diagnosis 2 " + msg2

    if re.match(standard, procedure1) == None or procedure1.rstrip() == "":
        return "Procedure 1 " + msg1 
    
    if re.match(standard_or_blank, procedure2) == None:
        return "Procedure 2 " + msg2
     
    if re.match(standard_or_blank, physician) == None:
        return "Physician " + msg2
    
    if re.match(standard_or_blank, clinic) == None:
        return "Clinic " + msg2 

    if re.match(standard_or_blank, referral) == None:
        return "Referral " + msg2
    
    if re.match(standard_or_blank, location) == None:
        return "Location " + msg2

    
    result = DateEdit(dateservice, "service")
    editMessage = result[0]
    flag = result[1]
    input = result[2]
    output = result[3]  
    if flag == False: 
        message = "Invalid Date of Service: " + editMessage
        return message 

    # lastly check for plan on the customer  
    planName = GetPlanName(request) 
 
    if planName.strip() == "":
        message = "You must assign a plan before a claim can be entered."
        return message 

    claimType = request.session["ClaimType"]

    if claimType == "m":
        # edit confine release if entered
       confineDate = request.POST['confine'] 
       defaultDateFieldValue = "None" # check this out  

       # confine date if not default edit ty
       if confineDate != defaultDateFieldValue and confineDate is not None \
          and confineDate != "":
          # (dateMessage, flag, input , result)
          result = DateEdit(confineDate, "service")
          message = result[0] 
          flag = result[1]
          editMessage = result[0]
          if flag == False:  
             message = "Invalid Confine Date on Medical Claim: "  +  editMessage
             return message 

        # release date if not default edit
       releaseDate = request.POST['release']  
        
       if releaseDate != defaultDateFieldValue and releaseDate is not None \
          and releaseDate != "":
          result = DateEdit(releaseDate, "service")
          message = result[0] 
          flag = result[1]
          editMessage = result[0]
          if flag == False: 
             message = "Invalid Release Date on Medical Claim: " + editMessage
             return message 

    if claimType == "d":
       toothNumber = request.POST['tooth_number'] 
       if re.match(tooth_pattern, toothNumber) == None: 
          return "Tooth number must be integer."
       fieldValue = int(toothNumber)
       if fieldValue == 0:
          return "Tooth number can not be zero."

    if claimType == "v":
        eyeware = request.POST['eyeware']
        if re.match(standard, eyeware) == None:
           return "Eyeware " + msg1 

    if claimType == "x":
        drugname = request.POST['drugname']
        if re.match(standard, drugname) == None:
           return "Drug Name" + msg1 

    passedEdits = ""
    return passedEdits

# ================ actions for customer ==============================

def AddCustomer(request): 
   
    customer = AssembleNewCustomer(request, "add")
    custDictionary = CustomerToDictionary(customer)
    notused = ""
    request.session["A45Token"] = notused
    message = RegisterCustomerSave(request, custDictionary) 
    good = ""
    if message == good:
       result =  "good"
    else:
       result = "bad"
    outputDictionary = { 'result': result,'message': message, 'customer': customer}
    return outputDictionary

def UpdateCustomer(request):
    
    customer = AssembleNewCustomer(request, "update") 

def BuildCustomer(request):
    customer = AssembleNewCustomer(request, "buildonly")
    return customer  

def BuildScreen(request):
    c = Customer()
    c.custid = request.POST['custId']
    # do not output, a password , it is input only, then saved.
    
    #c.custpassword = request.POST['custpassword']

    c.custfirst = request.POST['custfirst']
    c.custlast = request.POST['custlast']
    c.custmiddle = request.POST['custmiddle']

    c.custbirthdate = request.POST['custbirthdate']
    c.custaddr1 = request.POST['custaddr1']
    c.custaddr2 = request.POST['custaddr2']

    c.custgender = request.POST['custgender']
    c.custphone = request.POST['custphone']
    c.custemail = request.POST['custemail']

    c.custcity = request.POST['custcity']
    c.custstate = request.POST['custstate']
    c.custzip = request.POST['custzip']

    c.promotion_code = request.POST['promotioncode']

    # default plan to 'None' stop dict error
    c.plan = "None"
    
    return c


def AssembleNewCustomer(request, action): 
 

    if action == "buildonly":
       c = Customer()  # create customer to show screen only edit errors have occurred.
       c.customer_id = request.POST['custId']  
       c.plan = request.session['uplan'] # not on screen stored in session
       c.birth_date = request.POST['custbirthdate']
       promotioncode = ""
    
    if action == "add":
       c = Customer()  # create new customer
       c.customer_id = request.POST['custId']    
       # store custId when registering.
       request.session['custId'] = c.customer_id.rstrip()
       c.plan = "" 
       promotioncode = request.POST['promotioncode']  

    if action == "update":
        #
        promotioncode = "" 
        # get existing customer object from database to update.
        # fetch the customer from the database so no new one is created  
        custId = request.session['custId'].strip()
        
        c = GetCustomer(request, custId)
  
    # get saved password
    if action == "add" or action == "update":
       custpassword = request.session['regPassword'] # saved password  

    # cust password does not show up after being keyed, edited and saved.
    if action == "buildonly":
        custpassword = "" 
   
    # for all actions get screen values
    # and update (c) which is a new or existing customer object
    # depending on register or update process.

    # pull from screen
    custfirst = request.POST['custfirst']
    custlast = request.POST['custlast']
    custmiddle = request.POST['custmiddle']
    custbirthdate = request.POST['custbirthdate']
    custaddr1 = request.POST['custaddr1']
    custaddr2 = request.POST['custaddr2']
    custgender = request.POST['custgender']
    custphone = request.POST['custphone']
    custemail = request.POST['custemail']
    custcity = request.POST['custcity']
    custstate = request.POST['custstate']
    custzip = request.POST['custzip']   

    # copy screen contents to NEW object customer.
    c.first_name = custfirst
    c.last_name = custlast 
    c.middle_name = custmiddle 
    c.password = custpassword
    c.address_1 = custaddr1
    c.address_2 = custaddr2
    c.gender = custgender.upper()
    c.phone = custphone
    c.email = custemail
    c.city  = custcity
    c.state = custstate
    c.zip = custzip 
    # A45 requirees promotion_code 
    c.promotion_code = promotioncode

    if action == "add" or action == "update":
       # should be no errors since edit was before!
       (dateMessage, flag, input , result) = DateEdit(custbirthdate, "birth")
       if flag == True:
           c.birth_date = result
       else:
           # this should not happen but have left it in. edit preformed before.
           c.birth_date = "2021-03-03" # until edits fixed  
    
    
  
    if action == "update":
       # get the customer id from session
       c.customer_id = request.session['custId']
       # set the saved password from session 
       c.password = request.session['regPassword']  
       # not on screen pull from session.
       c.plan = request.session['uplan'] 
       cd = CustomerToDictionary(c) 
       SaveCustomer(request, cd)

    # end of update save operation
    return c 

def CustomerToDictionary(c):

    # A45 uses different spelling for custPassword on add,update.
    
    custDictionary = {

     "custId" : c.customer_id.strip(),
     "custPass" : c.password.strip(),  
     "custPassword" : c.password.strip(), 
     "custFirst" : c.first_name,
     "custMiddle" : c.middle_name,
     "custLast" : c.last_name, 
     "custEmail" : c.email,
     "custPhone" : c.phone,
     "custGender" : c.gender,
     "custBirthDate": c.birth_date, 
     "custAddr1" : c.address_1,
     "custAddr2" : c.address_2, 
     "custCity" : c.city,
     "custState" : c.state,
     "custZip" : c.zip, 
     "custPlan" : c.plan, 
     "PromotionCode" : c.promotion_code,
     "Encrypted" : "",
     "appId" : "A80",
     "extendColors" : "",
     'claimCount' : "" 

    }

    return custDictionary

def ClaimToDictionary(c):

  claimDictionary = {

    "ClaimIdNumber" : c.claim_id,
    "ClaimDescription" : c.description,
    "CustomerId" : c.customer_id,
    "PlanId" : c.plan_id,
    "PatientFirst": c.first_name,
    "PatientLast" : c.last_name,
    "Diagnosis1" : c.diagnosis1,
    "Diagnosis2" : c.diagnosis2,
    "Procedure1" : c.procedure1,
    "Procedure2" : c.procedure2,
    "Procedure3" : c.procedure3,
    "Physician" : c.physican,
    "Clinic" : c.clinic,
    "DateService" : c.date_service,
    "Service" :  c.service,
    "Location" : c.location,
    "TotalCharge" : c.total_charge,
    "CoveredAmount" : c.covered,
    "BalanceOwed" : c.owed,
    "PaymentAmount" : c.payment_amount,
    "PaymentDate" : c.payment_date,
    "DateAdded" : c.date_added,
    "AdjustedClaimId" : c.adjusted_claim_id,
    "AdjustingClaimId" : c.adjusting_claim_id,
    "AdjustedDate" : c.adjusted_date,
    "AppAdjusting" : c.app_adjusting,
    "ClaimStatus" : c.status,
    "Referral" : c.referral,
    "PaymentAction" : c.payment_action,
    "ClaimType" : c.claim_type,
    "DateConfine" : c.date_confine,
    "DateRelease" : c.date_release,
    "ToothNumber" : c.tooth_number,
    "DrugName" : c.drug_name,
    "Eyeware" : c.eye_ware

  }

  return claimDictionary

def ClaimAddSave(request, claim):

    
       urlPrefix = os.environ['A80UrlPrefix']
       apiSelect = "/addClaim" 
       apiString = urlPrefix + apiSelect   
       token = request.session["A45Token"] 
       claim["_csrf"] = token
       dir(claim)  
        
       response = requests.post(apiString, data=claim)
       response.encoding = "UTF-8"  
 
       if response == None:
            message = "1. customer not found"
            return message

       if response.status_code != 200:
           message = f"2. customer not found status is: {response.status_code}" 
           return message
     

       return 'good'

def RegisterCustomerSave(request, cust):

       urlPrefix = os.environ['A80UrlPrefix']
       apiSelect = "/register" 
       apiString = urlPrefix + apiSelect   
  
       response = requests.post(apiString, data=cust)
       response.encoding = "UTF-8"  

       if response == None:
            message = "1. customer not found"
            return message

       if response.status_code != 200:
           message = f"2. customer not found status is: {response.status_code}" 
           return message
     

       j = response.json()
       status = j['Status']
       message = j['Message']
       cust = j['Customer']
       token = '45object stuff decodes' 
 
     
       # not found and bad password will return message and Unsuccessful.
       if status == "Unsuccessful": 
          message = f"3. siginin fails: {message}"
          return message

       custId = cust.get("custId") 
     
       tokenString = j['Token'] 
       a45object = json.loads(tokenString)  
       a45data = a45object.get('A45Object') 
       token = a45data.get('token') 
 
       request.session['A45Token'] = token
       request.session['custId'] = custId

       good = ""
       return good

def SaveCustomer(request, cust):  
 
       urlPrefix = os.environ['A80UrlPrefix']
       apiSelect = "/update" 
       apiString = urlPrefix + apiSelect  
       token = request.session["A45Token"] 
       cust["_csrf"] = token  
       custId = cust['custId'] 
 
       response = requests.put(apiString, data=cust)
       response.encoding = "UTF-8"  

       response.encoding = "UTF-8" 

    
def GetCustomerData(request, custId):
     

       urlPrefix = os.environ['A80UrlPrefix']
       apiSelect = "/cust?id=" + custId  
       apiString = urlPrefix + apiSelect
       response = requests.request("GET",apiString)
       response.encoding = "UTF-8" 

       if response == None:
          return None

       if response.status_code != 200:
          return None

       j = response.json()
       status = j['Status']
       message = j['Message']
       cust = j['Customer'] 
 

         # not found and bad password will return message and Unsuccessful.
       if status == "Unsuccessful": 
          return None

       customer = BuildCustomerFromDict(cust)  
       return customer

def GetCustomer(request,custId):

       request.session['customerFound'] = "No"

       urlPrefix = os.environ['A80UrlPrefix']
       apiSelect = "/cust?id=" + custId  
       apiString = urlPrefix + apiSelect
       response = requests.request("GET",apiString)
       response.encoding = "UTF-8" 

       if response == None:
           message = f". Can not read customer {custId}." 
           request.session['menuMessage'] = message
           return render(request, "A80Insurance/menu.html")

       if response.status_code != 200:
          message = f"2. customer not read status is: {response.status_code}" 
          return message
     

       j = response.json()
       status = j['Status']
       message = j['Message']
       cust = j['Customer'] 
 

         # not found and bad password will return message and Unsuccessful.
       if status == "Unsuccessful": 
           message = f"3. siginin fails: {message}"
           return message 
 
     
       
       customer = BuildCustomerFromDict(cust) 
       # for register edit
       request.session['customerFound'] = "Yes"
       return customer
        

def FormatScreenDateFromDatabase(databaseDate):
   
    date_string = f"{databaseDate}" 
    month = date_string[5:7]
    day = date_string[8:10]
    year = date_string[2:4] 
    # format to mmddyyyy
    screenDate = month  + day  + year 
    return screenDate 

def BuildCustomerFromDict(o):
    c = Customer()
    c.customer_id = o.get('custId').rstrip()
    c.password = o.get('custPassword').rstrip()
    c.first_name = o.get('custFirst').rstrip()
    c.last_name = o.get('custLast').rstrip()
    c.middle_name = o.get('custMiddle').rstrip()
    
    birth_date = FormatScreenDateFromDatabase(o.get('custBirthDate'))
    c.birth_date = birth_date.rstrip()

    c.address_1 = o.get('custAddr1').rstrip()
    c.address_2 = o.get('custAddr2').rstrip()
    c.gender = o.get('custGender').rstrip()
    c.phone = o.get('custPhone').rstrip()

    c.email = o.get('custEmail').rstrip()
    c.city  = o.get('custCity').rstrip()
    c.state = o.get('custState').rstrip()
    c.zip = o.get('custZip').rstrip()

    c.plan = o.get('custPlan').rstrip()

    return c

def BuildCustomerFromObject(o):

    # copy database names back to screen data. 
    c = Customer() 
 
    c.customer_id = o.customer_id.rstrip()
    c.password = o.password.rstrip()
    c.first_name = o.first_name.rstrip()
    c.last_name = o.last_name.rstrip()
    c.middle_name = o.middle_name.rstrip()
 
    
    birth_date = FormatScreenDateFromDatabase(o.birth_date)
 

    c.birth_date = birth_date.rstrip()
 

    # =======================
    # html name = model name
    # =======================

    c.address_1 = o.address_1.rstrip()
    c.address_2 = o.address_2.rstrip()
    c.gender = o.gender.rstrip()
    c.phone = o.phone.rstrip()

    c.email = o.email.rstrip()
    c.city  = o.city.rstrip()
    c.state = o.state.rstrip()
    c.zip = o.zip.rstrip()
    c.plan = o.plan.rstrip()

    return c
 


def AddClaim(request):

    # request.session['NewClaimNumber'] for copy and adjustments.
    # request.session['ClaimNumber'] for adjustments - claim being adjusted.
    # reset right after adjustement logic in claim().

    a = request.session['ClaimType'] 


    service = request.POST["service"] 
 
    claim = BuildClaim(request, "add")  
    # claim id - WHEN ADJUSTMENT USE DEFINED CLAIM ID SETUP ALREADY
    newClaimNumber = request.session['NewClaimNumber']
    historyAction = False if newClaimNumber == "" else True
    if historyAction == True: 
        claim.claim_id = newClaimNumber # for copy and adjustments get new claim number
    else: 
        claim.claim_id = GetClaimId() # a new claim get new claim id

    # customer id 
    claim.customer_id = GetCustomerId(request) 
    # status
    claim.status = "Entered" 
    # date entered and other fields
    claim.procedure3 = ""
 

    # temp 
    claim.covered = 0.0
    claim.owed = 0.0 
 

    # other: 'PaymentAction', 'AppAjusting', 'AdjustedDate', 'AdjustingClaimId', 'AdjustedClaimId'
    # other: "PaymentDate", "PaymentAmount"

    claim.adjusted_claim_id = ""
    claim.adjusted_claim_id = ""
    claim.app_adjusting= ""
    claim.payment_amount = 0.0
    claim.payment_action = ""

    # dates: service, added, payment , adjusted 
    # ref: https://www.javatpoint.com/python-date
  
    # sql server format
    defaultDate = "17530101"
    now = datetime.now()
    #currentDate = now.strftime("%Y-%m-%d") 
    # SQL server format ...  
    currentDate = now.strftime("%Y%m%d")  
 
    #defaultDate = datetime.datetime(1753,1,1)
    #currentDate = datetime.now()
    claim.date_added = currentDate
    claim.payment_date = defaultDate
    claim.adjusted_date = defaultDate  

    

    # Adjustment  
    historyActionValue = request.session["HistoryAction"]
    buildingAdjustment = True if historyActionValue == "Adjust" else False
    if buildingAdjustment:
        claim.adjusted_claim_id = request.session["ClaimNumber"] 
        claim.status = "Adjustment"
    # 
    claimType = request.session['ClaimType']
 
 
    if claimType != "m": 
       claim.date_confine = defaultDate
       claim.date_release = defaultDate
    if claimType != 'd':
        claim.tooth_number = 0
    if claimType != 'v':
        claim.eye_ware = ""
    if claimType != 'x':
        claim.drug_name = "" 

    # for type m replace "None" 
    if claimType == "m":
        if claim.date_confine == "None":
            claim.date_confine = defaultDate
        if claim.date_release == "None":
            claim.date_release = defaultDate
    ## 

    # read from customer  
    claim.plan_id = GetPlanName(request)   

    
    service = request.POST["service"] 

    plan = "Basic Plan"



    # calculate the covered cost 
    #  
    results = CalculateCostsBasedOnPlan(request, service, plan, claimType) 
    #
    claim.total_charge = results[0]
    claim.covered = results[1]
    claim.owed = results[2] 
    #

    # workaround for development until read service, read plans coded
    # dont forget to code getPlan too,....
    
    
 

    claimDictionary = ClaimToDictionary(claim)
 

    saveResult = ClaimAddSave(request, claimDictionary)
    if saveResult != "good": 
       # save result has a message unless good ....
       resultObject = { 'status' : 'bad', 'message' : saveResult}
       return resultObject
 

    use = "New"
    historyActionValue = request.session['HistoryAction']
    if buildingAdjustment == True:
        use = "Adj"
    if historyActionValue == "Copy":
        use = "Copy"
    # set up action button 
    AddRecord(request, use, claim.claim_id) 

    if buildingAdjustment == True: 
       request.session["HistoryAction"] = "" 

       token = request.session['A45Token']

       adjustmentData = { "AdjustmentIdNumber" : claim.claim_id,
                          "ClaimIdNumber" : claim.adjusted_claim_id,
                          "AdjustedDate" : currentDate, 
                          "AppAdjusting" : "A80",
                          "_csrf" : token }

       # put('/stampAdjustedClaim')

       urlPrefix = os.environ['A80UrlPrefix']
       apiSelect = "/stampAdjustedClaim"    
       url = urlPrefix + apiSelect
       response = requests.put(url, data=adjustmentData)
       response.encoding = "UTF-8" 

       if response == None:
           message = f"null response on adj call..." 
           request.session['menuMessage'] = message
           return render(request, "A80Insurance/menu.html")

       if response.status_code != 200:
          message = f"2. bad code on adj -  status is: {response.status_code}"  
          request.session['menuMessage'] = message
          return render(request, "A80Insurance/menu.html")


    # end of adjusted claim update.

    # reset fields.
    request.session["NewClaimNumber"] = ""
    request.session["ClaimNumber"] = ""
    request.session["HistoryAction"] = ""
    
    message = f"Claim {claim.claim_id} successfully added."
    resultObject = { 'status' : 'good', 'message' : message}
    return resultObject


def BuildClaim(request , action): 
     
    # for edit put request data on screen 
    c = Claim()    
    buildingTheClaim = "build"  
    c.first_name = request.POST['first'] 
    c.last_name = request.POST['last']  
    c.description = request.POST['desc']
    c.diagnosis1 = request.POST['diag1'] 
    c.diagnosis2 = request.POST['diag2']
    c.procedure1 = request.POST['proc1']
    c.procedure2 = request.POST['proc2']
    c.physican = request.POST['phys']
    c.clinic = request.POST['clinic']
    c.referral = request.POST['referral'] 
    c.location = request.POST['location']   
    service = request.POST["service"]
    c.service = service
    c.date_service = request.POST['dateservice'] 

    # Get claim type from session.
    c.claim_type = request.session['ClaimType'] 

    claimType = c.claim_type.rstrip()  
    if claimType == "m":
        c.date_confine = request.POST['confine']  
        c.date_release = request.POST['release']
    if claimType == "d":
        c.tooth_number = request.POST["tooth_number"]
    if claimType == "v":
        c.eye_ware = request.POST["eyeware"]
    if claimType == "x":
        c.drug_name = request.POST["drugname"]
     
    if action == "add" or action == "update":
        intent = "build"
    else:
        intent = "edit"

    if intent == buildingTheClaim:
        # add or update : formate date to database format for
        # insertion into database... result should be good since was edited
        result = DateEdit(c.date_service, "service") 
        c.date_service = result[3]  

    #defaultDate = "1753-01-01" 
    # sql server date format
    defaultDate = "17530101" 
    empty = ""  
    medical = "m"
    if claimType == medical and intent == buildingTheClaim:
       # confine and release dates optional if unused put default date in.
       # when used format them via edit routine to database dates.
       confineDate = request.POST['confine']    
       if confineDate is None or confineDate == empty: # use default  
             c.date_confine = defaultDate
       else: 
             result = DateEdit(confineDate, "service") # format it for database.
             c.date_confine = result[3] 

       releaseDate = request.POST['release']    
       if releaseDate is None or releaseDate == empty: # use default 
           c.date_release = defaultDate
       else:
           result = DateEdit(releaseDate, "service") # format it for database.
           c.date_release = result[3]  
     
    return c

def Format1(date):
    result = FormatToScreen(date)
    return result


def FormatToScreen(date):  

    # entry screens - no slashes added.

    # reformat date from 1753-01-01 to "" or any other date to mmddyyyy 
    date = str(date)
    if date == "1753-01-01 00:00:00": 
        return ""
    if date == "1900-01-01 00:00:00":
        return ""
    # if yyyy-mm-dd flip to mmddyyyy 
    if date.find("-") > -1:
        #result = "" # python puts dashes in date and shows yyyy-mm-dd on screen
        # that is not wanted it should mmddyyyy or None
        # 
        y = date[0:4]
        m = date[5:7]
        d = date[8:10]
        slash = "/"
        result = m + slash + d + slash + y
        return result

     


def Format2(date):  
    # history screen add slashes

    # reformat date from 1753-01-01 to "" or any other date to mm/dd/yyyy for history 
    result = date
    if date == "1753-01-01": 
        result = ""
    # if yyyy-mm-dd flip to mmddyyyy
    if date.find("-") > -1:
        #result = "" # python puts dashes in date and shows yyyy-mm-dd on screen
        # that is not wanted it should mmddyyyy or None
        # 
        y = date[0:4]
        m = date[5:7]
        d = date[8:10]
        slash = "/"
        result = m + slash + d + slash + y

    # 
    return result  



def GetClaimId(): 

     now = datetime.now() # current date and time
     claimIdNumber = now.strftime("CL-%m-%d-%Y-%H:%M:%S") 
     return claimIdNumber 

def GetCustomerId(request):

    custId = request.session['custId']
    return custId

def GetPlanName(request):

      # get('/readPlan')

       urlPrefix = os.environ['A80UrlPrefix'] 
       custId = request.session['custId'] 
       apiSelect = "/readPlan?id=" + custId 
       url = urlPrefix + apiSelect
       response = requests.get(url)
       response.encoding = "UTF-8" 

       j = response.json()
       status = j['Status']
       message = j['Message']
       planObject = j['Plan']
 

       if status != "Successful":
          print ( f" GetPlanName bad read status {status} message {message}")
          return "" 
        
       planName = planObject['custPlan']
       name = planName.rstrip() 
       return name
 

def CalculateCostsBasedOnPlan(request, serviceName, planName , claimType):
    # read services 
    # read plans
    # Apply Plan Percent to services 
    # return covered cost do calcs in caller.  service charge - covered = owed.

    _service = serviceName.rstrip()
    _plan = planName.rstrip()

    # services
    # services = Service.objects.filter(service_name=_service, claimType=claimType)

    # app.get('/readServices')

    urlPrefix = os.environ['A80UrlPrefix']  
    apiSelect = "/readServices" 
    url = urlPrefix + apiSelect
    response = requests.get(url)
    response.encoding = "UTF-8" 

    if response == None:
          print("warn1: service read error.")
          return ""

    if response.status_code != 200:
          print(f"warn2: service read error. {response.status_code}")
          return ""

    sJson = response.json() 


    serviceCost = 0
    index = 0
    for service in sJson:  
        dbServiceName = service['ServiceName'] 
        if dbServiceName.strip() == _service:
           serviceCost = float(service['Cost'])
        index = index + 1
    # 
 

    #app.get('/readPlans)

    urlPrefix = os.environ['A80UrlPrefix']  
    apiSelect = "/readPlans" 
    url = urlPrefix + apiSelect
    response = requests.get(url)
    response.encoding = "UTF-8" 

    if response == None:
          print("warn3: plan(s) read error.")
          return ""

    if response.status_code != 200:
          print(f"warn4: plan(s) read error. {response.status_code}")
          return ""

    pJson = response.json()
    #return planName

    percent = 0.0
    index = 0 
    for plan in pJson: 
    
        if plan['PlanName'].strip() == _plan:
           percent = float(plan['Percent'])
     
    #
    # based on plan percent get the covered cost and
    # return 'that' to the caller.

    coveredCost = (serviceCost * percent) / 100
    #
    amountOwed = serviceCost - coveredCost 
 
    #
    return (serviceCost, coveredCost, amountOwed) 
    # 

def PayClaim(request):  #here

      if request.method == "GET":     

       # check for valid url must be signed in.
       if NotSignedIn(request) == True:  
          return render(request, "A80Insurance/notauthorized.html")

        # show payment screen. 
       
       claimNumber = request.session['ClaimNumber']
       message = "Please enter claim payment amount."
       return render(request, "A80Insurance/payclaim.html",
              {'claimNumber' : claimNumber, 'message' : message}) 
      
      if request.method == "POST": 
        # edit payment amount and update claim with payment amount and payment date
        message = "" 
        amount = request.POST['amount']   
         
        wholeNumnber = "^([0-9])+$" 
        decimalNumber = "^([0-9])+.([0-9])+$" 
        msg1 = " must be valid decimal number or whole number."
    
        if re.match(wholeNumnber, amount) == None and re.match(decimalNumber, amount) == None:
          message =  "Payment amount " + msg1 
          claimNumber = request.session['ClaimNumber']
          return render(request, "A80Insurance/payclaim.html",
                 { 'claimNumber' : claimNumber , 'amount' : amount, 'message' : message}) 

        # update claim payment amount and payment date with current  date  
        claimNumber = request.session['ClaimNumber']
 
        claim = getClaim(claimNumber)

        # update fields
 
        now = datetime.now()
        #
        #currentDate = now.strftime("%Y-%m-%d")
        # sql date  format   
        currentDate = now.strftime("%Y%m%d")
 
        amountPaid = float(amount)
 
        # put('/setClaimStatus')

        token = request.session['A45Token'] 

        urlPrefix = os.environ['A80UrlPrefix']
        apiSelect = "/setClaimStatus" 
        apiString = urlPrefix + apiSelect  

        paymentDictionary = { 

            "action" : "pay",
            "claimIdNumber" : claimNumber,
            "amount" : amountPaid,
            "date": currentDate,
            "_csrf" : token
        }
         
 
        response = requests.put(apiString, data=paymentDictionary)
        response.encoding = "UTF-8"  
        status = response.status_code
        if status == 200: 
           message = f"Claim {claim} Paid Successfully"
        else:
           message = "Claim Payment Error."

        request.session['menuMessage'] = message

        AddRecord(request, "Pay", claimNumber)

        return render(request, "A80Insurance/menu.html")


def DateEdit(input, type):

    # called for edit and update values ; may have to change output format for db date
    # and subsequent screen date  
    # screen date is input if error found

    # return (messge, ok-flag, input, output)

    # edits dates mmddyy or mmddyyyy with or with out slashes
    # type = birth or service
    # returns (message, data) 
 
    message = ""
    
    # return (message, False, input, input)

    slash = "/"
    slashesFound = input.find(slash) 

    if slashesFound > -1:
       message = "4. use mmddyy or mmddyyyy format -- no slashes."
       return (message, False , input, input) 
   

    length = len(input) 
    validShort = 6
    validLong = 8
    if length != validShort and length != validLong:
       message = "1. Invalid Date wrong length" 
       return (message, False , input, input)

    # get mm and dd characters
    mm = input[0:2]
    dd = input[2:4]
    yy = input[4:6] if length == validShort else input[4:8]
    
    year_str = input[4:6] if length == validShort else input[6:8]
    year = int(year_str)

    # convert to m d and y.
    m = int(mm)
    d = int(dd)
    y = int(yy) 

    dm = 31

    match m:
        case 9: dm = 30
        case 4: dm = 30
        case 11: dm = 30
        case 6: dm = 30
        case _: dm = 31
    
    if m == 2:
        dm = 29 if m % 4 == 0 else 28  
 

    if d == 0 or d > dm:
        message = "2. Invalid day of month bad date" 
        return (message, False , input, input)

    if m < 1 or m > 12:
        message ="3. Invalid month bad date"
        return (message, False, input, input)

    # birth dates should be entered as 4 digits to be unambigiuous 
    # but 2 are allowed if greater than next year jump to past

    # service dates are within plus minus 1 year
    
    # convert to 4 digit date based on input type
    # if birth type use cut off of next year + 1 to flip to cent - 1.
    # if 2 digits and service just add 2000.
 

    
    now = datetime.now() # current date and time
    current_year_str = now.strftime("%Y") 
    current_year = int(current_year_str)

    # interpret 2 digit year
    if length == validShort:
        cutOff = current_year + 1
        y4dig = y + 2000 

        if type == "service":
            y = y + 2000

        if type == "birth":  
            # future years assumned to be 1900s
            adjust = 1900 if y4dig > cutOff else 2000 
            y += adjust
    #
 

    # service date edit plus minus 1 year 
    minusOne = current_year - 1
    plusOne = current_year + 1
    
    if type == "service":
       if y < minusOne or y > plusOne:
          message = "4. Invalid service date out of range."
          return (message, False , input, input)


    year4  = str(y)
    # right new we accept 2 only; future - 1/2/33333 ; insure 2.
    m2 = "0" + mm if len(mm) == 1 else mm
    d2 = "0" + dd if len(dd) == 1 else dd 
    
    # should be in database format
    # yyyy-mm-dd 00:00

    dash = "-" 
    for_date_time_fields = " 00:00 "
    for_date_fields = ""
    if type == "service":
         suffix  = for_date_fields
    if type == "birth":
         suffix = for_date_time_fields
         
    # add appropriate suffix for type of field.
    #output = year4 + dash + m2 + dash + d2  + suffix

    # A45 adjust for sql server date constant to stored procedure:
    # yyyymmdd
    # sql server date format 
    sqlServerConstant = year4 + m2 + d2
    output = sqlServerConstant
 

    goodEdit = "Good Edit"
    return (goodEdit, True, input,  output)


# =============== Release 2 methods =====================

# prototype:  AddRecord(request, "act", claimIdNumber)

def AddRecord(request, action, claimIdNumber):

    # builds : literal, claimidNumber in session area.

    # find what is there
    comma = ","
    colon = ":"
    dash = "-"

    entry1 = request.session['entry1']
    entry2 = request.session['entry2']

    # act - create an abbreviation for the button literals to be displayed on history screen.
    # ex. Adj-01 where the 01 follows the last colon.

    firstColon = claimIdNumber.find(colon)
    afterFirstColon = firstColon + 1
    secondColon = claimIdNumber.find(colon,afterFirstColon)
    afterSecondColon = secondColon + 1
    claimSuffix = claimIdNumber[afterSecondColon:]
    act = action + dash + claimSuffix

    if entry1 == None:
        act = ""
        request.session['entry1'] = act + comma + claimIdNumber 

    elif entry2 == None:
        act = ""
        request.session['entry2'] = act + comma + claimIdNumber 
    else:
        # both used - move 1st to 2nd and add to 1st. 
        work = request.session['entry1']
        request.session['entry2'] = work 
        request.session['entry1'] = act + comma + claimIdNumber 
 
    return

def pullRecord(request, operation):
  

    # returns: literal, claimIdNumber based on 0 or 1 operation.
    none = "none"
    output = ""

    if operation != 0 and operation != 1:
        return none

    if operation == 0:
        output = request.session["entry1"] 
    
    if operation == 1:
        output = request.session['entry2']

    if output == None:
        return none
    
    if output == "":
        return none

    return output

    return

def show(request):

    print("-- show --")
    entry1 = request.session['entry1']
    entry2 = request.session['entry2']
    print(f"entry1 : {entry1} ")
    print(f"entry2 : {entry2} ")
    print("=======")
    return


def admin(request):  

     if request.method == "GET":
          
          adm = Adm()
          message = "Plese enter signin information..." 
          return render(request, "A80Insurance/admin.html",
              { 'adm' : adm, 'message': message })  

     if request.method == "POST":  
    
        adminEditResult = adminEdit(request)
        if adminEditResult != "good":
           message = adminEditResult 
           return render(request, "A80Insurance/admin.html", { 'message': message})

        request.session['admSignin'] = "Yes"

        message = "Enter requested action." 
        return render(request, "A80Insurance/action.html", { 'message': message})

def adminEdit(request):

        admId = request.POST['admId']  
        admPass = request.POST['admPass']  

        if admId == "":
            message = "Please enter a Administrator Id."
            return message 
        
        if admPass == "":
            message = "Please enter Admnistrator Password."
            return message 
 
        # some progames use a45 for this
        try:
           env_admId = os.environ['A80admId']
        except:
              message = "3. Please have administrator set up environment variables."
              return message 

        env_pass  = os.environ['A80admPass']

        if admId != env_admId:
            message = "Please enter correct Administrator Id."
            return message 
        
        if admPass != env_pass:
            message = "Please enter correct Admnistrator Password."
            return message 

        return "good"

def action(request):
  
     
    
     if request.method == "GET": 
          # check for valid url must be signed in.
          if AdmNotSignedIn(request) == True:
             return render(request, "A80Insurance/notauthorized.html") 

          message = "" 
          return render(request, "A80Insurance/action.html",
              { 'message': message })  


     if request.method == "POST": 

        selectedAction = request.POST['commit']
        
        # action can be : menu, claim, adjust..., or copy... 
        #
        listCustomerRequest = selectedAction.find("List Customers")
        resetCustomerRequest = selectedAction.find("Reset Customer")
        resetPasswordRequest = selectedAction.find("Reset Password") 
 
        found = 0 
        #
        if listCustomerRequest == found: 
            result = ListCustomers(request) 
            #   result = { 'status' : 'good', 'message' : message, 'data' : customerData}
            status = result['status']
            message = result['message']
            if status == "good":
               customerData = result['customerData']
               return render(request, "A80Insurance/listcustomers.html",
                  { 'message': message, 'customerData' : customerData})  
            else:
                 return render(request, "A80Insurance/action.html",
                  { 'message': message }) 

           # end customer request 

        if resetCustomerRequest == found: 

            result = EditCustomerResetFields(request)
            #   result = { 'status' : 'good', 'message' : message, 'data' : customerData} 
            message = result['message'] 
            return render(request, "A80Insurance/action.html",
                  { 'message': message }) 

           # end customer request 
           

        if resetPasswordRequest == found:

            result = EditPasswordResetFields(request) 
            #   result = { 'status' : 'good', 'message' : message, 'data' : customerData} 
            message = result['message'] 
            return render(request, "A80Insurance/action.html",
                   { 'message' : message })

           # end customer request 
        # 

        message = "" 
        return render(request, "A80Insurance/action.html",
              { 'message': message})     

def EditCustomerResetFields(request):

     standard = "^([0-9a-zA-Z\s])+$"

     custId =    request.POST['custId']  
     newCustId = request.POST['newCustId']

     if re.match(standard, custId) == None :
        message = "A valid customer id is required for customer reset."
        result = { 'status' : 'error', 'message' : message, 'data' : ''}
        return result

     if re.match(standard, newCustId) == None :
        message = "A valid new customer id is required for customer reset."
        result = { 'status' : 'error', 'message' : message, 'data' : ''}
        return result

     if custId == newCustId:
        message = "New Customer Id must be different than the Customer Id."
        result = { 'status' : 'error', 'message' : message, 'data' : ''}
        return result

    # first must exist

     result = GetCustomerData(request, custId)
     found = result == None
     if(found):
        message = "Customer to be reset does not exist." 
        result = { 'status' : 'error', 'message' : message, 'data' : ''}
        return result

    # reset must not exist 
    
     result = GetCustomerData(request, newCustId)
     print(f"admin new cust exist check result: {result}")
     found = result != None
     if(found):
        message = "Reset Customer already exists." 
        result = { 'status' : 'error', 'message' : message, 'data' : ''}
        return result

     message = ResetCustomer(request, custId, newCustId)
     good = ""
     if message == good:
        message = "Customer reset successfully."
        result = { 'status' : 'good', 'message' : message, 'data' : ''}
        return result
     else:
        result = { 'status' : 'error', 'message' : message, 'data' : ''}
        return result


def EditPasswordResetFields(request):

     standard = "^([0-9a-zA-Z\s])+$"

     custId =    request.POST['custId']  
     newPass = request.POST['custPassword'] 
     confirm = request.POST['conPassword']

     if re.match(standard, custId) == None :
        message = "A valid customer id is required for password reset."
        result = { 'status' : 'error', 'message' : message, 'data' : ''}
        return result

     if re.match(standard, newPass) == None :
        message = "A valid new password is required for password reset." 
        result = { 'status' : 'error', 'message' : message, 'data' : ''}
        return result
    
     if re.match(standard, confirm) == None :
        message = "A valid confirm password is required for password reset."
        result = { 'status' : 'error', 'message' : message, 'data' : ''}
        return result

     if newPass != confirm:
        message = "New password and confirm do not match."
        result = { 'status' : 'error', 'message' : message, 'data' : ''}
        return result

    # first must exist

     result = GetCustomerData(request, custId)
     found = result == None
     if(found):
        message = "Customer does not exist." 
        result = { 'status' : 'error', 'message' : message, 'data' : ''}
        return result 

     message = ResetPassword(request, custId, newPass )
     good = ""
     if message == good:
        message = "Password reset successfully."
        result = { 'status' : 'good', 'message' : message, 'data' : ''}
        return result
     else:
        result = { 'status' : 'error', 'message' : message, 'data' : ''}
        return result


def ResetCustomer(request, custId, newCustId):

       # put('/resetCustomerId')

       message = "" # good result 

       urlPrefix = os.environ['A80UrlPrefix']
       apiSelect = "/resetCustomerId"
       url = urlPrefix + apiSelect

       token = request.session['A45Token']

       resetCustData = { 

            'custId' : custId,
            'newCustId' : newCustId,
            '_csrf' : token

       } 

       response = requests.put(url, data=resetCustData)
       response.encoding = "UTF-8" 
      
       if response == None:
           message = f".1 Can not reset customer."  
           return message

       if response.status_code != 200:
          message = f"2. customer not reset status is: {response.status_code}"  
          return message

       return ""


def ResetPassword(request, custId, newPass):

    
       message = "" # good result 

      # app.put('/resetPassword')

       urlPrefix = os.environ['A80UrlPrefix']
       apiSelect = "/resetPassword"
       url = urlPrefix + apiSelect
       token = request.session['A45Token']
      
       passwordResetData = {

            'custId' : custId,
            'newPassword' : newPass,
            '_csrf' : token

       }
 

       response = requests.put(url, data=passwordResetData)
       
       response.encoding = "UTF-8"  
 

       if response == None:
           message = f". Can not reset password."  
           return message

       if response.status_code != 200:
          message = f"2. can not reset password status is: {response.status_code}"   
          return message 

       return ""
        
    
def ListCustomers(request):

       # app.get('/custList',

       
    
       urlPrefix = os.environ['A80UrlPrefix']
       apiSelect = "/custList"
       url = urlPrefix + apiSelect
       response = requests.get(url)
       response.encoding = "UTF-8" 

       if response == None:
           message = f". Can not read customers."  
           result = { 'status' : 'error', 'message' : message, 'data' : ''}
           return result

       if response.status_code != 200:
          message = f"2. cstomers not read status is: {response.status_code}"  
          result = { 'status' : 'error', 'message' : message, 'data' : ''}
          return result
       
       j = response.json()  
  
       customerData = []
       for r in j:
 

           custDictEntry = {

            'custId' : r['custId'],
            'custFirst' : r['custFirst'],
            'custLast' : r['custLast'],
            'appId' : r['appID'] 

           }    
           customerData.append(custDictEntry)
         
       count = len(customerData)
       message = f" {count} Customer(s) found." 
       result = { 'status' : 'good', 'message' : message, 'customerData' : customerData}
       return result
 

    


