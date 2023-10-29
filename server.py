import threading
from slugify import slugify
from os.path import basename, splitext
from pytube import Stream
import socket
import json
from pytube import YouTube

#request = {
#        "url": "https://",
#        "format" : "360p",
#        "trim" : {
#            "start" : "00:01:20",
#            "end" : "00:00:35",
#            }
#}

class Server:
    def __init__(self, ip, port) : 
        self.ip = ip
        self.port = port
        self.req_vals = ['url', 'format']
        print("[+]Server started")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.ip, self.port))
        server.listen()
        print(" UP and RUNNING ")
        self.get_clients(server)
    def get_clients(self,server) : 
        while True : 
            conn, addr = server.accept()
            print("connection received from ", addr[0])
            threading.Thread(target=self.session, args=(conn,)).start()
    def session(self, conn) : 
        while True :
            request = conn.recv(1024).decode()
            print("request from client : ", request)
            json_req = json.loads(request)
            print("request converted to json") 
            if self.check_req(req_list=self.req_vals, elems=[i for i in json_req.keys()]) : 
                print('entered if block')
                url = json_req.get('url')
                format = json_req.get('format')+"p"
                if json_req.get('trim') : 
                    trim = json_req.get('trim')
                    print(trim)
                else : 
                    trim = None
                    print('no trim provided')
                print(url, format) 
                if trim : 
                    self.process_video(url=url, res=format, trim=trim, conn=conn)
                    break
                else : 
                    self.process_video(url=url, res=format, conn=conn)
                    break
    def process_video(self, url:str, res:str, conn,  trim=None) :
            yt = YouTube(url)
            streams = yt.streams
            print(streams)
            if res in [i.resolution for i in streams] :
                stream:Stream = streams.filter(res=res).first()

                if not stream.includes_audio_track : 
                    print("[+]Downloading Audio...")
                    audio = self.download_audio(streams,yt.title)
                    print("[+]Audio downloaded successfully at ", audio)
                    print("[+]Stream found \nProceeding to download")
                    location = stream.download('downloads', filename=slugify(yt.title))
                    print('downloaded at ', location)
                    location, return_code = self.merge_audio_video(audio, location, is_trim = True if trim else False)
                    if return_code == 0 : 
                        conn.send("Ok".encode())
                    else : 
                        conn.send("Err".encode())
                    if trim: 
                        print("[+]Trimming video...")
                        file = self.trim_video(frm=trim.get('start'),to=trim.get('end'), video=location, length=yt.length)
                        if file : 
                            print("[/]Sending raw data...")
                            self.send_raw(path=file, conn=conn)
                            print("[+]Data sent successfully")
                        else : 
                            print("Error while trimming video!")
                        return
                    else : 
                        self.send_raw(path=location, conn=conn)
                else :
                    print("[+]Stream found \nProceeding to download video")
                    location = stream.download('downloads', filename=slugify(yt.title))
                    conn.send("Ok".encode())
                    print('downloaded at ', location)
                    if trim : 
                        print("[+]Trimming video...")
                        file = self.trim_video(frm=trim.get('start'),to=trim.get('end'), video=location, length=yt.length)
                        if file : 
                            print("[/]Sending file...")
                            self.send_raw(path=file, conn=conn)
                            print("[+]Data sent successfullly")
                    else : 
                       self.send_raw(path=location,conn=conn) 
     
            else : 
                print("stream not found...\nPlease try again")
#            if stream : 
#                print("stream found for res {}: \n {}\nProceeding to download...".format(res, stream))
#                location = stream.first().download();
#                print("Video successfully downloaded at ", location)
#            else : 
#                print("stream not found for res {}", res); 
     

    def get_file_contents(self, filename:str) :
        with open(filename, 'rb') as f : 
            contents = f.read()
            return contents
    def send_raw(self, path, conn) :
        print(conn)
        from os.path import isfile
        if isfile(path) : 
            file_contents = self.get_file_contents(path)
            print(len(file_contents))
            print("[\\]Sending data to client...")
            conn.sendall(file_contents)
            print("[+]Data sent successfully")

    def get_sec(self, time_str:str) : 
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + int(s) 
    def trim_video(self, frm:str, to:str, video, length:int) : 
        from time import strftime, gmtime;
        from subprocess import run

        frm_s, to_s = self.get_sec(frm), self.get_sec(to)        
        print(frm_s, to_s, video, length)
        if (frm_s < length)  :
            print("entered second if")
            duration = strftime("%H:%M:%S", gmtime(to_s - frm_s))
            print("duration of the video is : ", duration)
            output_file = "output/completed_" + slugify(splitext(video)[0])+".mp4"
            print(output_file)
            # cnge aac below
            command = 'ffmpeg -y -i {i} -ss {s} -t {t}  -c:v copy -c:a aac "{o}"'.format(i=video,s=frm, t=duration, o=output_file)

            run(command, shell=True)
            print("Successfully trimmed the video")
            return output_file
        return None
    def merge_audio_video(self, audio_file:str, video_filename:str, is_trim=True) :
        print("[MErging video...]")
        import subprocess
        from slugify import slugify
        
        if is_trim :     
            output_file = "downloads/completed_" + slugify(basename(splitext(video_filename)[0]))+ ".mp4"
        else : 
            output_file = "output/completed_" + slugify(basename(splitext(video_filename)[0]))+ ".mp4"

        print(video_filename, audio_file, output_file)
        command = 'ffmpeg -i "{v}" -i "{a}" -c:v copy -c:a aac -strict experimental "{o}" -y'.format(v=video_filename, a=audio_file, o=output_file) 
        return_code =  subprocess.run(command, shell=True).returncode
        print("[+]Audio & Video successfully merged")
        return (output_file, return_code)
    
    def download_audio(self, streams, title) : 
        from os.path import splitext;
        from os import remove
        import subprocess
    
        loc = streams.get_audio_only().download('downloads', slugify(title))
        filename = splitext(loc)[0] + ".mp3"
        subprocess.run('ffmpeg -i "{i}" "{o}" -y'.format(i=loc, o=filename),shell=True)
        remove(loc)

        return filename

    def check_req(self, req_list:list, elems:list, exception='trim') : 
        for elem in elems : 
            if elem in req_list : 
                pass
            elif elem == exception : 
                pass
            else :
                print('error, ', elem)
                break
        else : 
            return True
        return False 
if __name__ == '__main__' : 
    Server(ip="127.0.0.1", port=8080);
