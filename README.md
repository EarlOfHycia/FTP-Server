# Documentation

## server.py

Script for a Simple Password-Protected **FTP Server** which serves requests of storing and retrieving  *.txt* and *.jpg* files.

## client.py

Script for logging into the server started using above script.

Clients can be normal users or Admin.  
Clients(except Admin) need to first sign up providing a nickname, a username, and a password.  
After signing up, clients can login.

**Normal Users** can view all the files stored on the server, upload and download *.txt* and *.jpg* files.  
`LIST`: To list all the files on the server  
`STOR <file>`: To upload a file  
`RETR <file>`: To download a file

**Admin** can ban/unban and add/delete *Normal Users* from the Server  
`BAN <username>`: To ban a user  
`UNBAN <username>`: To unban a user  
`DEL <username>`: To remove a user from the server permanantly  
`ADD <nickname> <username> <password>`: To add a user with given details

**NOTE**: The Admin login credentials are: USERNAME-"dny" and PASSWORD-"123" 