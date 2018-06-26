

# Installation documentation
# https://dev.mysql.com/doc/connector-python/en/connector-python-installation.html


import mysql.connector

config = {
  'user': 'root',
  'password': '123456',
  'host': '127.0.0.1',
  'database': 'prod_event_db',
  'raise_on_warnings': True,
  'use_pure': False,
}

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()


select_query = ("SELECT * FROM attendees")
cursor.execute(select_query)

for result in cursor:
    print result




insert_query = ("INSERT INTO elements "
              "(name, event_id) "
              "VALUES (%(name)s, %(event_id)s)")
insert_data = {
  'name': "element Name",
  'event_id': 11,
}
cursor.execute(insert_query,insert_data)
cnx.commit()



update_query = ("UPDATE  elements SET  name =  'element name' WHERE  elements.id =2")
cursor.execute(update_query)
cnx.commit()



cursor.close()
cnx.close()