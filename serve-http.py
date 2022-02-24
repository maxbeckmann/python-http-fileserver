#!/usr/bin/env python3

import socketserver
import http.server
import cgi
from pathlib import Path
 
PORT = 8000

def read_in_chunks(file_object, content_len, chunk_size=1024):
    while content_len > chunk_size:
        yield file_object.read(chunk_size)
        content_len -= chunk_size
    yield file_object.read(content_len)
    

class SimpleHTTPRequestHandlerWithUploads(http.server.SimpleHTTPRequestHandler):
 
    def do_POST(self):
        """Serve a POST request."""
        files_ok = {}
        try:
            content_type, options = cgi.parse_header(self.headers['Content-Type'])
            if content_type == 'multipart/form-data':
                files_ok = self.handle_post_upload_form()
            else:
                # use this as a catch-all solution for any other content type beyond the special-formatted multipart form. 
                # usually 'application/x-www-form-urlencoded', but e.g. CertReq will state 'application/json'
                files_ok = self.handle_post_plain_body()

            assert files_ok is not {}
            status_msg = ""
            for file_path in files_ok:
                status_msg += f"{file_path} OK\n"
            self.send_status(200, status_msg)
                
        except Exception as ex:
            self.send_status(400, f"fail: {str(ex)}\n")

    def handle_post_plain_body(self):
        """
        Reads binary file contents from the request body and writes to the path indicated by the request location. 
        Creates new files and directories where necessary. 

        NOTE: You must specify an output location as the original file name is not transmitted along the file. 
        """
        content_length = int(self.headers['content-length'])
        contents = read_in_chunks(self.rfile, content_length)
        file_path = Path() / self.path[1:]
        if file_path.is_dir():
            raise RuntimeError("location is a directory")
                
        self.store_file(file_path, contents)
        return {file_path}
    
    def handle_post_upload_form(self):
        """
        Handles file uploads from web forms (or tools mimicking that convention). 
        Reads binary file contents from the POST request variable `file` and stores them to the location stated by the request variable `filename`. 
        Also accepts multiple file uploads at once, when the POST request array `file[]` was used instead. 
        Creates new files and directories where necessary. 
        """
        files_ok = {}
        form = cgi.FieldStorage( fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST', 'CONTENT_TYPE':self.headers['Content-Type'], })
        if isinstance(form["file"], list):
            for record in form["file"]:
                file_path = Path() / record.filename
                contents = read_in_chunks(record.file)
                self.store_file(file_path, contents)
                files_ok |= {file_path}
        else:
            file_path = Path() / form["file"].filename
            contents = read_in_chunks(form["file"].file)
            self.store_file(file_path, contents)
            files_ok |= {file_path}
        return files_ok

    def store_file(self, file_path, contents):
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb+") as out_file:
            for chunk in contents:
                out_file.write(chunk)
    
    def send_status(self, status_code, message):
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(message)))
        self.end_headers()
        self.wfile.write(message.encode())
 
if __name__ == '__main__':
    Handler = SimpleHTTPRequestHandlerWithUploads

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()