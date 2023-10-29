import socket
import json



#request = {
#        "url": "https://",
#        "format" : "360p",
#        "trim" : {
#            "start" : "00:01:20",
#            "end" : "00:00:35",
#            }
#}

class Client:
    def __init__(self,server_ip:str, server_port:int): 
        self.ip = server_ip
        self.port = server_port

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((self.ip, self.port))
        self.session(server)  
    def session(self, server) : 
        request_msg  = json.dumps({
                "url" : "https://www.youtube.com/watch?v=PivpCKEiQOQ",
                "format" : "480",
                "trim" : {
                    "start" : "00:02:30",
                    "end" : "00:04:00",
                    }
                
        })
        server.send(request_msg.encode())
        self.get_video(server)

    def get_video(self, s) :
        res_code = s.recv(1024).decode()
        if res_code == "Ok" : 
            print("Video available")
            self.receive_data(s)
        elif res_code == "Err" :
            print("Error while fetching video")
        else :
            print("Unknown code :", res_code)
    def receive_data(self,s) :  
        filename = input("Enter the filename: ")
        with open("{}.mp4".format(filename), "wb") as f : 
            print("Writing to file...")
            while True :
                chunk = s.recv(2048);
                print(chunk)
                if chunk != b'': 
                    f.write(chunk)
                else :
                    print("data received completely")
                    break
            print("data written to file")

        print("video contents written to file successfully") 
if __name__ == '__main__' : 
    Client(server_ip="127.0.0.1", server_port=8080)


