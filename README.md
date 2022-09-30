# Udacity-NanoDegree-Data-Modeling-with-Apache-Cassandra
In this project, we work on data modeling using Cassandra Database where we first create a cluster and a keyspace. In designing Cassandra DBs, the main point is that DBs are created based on the required queries. So, for each main query we need to create a database. Accordingly, 

For Query 1, the Primary Key has two fields: sessionId is the partition key, and itemInSession is clustering key. Partitioning is done by sessionId and within that partition, rows are ordered by the itemInSession.

For Query 2, the Primary Key has a nested form with a composite partition key "(user_id, session_id)" and clustering key "item_in_session" where rows in each partiotion are ordered by the clustering key.

For Query 3, the Primary Key is song and partition key is user_id and rows in each partiotion are ordered by the clustering key.

There are 3 main queries and, accordingly, 3 data DBs are created as follows:
1) Table session_item_songs is created for the query: Give me the artist, song title and song's length in the music app history that was heard during sessionId = xxx, and itemInSession = yyy

SELECT artist, song_title, song_length FROM session_item_songs WHERE sessionId = 338 AND itemInSession = 4

2) Table user_session_songs is created for the query: Give me only the following: name of artist, song (sorted by itemInSession) and user (first and last name) for userid = xxx, sessionid = yyy

SELECT artist , song , first_name , last_name FROM user_session_songs WHERE user_id = 10 and session_id = 182 order by item_in_session 

3) Table users_songs is created for the query: Give me every user name (first and last) in my music app history who listened to the song ‘xxx’

SELECT first_name , last_name FROM users_songs WHERE song = 'All Hands Against His Own'

The DBs store data from “event_datafile_new.csv” at the root. This file is processed to create denormalized dataset required for creating the above DBs. By running the .ipynb file we can create the DBs, insert data into them and then query the DBs
