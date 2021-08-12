from django_cassandra_engine.models import DjangoCassandraModel
from cassandra.cqlengine import columns
 
class signup(DjangoCassandraModel):
       username = columns.Text(max_length = 30,primary_key=True)
       password = columns.Text(max_length =30)
       email = columns.Text(max_length =30)



# Create your models here.
