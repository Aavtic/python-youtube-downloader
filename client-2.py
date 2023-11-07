import requests
import json

# Define the server URL
port = input("enter the port to connect to : ")
if not port : 
    server_url = 'http://127.0.0.1:8080'  # Replace with the actual server URL
else : 
    server_url = f'http://127.0.0.1:{int(port)}'

# JSON data to send in the GET request
json_data = {
                "url" : "https://www.youtube.com/watch?v=s7wLYzRJt3s",
                "format" : "360",
                "trim" : {
                    "start" : "00:01:00",
                    "end" : "00:01:30",
                    }
                
        }
# Send the GET request with JSON data in the body
response = requests.post(server_url, data=json.dumps(json_data))
print(response.content)

with open("received.mp4", 'wb') as f : 
    f.write(response.content)
print("{} bytes written".format(len(response.content)))
# Check the response
if response.status_code == 200:
    print('Response from server:')
    print(response.text)
else:
    print(f'Error: {response.status_code}')
