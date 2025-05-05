import http.server
import socketserver
import subprocess
import json
from itertools import groupby

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print ("MY SERVER: I got a GET request.")
        if self.path == '/event/network/bandwidth':
            print ("MY SERVER: The GET request is for the Interface URL.")
            self.path = 'interface_page.html'
        if self.path == '/event/network/load':
            print ("MY SERVER: The GET request is for the client URL.")
            self.path = 'client_page.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        print ("MY SERVER: I got a POST request.")
        if self.path == '/event/network/bandwidth':
            print ("MY SERVER: The POST request is for the /network/bandwidth.")
       
        
        
            content_length = int(self.headers['Content-Length'])
            post_body = self.rfile.read(content_length)
            data = json.loads(post_body)
            print ("MY SERVER: The post data I received from the request has following data:\n", data)

            #post_data_str = post_data_bytes.decode("UTF-8")
            #list_of_post_data = post_data_str.split('&')
            
            #post_data_dict = {}
            #for item in list_of_post_data:
             #   variable, value = item.split('=')
              #  post_data_dict[variable] = value

           # print ("MY SERVER: I have changed the post data to a dict and here it is:\n", post_data_dict)
    
            rate = int(data['mbps'])
            print ("Rate is:\n", rate)
            srate=str(rate)
            ttime=(data['time'])

            sttime=""
            tsymbol=""
            for s in ttime:
                if s.isdigit():
                    sttime=sttime+s
                else:
                    tsymbol=tsymbol+s
            waittime=int(sttime)
            realtime=0

            if tsymbol=='s':
                realtime=waittime
            if tsymbol=='m':
                realtime=waittime*60
            if tsymbol=='h':
                realtime=waittime*3600

            siftime=str(realtime)

            print ("Time is:\n", realtime)
            print ("Time Sym:\n", tsymbol)
            subprocess.Popen(['./manageInterface.sh %s %s ' %(srate,siftime)], shell = True) 

            self.path = 'interface_okay.html'

        if self.path == '/event/network/load':
            print ("MY SERVER: The POST request is for the /client URL.")
        
            content_length = int(self.headers['Content-Length'])
            post_body = self.rfile.read(content_length)
            data = json.loads(post_body)
            print ("MY SERVER: The post data I received from the request has following data:\n", data)


                
            size = int(data['mb'])
            ssize=str(size)
            print ("Load is:\n", size)
            ttime=(data['time'])

            sttime=""
            tsymbol=""
            for s in ttime:
                if s.isdigit():
                    sttime=sttime+s
                else:
                    tsymbol=tsymbol+s
            waittime=int(sttime)
            realtime=0

            if tsymbol=='s':
                realtime=waittime
            if tsymbol=='m':
                realtime=waittime*60
            if tsymbol=='h':
                realtime=waittime*3600

            print ("Time in load is:\n", realtime)
            print ("Time Sym:\n", tsymbol)
            scltime=str(realtime)
            

            subprocess.Popen(['./manageLoad.sh %s %s ' %(ssize,scltime)], shell = True)
            self.path = 'client_okay.html'


        return http.server.SimpleHTTPRequestHandler.do_GET(self)
 

# Create an object of the above class
handler_object = MyHttpRequestHandler

PORT = 8000
my_server = socketserver.TCPServer(("", PORT), handler_object)
print ("MY SERVER \n", PORT)
# Start the server
my_server.serve_forever()