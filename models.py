from unittest.util import _MAX_LENGTH
from django.db import models

# Signin Screen

class Signin(models.Model): 
    customer_id = models.CharField(max_length=20,default='none')
    password = models.CharField(max_length=20,default='n/aa')


class Adm(models.Model): 
    admId = models.CharField(max_length=20,default='none')
    admpass = models.CharField(max_length=20,default='n/aa')  

# Customer, Claim 

class Customer(models.Model):
 
    customer_id = models.CharField(max_length=20,default='none',db_column="custId")
    password = models.CharField(max_length=20,default='n/aa',db_column="custPassword")

    first_name = models.CharField(max_length=30,default='none',db_column="custFirst")
    middle_name = models.CharField(max_length=15,blank=True,default='',db_column="custMiddle")
    last_name = models.CharField(max_length=30,default='none',db_column="custLast")

    birth_date = models.DateTimeField(db_column="custBirthDate")

    MALE = 'M'
    FEMALE = 'F'
    GENDER_CHOICES = [(MALE,'Male'),(FEMALE,'Female')] 
    gender = models.CharField(max_length=4,choices=GENDER_CHOICES,default=MALE,db_column="custGender")

    phone = models.CharField(max_length=15,default='',db_column="custPhone") 
    email = models.CharField(max_length=15,default='',db_column="custEmail")
 
    address_1 = models.CharField(max_length=15,default='',db_column="custAddr1")  
    address_2 = models.CharField(max_length=15,blank=True, db_column="custAddr2") 

    city = models.CharField(max_length=15,default='',db_column="custCity") 
    state = models.CharField(max_length=2,default='',db_column="custState") 
    zip = models.CharField(max_length=14,default='',db_column="custZip")

    # manually added
    plan = models.CharField(max_length=4,default="",db_column="custPlan")

    promotion_code = models.CharField(max_length=4,default="",db_column="PromotionCode")

    def __str__(self):
        know = self.customer_id 
        return know

    class Meta:
        db_table = "Customer"


class Claim(models.Model):  

    claim_id = models.CharField(max_length=15,default='none',db_column="ClaimIdNumber") 
    customer_id = models.CharField(max_length=20, db_column="CustomerId")   
    status = models.CharField(max_length=10,default='Entered',db_column="ClaimStatus")  
    description = models.CharField(max_length=20, default='', db_column="ClaimDescription")   

    first_name = models.CharField(max_length=30, default='', db_column="PatientFirst") 
    last_name = models.CharField(max_length=30,default='',blank=True, db_column="PatientLast")

    diagnosis1 = models.CharField(max_length=10,default='' , db_column="Diagnosis1")  
    diagnosis2 = models.CharField(max_length=10,default='' , db_column="Diagnosis2") 
    
    procedure1 = models.CharField(max_length=10,default='' , db_column="Procedure1")
    procedure2 = models.CharField(max_length=10,default='' , db_column="Procedure2") 
    procedure3 = models.CharField(max_length=10,default='' , db_column="Procedure3")

    physican = models.CharField(max_length=20,default='', db_column="Physician")   
    clinic = models.CharField(max_length=35,default='', db_column="Clinic")   
      
    location = models.CharField(max_length=35,default='', db_column="Location")   
    referral = models.CharField(max_length=35,default='', db_column="Referral")  
    
    # defines percent of any service chosen
    plan_id = models.CharField(default="None",max_length=12,db_column="PlanId") 

    #service
    service = models.CharField(max_length=10,db_column="Service") 

    # date of service
    date_service = models.DateField(db_column="DateService")

    # total charge
    total_charge = models.DecimalField(max_digits=10,decimal_places=2,default=0.00,db_column="TotalCharge")

    # plan cost (pulled from service db)
    covered = models.DecimalField(max_digits=10,decimal_places=2,default=0.00,db_column="CoveredAmount") 

    # cost minus cost times plan-percent (computed)
    owed = models.DecimalField(max_digits=10,decimal_places=2,default=0.00,db_column="BalanceOwed") 

    # date added
    date_added = models.DateField(db_column="DateAdded")

    # claim type 
    claim_type = models.CharField(max_length=1, db_column="ClaimType")

    # type fields 
    date_confine = models.DateField(db_column="DateConfine")
    date_release = models.DateField(db_column="DateRelease")
    #
    tooth_number = models.IntegerField( db_column="ToothNumber")
    #
    eye_ware = models.CharField(max_length=10, default="",db_column="Eyeware")
    #
    drug_name = models.CharField(max_length=10, default="",db_column="DrugName")
  
    app_adjusting = models.CharField(max_length=4,default="",db_column="AppAdjusting")
    adjusting_claim_id = models.CharField(max_length=20, blank=True,default='', db_column="AdjustingClaimid")  
    adjusted_claim_id = models.CharField(max_length=20, blank=True, default='', db_column="AdjustedClaimId") 
    adjusted_date  = models.DateField(db_column="AdjustedDate")
    #
    payment_amount = models.DecimalField(max_digits=10,decimal_places=2,default=0.00,db_column="PaymentAmount") 
    payment_action = models.CharField(max_length=4,default="", db_column="PaymentAction")
    payment_date  = models.DateField(db_column="PaymentDate")


    def __str__(self):
        return self.claim_id

    class Meta:
        db_table = "Claim"


class Plan(models.Model):  
 
    plan_name = models.CharField(max_length=30,db_column="PlanName") 
    plan_percent = models.DecimalField(max_digits=2,decimal_places=2, db_column="Percent") 
    plan_literal = models.CharField(max_length=45,db_column="PlanLiteral")
    #
    def __str__(self):
        return self.plan_name

    class Meta:
        db_table = "Plan"

class Service(models.Model):  

     service_id = models.IntegerField(db_column="Id")
     service_name = models.CharField(max_length=30,db_column="ServiceName") 
     service_cost = models.DecimalField(max_digits=10,decimal_places=2,db_column="Cost")
     claimType = models.CharField(max_length=1,db_column="ClaimType") 
     #
     def __str__(self):
        return self.service_name

     class Meta:
        db_table = "Service"