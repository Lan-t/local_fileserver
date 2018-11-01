# -*- coding: utf-8 -*-

from http.server import HTTPServer, SimpleHTTPRequestHandler
import mosules

class MyHandler(SimpleHTTPRequestHandler):

    def do_GET(self):

        c = mosules.get_class(self.path)
        body = c.make_res_body()
        
        l = f'''\
=======GET=======
addr:     {str(self.client_address[0])}
port:     {str(self.client_address[1])}
date:     {self.date_time_string()}
req_line: {self.requestline}
-----headers-----
{str(self.headers)}
=================
'''

        log(l)

        self.send_response(c.status_num)
        self.send_header('Content-type', c.content_type)
        self.send_header('Content-length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        data = b''

        try:
            content_len = int(self.headers.get('content-length'))
            data = self.rfile.read(content_len)
        except TypeError:
            pass
        
        c = mosules.post_class(self.path, data)
        body = c.save_file()

        l = f'''\
=======POST======
addr:     {str(self.client_address[0])}
port:     {str(self.client_address[1])}
date:     {self.date_time_string()}
req_line: {self.requestline}
-----headers-----
{str(self.headers)}
=================
'''

        log(l)
        self.send_response(c.status_num)
        self.send_header('Content-type', c.content_type)
        self.send_header('Content-length', len(body))
        self.end_headers()
        self.wfile.write(body)

def log(message):
    open('log', 'a').write(message)

host = ''
port = 80
httpd = HTTPServer((host, port), MyHandler)
print('serving at port', port)
httpd.serve_forever()

