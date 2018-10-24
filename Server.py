# -*- coding: utf-8 -*-

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import urllib.parse
import pathlib
import glob
import shutil

class MyHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        body = b""
        drive = 'C'
        encode = 'UTF-8'
        urlencode = 'UTF-8'
        dirdownload = False
        print(self.path)
        parse_url = urllib.parse.urlparse(self.path)
        path = parse_url.path
        query = parse_query(parse_url.query)
        
        keys = query.keys()
        if 'drive' in keys:drive = query['drive']
        if 'encode' in keys:encode = query['encode']
        if 'urlencode' in keys:urlencode = query['urlencode']
        if 'dirdownload' in keys:
            if query['dirdownload'] == 'true':
                dirdownload = True

        path = urllib.parse.unquote(path, urlencode)

        path = parse_path_os(path, drive)

        body = make_res_body(path, parse_url.query, dirdownload, encode)

        

        self.send_response(200)
        #self.send_header('Content-type', 'text; charset='+encode)
        self.send_header('Content-length', len(body))
        self.end_headers()
        self.wfile.write(body)

def parse_query(query):
    if query == '':
        return {}

    query_list = query.split('&')
    query_dic = {}
    for q in query_list:
        key, value = q.split('=')
        query_dic[key] = value
    return query_dic

def parse_path_os(path, drive='C'):
    if os.name == 'nt':
        return drive + ':' + path.replace('/', os.sep)
    elif os.name == 'posix':
        return path

def parse_path_url(path):
    if os.name == 'nt':
        return path[2:].replace(os.sep, '/')
    elif os.name == 'posix':
        return path
   
def make_res_body(path, query, zipflag, encode='UTF-8'):
    if os.path.isdir(path):
        if zipflag:
            return make_zip(path)
        path_list = [ i for i in glob.glob(path.rstrip(os.sep) + os.sep + '*') ]
        dir_list = []
        file_list = []

        for i in range(len(path_list)):
            if os.path.isdir(path_list[i]):
                path_list[i] += os.sep
                dir_list.append(path_list[i])
            else:
                file_list.append(path_list[i])

        return make_html(path, query, encode, dir_list, file_list)

    elif os.path.isfile(path):
        return open(path, 'rb').read()


def make_html(path, query, encode, dir_list, file_list):
    url_path = parse_path_url(path)
    back = '/'.join(url_path.split('/')[:-2])+'/'
    body =\
f'''<html>
<head>
<title>{path}</title>
</head>

<body>
<p><a href="{url_path}?{query}&dirdownload=true">download</a></p>
<p><a href="{back}?{query}">back</a></p>
<h1>directory</h1>
<br/>
'''
    for d in dir_list:
        href = parse_path_url(d)
        body +=\
f'''
<p><a href="{href}?{query}">{d}</a></p>
'''
    # end for

    body += '<h1>file</h1>\n'

    for f in file_list:
        href = parse_path_url(f)
        body +=\
f'''
<p><a href="{href}?{query}">{f}</a></p>
'''
    #end for

    return  body.encode(encode)
    
def make_zip(path):
    shutil.make_archive(os.sep+'tmp_zip', 'zip', path)
    ziptmp = open(os.sep+'tmp_zip.zip', 'rb').read()
    os.remove(os.sep+'tmp_zip.zip')
    return ziptmp


host = ''
port = 80
httpd = HTTPServer((host, port), MyHandler)
print('serving at port', port)
httpd.serve_forever()

