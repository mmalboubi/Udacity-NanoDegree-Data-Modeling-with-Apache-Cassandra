#!/usr/bin/env python
# coding: utf-8

# # Part I. ETL Pipeline for Pre-Processing the Files

# ## PLEASE RUN THE FOLLOWING CODE FOR PRE-PROCESSING THE FILES

# #### Import Python packages 

# In[1]:


# Import Python packages 
import pandas as pd
import cassandra
import re
import os
import glob
import numpy as np
import json
import csv


# #### Creating list of filepaths to process original event csv data files

# In[2]:


# checking your current working directory
print(os.getcwd())

# Get your current folder and subfolder event data
filepath = os.getcwd() + '/event_data'

# Create a for loop to create a list of files and collect each filepath
for root, dirs, files in os.walk(filepath):
    
# join the file path and roots with the subdirectories using glob
    file_path_list = glob.glob(os.path.join(root,'*'))
    #print(file_path_list)


# #### Processing the files to create the data file csv that will be used for Apache Casssandra tables

# In[3]:


# initiating an empty list of rows that will be generated from each file
full_data_rows_list = [] 
    
# for every filepath in the file path list 
for f in file_path_list:

# reading csv file 
    with open(f, 'r', encoding = 'utf8', newline='') as csvfile: 
        # creating a csv reader object 
        csvreader = csv.reader(csvfile) 
        next(csvreader)
        
 # extracting each data row one by one and append it        
        for line in csvreader:
            #print(line)
            full_data_rows_list.append(line) 
            
# uncomment the code below if you would like to get total number of rows 
print(len(full_data_rows_list))
# uncomment the code below if you would like to check to see what the list of event data rows will look like
print(full_data_rows_list)

# creating a smaller event data csv file called event_datafile_full csv that will be used to insert data into the \
# Apache Cassandra tables
csv.register_dialect('myDialect', quoting=csv.QUOTE_ALL, skipinitialspace=True)

with open('event_datafile_new.csv', 'w', encoding = 'utf8', newline='') as f:
    writer = csv.writer(f, dialect='myDialect')
    writer.writerow(['artist','firstName','gender','itemInSession','lastName','length',                'level','location','sessionId','song','userId'])
    for row in full_data_rows_list:
        if (row[0] == ''):
            continue
        writer.writerow((row[0], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[12], row[13], row[16]))


# In[4]:


# check the number of rows in your csv file
with open('event_datafile_new.csv', 'r', encoding = 'utf8') as f:
    print(sum(1 for line in f))


# # Part II. Complete the Apache Cassandra coding portion of your project. 
# 
# ## Now you are ready to work with the CSV file titled <font color=red>event_datafile_new.csv</font>, located within the Workspace directory.  The event_datafile_new.csv contains the following columns: 
# - artist 
# - firstName of user
# - gender of user
# - item number in session
# - last name of user
# - length of the song
# - level (paid or free song)
# - location of the user
# - sessionId
# - song title
# - userId
# 
# The image below is a screenshot of what the denormalized data should appear like in the <font color=red>**event_datafile_new.csv**</font> after the code above is run:<br>
# 
# <img src="images/image_event_datafile_new.jpg">

# ## Begin writing your Apache Cassandra code in the cells below

# #### Creating a Cluster

# In[5]:


# This should make a connection to a Cassandra instance your local machine 
# (127.0.0.1)

from cassandra.cluster import Cluster
cluster = Cluster()

# To establish connection and begin executing queries, need a session
session = cluster.connect()


# #### Create Keyspace

# In[6]:



try:
    session.execute("""
    CREATE KEYSPACE IF NOT EXISTS sparkify 
    WITH REPLICATION = 
    { 'class' : 'SimpleStrategy', 'replication_factor' : 1 }"""
)

except Exception as e:
    print(e)


# #### Set Keyspace

# In[7]:


# Set KEYSPACE to the keyspace specified above
try:
    session.set_keyspace('sparkify')
except Exception as e:
    print(e)


# ### Now we need to create tables to run the following queries. Remember, with Apache Cassandra you model the database tables on the queries you want to run.

# ## Create queries to ask the following three questions of the data
# 
# ### 1. Give me the artist, song title and song's length in the music app history that was heard during  sessionId = 338, and itemInSession  = 4
# 
# 
# ### 2. Give me only the following: name of artist, song (sorted by itemInSession) and user (first and last name) for userid = 10, sessionid = 182
#     
# 
# ### 3. Give me every user name (first and last) in my music app history who listened to the song 'All Hands Against His Own'
# 
# 
# 

# In[8]:


# Createing the table for artist, song title and song's length in the music 
# app history that was heard during particular sessionID 
#with a particular itemInSession
try:
    session.execute("""
        CREATE TABLE IF NOT EXISTS session_item_songs
        (sessionId int, itemInSession int, artist text, song_title text, song_length float,
        PRIMARY KEY(sessionId, itemInSession))
        """)
except Exception as e:
    print(e)


# In[9]:


# Insert data into DB
file = 'event_datafile_new.csv'

with open(file, encoding = 'utf8') as f:
    csvreader = csv.reader(f)
    next(csvreader) # skip header
    for line in csvreader: # 8, 3, 0, 9, 5
        query = "INSERT INTO session_item_songs (sessionId, itemInSession, artist, song_title, song_length)"
        query = query + " VALUES (%s, %s, %s, %s, %s)"
        session.execute(query, (int(line[8]), int(line[3]), line[0], line[9], float(line[5])))
        
print('inserting in session_item_songs done')


# #### Do a SELECT to verify that the data have been inserted into each table

# In[10]:


# Acquire and verify data for sessionId=338 and itemInSession=4
rows = session.execute("""SELECT artist, song_title, song_length 
FROM session_item_songs WHERE sessionId = 338 AND itemInSession = 4""")

for row in rows:
    print(row.artist, row.song_title, row.song_length)


# ### COPY AND REPEAT THE ABOVE THREE CELLS FOR EACH OF THE THREE QUESTIONS

# In[11]:


# Creating a table for storing artist, song, user and sessions Info 
# to query based on userId and sessionId and itemInSession
try:
    session.execute("""
            CREATE TABLE IF NOT EXISTS  user_session_songs
                (artist text, song text, first_name text, last_name text,
                user_id int, session_id int, item_in_session int, 
                PRIMARY KEY ((user_id, session_id), item_in_session))
    """) 
except Exception as e:
    print(e)


# In[12]:


#Insert data into DB
file = 'event_datafile_new.csv'

with open(file, encoding = 'utf8') as f:
    csvreader = csv.reader(f)
    next(csvreader) 
    for line in csvreader:
        query = "INSERT INTO user_session_songs (artist, song, first_name, last_name, user_id, session_id, item_in_session)"
        query = query + " VALUES (%s, %s, %s, %s, %s, %s, %s)"
        session.execute(query, (line[0], line[9], line[1], line[4], int(line[10]), int(line[8]), int(line[3])))
print('inserting into user_session_songs is done')        


# In[13]:


#Acquire and verify data for userid = 10, sessionid = 182
rows = session.execute(""" SELECT artist , song , first_name , last_name 
FROM user_session_songs WHERE user_id = 10 and session_id = 182 order by item_in_session 
""")
for row in rows:
    print (row.artist , row.song , row.first_name , row.last_name)


# In[14]:


# Creating a table for storing user and song, user Info 
# to query based on song title
try:
    session.execute("""
            CREATE TABLE IF NOT EXISTS  users_songs
                (song text, user_id int, first_name text, last_name text,
                PRIMARY KEY (song, user_id))
    """) 
except Exception as e:
    print(e)               


# In[15]:


# Insert data into DB
file = 'event_datafile_new.csv'

with open(file, encoding = 'utf8') as f:
    csvreader = csv.reader(f)
    next(csvreader) 
    for line in csvreader:
        query = "INSERT INTO users_songs (song, user_id, first_name, last_name)"
        query = query + " VALUES (%s, %s, %s, %s)"
        session.execute(query, (line[9], int(line[10]), line[1], line[4]))
print('inserting into users_songs is done') 


# In[16]:


# Acquire and verify data for song=''All Hands Against His Own'
rows = session.execute(""" SELECT first_name , last_name 
FROM users_songs WHERE song = 'All Hands Against His Own' """)
for row in rows:
    print (row.first_name , row.last_name)


# In[ ]:





# In[ ]:





# ### Drop the tables before closing out the sessions

# In[ ]:





# In[17]:


session.execute("DROP TABLE session_item_songs")
session.execute("DROP TABLE user_session_songs")
session.execute("DROP TABLE users_songs")


# ### Close the session and cluster connection¶

# In[18]:


session.shutdown()
cluster.shutdown()


# In[ ]:





# In[ ]:




