"""
#### 2-Clause BSD licence:

Copyright 2023 Alfredo Ortega @ortegaalfredo

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from neuroengine import Neuroengine
import sys,os
# This code provides an example of how to utilize the neuroengine.ai API 
# to send prompts to a published service and receive the answer as a stream.

# Define the service name
service_name = 'Neuroengine-Large'

# Prompt
prompt="Hello, write a poem"
print(f"Prompt: {prompt}\nResponse:")

#Create the API object
api=Neuroengine(service_name=service_name)

#The streamkey string must be a unique ID to identify your new stream
streamkey=os.urandom(32).hex()
print(f"Key: {streamkey}")

# Stream loop
while(True):
    response=api.request(prompt,streamkey=streamkey,max_new_len=1000)
    if response=='': #EOS
        print('')
        break
    sys.stdout.write(response)
    sys.stdout.flush()

