<p align="center" width="100%">
<a ><img src="logoai-small.jpg" alt="neuroengine" style="width: 20%; min-width: 300px; display: block; margin: auto;"></a>
</p>

# Neuroengine LLM API server

NeuroEngine is a platform that allows users to share their LLM (Large Language Model) creations with others. The service provides an easy-to-use JSON API for accessing these models, as well as a optional user-friendly web interface where you can interact with the model as a chat-bot.

## Connecting to an existing LLM:

This is an example python client, you will need the LLM service name (I.E. 'MYGPT' or 'Neuroengine-Large') and an optional key:

```
from neuroengine import Neuroengine

# Define the server address and port
service_name = 'Neuroengine-Large'
api=Neuroengine(service_name=service_name)

prompt="Hello!"
response=api.request(prompt)

print(f"Prompt: {prompt}\nResponse: {response}")
```

Many models do not require a key for access, but they may still be subject to usage limits or restrictions (quotas).

## Sharing your LLM

To use a locally hosted LLM with the Neuroengine API, you'll need to follow these steps:

1. Choose a unique name for your service and obtain a service key from the web interface.
2. Use this python code to connect to the Neuroengine API and share your LLM:

```
from neuroengine import NeuroengineServer

# share a local language model (LLM), and reply to prompts using the API

service="MYGPT"
service_key="DEMOKEY"

def answerMessage(prompt):
    # Here you connect to your LLM and answer the prompt
    response='{"reply":"This is the LLM"}'
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
```

Once you login, a web chatbot is available at https://www.neuroengine.ai/servicename 

Note: Currently, Neuroengine does not locally host any Large Language Models (LLM). It acts as a proxy, allowing remote users to connect to locally hosted LLMs.



