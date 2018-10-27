# -*- coding: utf-8 -*-

import os
import urllib.parse
import pathlib
import glob
import shutil
import mimetypes


class res_class:
    path = '/'
    query = ''
    coding = 'UTF-8'

    content_type = 'text/plain'
    status_num = 400

    def set_res_head(self, num, type_s):
        self.status_num = num
        self.content_type = type_s

    @staticmethod
    def parse_path_os(path, drive='C'):
        if os.name == 'nt':
            return drive + ':' + path.replace('/', os.sep)
        elif os.name == 'posix':
            return path

    @staticmethod
    def parse_path_url(path):
        if os.name == 'nt':
            return path[2:].replace(os.sep, '/')
        elif os.name == 'posix':
            return path

    @staticmethod
    def parse_query(query):
        if query == '':
            return {}

        query_list = query.split('&')
        query_dic = {}
        for q in query_list:
            key, value = q.split('=')
            query_dic[key] = value
        return query_dic


class get_class(res_class):
    zipflag = False


    def __init__(self, req_path):
        parse_url = urllib.parse.urlparse(req_path)
        self.query = parse_url.query
        query_dic = self.parse_query(self.query)

        url_coding = 'UTF-8'
        drive = 'C'
        keys = query_dic.keys()
        if 'drive' in keys: drive = query_dic['drive']
        if 'coding' in keys: self.coding = query_dic['coding']
        if 'urlcoding' in keys: url_coding = query_dic['urlcoding']
        if 'dirdl' in keys:
            if query_dic['dirdl'] == 'true':
                self.zipflag = True

        self.path = self.parse_path_os(urllib.parse.unquote(parse_url.path, url_coding), drive)


    def make_res_body(self):
        if os.path.isdir(self.path):

            if self.zipflag:
                self.set_res_head(200, 'application/zip')
                return self.make_zip(self.path)
            
            self.set_res_head(200, 'text/html; charset='+self.coding)
            return self.make_html(self.make_pathlist())

        elif os.path.isfile(self.path):
            self.set_res_head(200, mimetypes.guess_type(self.path)[0])
            return open(self.path, 'rb').read()

        else:
            self.set_res_head(404, 'text/html; charset='+self.coding)
            return b'''
<html>
<head>
<tittle>not found</title>
</head>

<body>
<h1>file or directory not found</h1>
</body>
</html>
'''

    def make_html(self, path_list):
        url_path = self.parse_path_url(self.path)
        back = '/'.join(url_path.split('/')[:-2])+'/'
        body =\
f'''<html>
<head>
<title>{self.path}</title>
</head>

<body>
<p><a href="{url_path}?{self.query}&dirdl=true">download</a></p>
<p><a href="/?{self.query}"</a>root</p>
<p><a href="{back}?{self.query}">back</a></p>
<h1>directory</h1>
<br/>
'''
        for d in path_list[0]:
            href = self.parse_path_url(d)
            body +=\
f'''
<p><a href="{href}?{self.query}">{d}</a></p>
'''
        # end for

        body += '<h1>file</h1>\n'

        for f in path_list[1]:
            href = self.parse_path_url(f)
            body +=\
f'''
<p><a href="{href}?{self.query}">{f}</a></p>
'''
        #end for
        body += '</html>'
        return  body.encode(self.coding)

    
    def make_pathlist(self):
        path_list = [ i for i in glob.glob(self.path.rstrip(os.sep) + os.sep + '*') ]
        dir_list = []
        file_list = []

        for i in range(len(path_list)):
            if os.path.isdir(path_list[i]):
                path_list[i] += os.sep
                dir_list.append(path_list[i])
            else:
                file_list.append(path_list[i])

        return dir_list, file_list
    
    @staticmethod
    def make_zip(path):
        shutil.make_archive(os.sep+'tmp_zip', 'zip', path)
        ziptmp = open(os.sep+'tmp_zip.zip', 'rb').read()
        os.remove(os.sep+'tmp_zip.zip')
        return ziptmp



class post_class(res_class):
    post_data = b''
    mode = 'n' ## new(n), write(w)

    def __init__(self, req_path, data):
        parse_url = urllib.parse.urlparse(req_path)
        self.query = parse_url.query
        query_dic = self.parse_query(self.query)

        url_coding = 'UTF-8'
        drive = 'C'
        keys = query_dic.keys()
        if 'drive' in keys: drive = query_dic['drive']
        if 'coding' in keys: self.coding = query_dic['coding']
        if 'urlcoding' in keys: url_coding = query_dic['urlcoding']
        if 'mode' in keys: self.mode = query_dic['mode']

        self.path = self.parse_path_os(urllib.parse.unquote(parse_url.path, url_coding), drive)

        self.post_data = data
        self.status_num = 200
        self.content_type = 'text/json'

    def save_file(self):

        if os.path.exists(self.path):
            if os.path.isdir(self.path):
                return f'''
{{
    "state":-1
    "message":"this_directory_is_exist",
    "request_path":"{self.path}"
}}
'''.encode()

            if os.path.isfile(self.path):
                if self.mode == 'n':
                    while os.path.exists(self.path): self.path += '_new'
                    try: open(self.path, 'wb').write(self.post_data)
                    except PermissionError: return self.permission_error_message()

                    return f'''
{{
    "state":0
    "message":made_new_file"
    "request_path":"{self.path}"
}}
'''.encode()
                elif self.mode == 'w':
                    try: open(self.path, 'wb').write(self.post_data)
                    except PermissionError: return self.permission_error_message()

                    return f'''
{{
    "state":0
    "message":over_write_file"
    "request_path":"{self.path}"
}}
'''.encode()

        elif self.path[-1] == os.sep:
            try: os.makedirs(self.path)
            except PermissionError: return self.permission_error_message()
            
            return f'''
{{
    "state":0
    "message":make_new_directory"
    "request_path":"{self.path}"
}}
'''.encode()

        else:
            print(self.path.split(os.sep)[:-1])
            dir = os.sep.join(self.path.split(os.sep)[:-1])+os.sep
            if not os.path.exists(dir):
                try: os.makedirs(dir)
                except PermissionError: return self.permission_error_message()

            try: open(self.path, 'wb').write(self.post_data)
            except PermissionError: return self.permission_error_message()
            return f'''
{{
    "state":0
    "message":make_new_file"
    "request_path":"{self.path}"
}}
'''.encode()

    def permission_error_message(self):
        return f'''
{{
    "state":-1
    "message":permission_error"
    "request_path":"{self.path}"
}}
'''.encode()
