"""
#### 2-Clause BSD licence:

Copyright 2023 Alfredo Ortega @ortegaalfredo

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import socket
import select
import time
import json
import http.client
import ssl
# Client class
class Neuroengine:
    #__init__(): Initializes a new instance of the neuroengine class.
    #Parameters:
    #   server_address: A string representing the server address.
    #   server_port: An integer representing the server port.
    #   service_name: A string representing the name of the service.
    #   key (optional): A string representing an optional key.
    #   verify_ssl (optional): A boolean indicating whether to verify SSL certificates or not.

    def __init__(self, service_name, server_address="api.neuroengine.ai",server_port=443,key="",verify_ssl=True):
        self.server_address=server_address
        self.server_port=server_port
        self.service_name=service_name
        self.key=key
        self.verify_ssl=verify_ssl

    #getmodel(): Return a list of active LLM models in the server

    def getModels(self):
        command = {'command': 'getmodels' }
        response=self.send(command)
        return response

    #request(): Sends a request to the server and returns the response.
    #Parameters:
    #   prompt: A string representing the prompt message.
    #   temperature (optional): A float indicating the randomness of the response.
    #   top_p (optional): A float representing the cumulative probability for top-p sampling.
    #   top_k (optional): An integer representing the number of top-k tokens to consider.
    #   repetition_penalty (optional): A float indicating the penalty for repeating tokens.
    #   max_new_len (optional): An integer representing the maximum length of the generated response.
    #   seed (optional): An integer representing the seed for random number generation.
    #Returns:
    #   A string containing the response from the server.

    def request(self, prompt,temperature=1.0,top_p=0.9,top_k=40,repetition_penalty=1.2,max_new_len=128,seed=0):
        # Create a JSON message
        command = {
            'message': prompt,
            'temperature': temperature,
            'top_p':top_p,
            'top_k':top_k,
            'repetition_penalty':repetition_penalty,
            'max_new_len':max_new_len,
            'seed':seed
        }
        try:
            response=self.send(command)
        except:
            response={}
            response["reply"]="Connection error"
        return response["reply"]

    def send(self,command):
        json_data = json.dumps(command)
        # Create an HTTP connection
        if (self.verify_ssl):
            connection = http.client.HTTPSConnection(self.server_address, self.server_port)
        else:
            connection = http.client.HTTPSConnection(self.server_address, self.server_port, context = ssl._create_unverified_context())

        # Send a POST request with the JSON message
        headers = {'Content-Type': 'application/json'}
        connection.request('POST', f'/{self.service_name}', json_data, headers)

        # Get the response from the server
        response = connection.getresponse().read().decode()
        connection.close()
        response = json.loads(response)
        return response

# Server class, use it to share your LLM

class NeuroengineServer:

    #__init__(): Initializes a new instance of the neuroengine Server class
    #Parameters:
    #   server_address: A string representing the server address.
    #   server_port: An integer representing the server port.
    #   service_name: A string representing the name of the service.
    #   key (optional): A string representing an optional key.
    def __init__(self, server_address="api.neuroengine.ai",server_port=4444):
        self.server_address=server_address
        self.server_port=server_port

    def login(self,service_name,service_key):
        # Create a socket object
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Wrap the socket with SSL
        ssl_context = ssl.create_default_context()
        self.ssl_socket = ssl_context.wrap_socket(self.client_socket,server_hostname=self.server_address)
        # Connect to the server
        self.ssl_socket.connect((self.server_address,self.server_port))
        # Login to server
        logindata={}
        logindata["user"]=service_name
        logindata["key"]=service_key
        data=json.dumps(logindata)
        self.ssl_socket.sendall(data.encode())
        response = self.ssl_socket.recv(10240)
        if (response.strip().decode()=="OK"):
            self.service_name=service_name
            self.service_key=service_key
            self.pingtime=time.time()
            return(0)
        else:
            self.ssl_socket.shutdown(socket.SHUT_WR)
            return(-1)

    def is_socket_closed(self,sock):
        if time.time()-self.pingtime>60:
            return True
        else: 
            return False

    def has_bytes_to_receive(self,sock):
        try:
            r, _, _ = select.select([sock], [], [], 0)
            return sock in r
        except socket.error:
            return False


    def listen(self,answerCallback):
            # Listen for data from the server
        while True:
            # Attempt reconnect if server is down
            while(self.is_socket_closed(self.client_socket)):
                print("Neuroengine.ai: connection error, retrying...")
                time.sleep(5)
                try:
                    self.login(self.service_name,self.service_key)
                except: pass
            try:
                # Check if there are bytes in the socket
                if self.has_bytes_to_receive(self.ssl_socket)==False:
                    time.sleep(1)
                    continue
                # Read bytes
                data = self.ssl_socket.recv(10240)
                if not data:
                    self.pingtime=0
                    continue
                received_string = data.decode()
                request = json.loads(received_string)
                # We received a keep-alive ping
                if ("ping" in request):
                    self.pingtime=time.time()
                    continue
                # Process request
                response=answerCallback(request).encode()
                # Send len
                self.ssl_socket.sendall(("%08X" % len(response)).encode())
                # Send message
                self.ssl_socket.sendall(response)
            except Exception as e:
                print(f"Error: {str(e)}")
                self.pingtime=0
                pass
