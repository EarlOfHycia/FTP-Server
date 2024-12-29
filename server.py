import socket
import threading
import time
import os

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip_addr = socket.gethostbyname(socket.gethostname())
port = 3456

server.bind((ip_addr, port))

server.listen(5)
print(f"\nServer has started listening on {ip_addr}:{port}")

user_data = [['-1', '-1', '-1', '-1']]
number_of_active_clients = 0
failed_admin_login = []

# functions
def handle_signup(client):
    client.send("nick".encode())
    nick = client.recv(100).decode('utf-8')

    client.send("username".encode())
    username = client.recv(100).decode('utf-8')
    # print(f"\n Received user_name {username}")
    check = 1
    while check:
        for i in range(len(user_data)):
            # print(f"\n {i}")
            if username == user_data[i][1]:
                client.send("1".encode())
                username = client.recv(100).decode('utf-8')
                # print(f"\n received username {username}")
                break

            if i == len(user_data)-1:
                client.send("0".encode())
                check = 0
                break

    client.recv(10).decode('utf-8')
    # print("\n received garbage")
    client.send("password".encode())
    # print(f"\n sent flag password")
    password = client.recv(100).decode('utf-8')
    # print(f"\n received password")
    return [nick, username, password, "not_banned"]


def handle_login(client):
    client.send("login".encode())
    try_username = client.recv(100).decode('utf-8')
    client.send('interrupt'.encode())
    try_password = client.recv(100).decode('utf-8')
    for data in user_data:
        if try_username == data[1] and try_password == data[2]:
            if data[3] == "not_banned":
                return data
            else:
                return "-1", "-1", "-1", "-1"

    return "-0", "-0", "-0", "-0"


def handle_functions(client, user):
    client.send("function_options".encode())
    message = ""
    while message != "EXIT":
        message = client.recv(1000).decode('utf-8')
        words = message.split(" ")
        client.send(words[0].encode())

        list = os.listdir()

        # list all files
        if words[0] == "LIST":

            time.sleep(0.0001)
            for f in list:
                client.send(f.encode())
                time.sleep(0.0001)

            client.send("LIST_END".encode())

        # retrieve files
        elif words[0] == "RETR":
            index = -1
            count = 0
            for f in list:
                if f != words[1]:
                    count += 1
                    continue
                index = count

            if index == -1:
                client.send("no_file".encode())

            else:
                print(f"\nUser {user[1]} requesting file {words[1]}...")
                client.send("file_found".encode())
                time.sleep(0.00001)
                extension = words[1].split('.')[1]
                # print(f"\nextension is {extension}")

                count = 1
                if extension == "jpg":
                    with open(words[1], 'rb') as file:
                        image_data = file.read()

                    client.sendall(len(image_data).to_bytes(4, byteorder='big'))
                    time.sleep(0.0001)
                    client.sendall(image_data)
                print(f"\n{words[1]} sent to user {user[1]}...")
                time.sleep(1)

                if extension == "txt":
                    file = open(words[1], 'r')
                    txt_data = file.read()
                    client.sendall(len(txt_data).to_bytes(length=4, byteorder='big'))
                    time.sleep(0.00001)
                    client.sendall(txt_data.encode())
                    file.close()
                    if count:
                        print(f"\n{words[1]} sent to user {user[1]}...")
                        count -= 1
                    time.sleep(1)

        # store files
        elif words[0] == "STOR":
            extension = words[1].split('.')[1]

            if extension == "txt":
                txt_size_bytes = client.recv(4)
                txt_size = int.from_bytes(txt_size_bytes, byteorder='big')
                txt_data = ""
                while len(txt_data) < txt_size:
                    chunk = client.recv(txt_size - len(txt_data)).decode('utf-8')
                    if not chunk:
                        break

                    txt_data += chunk

                with open(words[1], 'w') as file:
                    file.write(txt_data)

                print(f"\n{words[1]} received from {user[1]}")

            if extension == "jpg":
                image_size_bytes = client.recv(4)
                image_size = int.from_bytes(image_size_bytes, byteorder='big')

                image_data = b''
                while len(image_data) < image_size:
                    chunk = client.recv(image_size - len(image_data))
                    if not chunk:
                        break
                    image_data += chunk

                with open(words[1], 'wb') as file:
                    file.write(image_data)

                print(f"\n{words[1]} received from {user[1]}...")

        # exit
        elif words[0] == "EXIT":
            print(f"\nUser {user[1]} has logged out of the server...")
            break

        # invalid command
        else:
            client.send("invalid_command".encode())


def handle_admin_login():
    client.send("admin_login".encode())
    try_username = client.recv(100).decode('utf-8')
    client.send("trash".encode())
    try_password = client.recv(100).decode('utf-8')

    if try_username == "dny" and try_password == "123":
        return 1

    else:
        return 0


def search_user(username):
    for user in user_data:
        if username == user[1]:
            return user


def handle_admin_functions(client):

    client.send("admin_options".encode())

    command = ""
    while command != "EXIT":
        command = client.recv(100).decode('utf-8')

        words = command.split()

        if words[0] == "BAN":
            user = search_user(words[1])
            user[3] = "banned"
            print(f"\nADMIN has banned {user[1]}")

        elif words[0] == "UNBAN":
            user = search_user(words[1])
            user[3] = "not_banned"
            print(f"\nADMIN has unbanned {user[1]}")

        elif words[0] == "DEL":
            user = search_user(words[1])
            user_data.remove(user)
            print(f"\nADMIN removed {user[1]} from the server")

        elif words[0] == "ADD":
            new_user = [words[1], words[2], words[3], "not_banned"]
            user_data.append(new_user)
            print(f"\nADMIN added {new_user[1]} to the server")

        else:
            break

    print(f"\nADMIN has logged out...")


def handle_client(client, address):
    print(f"\nConnection established with {address}")

    while 1:
        client.send("connection_message".encode())
        answer = client.recv(100).decode('utf-8')

        # client signup
        if answer == "1":
            user_data.append(handle_signup(client))

        # client login
        elif answer == "2":
            result = handle_login(client)
            if result[0] != "-1" and result[0] != "-0":
                print(f"\n{result[0]} has logged into the server")
                # client.send("login_success".encode())
                handle_functions(client, result)
            elif result[0] == "-1":
                client.send("banned".encode())
                time.sleep(0.00001)

            else:
                client.send("no_user".encode())
                time.sleep(0.00001)

        # admin login
        elif answer == "3":
            result = handle_admin_login()
            if result:
                print(f"\nADMIN has logged in...")
                handle_admin_functions(client)

            else:
                client.send("wrong admin login".encode())
                print(f"\nAn unsuccessful attempt to login as ADMIN was made.."
                      f"\nADMIN please check failed ADMIN logins list..")
                failed_admin_login.append(address)

        # exit
        elif answer == "4":
            client.send("FINAL_EXIT".encode())
            print(f"\nConnection with client {address} has closed")
            return 0

        # invalid choice
        else:
            client.send("error1".encode())
            time.sleep(0.0001)


print(f"\nWaiting for connection...")
while 1:
    client, address = server.accept()
    number_of_active_clients += 1
    print(f"\nNumber of active connections : {number_of_active_clients}")
    t = threading.Thread(target=handle_client, args=(client, address))
    t.start()
