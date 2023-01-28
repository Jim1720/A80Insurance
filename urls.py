 
 # urls.py 

from django.urls import path

from . import views     

app_name = 'A80Insurance'
urlpatterns = [ 
     
    path('', views.start, name='start'), 
    path('hello', views.hello, name='hello'),
    path('index', views.index, name='index'),  
    path('start', views.start, name='start'),   
    path('classic', views.classic, name='classic'),
    path('register',views.register,name='register'),    
    path('signin', views.signin, name='signin'),   
    path('update', views.update, name='update'),
    path('claim',views.claim, name='claim'),
    path('history', views.history, name='history'),
    path('plan', views.plan, name='plan'),
    path('signout', views.signout, name='signout'),
    path('menu', views.menu, name='menu'),    
    path('info', views.info, name='info'),   
    path('about', views.about, name='about'),   
    path('payclaim', views.PayClaim, name='payclaim'),  
    path('notauthorized', views.notauthorized, name='notauthorized'), 
    path('admin', views.admin, name='admin'),  
    path('action', views.action, name='action')


]