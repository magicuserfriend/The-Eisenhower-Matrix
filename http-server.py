import socket
import sys

from messages import Request, Response
import cgi


class HTTPServer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        # self.blacklist = []

    def run_server(self):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((self.ip, self.port))
            backlog = 10  # Размер очереди входящих подключений, т.н. backlog
            server_socket.listen(backlog)

            while True:
                client_socket, address = server_socket.accept()
                self.serve_client(client_socket)
        except KeyboardInterrupt:
            server_socket.close()

    def serve_client(self, client_socket):
        data = client_socket.recv(1024).decode('utf-8')
        print(data)
        request = self.parse_request(data)
        response_data = self.handle_request(request)
        response = f'HTTP/1.1 {response_data.status} {response_data.reason}\r\n'
        if response_data.headers:
            for (key, value) in response_data.headers:
                response += f'{key}: {value}\r\n'
        response += '\r\n'
        print(response)
        response = response.encode('utf-8')
        if response_data.body:
            response = response + response_data.body
        client_socket.send(response)
        client_socket.shutdown(socket.SHUT_WR)

    def parse_request(self, data):
        query, body = None, None
        data_array = data.split()
        method, target, version = data_array[0], data_array[1], data_array[2]
        if str(target).find('?') != -1:
            query = target[str(target).find('?')+1:]
            target = target[:str(target).find('?')]
        if target == '/': target = '/index.html'
        headers_array = data_array[3:]        
        for element in data_array:
            if 'Content-Length' in str(element):
                body = headers_array.pop(-1)
                return Request(method, target, version, headers_array, body=body)
        else:
            return Request(method, target, version, headers_array, query=query)
 
    def handle_request(self, request):
        path = request.target
        content_type, body, status, reason = '', '', '', ''
        #if 'cgi.py' in str(path) and 'POST' in str(request.method):
        if 'POST' in str(request.method):
            print('POST cgi.py')
            return cgi.handle_create_user(request)
        elif 'cgi.py' in str(path) and 'GET' in str(request.method):
            print('GET cgi.py')
            return cgi.handle_get_users(request)
        elif '.html' in str(path):
            content_type = 'text/html; charset=uft-8'
        elif '.css' in str(path):
            content_type = 'text/css'
        else:
            pass # TODO сообщение об ошибке
        try:
            with open(f'files{path}', 'rb') as file:
                body = file.read()
            status, reason = '200', 'OK'
        except:
            body = 'Sorry, bro! No page...'.encode('utf-8')
            status, reason = '404', 'Not Found'
        headers = [('Content-Type', content_type), ('Content-Length', len(body))]
        return Response(status, reason, headers, body)


if __name__ == '__main__':
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    serv = HTTPServer(host, port)
    serv.run_server()
