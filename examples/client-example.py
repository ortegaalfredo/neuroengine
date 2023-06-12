from neuroengine import Neuroengine

# This code provides an example of how to utilize the neuroengine.ai API 
# to send prompts to a published service and receive corresponding answers.

# Define the server address and port
service_name = 'MYGPT'
prompt="Hello!"

api=Neuroengine(service_name=service_name)
response=api.request(prompt)

print(f"Prompt: {prompt}\nResponse: {response}")
