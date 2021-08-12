from django.shortcuts import render,redirect
from django.http import HttpResponse
from shop.models import product,purchasedetail,cart as cartlist,tempre,tempcn,customer,staff,allstaff
from PIL import Image
from django import forms
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
import datetime
from datetime import date,timedelta
import re

mydate = datetime.datetime.now()
month= mydate.strftime("%B")
cartproduct={}
productable=product.objects.all()
for i in productable:
    if i.season!=month and i.season!="all" :
        product.objects.filter(pname=i.pname).update(stockavailable="no",itemavail=0)
DATE=date.today()
tdate=DATE-timedelta(days=2)
d=purchasedetail.objects.all()
for i in d:
    if i.cname=="admin":
           purchasedetail.objects.filter(orderno=i.orderno).update(status="delivered")
    if i.date!=str(DATE) and i.status=="tobedelivered":
        purchasedetail.objects.filter(orderno=i.orderno).update(status="cancelled")


def show(request):
    if request.session['user']:
         t=product.objects.all()
         user=request.session['user']
         msg="welcome"
         ordno=1
         while True:
             if cartlist.objects.filter(idno=ordno).exists():
                     ordno+=1
             else:
                 cartlist.objects.create(idno=ordno,img="####")
                 break
         if request.method == "POST":
              for i in t:
                 products=i.img
                 remove = request.POST.get(products, False);
                 if remove == "Add to Cart":
                     if cartlist.objects.filter(cname=user,pname=i.pname).exists():
                         msg="item already in cart"
                         continue
                     
                     cartlist.objects.create(idno=ordno,cname=user,pname=i.pname,img=i.img,cost=i.cost) 
                     msg="item added to cart"      
              submit = request.POST.get('filters',False)
              if submit=="applyfilter":
                  pmodel = request.POST['pmodel']
                  seasons = request.POST['season']
                  if seasons =="season":
                         season=month
                         if pmodel=="all":
                             t=product.objects.filter(season=season)
                         else:
                             t=product.objects.filter(season=season,pmodel=pmodel)
                  else:
                        if pmodel=="all":
                            t=product.objects.all()
                        else:
                            t=product.objects.filter(pmodel=pmodel)
              search=request.POST.get('search',False)
              if search=="search":
                 d=tempre.objects.all()
                 for i in d:
                     tempre.objects.filter(pname=i.pname).delete()
                 item=request.POST['item']
                 t=product.objects.filter(pname=str(item))
                 if len(t)==0:
                     item=item.lower()
                     A=item[0]+item[1]
                     v="^"+str(A)+".*$"
                     t=product.objects.all()
                     for i in t:
                         p=i.pname
                         p=p.lower()
                         x=re.search(v,p)
                         if (x):
                            tempre.objects.create(pname=i.pname,img=i.img,cost=i.cost,season=i.season,pmodel=i.pmodel,stockavailable=i.stockavailable)

                           
                         else :
                             continue
                     t=tempre.objects.all()


              
         listm=[]
         listm.append("all")
         listm.append(month)
         
         return render(request,'shop/show.html',{'detail':t,'user':user,'month':listm,'msg':msg})
    else:
        return render(request,'flower/home.html')
def cart(request):
      user = request.session["user"]
      t=cartlist.objects.filter(cname=user)
      if len(t)>0:
        return render(request,'shop/cart.html',{'product':t,'cart':t})
      else:
          return render(request,'shop/cart.html',{'msg':'no items in cart'})



def purchase(request):
   if request.method == "POST":
         user=request.session["user"]
     
         list1=[]
         list2=[]
         list3=[]
         r=0
         t=cartlist.objects.filter(cname=user)
         if(len(t)<=0):
              return render(request,'shop/cart.html',{'msg':'no items in cart'})

         for i in t:

             dict1={}
             
             E = request.POST[i.img]
             if  E!='0':
                 dict1["product"]=i.pname
                 dict1["quantity"]=int(E)
                 dict1["cost"]=int(E)*int(i.cost)
                 dict1["picture"]=i.img
                 r=r+dict1["cost"]
                 no="*"
                 purchaseproduct = str(i.pname)+str(no)+str(E)+"="+str(i.cost*int(E))
                 list1.append(dict1)
                 list2.append(purchaseproduct)
                 list3.append(dict1['picture'])
     
         ordno=1
         cartproduct[user]=list1
         while True:
             if purchasedetail.objects.filter(orderno=ordno).exists():
                     ordno+=1
             else:
                    purchasedetail.objects.create(orderno=ordno)
                    break
         if request.session['admin']:
            orderby=request.session["admin"]
         else:
            orderby=user
         global commitpurchase 
         commitpurchase = purchasedetail(cname=user,orderno=ordno,productdetails=list2,totalcost=r,img=list3,status='tobedelivered',date=str(DATE),orderby=orderby)  
         t=product.objects.all()
         for i in cartproduct[user]:
             pname=i["product"]
             for i in t:
                 if i.pname==pname:
                     if i.itemavail<=0:
                         t=product.objects.all()
                         return render(request,'shop/show.html',{'msg':"the product has been sold out now",'detail':t,'user':user})
                         

         return render(request,'shop/purchase.html',{'list':cartproduct[user],'totalcost':r,'user':user,'orderno':ordno})
      
   else:
          return render(request,'flower/login.html')
def confirmorder(request):
    if request.method =="POST":
        user=request.session['user']
        orderno=request.POST['orderno']
        phone=request.POST['phone']
        string=str(phone)

        r=0
        productlist=[]
        pimage=[]
        productname=[]
        cancel=0
        for i in cartproduct[user]:
            dict3={} 
            products=i["product"]
            quantity=i["quantity"]
            cost=i["cost"]
            image=i["picture"]
            remove = request.POST.get(products, False);
            
            if remove:
                cancel=1
                
            else:
               dict3['product']=products
               dict3['quantity']=quantity
               dict3['cost']=cost
               dict3['picture']=image
               r=r+cost
               productlist.append(dict3)
               no="*"
               purchaseproduct=str(product)+str(no)+str(quantity)+"="+str(cost)
               productname.append(purchaseproduct)
               pimage.append(image)
        if request.session["admin"]:
            orderby=request.session["admin"]
        else:
            orderby=user
        
        if cancel==1:
                  global commitpurchase
                  commitpurchase = purchasedetail(cname=user,orderno=orderno,productdetails=productname,totalcost=r,img=pimage,status='tobedelivered',date=str(DATE),orderby=orderby)
        if len(productlist)==0:
            purchasedetail.objects.filter(orderno=orderno).delete()
            t=product.objects.all()
            listm=[]
            listm.append("all")
            listm.append(month)
            return render(request,'shop/show.html',{"msg":"No ORDER HAS BEEN PLACED",'user':user,'detail':t,'month':listm})  
        commitpurchase.save()
        for i in productlist:
            pname=i['product']
            quantity=i['quantity']
            t=product.objects.all()
            for i in t:
               if pname==i.pname:
                  avail=i.itemavail-int(quantity)
                  if avail<=0:
                      stock="no"
                  else:
                      stock="yes"
                  product.objects.filter(pname=pname).update(itemavail=avail,stockavailable=stock)
        if customer.objects.filter(phonenumber=str(phone)).exists():
                 e=customer.objects.all()
                 for i in e:
                     if i.phonenumber==str(phone):
                         i.orderno.append(orderno)
                         customer.objects.filter(phonenumber=phone).update(orderno=i.orderno)



             
        else:
            order=[]
            order.append(orderno)
            customer.objects.create(phonenumber=phone,orderno=order,cname=orderby)
        return render(request,'shop/orderconfirm.html',{'user':user,'orderno':orderno,'product':productlist,'totalcost':r})
    else:
        return show(request)
def showorder(request):
    if request.session['user']:
        user=request.session['user']
        p=purchasedetail.objects.filter(cname=user)
        orderno=''
        
        for i in p:
            j="cancelorder"
            remove = request.POST.get(str(i.orderno),False)
            if remove==j:
                purchasedetail.objects.filter(orderno=i.orderno).update(status='cancelled')
                orderno="orderno"+str(i.orderno)+"hasbeencancelled"
        detail=purchasedetail.objects.filter(cname=user)
        filtr=request.POST.get('apply',False)
        if filtr=="delivered":
            detail=purchasedetail.objects.filter(cname=user,status='delivered')
        elif filtr=="cancelledorder":
            detail=purchasedetail.objects.filter(cname=user,status='cancelled')

        elif filtr=='tobedelivered':
            detail=purchasedetail.objects.filter(cname=user,status='tobedelivered')


        return render(request,'shop/showorder.html',{'detail':detail,'user':user,'orderno':orderno})
    else:
        return show(request)
              
def logout(request):
  if request.session["user"]:
     t=cartlist.objects.filter(cname=request.session["user"])
     if len(t)>0:
       for i in t:
         cartlist.objects.filter(idno=i.idno).delete()
     request.session['user']=0
     if request.session["admin"]:
         request.session["admin"]=0
         return update(request)
     else:
         return loggedout(request)
  if request.session['shop']:
        request.session['shop']=0
        return loggedout(request)
  else:
        return render(request,'flower/home.html',{'msg':'login to continue'})


def loggedout(request):
        return render(request,'flower/home.html',{'msg':'loggedout succesfully'})

        

          
def updateproduct(request):
        if request.method=="POST":
            name=request.POST['name']
            password=request.POST["pass"]
            if staff.objects.filter(sname=name,password=password).exists() or (name=="admin" and password=="aravinthraj"):
                request.session['shop']="admin"
                return update(request)
            else:
               return render(request,'shop/adminlogin.html',{'msg':'passwordmismatch'})
        else:
            return render(request,'shop/adminlogin.html')

def insert(request):
  if request.session['shop']:
    if request.method == 'POST':
      submit=request.POST['update']
      if submit=="insert":
        pname = request.POST['pname']
        img=request.FILES['img']
        fs = FileSystemStorage()
        name=fs.save(img.name, img)
        url=fs.url(name)
        cost = request.POST['cost']
        season=request.POST['season']
        stock=request.POST['stock']
        pmodel=request.POST['pmodel']
        if stock=="yes" and (season=="all" or season==month):
            itemavail=10
        else:
            itemavail=0
        product.objects.create(pname=pname,img=url,cost=cost,season=season,pmodel=pmodel,stockavailable=stock,itemavail=itemavail)
        return render(request,'shop/update.html',{'msg':'update success'})
      elif submit=="stockupdate":
          pname = request.POST['pname']
          stock = request.POST['itemavail']
          t=product.objects.filter(pname=pname)
          if len(t)<=0:
                    return render(request,'shop/update.html',{'msg':"no items matched for update"})

          for i in t:
              stockavailable="no"
              if i.season==month or i.season=="all":
                  if int(stock)>=1:
                      stockavailable="yes"
              
          product.objects.filter(pname=pname).update(itemavail=stock,stockavailable=stockavailable)
          return update(request)
     

      elif submit=="costupdate":
         pname = request.POST['pname']
         cost = request.POST['cost']
         t=product.objects.filter(pname=pname)
         if len(t)<=0:
                    return render(request,'shop/update.html',{'msg':"no items matched for update"})

         product.objects.filter(pname=pname).update(cost=cost)
         return update(request)
      elif submit=="finditem":
            pname = request.POST['pname']
            t=product.objects.filter(pname=pname)
            if len(t)>=1:
                 return render(request,'shop/update.html',{'msg':"item found",'detail':t})
            elif pname=="all":
                t=product.objects.all()
                return render(request,'shop/update.html',{'msg':"item found",'detail':t})

            else:
                 return render(request,'shop/update.html',{'msg':"no item  found"})
      elif submit=="findbyorder":
        orderno=request.POST['orderno']
        t=purchasedetail.objects.filter(orderno=orderno)
        w=customer.objects.all()
        for i in w:
            for j in i.orderno:
                if int(j)==int(orderno):
                   w=customer.objects.filter(cname=i.cname)
                   break
            else:
                 continue
        return render(request,'shop/update.html',{'msg':"details found",'details':t,'detail1':w})
      elif submit=="findbycustomer":
         t=tempcn.objects.all()
         for i in t:
             tempcn.objects.filter(orderno=i.orderno).delete()
         cname=request.POST['cname']
         t=purchasedetail.objects.filter(cname=cname)
         f=customer.objects.filter(cname=cname)
         if cname=="all":
             t=purchasedetail.objects.all()
             f=customer.objects.all()
         if len(t)>=1:
             return render(request,'shop/update.html',{'msg':"details found",'details':t,'detail1':f})
         else:
              if len(t)==0:
                     cname=cname.lower()
                     A=cname[0]+cname[1]
                     v="^"+str(A)+".*$"
                     t=purchasedetail.objects.all()
                     for i in t:
                         p=i.cname
                         p=str(p).lower()
                         x=re.search(v,p)
                         if (x):
                            tempcn.objects.create(cname=i.cname,orderno=i.orderno,totalcost=i.totalcost,productdetails=i.productdetails,status=i.status,date=i.date,orderby=i.orderby)
                         else:
                            continue
                     t=tempcn.objects.all()
                     if len(t)>=1:              
                        return render(request,'shop/update.html',{'msg':"some details found",'details':t})
                     else:
                        return render(request,'shop/update.html',{'msg':"details not found"})
      elif submit=="shop":
              user=request.POST['cname']
              request.session["user"]="admin"
              request.session["admin"]=user
              return show(request)
      elif submit=="deleteitem":
          pname=request.POST['pname']
          product.objects.filter(pname=pname).delete()
          return render(request,'shop/update.html',{'msg':"product deleted"})
      elif submit=="cancelorder":
          orderno=request.POST['orderno']
          purchasedetail.objects.filter(orderno=orderno).update(status="cancelled")
          return render(request,'shop/update.html',{'msg':"order cancelled"})

      elif submit=="delivered":
          orderno=request.POST['orderno']
          purchasedetail.objects.filter(orderno=orderno).update(status="delivered")
          return render(request,'shop/update.html',{'msg':"order status updated"})
      elif submit=="todaysbusiness" or submit=="totalbusiness":
          if submit=="todaysbusiness":
              t=purchasedetail.objects.filter(date=DATE)
          if submit=="totalbusiness":
              t=purchasedetail.objects.all()
          today=0
          for i in t:
              if i.totalcost==None:
                   continue
              today=today+int(i.totalcost)
          return render(request,'shop/update.html',{'today':'TOTAL:'+str(today)+' rupees'})
      elif submit=="addstaff":
          sname=request.POST['sname']
          phonenumber=request.POST['phone']
          salary=request.POST['salary']
          password=request.POST['password']
          if staff.objects.filter(phonenumber=phonenumber).exists():
                        return render(request,'shop/update.html',{'msg':"staff phonenumber exists"})
          else:
              staff.objects.create(sname=sname,phonenumber=phonenumber,salary=salary,password=password,dateofjoining=str(DATE))
              allstaff.objects.create(sname=sname,phonenumber=phonenumber,salary=salary,dateofjoining=str(DATE))
              return render(request,'shop/update.html',{'msg':"staff added"})
      elif submit=="salaryupdate":
          phonenumber=request.POST['phone']
          salary=request.POST['salary']

          if staff.objects.filter(phonenumber=phonenumber).exists():
                staff.objects.filter(phonenumber=phonenumber).update(salary=salary)
                allstaff.objects.filter(phonenumber=phonenumber).update(salary=salary)
                return render(request,'shop/update.html',{'msg':"salary updated"})
          elif allstaff.objects.filter(phonenumber=phonenumber).exists():
               allstaff.objects.filter(phonenumber=phonenumber).update(salary=salary)
               return render(request,'shop/update.html',{'msg':"salary updated"})


          else:
                return render(request,'shop/update.html',{'msg':"staff not exist"})
      elif submit=="removestaff":
                phonenumber=request.POST['phone']
                if staff.objects.filter(phonenumber=phonenumber).exists():
                       staff.objects.filter(phonenumber=phonenumber).delete()
                       allstaff.objects.filter(phonenumber=phonenumber).delete()
                       return render(request,'shop/update.html',{'msg':"staff removed"})

                elif allstaff.objects.filter(phonenumber=phonenumber).exists():
                        allstaff.objects.filter(phonenumber=phonenumber).delete()
                        return render(request,'shop/update.html',{'msg':"staff removed"})





                else:
                      return render(request,'shop/update.html',{'msg':"staff not exist"})
      elif submit=="addnewstaff":
           sname=request.POST['sname']
           phonenumber=request.POST['phone']
           salary=request.POST['salary']
           if allstaff.objects.filter(phonenumber=phonenumber).exists():
                        return render(request,'shop/update.html',{'msg':"staff phonenumber exists"})
           else:
              allstaff.objects.create(sname=sname,phonenumber=phonenumber,salary=salary,dateofjoining=str(DATE))
              return render(request,'shop/update.html',{'msg':"staff added"})
      elif  submit=="tobedelivered":
         t=purchasedetail.objects.filter(status="tobedelivered")
         if len(t)>0:
           return render(request,'shop/update.html',{'details':t})
         else:
           return render(request,'shop/update.html',{'msg':"no orders pending"})
      elif submit=="findstaffbyname":
          sname=request.POST['sname']
          if sname=="all":
              t=allstaff.objects.all()
              return render(request,'shop/update.html',{'sdetail':t})


          elif allstaff.objects.filter(sname=sname).exists():
              t=allstaff.objects.filter(sname=sname)
              return render(request,'shop/update.html',{'sdetail':t})

          else:
              return render(request,'shop/update.html',{'msg':"no staff found"})
      elif submit=="findstaffbynumber":
          phonenumber=request.POST['phone']
          t= allstaff.objects.filter(phonenumber=phonenumber)
          if len(t)>0:
               return render(request,'shop/update.html',{'sdetail':t})
          else:
              return render(request,'shop/update.html',{'msg':"no staff found"})





  else:
                  return render(request,'shop/adminlogin.html')
       











   

          
def update(request):
   if request.session['shop']:
      return render(request,'shop/update.html')
   else:
       return render(request,'shop/adminlogin.html')
  

        
        



             

# Create your views here.