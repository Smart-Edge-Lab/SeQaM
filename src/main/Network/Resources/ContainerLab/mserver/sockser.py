#import socket
#from PIL import Image
#import io

# Server configuration
#HOST = '172.22.174.198'  # Server's IP address
#PORT = 8080        # Port to listen on

from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi

class ImageReceiver(BaseHTTPRequestHandler):
    def do_POST(self):
        content_type, _ = cgi.parse_header(self.headers['Content-Type'])
        if content_type == 'multipart/form-data':
            form_data = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            if 'image' in form_data:
                image_file = form_data['image']
                # You can save the image file or process it as needed
                with open('received_image.jpg', 'wb') as f:
                    f.write(image_file.file.read())
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'Image received successfully')
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Image not found in request')
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid Content-Type')

def run_server(port=8080):
    #server_address = ('172.22.174.198', port)
    server_address = ('', port)
    httpd = HTTPServer(server_address, ImageReceiver)
    print(f'Starting server on  {server_address} port  {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()

