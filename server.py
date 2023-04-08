import json
import sys
import io
import molsql
import urllib
import cgi
import email
import molecule
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
    angleX = 0
    angleY = 0
    angleZ = 0
    # Get Homepage
    def do_GET(self):
        # Check user is at home page
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

            self.wfile.write(bytes(molecules_json, "utf-8"))
        elif (self.path == '/svg'):
            if (MyHandler.present_molecule == "Empty"):
                # database empty
                self.send_response(204) # No Content
                self.send_header("Content-type", "image/svg+xml")
                self.end_headers()
                return
            
            molecules = db.getMolecules()
        
            self.send_response( 200 ) # OK
            self.send_header("Content-type", "image/svg+xml") #Declare content type (image display)
            self.end_headers() #End declaration
            
            for mol in molecules:
                # Check if the name of the current molecule matches the target name
                if mol['name'] == MyHandler.present_molecule:
                    acount = mol['atom_count']
                    break
            length = int(self.headers.get('Content-Length', 0)) #Declare length of page
            # Get molecule and setup SVG
            MolDisplay.radius = db.radius()
            MolDisplay.element_name = db.element_name()
            MolDisplay.header += db.radial_gradients()
            mol = db.load_mol(MyHandler.present_molecule)
            
            if (MyHandler.angleX != 0):
                mx = molecule.mx_wrapper(int(MyHandler.angleX), 0, 0)
                mol.xform( mx.xform_matrix )
            if (MyHandler.angleY != 0):
                mx = molecule.mx_wrapper(0, int(MyHandler.angleY), 0)
                mol.xform( mx.xform_matrix )
            if (MyHandler.angleZ != 0):
                mx = molecule.mx_wrapper(0, 0, int(MyHandler.angleZ))
                mol.xform( mx.xform_matrix )
            mol.sort()
            
            svg = mol.svg()
            if (int(acount) < 5):
                svg = svg.replace('<svg ', '<svg id="display-svg" version="1.1" viewBox="0 0 1000 1000" width="500px" height="400px" preserveAspectRatio="xMidYMid meet" ')
            elif (5 < int(acount) and int(acount) < 15):
                svg = svg.replace('<svg ', '<svg id="display-svg" version="1.1" viewBox="0 0 1000 1000" width="500px" height="400px" preserveAspectRatio="xMidYMid meet" style="transform: scale(0.9);" ')
            elif (15 < int(acount) and int(acount) < 30):
                svg = svg.replace('<svg ', '<svg id="display-svg" version="1.1" viewBox="0 0 1000 1000" width="500px" height="400px" preserveAspectRatio="xMidYMid meet" style="transform: scale(0.7);" ')
            else:
                svg = svg.replace('<svg ', '<svg id="display-svg" version="1.1" viewBox="0 0 1000 1000" width="500px" height="400px" preserveAspectRatio="xMidYMid meet" style="transform: scale(0.5);" ')

            self.wfile.write( bytes(svg, "utf-8" ) ) #Create Page
        elif self.path == '/background.jpg':
            self.send_response(200)
            self.send_header('Content-type', 'image/jpg')
            with open('background.jpg', 'rb') as f:
                img = f.read()
            self.send_header('Content-length', len(img))
            self.end_headers()
            self.wfile.write(img)
        elif self.path == '/hanken-grotesk.woff2':
            self.send_response(200)
            self.send_header('Content-type', 'font/woff2')
            with open('hanken-grotesk.woff2', 'rb') as f:
                font = f.read()
            self.send_header('Content-length', len(font))
            self.end_headers()
            self.wfile.write(font)
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

                message = " has been added."
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
                message = " has been removed."
                response_length = len(message)
                self.send_response(200)  # OK
                self.send_header("Content-type", "text/plain")
                self.send_header("Content-length", response_length)
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

            if db.molecule_exists(mol_name):
                # Handle invalid molecule name error
                response_body = "Invalid Molecule Name"
                response_length = len(response_body.encode('utf-8'))
                self.send_response(406) # Not Acceptable
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
            try:
                db.add_molecule(mol_name, file)
            except:
                # Handle invalid SDF file error
                response_body = "Invalid SDF file"
                response_length = len(response_body.encode('utf-8'))
                self.send_response(400)
                self.send_header("Content-type", "text/plain")
                self.send_header("Content-length", response_length)
                self.end_headers()
                self.wfile.write(response_body.encode('utf-8'))
                return
            else:
                response_body = "STORED"
                print("looks good to me")
                # Send response to client
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
        elif (self.path == "/angle"):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            postvars = urllib.parse.parse_qs(body.decode('utf-8'))
            
            rotation_axis = postvars['axis'][0]
            if (rotation_axis == "x"):
                MyHandler.angleX = (MyHandler.angleX + 10) % 360
            elif (rotation_axis == "y"):
                MyHandler.angleY = (MyHandler.angleY + 10) % 360
            elif (rotation_axis == "z"):
                MyHandler.angleZ = (MyHandler.angleZ + 10) % 360
            
            
            # Send success response
            response_body = "Degree changed incremented successfully"
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
