import random
import signal
import socket
import sys
import time

class Server:
    def __init__(self, port):
        self.port = port
        self.socket = socket.socket()
        self.socket.bind(('', port))
        login_form = """
            <form action = "http://localhost:%d" method = "post">
            Name: <input type = "text" name = "username">  <br/>
            Password: <input type = "text" name = "password" /> <br/>
            <input type = "submit" value = "Submit" />
            </form>
            """ % port
        self.login_page = "<h1>Please login</h1>" + login_form
        self.bad_creds_page = "<h1>Bad user/pass! Try again</h1>" + login_form
        self.logout_page = "<h1>Logged out successfully</h1>" + login_form
        self.success_page = """
            <h1>Welcome!</h1>
            <form action="http://localhost:%d" method = "post">
            <input type = "hidden" name = "action" value = "logout" />
            <input type = "submit" value = "Click here to logout" />
            </form>
            <br/><br/>
            <h1>Your secret data is here:</h1>
            """ % port
        self.name_pass_dict = {}
        self.secret_dict = {}
        self.extract()
        

    def start_new(self):
        self.socket.listen(2)
        client, addr = self.socket.accept()
        return client

    def run_server(self):
        client = self.start_new()
        while(True):
            
            print("got connection")
            req = client.recv(100)
            print("got data")
            
            header_body = req.split('\r\n\r\n')
            headers = header_body[0]
            
            body = '' if len(header_body) == 1 else header_body[1]
            print("headers:")
            print(headers)
            print("body")
            print(body)
            print()
            if("GET" in headers):
                print("GET was in headers")
                self.send_login_page(client)
            elif("POST" in headers):
                self.send_success_page(client)
            elif(req == ''):
                print("closing and starting new")
                client.close()
                client = self.start_new()
            #client.close()
            
        self.start_new()
        first_req = self.client.recv(100)
        headers, body = self.rec_and_clean(first_req)
        print(body)
        #
        #print("about to print")
        #print("body: ", body)
        #user, password = self.get_user_and_pass_from_body(body)
        return
        if(user not in self.name_pass_dict):
            print("user does not exist")
            self.send_bad_creds_page()

        elif(self.name_pass_dict[user] != password):
            print("wrong password for username")
            self.send_bad_creds_page()

        else:
            print("correct user and pass")
            self.send_success_page()


        print("served one connection")
        self.client.close()
        
        


    def send_login_page(self, client):
        self.send_response(client, '', self.login_page)

    def send_success_page(self, client):
        self.send_response(client, '', self.success_page)

    def send_logout_page(self, client):
        rand_val = random.getrandbits(64)
        headers_to_send = 'Set-Cookie: token=' + str(rand_val) + '\r\n'
        self.send_response(client, headers_to_send, self.logout_page)

    def send_bad_creds_page(self, client):
        self.send_response(client, '', self.bad_creds_page)

    
    def send_response(self, client, headers_to_send, html_content_to_send):
        response  = 'HTTP/1.1 200 OK\r\n'
        response += headers_to_send
        response += 'Content-Type: text/html\r\n\r\n'
        response += html_content_to_send
        self.print_value('response', response)    
        client.send(response)
        

    def get_user_and_pass_from_body(self, body):
        post_dict = {}
        
        post_data = body.split("&")
        for data in post_data:
            if len(data.split("=")) == 2:
                k, v = data.split("=")
                post_dict[k] = v
        user = post_dict['username']
        psw = post_dict['password']
        return (user, psw)
        

    def rec_and_clean(self, req):
        
        header_body = req.split('\r\n\r\n')
        headers = header_body[0]
        body = '' if len(header_body) == 1 else header_body[1]
        
        #self.print_value('headers', headers)
        #self.print_value('entity body', body)
        return (headers, body)

    def print_value(self, tag, value):
        print("Here is the", tag)
        print("\"\"\"")
        print(value)
        print("\"\"\"")
        print()

    def extract(self):
        file_path = './passwords.txt'
        with open(file_path, 'r') as f:
            data = f.readlines()
            
        for l in data:
            name, pwd = l.strip().split(' ')
            self.name_pass_dict[name] = pwd
        
        # extract secret data
        secret_path = './secrets.txt'
        with open(file_path, 'r') as f:
            secret_data = f.readlines()
        
        for l in secret_data:
            name, pwd = l.strip().split(' ')
            self.secret_dict[name] = pwd

    def close_connection(self):
        self.socket.close()

    def sigint_handler(self, sig, frame):
        print('Finishing up by closing listening socket...')
        self.socket.close()
        sys.exit(0)

if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    server = Server(port)
    signal.signal(signal.SIGINT, server.sigint_handler)

    server.run_server()
