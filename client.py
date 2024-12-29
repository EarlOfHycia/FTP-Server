import socket
import os
import sys
import time

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip_addr = socket.gethostbyname(socket.gethostname())
port = 3456

# connection_message
connection_message = (f"\nWhat do you want to do?"
                      f"\n1.Signup"
                      f"\n2.Login"
                      f"\n3.Admin Login"
                      f"\n4.Exit"
                      f"\nEnter your choice (Number)--->")

try:
    client.connect((ip_addr, port))

except:
    sys.exit(f"\nThe server is not running\n")

while 1:
    # print(f"\n waiting for message")
    message = client.recv(100).decode('utf-8')
    # print(f"\n message received")

    if message == "FINAL_EXIT":
        print(f"\nThank you for your visit")
        break

    elif message == "connection_message":
        print(connection_message)
        choice = input()
        client.send(choice.encode())

    elif message == "no_user":
        print(f"\nIncorrect Credentials Entered...")

    elif message == "admin_login":
        try_username = input(f"\nUsername--->")
        client.send(try_username.encode())
        client.recv(100)
        try_password = input(f"\nPassword--->")
        client.send(try_password.encode())

    elif message == "admin_options":
        print(f"\nWelcome ADMIN..."
              f"\nUse the following commands to perform actions as required:"
              f"\nBAN : To ban a user from the server (Please provide only one username at a time)"
              f"\nUNBAN : To ban a user from the server (Please provide only one username at a time)"
              f"\nDEL : To remove a user from the server (Please provide only one username at a time)"
              f"\nADD : To add a user to the server (Please provide Name, Username and Password separated by spaces as displayed below"
              f"\nUsage ::: ADD <Name> <Username> <Password>"
              f"\nEXIT : To log out of the server")

        command = input(f"\nEnter Your Command--->")

        while command != "EXIT":
            client.send(command.encode())
            command = input("\nEnter Your Command--->")

        client.send("EXIT".encode())

    elif message == "wrong admin login":
        print(f"\nIncorrect Credentials...")

    elif message == "banned":
        print(f"\nYou have been banned from the Server...")

    elif message == "nick":
        nick = input(f"\nNickname cannot contain \"-\" character and spaces..."
                     f"\nYour Nickname--->")
        client.send(nick.encode())

    elif message == "username":
        username = input(f"\nUsername cannot contain spaces..."
                         f"\nChoose your username--->")
        client.send(username.encode())
        status_check = client.recv(100).decode('utf-8')
        # print(f"\n Received status_check {status_check}")
        while status_check == "1":
            username = input(f"\nUsername already taken.\nPlease choose another username--->")
            client.send(username.encode())
            status_check = client.recv(100).decode('utf-8')
            # print(f"\n received status check {status_check}")
        client.send("tp".encode())

    elif message == "password":
        password = input(f"\nChoose your password--->")
        r_password = input(f"\nRe-enter your password--->")

        while password != r_password:
            print(f"\nPasswords don't match...\nPlease try again...")
            password = input(f"\nChoose your password--->")
            r_password = input(f"\nRe-enter your password--->")

        client.send(password.encode())

    elif message == "login":
        try_user_name = input(f"\nUsername--->")
        client.send(try_user_name.encode())
        client.recv(100)
        try_password = input(f"\nPassword--->")
        client.send(try_password.encode())

    elif message == "error1":
        print(f"\nPlease select a valid option...")

    elif message == "quit":
        print(f"\nYou have logged out successfully...")
        client.close()
        break

    elif message == "function_options":
        print(f"\nUse the following commands to perform actions as required:"
              f"\nLIST : To list all the files in the server"
              f"\nRETR : To retrieve a file from the server (Please give only one file as argument)"
              f"\nSTOR : To store a file on the server (Please give only one file as argument)"
              f"\nEXIT : To exit/log out of the server")

        commandS = ""
        commandR = ""

        while commandR != "EXIT":
            commandS = input("\nEnter Your Command--->\n")
            client.send(commandS.encode())
            commandR = client.recv(100).decode('utf-8')

            if commandR == "LIST":
                filename = client.recv(100).decode('utf-8')
                while filename != "LIST_END":
                    print(f"{filename}")
                    filename = client.recv(100).decode('utf-8')

            elif commandR == "RETR":
                result = client.recv(100).decode('utf-8')
                if result == "no_file":
                    print(f"\nNo such file exists on the server...")

                else:
                    list = commandS.split()
                    extension = list[1].split('.')[1]

                    if extension == "txt":
                        txt_size_bytes = client.recv(4)
                        txt_size = int.from_bytes(txt_size_bytes, byteorder='big')
                        txt_data = ""
                        while len(txt_data) < txt_size:
                            chunk = client.recv(txt_size - len(txt_data)).decode('utf-8')
                            if not chunk:
                                break

                            txt_data += chunk

                        with open(list[1], 'w') as file:
                            file.write(txt_data)

                        print(f"\n{list[1]} received")

                    if extension == "jpg":
                        image_size_bytes = client.recv(4)
                        image_size = int.from_bytes(image_size_bytes, byteorder='big')

                        image_data = b''
                        while len(image_data) < image_size:
                            chunk = client.recv(image_size - len(image_data))
                            if not chunk:
                                break
                            image_data += chunk

                        with open(list[1], 'wb') as file:
                            file.write(image_data)

                        print(f"\n{list[1]} received...")

            elif commandR == "STOR":

                flist = os.listdir()

                words = commandS.split()
                extension = words[1].split('.')[1]

                index = - 1
                count = 0
                for f in flist:
                    if f != words[1]:
                        count += 1
                        continue
                    index = count

                if index == -1:
                    print(f"\nNo such file exists in current directory...")

                else:
                    print(f"\nInitiating upload of file {flist[index]}...")
                    pcount = 1
                    if extension == "txt":
                        file = open(words[1], 'r')
                        txt_data = file.read()
                        client.sendall(len(txt_data).to_bytes(length=4, byteorder='big'))
                        time.sleep(0.00001)
                        client.sendall(txt_data.encode())
                        file.close()
                        if pcount:
                            print(f"\n{words[1]} has been stored on the server...")
                            pcount -= 1
                        time.sleep(1)

                    if extension == "jpg":
                        with open(words[1], 'rb') as file:
                            image_data = file.read()

                        client.sendall(len(image_data).to_bytes(4, byteorder='big'))
                        time.sleep(0.0001)
                        client.sendall(image_data)
                    print(f"\n{words[1]} has been stored on the server...")
                    time.sleep(1)

            elif commandR == "EXIT":
                break

            else:
                print(f"\nInvalid Command...")

        print(f"\nYou have logged out of the server...")

    else:
        print(f"\nreceived garbage: {message}")

client.close()
