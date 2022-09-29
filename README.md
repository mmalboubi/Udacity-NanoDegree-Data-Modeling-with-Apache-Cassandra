# Udacity-NanoDegree-Data-Modeling-with-Apache-Cassandra
In this project, we work on data modeling using Cassandra Database where we first create a cluster and a keyspace. In designing Cassandra DBs, the main point is that DBs are created based on the required queries. So, for each main query we need to create a database. 

There are 3 main queries and, accordingly, 3 data DBs are created as follows:
1) Table session_item_songs is created for the query: Give me the artist, song title and song's length in the music app history that was heard during sessionId = xxx, and itemInSession = yyy
2) Table user_session_songs is created for the query: Give me only the following: name of artist, song (sorted by itemInSession) and user (first and last name) for userid = xxx, sessionid = yyy
3) Table users_songs is created for the query: Give me every user name (first and last) in my music app history who listened to the song ‘xxx’

These DBs store data from “event_datafile_new.csv” at the root. This file is processed to create denormalized dataset required for creating the above DBs. By running the .ipynb file we can create the DBs, insert data into them and then query the DBs.
