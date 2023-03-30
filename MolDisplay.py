import molecule

#Manditory Defines
header = """<svg version="1.1" width="1000" height="1000"
xmlns="http://www.w3.org/2000/svg">"""
footer = """</svg>"""
offsetx = 500
offsety = 500

#Atom Class
class Atom:
    def __init__(self, c_atom):
        self.atom = c_atom
        self.z = c_atom.z

    def __str__(self):
        return '{} {} {} {}' .format(self.atom.element, self.atom.x, self.atom.y, self.atom.z)

    def svg(self):
        rad = radius[self.atom.element]
        colour = element_name[self.atom.element]
        return ' <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' % (self.atom.x * 100.0 + offsetx, self.atom.y * 100 + offsety, rad, colour)

#Bond Class
class Bond:
    #Bond Constructor
    def __init__(self, c_bond):
        #Set z and bond values
        self.z = c_bond.z
        self.bond = c_bond

    # Method to return a string representation of a bond
    def __str__(self):
        return f"x1:{self.bond.x1} x2:{self.bond.x2} y1:{self.bond.y1} y2:{self.bond.y1} z:{self.bond.z} len:{self.bond.len} dx:{self.bond.dx} dy:{self.bond.dy}"

    # Method to return a svg string representation of a bond
    def svg(self):
        # Bond coordinates calculation
        atomx1 = (self.bond.x1 * 100) + offsetx
        atomx2 = (self.bond.x2 * 100) + offsetx
        atomy1 = (self.bond.y1 * 100) + offsety
        atomy2 = (self.bond.y2 * 100) + offsety
        # Bond coordinates calculation
        # if(self.bond.dy != 0):
        posx1 = atomx1 + self.bond.dy * 10
        posx2 = atomx2 + self.bond.dy * 10
        negx1 = atomx1 - self.bond.dy * 10
        negx2 = atomx2 - self.bond.dy * 10

        # if(self.bond.dx != 0):
        posy1 = atomy1 + self.bond.dx * 10
        posy2 = atomy2 + self.bond.dx * 10
        negy1 = atomy1 - self.bond.dx * 10
        negy2 = atomy2 - self.bond.dx * 10

        return '  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' % (negx1, posy1, posx1, negy1, posx2, negy2, negx2, posy2)

#Molecule subclass
class Molecule(molecule.molecule):
    #Molecule to String
    def __str__(self):
        string = ""
        #Atoms to String
        for i in range(self.atom_no):
            atom = self.get_atom(i)
            newAtom = Atom(atom)
            string += newAtom.__str__()
            string += "\n"
        #Bonds to String
        for i in range(self.bond_no):
            bond = self.get_bond(i)
            newBond = Bond(bond)
            string += newBond.__str__()
            string += "\n"

        return string

    #Molecule to SVG (String) 
    def svg(self):
        #String to Header
        string = header
        i = 0
        j = 0
        #Merge anad Sort Bonds and Atoms
        while(i != self.atom_no and j != self.bond_no):
            #Compare the next atom and a bond
            tAtom = self.get_atom(i)
            tBond = self.get_bond(j)
            newAtom = Atom(tAtom)
            newBond = Bond(tBond)
            #Get smallest z value
            if(newAtom.z < newBond.z):
                #Add atom to string
                string += newAtom.svg()
                i += 1
            else:
                #Add bond to string
                string += newBond.svg()
                j += 1

        #Add the rest of the atoms and bonds
        if(i == self.atom_no):
            for k in range(j, self.bond_no):
                #Add bond to string
                tBond = self.get_bond(k)
                newBond = Bond(tBond)
                string += newBond.svg()
        else:
            for m in range(i, self.atom_no):
                #Add atom to string
                tAtom = self.get_atom(m)
                newAtom = Atom(tAtom)
                string += newAtom.svg()
        #Add footer to string
        string += footer
        return string

    #File to Molecule
    def parse(self, fileObj):
        #Read file
        data = fileObj.read()
        numLine = 0
        #Iterate through every line in file
        for line in data.split("\n"):
            #Increment line count
            numLine += 1
            #Line 4 --> Save bond and atoms counts 
            if(numLine == 4):
                #Parse data
                string = line.split()
                #Save data
                numAtom = int(string[0])
                numBond = int(string[1])
            #Pointer is at the atom content
            elif(numLine > 4 and numAtom != 0):
                #Parse data
                string = line.split()
                #Save data
                self.append_atom(string[3], float(string[0]), float(string[1]), float(string[2]))
                numAtom = numAtom -  1
            #Pointer is at the bond content
            elif(numLine > 4 and numAtom == 0 and numBond != 0):
                #Parse data
                string = line.split()
                #Save data
                self.append_bond(int(string[0]) - 1, int(string[1]) - 1, int(string[2]))
                numBond = numBond - 1
