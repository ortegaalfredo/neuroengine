<p align="center" width="100%">
<a ><img src="logoai-small.jpg" alt="neuroengine" style="width: 20%; min-width: 300px; display: block; margin: auto;"></a>
</p>

# Neuroengine LLM API server

NeuroEngine is a platform that allows users to share their LLM (Large Language Model) creations with others. The service provides an easy-to-use JSON API for accessing these models, as well as a optional user-friendly web interface where you can interact with the model as a chat-bot.

Main site is located at [https://www.neuroengine.ai](https://www.neuroengine.ai)

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

## Streaming requests

Initial support for streaming is present. For this, you only need to provide an additional parameter: a randomly generated streaming key.

With this key, you can retrieve partial requests, and repeatedly call the API until all tokens are retrieved. For an example, see [streaming-example.py](https://github.com/ortegaalfredo/neuroengine/blob/main/examples/streaming-example.py).

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


# Documentation

## API request:

### Constructor
    api=Neuroengine(service_name=service_name)

Service name is the identifier of the LLM as showed on the neuroengine.ai site, or via the 'getmodels()' api call.

### request()
This API call sends a request to the server and returns the response.

    def request(self,
                prompt,
                temperature=1.0,
                top_p=0.9,
                top_k=40,
                repetition_penalty=1.2,
                max_new_len=128,
                seed=0,
                raw=False,
                tries=5)
Example:

```
service_name = 'Neuroengine-Large'
prompt="Hi LLM!"
api=Neuroengine(service_name=service_name)
response=api.request(prompt)
print(response)
```
#### Parameter description:

        - prompt (str): The text prompt that will be used to generate the response.
        - temperature (float): Controls the randomness of the output. Higher values (e.g., 1.0) make the output more random, while lower values (e.g., 0.2) make it more deterministic. Default is 1.0.
        - top_p (float): Determines the cumulative probability threshold for generating the output. Tokens with cumulative probability higher than this value are considered for sampling. Default is 0.9.
        - top_k (int): Controls the number of top tokens to consider for generating the output. Only the top-k tokens are used for sampling. Default is 40.
        - repetition_penalty (float): Controls the penalty applied to repeated tokens in the output. Higher values (e.g., 1.2) discourage repeating tokens, while lower values (e.g., 0.8) encourage repetition. Default is 1.2.
        - max_new_len (int): Controls the maximum length of the generated response. The response will be truncated if its length exceeds this value. Default is 128.
        - seed (int): The random seed for generating the response. Use this to control the repeatability of the output. Default is 0.
        - raw (bool): If True, the prompt will be send straight to the model without any pre-prompt or system prompt. Default is False.
        - tries (int): The number of attempts to send the request in case of errors before giving up. Default is 5.
	- gettokens (int): The amont of tokens to get in each streaming call, default is 20. This is a partial response, you must call several times using the same streamkey until the function return an empty string.
        - streamkey (str): An unique ID to identify your stream session. Generate this ID securely, at least 32 bytes. If no streamkey is provided, the request will be not streamed, and the complete reply will be returned in a single call.    
Returns:
        - str: The generated response or an error message, depending on the success of the request.

#### Raw Json Call
To make a raw json api call, do a HTTPS POST request to https://api.neuroengine.ai/{name}/ (name is the LLM model name, see getModels()) with the following format:

```
{
    "message": "Hello LLM",
    "temperature": 1.0,
    "top_p": 0.9,
    "top_k": 40,
    "repetition_penalty": 1.2,
    "max_new_len": 128,
    "seed": 0,
    "raw": "False",
    "key" : "key1234",
    "gettokens": 20

}
```
Field description:

    -"message" (str): The input text prompt or message that will be used as the basis for generating the response. This is a required parameter.

    -"temperature" (float): A parameter controlling the randomness of the generated output. Higher values (e.g., 1.0) make the output more random, while lower values (e.g., 0.2) make it more deterministic.

    -"top_p" (float): A parameter that determines the cumulative probability threshold for token sampling. Tokens with cumulative probability higher than this value are considered for sampling.

    -"top_k" (int): The number of top tokens to consider for token sampling. Only the most probable top_k tokens are used for generating the output.

    -"repetition_penalty" (float): A penalty applied to repeated tokens in the generated output. Higher values (e.g., 1.2) discourage repeating tokens, while lower values (e.g., 0.8) encourage repetition.

    -"max_new_len" (int): The maximum length of the generated response. If the response length exceeds this value, it will be truncated.

    -"seed" (int): A random seed used for generating the response. It helps control the reproducibility of the generated output.

    -"raw" (str): If True, the prompt will be send straight to the model without any pre-prompt or system prompt. Default is False.

    -"gettokens"(int): The amont of tokens to get in each streaming call, default is 20. This is a partial response, you must call several times using the same streamkey until the function return an empty string.

    -"key" (str): An unique ID to identify your stream session. Generate this ID securely, at least 32 bytes. If no streamkey is provided, the request will be not streamed, and the complete reply will be returned in a single call.


These parameters collectively define the settings and characteristics of the response generated based on the provided input prompt.

#### Raw Json Response

The raw Json response has this form:

    {"reply": "LLM Reply", "errorcode": 0}

Field description:

    -"reply" (str): The response message generated by the LLM.

    -"errorcode" (int): An error code indicating the status of the response. Here, the value is 0, which signifies a successful response without any errors.

### getModels()

Return a list of active LLM models in the server

Example:

```
api=Neuroengine("Neuroengine-Large")
models=api.getModels()
```

Return an array of dictionaries with information about available models, Ej.:

```
[
  {'numreq': 19754,
   'connected': True,
   'comment': 'LLM description',
   'operator': '@ortegaalfredo',
   'name': 'Neuroengine-Large',
   'queuelen': 0},
]
```

Description of parameters:
    -"numreq" (int): The number of requests made or processed so far in the server.

    -"connected" (bool): A boolean value (true or false) indicating whether the LLM is currently connected and available to use.

    -"comment" (str): A description or comment associated with the LLM, containing information as size and license.

    -"operator" (str): Information about the operator or user responsible for the LLM.

    -"name" (str): The name of the LLM. This is the identification used in the request() API.

    -"queuelen" (int): The length of the LLM request queue. This signify the number of queries waiting in a queue for processing.
