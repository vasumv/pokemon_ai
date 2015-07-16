import SimpleHTTPServer
import SocketServer

HOST = "localhost"
PORT = "8888"

handler = SimpleHTTPServer.SimpleHTTPRequestHandler
httpd = SocketServer.TCPServer(("", PORT), handler)

print "serving at port", PORT
httpd.serve_forever()
