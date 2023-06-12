import socket
import json
import http.client
import ssl

# Client class
class Neuroengine:
    server_address:str
    server_port:int
    service_name:str
    verify_ssl:bool
    key:str


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
        data = {
            'message': prompt,
            'temperature': temperature,
            'top_p':top_p,
            'top_k':top_k,
            'repetition_penalty':repetition_penalty,
            'max_new_len':max_new_len,
            'seed':seed
        }
        json_data = json.dumps(data)

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
        return response["reply"]

# Server class, use it to share your LLM

class NeuroengineServer:
    server_address:str
    server_port:int
    service_name:str
    key:str


    #__init__(): Initializes a new instance of the neuroengine Server class
    #Parameters:
    #   server_address: A string representing the server address.
    #   server_port: An integer representing the server port.
    #   service_name: A string representing the name of the service.
    #   key (optional): A string representing an optional key.
    def __init__(self, server_address="api.neuroengine.ai",server_port=4444):
        self.server_address=server_address
        self.server_port=server_port
        # Create a socket object
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Wrap the socket with SSL
        ssl_context = ssl.create_default_context()
        self.ssl_socket = ssl_context.wrap_socket(self.client_socket,server_hostname=server_address)
        # Connect to the server
        self.ssl_socket.connect((server_address,server_port))

    def login(self,service_name,service_key):
        # Login to server
        logindata={}
        logindata["user"]=service_name
        logindata["key"]=service_key
        data=json.dumps(logindata)
        self.ssl_socket.sendall(data.encode())
        response = self.ssl_socket.recv(10240)
        if (response.strip().decode()=="OK"):
            return(0)
        else:
            self.ssl_socket.shutdown(socket.SHUT_WR)
            return(-1)

    def listen(self,answerCallback):
            # Listen for data from the server
        while True:
            data = self.ssl_socket.recv(10240)
            if not data:
                continue
            received_string = data.decode()
            request = json.loads(received_string)
            # We received a keep-alive ping, ignore
            if ("ping" in request):
                continue
            # Process request
            response=answerCallback(request).encode()
            # Send len
            self.ssl_socket.sendall(("%08X" % len(response)).encode())
            # Send message
            self.ssl_socket.sendall(response)
