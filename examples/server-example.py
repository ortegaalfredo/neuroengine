from neuroengine import NeuroengineServer

# This code provides an example of how to log in to neuroengine.ai, 
# share a local language model (LLM), and reply to prompts using the API

service="MYGPT"
service_key="DEMO"

def answerMessage(request):
    response='{"reply":"This is the LLM"}'
    print(f"Request received. Answer: {response}")
    return response

# Connect to server
server=NeuroengineServer()

# Login
if (server.login(service,service_key) <0):
    print("Error logging in.")
    exit(0)
else:
    print("Logged in!")

# Serve forever
server.listen(answerMessage)
