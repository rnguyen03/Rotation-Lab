import os
import sqlite3
from MolDisplay import Atom, Bond, Molecule
import MolDisplay

class Database:
    # Init Method
    def __init__(self, reset=False):
        if reset and os.path.isfile('molecules.db'):
            os.remove('molecules.db')
        self.conn = sqlite3.connect('molecules.db')
        
    # Create Table
    def create_tables(self):
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Elements(
            ELEMENT_NO INTEGER NOT NULL,
            ELEMENT_CODE VARCHAR(3) NOT NULL PRIMARY KEY,
            ELEMENT_NAME VARCHAR(3) NOT NULL,
            COLOUR1 CHAR(6) NOT NULL,
            COLOUR2 CHAR(6) NOT NULL,
            COLOUR3 CHAR(6) NOT NULL,
            RADIUS DECIMAL(3) NOT NULL
        ); """)

        self.conn.execute("""CREATE TABLE IF NOT EXISTS Atoms(
            ATOM_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            ELEMENT_CODE VARCHAR(3) NOT NULL REFERENCES Elements(ELEMENT_CODE),
            X DECIMAL(7,4) NOT NULL,
            Y DECIMAL(7,4) NOT NULL,
            Z DECIMAL(7,4) NOT NULL
        );""")

        self.conn.execute(""" CREATE TABLE IF NOT EXISTS Bonds(
            BOND_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
            A1 INTEGER NOT NULL,
            A2 INTEGER NOT NULL,
            EPAIRS INTEGER NOT NULL
        );""")

        self.conn.execute(""" CREATE TABLE IF NOT EXISTS Molecules(
            MOLECULE_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            NAME TEXT UNIQUE NOT NULL
        ); """)

        self.conn.execute(""" CREATE TABLE IF NOT EXISTS MoleculeAtom(
            MOLECULE_ID INTEGER NOT NULL REFERENCES Molecules(MOLECULE_ID),
            ATOM_ID INTEGER NOT NULL REFERENCES Atoms(ATOM_ID),
            PRIMARY KEY(MOLECULE_ID,ATOM_ID)
        ); """)

        self.conn.execute(""" CREATE TABLE IF NOT EXISTS MoleculeBond(
            MOLECULE_ID INTEGER NOT NULL REFERENCES Molecules(MOLECULE_ID),
            BOND_ID INTEGER NOT NULL REFERENCES Bonds(BOND_ID),
            PRIMARY KEY(MOLECULE_ID,BOND_ID)
        ); """)

    # Set Item in Table
    def __setitem__(self, table, values):
        # Set format
        str_format = "("+",".join(["?"] * len(values)) + ")"
        # Insert Item
        command = f"INSERT INTO {table} VALUES {str_format}"
        self.conn.execute(command, values)
        # Commit change
        self.conn.commit()
        
     # Add atom
    def add_atom(self, molname, atom):
        # Insert atom values
        query1 = "INSERT INTO Atoms (ELEMENT_CODE, X, Y, Z) VALUES (?, ?, ?, ?)"
        values1 = (atom.atom.element, atom.atom.x, atom.atom.y, atom.atom.z)
        cursor = self.conn.cursor()
        cursor.execute(query1, values1)
        # Commit change
        self.conn.commit()

        # Find atom ID
        atom_id = cursor.lastrowid

        # Find molecule ID
        query2 = "SELECT MOLECULE_ID FROM Molecules WHERE NAME = ?"
        values2 = (molname,)
        cursor.execute(query2, values2)
        molecule_id = cursor.fetchone()[0]

        # Insert IDs
        query3 = "INSERT INTO MoleculeAtom VALUES (?, ?)"
        values3 = (molecule_id, atom_id)
        cursor.execute(query3, values3)
        # Commit change
        self.conn.commit()

    # Add bond
    def add_bond(self, molname, bond):
        # Insert bond values
        query1 = "INSERT INTO Bonds (A1, A2, EPairs) VALUES (?, ?, ?)"
        values1 = (bond.bond.a1, bond.bond.a2, bond.bond.epairs)
        cursor = self.conn.cursor()
        cursor.execute(query1, values1)
        # Commit change
        self.conn.commit()

        # Get bond ID
        bond_id = cursor.lastrowid

        # Get molecule ID
        query2 = "SELECT MOLECULE_ID FROM Molecules WHERE NAME = ?"
        values2 = (molname,)
        cursor.execute(query2, values2)
        molecule_id = cursor.fetchone()[0]

        # Insert IDs
        query3 = "INSERT INTO MoleculeBond VALUES (?, ?)"
        values3 = (molecule_id, bond_id)
        cursor.execute(query3, values3)
        # Commit change
        self.conn.commit()

    # Add molecule
    def add_molecule(self, name, fp):
        # Declare Object
        molecule = Molecule()
        # Parse file
        molecule.parse(fp)
        # Insert Molecule into table
        command = f"INSERT INTO Molecules (NAME) VALUES (?)"
        self.conn.execute(command, (name,))
        # Commit change
        self.conn.commit()

        # Add all atoms in Molecule
        for atoms in range(molecule.atom_no):
            self.add_atom(name, Atom(molecule.get_atom(atoms)))

        # Add all bonds in Molecule
        for bonds in range(molecule.bond_no):
            self.add_bond(name, Bond(molecule.get_bond(bonds)))
            
    # Create molecule object
    def load_mol( self, name ):
        # Declare Object
        molecule = MolDisplay.Molecule()
        
        # Atom Fetch
        pointer = self.conn.cursor()
        command1 = f"""SELECT *
                            FROM Atoms, MoleculeAtom, Molecules
                            WHERE Atoms.ATOM_ID = MoleculeAtom.ATOM_ID AND Molecules.NAME = ? AND Molecules.MOLECULE_ID = MoleculeAtom.MOLECULE_ID
                            ORDER BY ATOM_ID ASC"""
                            
        pointer.execute(command1, (name,))
        atoms = pointer.fetchall()

        # Iterate thorugh atoms
        for atom in atoms:
            molecule.append_atom(atom[1], atom[2], atom[3], atom[4])

        # Bond Fetch
        command2 = """SELECT *
                            FROM Bonds, MoleculeBond, Molecules
                            WHERE Bonds.BOND_ID = MoleculeBond.BOND_ID AND Molecules.NAME = ? AND Molecules.MOLECULE_ID = MoleculeBond.MOLECULE_ID
                            ORDER BY BOND_ID ASC"""
        pointer.execute(command2, (name,))
        bonds = pointer.fetchall()

        # Iterate thorugh bonds
        for bond in bonds:
            molecule.append_bond(bond[1], bond[2], bond[3])

        # return molecule
        return molecule

    # Create hashmap/dictionary
    def radius(self):
        # Return query as dictionary
        return dict(self.conn.execute("""SELECT ELEMENT_CODE, RADIUS FROM ELEMENTS""").fetchall())

    # Create hashmap/dictionary
    def element_name(self):
        # Return query as dictionary
        return {row[0]: row[1] for row in self.conn.execute("SELECT ELEMENT_CODE, ELEMENT_NAME FROM ELEMENTS").fetchall()}

    # Method to create svg's
    def radial_gradients(self):
        # Get values from Elements Table
        cursor = self.conn.cursor()
        cursor.execute("SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 FROM Elements")
        elements = cursor.fetchall()

        # create a list comprehension to build the SVG string
        svg = "\n".join([
            f'<radialGradient id="{e[0]}" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">'
            f'<stop offset="0%%" stop-color="#{e[1]}"/>'
            f'<stop offset="50%%" stop-color="#{e[2]}"/>'
            f'<stop offset="100%%" stop-color="#{e[3]}"/>'
            f'</radialGradient>'
            for e in elements
        ])

        # return string representation of svg
        return svg
    
            
if __name__ == "__main__":
    db = Database(reset=False); # or use default
    MolDisplay.radius = db.radius()
    MolDisplay.element_name = db.element_name()
    MolDisplay.header += db.radial_gradients()
    for molecule in [ 'Water', 'Caffeine', 'Isopentanol' ]:
        mol = db.load_mol( molecule )
        mol.sort()
        fp = open( molecule + ".svg", "w" )
        fp.write( mol.svg() )
        fp.close()