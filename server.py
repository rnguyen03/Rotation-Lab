import json
import sys
import io
import molsql
import urllib
import cgi
import email
from rdkit import Chem
import MolDisplay
from http.server import HTTPServer, BaseHTTPRequestHandler

public_files = ['/elements.html', '/upload-sdf.html', '/molecules.html',
                '/home.html', '/viewer.html','/style.css', '/elements.js',
                '/uploadsdf.js', '/molecules.js', '/viewer.js']
db = molsql.Database(reset=True)
db.create_tables()


class MyHandler(BaseHTTPRequestHandler):
    # Class variable declaration
    present_molecule = "Empty"
    # Get Homepage
    def do_GET(self):
        # Check user is at home page
        print(self.path)
        if self.path in public_files:   # make sure it's a valid file
            self.send_response(200)  # OK
            if (self.path == '/'):
                self.path = '/home.html'
            # Declare content type (text)
            self.send_header("Content-type", "text/html")
            fp = open(self.path[1:])
            # [1:] to remove leading / so that file is found in current dir

            # load the specified file
            page = fp.read()
            fp.close()

            self.send_header("Content-length", len(page))
            self.end_headers()

            self.wfile.write(bytes(page, "utf-8"))  # Create Page
        elif (self.path == '/get-molecules'):

            # get molecules data
            molecules = db.getMolecules()
            if len(molecules) == 0:
                # database empty
                self.send_response(204) # No Content
                self.send_header("Content-type", "application/json")
                self.end_headers()
                return
            
            self.send_response(200) # OK
            self.send_header("Content-type", "application/json")
            self.end_headers()
            molecules_json = json.dumps(molecules)
            print(f"SENT: {molecules_json}")

            self.wfile.write(bytes(molecules_json, "utf-8"))
        elif (self.path == '/svg'):
            print(MyHandler.present_molecule)
            if (MyHandler.present_molecule == "Empty"):
                # database empty
                self.send_response(204) # No Content
                self.send_header("Content-type", "image/svg+xml")
                self.end_headers()
                return
        
            self.send_response( 200 ) # OK
            self.send_header("Content-type", "image/svg+xml") #Declare content type (image display)
            self.end_headers() #End declaration

            length = int(self.headers.get('Content-Length', 0)) #Declare length of page
            # Get molecule and setup SVG
            MolDisplay.radius = db.radius()
            MolDisplay.element_name = db.element_name()
            MolDisplay.header += db.radial_gradients()
            mol = db.load_mol(MyHandler.present_molecule)
            mol.sort()
            
            print(mol.svg())

            self.wfile.write( bytes( mol.svg(), "utf-8" ) ) #Create Page

        else:
            self.send_response(404)  # Notify 404 error
            self.end_headers()  # End declaration
            self.wfile.write(bytes("404: not found", "utf-8"))  # Create Page

    # get Molecule Page
    def do_POST(self):
        # Check user is at molecule page
        if (self.path == "/elements.html"):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            postvars = urllib.parse.parse_qs(body.decode('utf-8'))

            # Check string for requested operation
            operation = postvars['operation'][0]
            if (operation == "add"):
                # Parse for data
                element_code = str(postvars['eCode'][0])
                element_num = postvars['eNumber'][0]
                element_name = str(postvars['eName'][0])
                col1 = str(postvars['col1'][0]).lstrip('#')
                col2 = str(postvars['col2'][0]).lstrip('#')
                col3 = str(postvars['col3'][0]).lstrip('#')
                radius = postvars['rad'][0]

                # Store Data
                db['Elements'] = (element_num, element_code,
                                  element_name, col1, col2, col3, radius)

                message = f"{element_name} has been added."
                response_length = len(message)

                # Send response to client
                self.send_response(200)  # OK
                self.send_header("Content-type", "text/plain")
                self.send_header("Content-length", response_length)
                self.end_headers()
            elif (operation == "remove"):
                element_name = postvars['reName'][0]
                db.remove_element(element_name)

                # Send response to client
                message = f"{element_name} has been removed."
                self.send_response(200)  # OK
                self.send_header("Content-type", "text/plain")
                self.send_header("Content-length", content_length)
                self.end_headers()
        elif (self.path == "/upload-sdf.html"):
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            mol_name = form['mol-name'].value
            sdf_file = form['sdf-file'].value

            # Validate SDF extention
            content_disposition = form['sdf-file'].headers['Content-Disposition']
            filename = cgi.parse_header(content_disposition)[1]['filename']
            extension = filename.split('.')[-1]
            if extension != 'sdf':
                # Handle invalid SDF file error
                response_body = "Invalid SDF file"
                response_length = len(response_body.encode('utf-8'))
                self.send_response(400)
                self.send_header("Content-type", "text/plain")
                self.send_header("Content-length", response_length)
                self.end_headers()
                self.wfile.write(response_body.encode('utf-8'))
                return

            if not db.molecule_exists:
                # Handle invalid molecule name error
                response_body = "Invalid Molecule Name"
                response_length = len(response_body.encode('utf-8'))
                self.send_response(406)
                self.send_header("Content-type", "text/plain")
                self.send_header("Content-length", response_length)
                self.end_headers()
                self.wfile.write(response_body.encode('utf-8'))
                return

            # Create Molecule
            tFile = io.BytesIO(sdf_file)
            file = io.TextIOWrapper(tFile)
            # for i in range(4):
            #     file.readline()

            # Add molecule into database
            db.add_molecule(mol_name, file)

            # Send response to client
            response_body = "STORED"
            response_length = len(response_body.encode('utf-8'))
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", response_length)
            self.end_headers()
            self.wfile.write(response_body.encode('utf-8'))
        elif (self.path == "/view-molecule"):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            postvars = urllib.parse.parse_qs(body.decode('utf-8'))
        
            # Recieve name of molecule
            molecule_name = postvars['moleculeName'][0]
            
            if not db.molecule_exists:
                # Handle invalid molecule name error
                response_body = "Invalid Molecule Name"
                response_length = len(response_body.encode('utf-8'))
                self.send_response(400)
                self.send_header("Content-type", "text/plain")
                self.send_header("Content-length", response_length)
                self.end_headers()
                self.wfile.write(response_body.encode('utf-8'))
                return
                
            # Store Name
            MyHandler.present_molecule = molecule_name
            
            # Send success response
            response_body = "Molecule name stored successfully"
            response_length = len(response_body.encode('utf-8'))
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", response_length)
            self.end_headers()
            self.wfile.write(response_body.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: not found", "utf-8"))  # Create Page


# Server Start
httpd = HTTPServer(('localhost', int(sys.argv[1])), MyHandler)
httpd.serve_forever()


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

# Connect to Server

# Validate the SDF file
# try:
#     mols = Chem.SDMolSupplier(io.BytesIO(sdf_file))
#     if mols is None or len(mols) == 0:
#         raise ValueError('Invalid SDF file')
# except:
#     # Handle invalid SDF file error
#     response_body = "Invalid SDF file"
#     response_length = len(response_body.encode('utf-8'))
#     self.send_response(400)
#     self.send_header("Content-type", "text/plain")
#     self.send_header("Content-length", response_length)
#     self.end_headers()
#     self.wfile.write(response_body.encode('utf-8'))
#     return
