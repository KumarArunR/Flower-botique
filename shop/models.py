from django_cassandra_engine.models import DjangoCassandraModel
from cassandra.cqlengine import columns

text=columns.Text(min_length=1) 
integer=columns.Integer()

class product(DjangoCassandraModel):
       pname = columns.Text(max_length = 30,primary_key=True)
       img = columns.Text(min_length = 2)
       cost = columns.Integer()
       stockavailable = columns.Text(max_length=20)
       itemavail=columns.Integer()
       season =columns.Text(max_length=20,default="all")
       pmodel = columns.Text(max_length=40)
class purchasedetail(DjangoCassandraModel):
       cname = columns.Text(max_length=30)
       orderno = columns.Integer(primary_key=True)
       productdetails = columns.List(value_type=text)    
       totalcost=  columns.Integer() 
       img = columns.List(value_type=text)
       status=columns.Text(max_length=30)
       date=columns.Text(max_length=30)
       orderby=columns.Text(max_length=30)
class customer(DjangoCassandraModel):
      phonenumber= columns.Text(primary_key=True,max_length=10)
      cname = columns.Text(max_length=30)
      orderno=columns.List(value_type=integer)



class cart(DjangoCassandraModel):
       idno = columns.Integer(primary_key=True)
       pname = columns.Text(max_length = 30)
       cname = columns.Text(max_length=30)
       img = columns.Text(min_length = 2)
       cost = columns.Integer()

class staff(DjangoCassandraModel):
        phonenumber= columns.Text(primary_key=True,max_length=10)
        sname = columns.Text(max_length=30)
        salary= columns.Integer() 
        password = columns.Text(max_length=30)
        dateofjoining=columns.Text(max_length=30)
class allstaff(DjangoCassandraModel):
       phonenumber= columns.Text(primary_key=True,max_length=10)
       sname = columns.Text(max_length=30)
       salary= columns.Integer() 
       dateofjoining =columns.Text(max_length=30)



        



class tempre(DjangoCassandraModel):
       pname = columns.Text(max_length = 30,primary_key=True)
       img = columns.Text(min_length = 2)
       cost = columns.Integer()
       stockavailable = columns.Text(max_length=20)
       season =columns.Text(max_length=20,default="all")
       pmodel = columns.Text(max_length=40)
class tempcn(DjangoCassandraModel):
       cname = columns.Text(max_length=30)
       orderno = columns.Integer(primary_key=True)
       productdetails = columns.List(value_type=text)    
       totalcost=  columns.Integer() 
       status=columns.Text(max_length=30)
       date=columns.Text(max_length=30)
       orderby=columns.Text(max_length=30)





# Create your models here.


# Create your models here.
