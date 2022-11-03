import socket
import signal
import sys
import random

# Read a command line argument for the port where the server
# must run.
port = 8080
if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    print("Using default port 8080")

# Start a listening server socket on the port
sock = socket.socket()
sock.bind(('', port))
sock.listen(2)

### Contents of pages we will serve.
# Login form
login_form = """
   <form action = "http://localhost:%d" method = "post">
   Name: <input type = "text" name = "username">  <br/>
   Password: <input type = "text" name = "password" /> <br/>
   <input type = "submit" value = "Submit" />
   </form>
""" % port
# Default: Login page.
login_page = "<h1>Please login</h1>" + login_form
# Error page for bad credentials
bad_creds_page = "<h1>Bad user/pass! Try again</h1>" + login_form
# Successful logout
logout_page = "<h1>Logged out successfully</h1>" + login_form
# A part of the page that will be displayed after successful
# login or the presentation of a valid cookie
success_page = """
   <h1>Welcome!</h1>
   <form action="http://localhost:%d" method = "post">
   <input type = "hidden" name = "action" value = "logout" />
   <input type = "submit" value = "Click here to logout" />
   </form>
   <br/><br/>
   <h1>Your secret data is here:</h1>
""" % port

#### Helper functions
# Printing.
def print_value(tag, value):
    print("Here is the", tag)
    print("\"\"\"")
    print(value)
    print("\"\"\"")
    print()

# Signal handler for graceful exit
def sigint_handler(sig, frame):
    print('Finishing up by closing listening socket...')
    sock.close()
    sys.exit(0)
# Register the signal handler
signal.signal(signal.SIGINT, sigint_handler)


# TODO: put your application logic here!
# Read login credentials for all the users
# Read secret data of all the users
#extract user and password data
data = ''
file_path = './passwords.txt'
with open(file_path, 'r') as f:
    data = f.readlines()
    
name_pass_dict = {} #stores user->password dict
for l in data:
    name, pwd = l.strip().split(' ')
    name_pass_dict[name] = pwd
#print(name_pass_dict)

secret_data = ''
# extract secret data
secret_path = './secrets.txt'
with open(secret_path, 'r') as f:
    secret_data = f.readlines()

secret_dict = {} #stores user-> secret phrase dict
for l in secret_data:
    name, pwd = l.strip().split(' ')
    secret_dict[name] = pwd
#print(secret_dict)



### Loop to accept incoming HTTP connections and respond.
cookie_dict = {}
while True:
    client, addr = sock.accept()
    req = client.recv(1024)

    # Let's pick the headers and entity body apart
    header_body = req.split('\r\n\r\n')
    headers = header_body[0]
    body = '' if len(header_body) == 1 else header_body[1]
    #print_value('headers', headers)
    #print_value('entity body', body)

    # TODO: Put your application logic here!
    # Parse headers and body and perform various actions

    # You need to set the variables:
    # (1) `html_content_to_send` => add the HTML content you'd
    # like to send to the client.
    # Right now, we just send the default login page.
    #print("headers:")
    #print(headers)
    #print("headers:")
    #print(headers)
    #print(body)
   
    if("GET" in headers):
        print("got GET")
        html_content_to_send = login_page
        headers_to_send = ''
    elif("POST" in headers):
        print("got POST")
        #print("headers")
        #print(headers)
        #print("body")
        #print(body)
        if("action=logout" in body):
            print("user requested log out")
            cookie_number = headers.split("Cookie: token=")[1].split("\n")[0]
            if(cookie_number in cookie_dict):
                print("expiring cookie {}".format(cookie_number))
                cookie_dict.pop(cookie_number)
            else:
                print("cookie {} not found but logging out anyway".format(cookie_number))
            headers_to_send = 'Set-Cookie: token=; expires=Thu, 01 Jan 1970 00:00:00 GMT\r\n'
            html_content_to_send = login_page
        elif("Cookie" in headers):
            
            cookie_number = headers.split("Cookie: token=")[1].split("\n")[0]
            if(cookie_number in cookie_dict):
                print("valid cookie: {}".format(cookie_number))
                user_posted = cookie_dict[cookie_number]
                html_content_to_send = success_page + secret_dict[user_posted]
                
            else:
                print("cookie number {} not valid".format(cookie_number))
                #print(type(cookie_number))
                html_content_to_send = bad_creds_page
            headers_to_send = ''
        else:
            post_dict = {}
            post_data = body.split("&")
            #print("post_data")
            #print(post_data)
            for data in post_data:
                if len(data.split("=")) == 2:
                    k, v = data.split("=")
                    post_dict[k] = v
            #print(post_dict)

            #print("headers:")
            #print(headers)
            
                
            if("username" not in post_dict or "password" not in post_dict):
                html_content_to_send = bad_creds_page
            
            else:
                user_posted = post_dict["username"]
                password_posted = post_dict["password"]
                if(user_posted not in name_pass_dict):
                    html_content_to_send = bad_creds_page
                elif(name_pass_dict[user_posted] == password_posted):
                    html_content_to_send = success_page + secret_dict[user_posted]
                    cookie_number = str(random.getrandbits(64))
                    cookie_dict[cookie_number] = user_posted
                    headers_to_send = 'Set-Cookie: token=' + str(cookie_number) + '\r\n'
                    print("logged in, sending cookie {}".format(cookie_number))
                    #print(type(cookie_number))
                else:
                    html_content_to_send = bad_creds_page
            
    # But other possibilities exist, including
    # html_content_to_send = success_page + <secret>
    # html_content_to_send = bad_creds_page
    # html_content_to_send = logout_page
    
    # (2) `headers_to_send` => add any additional headers
    # you'd like to send the client?
    # Right now, we don't send any extra headers.
    

    # Construct and send the final response
    response  = 'HTTP/1.1 200 OK\r\n'
    response += headers_to_send
    response += 'Content-Type: text/html\r\n\r\n'
    response += html_content_to_send
    #print_value('response', response)    
    client.send(response)
    client.close()
    
    print("Served one request/connection!")
    print

# We will never actually get here.
# Close the listening socket
sock.close()
