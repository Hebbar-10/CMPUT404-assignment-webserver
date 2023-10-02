#  coding: utf-8 
import socketserver
import os
import mimetypes

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        # Receive the client's request and decode it from bytes to a string.
        self.data = self.request.recv(1024).strip().decode('utf-8')
        print("Got a request of: %s\n" % self.data)
        
        # Extract the first line of the request, containing the HTTP method, path, and version.
        request_line = self.data.splitlines()[0]
        method, path, version = request_line.split(' ')
        
        # Ensure that the server only processes GET requests. If not, respond with a 405 status.
        if method != 'GET':
            self.send_response(405, "Method Not Allowed")
            return
        
        # Construct the entire path to the requested file/directory.
        base_dir = os.path.abspath('./www')
        file_path = os.path.abspath(os.path.join(base_dir, path.lstrip('/')))
        
        # Ensure that the requested path is within the allowed directory. If not, respond with a 404 status.
        if not file_path.startswith(base_dir):
            self.send_response(404, "Not Found")
            return
        
        # If the requested path is a directory, handle potential redirects or default file serving.
        if os.path.isdir(file_path):
            # If the directory path doesn't end with '/', redirect to the correct path.
            if not path.endswith('/'):
                correct_path = path + '/'
                self.send_redirect(correct_path)
                return
            # Serve the default 'index.html' file for directory requests.
            file_path = os.path.join(file_path, 'index.html')
        
        # Attempt to read and serve the requested file.
        try:
            # Determine the MIME type of the file for proper serving.
            mime_type, _ = mimetypes.guess_type(file_path)
            with open(file_path, 'r') as file:
                content = file.read()
            self.send_response(200, "OK", content, mime_type)
        except FileNotFoundError:
            # If the file doesn't exist, respond with a 404 status.
            self.send_response(404, "Not Found")

    def send_response(self, status_code, status_message, content="", content_type="text/html"):
        # Construct the standard HTTP response headers.
        response_headers = f"HTTP/1.1 {status_code} {status_message}\r\n" \
                        f"Content-Type: {content_type}\r\n" \
                        f"Content-Length: {len(content)}\r\n" \
                        "\r\n"
        # Combine headers and content, then send the response to the client.
        http_response = response_headers + content
        self.request.sendall(http_response.encode('utf-8'))

    def send_redirect(self, location):
        # Construct the HTTP headers for a 301 redirect response.
        response_headers = f"HTTP/1.1 301 Moved Permanently\r\n" \
                        f"Location: {location}\r\n" \
                        "\r\n"
        # Send the redirect response to the client.
        self.request.sendall(response_headers.encode('utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
