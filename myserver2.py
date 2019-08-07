import os
import cgi

from http import cookies
from http.server import (BaseHTTPRequestHandler,
                         HTTPServer)
from urllib.parse import parse_qs


SERVER_ADDRESSES = {1: '127.0.0.1:8001', 2: '127.0.0.2:8002'}


class HttpProcessor(BaseHTTPRequestHandler):
    URLS = {
        'HOME': '/',
        'AUTH': '/auth',
        'CHARGE': '/charge',
        'LOGOUT': '/out',
    }

    DEFAULT_ROUTING = {
        URLS['HOME']: '/'.join([os.getcwd(), 'auth.html']),
        URLS['AUTH']: '/'.join([os.getcwd(), 'auth.html']),
        URLS['CHARGE']: '/'.join([os.getcwd(), 'charge.html']),
        URLS['LOGOUT']: '/'.join([os.getcwd(), 'auth.html']),
    }

    def do_GET(self):
        self.routing()
        self.fill_header()
        self.path = self.DEFAULT_ROUTING[self.path]
        payload = self.context()
        self.rendering_with_params(**payload)
        # self.wfile.write(self.data_to_response)

    def do_POST(self):
        # if self.path == self.URLS['CHARGE']:
        #     self.send_response(301)
        #     new_path = ''.join(['http://', SERVER_ADDRESSES[1], self.path])
        #     print(new_path)
        #     self.send_header('Location', new_path)
        #     self.end_headers
        # else:
        # if self.path == self.URLS['CHARGE']:
        #     form = cgi.FieldStorage(
        #         fp=self.rfile,
        #         headers=self.headers,
        #         environ={'REQUEST_METHOD': 'POST'}
        #     )
        #     purchase = form.getvalue("purchase")
        # print(purchase)
        self.routing()
        # new_path = ''.join(['http://', SERVER_ADDRESSES[1], self.path])
        # self.send_header('Location', new_path)
        self.fill_header()
        if self.path == self.URLS['CHARGE']:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            purchase = form.getvalue("purchase")
            self.path = self.DEFAULT_ROUTING[self.path]
            payload = {
                '{{from_form.purchase}}': purchase,
            }
            payload = self.context(**payload)
            self.rendering_with_params(**payload)
        # print(self.data_to_response)
        # self.wfile.write(self.data_to_response)
        return

    def routing(self):
        if self.path not in self.DEFAULT_ROUTING:
            self.send_error(404, message="Page Not Found")
        # elif self.path: # != self.URLS['CHARGE']:
        #     self.send_response(200, message="OK")
        # else:
        #     self.send_response(301)
        else:
            self.send_response(200)

    def fill_header(self):
        self.send_header('content-type', 'text/html')
        if self.path in (self.URLS['HOME'], self.URLS['AUTH']):
            self.handle_auth("OK")
        elif self.path == self.URLS['CHARGE']:
            self.handle_charge()
        elif self.path == self.URLS['LOGOUT']:
            self.handle_auth()
        self.end_headers()

    def handle_auth(self, auth_val=0):
        cookie = cookies.SimpleCookie()
        cookie["auth_cookie"] = auth_val
        self.send_header("Set-Cookie", cookie.output(header='', sep=''))

    def handle_charge(self):
        if not self.headers.get("cookie") or self.headers.get("cookie") != 'auth_cookie=OK':
            self.send_error(403, message="Forbidden")

    def context(self, **kwargs):
        default = {
            '{{server_a}}': SERVER_ADDRESSES[1],
            '{{server_b}}': SERVER_ADDRESSES[2],
        }
        for key, value in kwargs.items():
            default[key] = value
        return default

    def rendering_with_params(self, **kwargs):
        with open(self.path, encoding='UTF-8') as page:
            full_data = []
            for line in page:
                for key, value in kwargs.items():
                    if line.find(key) != -1:
                        line = line.replace(key, value)
                full_data.append(line)
            data = ''.join(full_data)
            # self.data_to_response = data.encode(encoding="UTF-8")
            self.wfile.write(data.encode(encoding="UTF-8"))


if __name__ == "__main__":
    server_config = SERVER_ADDRESSES[2]
    server_addr, server_port = server_config.split(':')
    try:
        my_server = HTTPServer((server_addr, int(server_port)), HttpProcessor)
        my_server.serve_forever()
    except KeyboardInterrupt:
        my_server.shutdown()
