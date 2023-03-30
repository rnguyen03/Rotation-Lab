import sys
import io
from MolDisplay import Molecule
from http.server import HTTPServer, BaseHTTPRequestHandler

public_files = [ '/index.html', '/style.css', '/script.js' ];

class MyHandler( BaseHTTPRequestHandler ):
    #Get Homepage
    def do_GET(self):
        #Check user is at home page
        if self.path in public_files:   # make sure it's a valid file
            self.send_response( 200 ) # OK
            self.send_header( "Content-type", "text/html" ) #Declare content type (text)
            fp = open( self.path[1:] ) 
            # [1:] to remove leading / so that file is found in current dir

            # load the specified file
            page = fp.read()
            fp.close()
            
            self.send_header( "Content-length", len(page) ) #Declare length of page
            self.end_headers() #End declaration

            self.wfile.write( bytes( page, "utf-8" ) ) #Create Page

        else:
            self.send_response( 404 ) #Notify 404 error
            self.end_headers() #End declaration
            self.wfile.write( bytes( "404: not found", "utf-8" ) ) #Create Page
            
    #get Molecule Page
    def do_POST(self):
        
        #Check user is at molecule page
        if (self.path == "/molecule"):
            self.send_response( 200 ) # OK
            self.send_header("Content-type", "image/svg+xml") #Declare content type (image display)
            self.end_headers() #End declaration

            length = int(self.headers.get('Content-Length', 0)) #Declare length of page
        
            #Convert and get file object
            data = self.rfile.read(length)
            tFile = io.BytesIO(data)
            file = io.TextIOWrapper(tFile)
            
            # Skip the first 4 lines
            for i in range(4):
                file.readline()

            #Create Molecule
            mol = Molecule()
            mol.parse(file) 
            mol.sort()

            self.wfile.write( bytes( mol.svg(), "utf-8" ) ) #Create Page

        else:
            self.send_response( 404 )
            self.end_headers()
            self.wfile.write( bytes( "404: not found", "utf-8" ) ) #Create Page


# home_form = """
# <html>
#     <head>
#         <title> File Upload </title>
#     </head>
#     <body>
#         <h1> File Upload </h1>
#             <form action="molecule" enctype="multipart/form-data" method="post">
#             <p>
#                 <input type="file" id="sdf_file" name="filename"/>
#             </p>
#             <p>
#                 <input type="submit" value="Upload"/>
#             </p>
#         </form>
#     </body>
# </html>
# """

#Connect to Server
httpd = HTTPServer( ( 'localhost', int(sys.argv[1]) ), MyHandler )
httpd.serve_forever()