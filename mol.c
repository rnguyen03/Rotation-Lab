#include "mol.h"
//Copy values into atom, assume memory has been allocated
void atomset(atom* atom, char element[3], double* x, double* y, double* z) {
	strcpy(atom->element, element); //Store element name to atom member
	atom->x = *x; //Store x value to atom member
	atom->y = *y; //Store y value to atom member
	atom->z = *z; //Store z value to atom member
}

//Copy values of atom to location of pointers
void atomget(atom* atom, char element[3], double* x, double* y, double* z) {
	//Exit and print error msg if atom is null
	if (atom == NULL) {
		fprintf(stderr, "%s", "Error atom uninitialized..\n");
		exit(1);
	}
	strcpy(element, atom->element); //Store atom name to string
	*x = atom->x; //Store atom x value to double
	*y = atom->y; //Store atom y value to double
	*z = atom->z; //Store atom z value to double
}

//Copy values into bond, assume memory has been allocated.
void bondset(bond* bond, unsigned short* a1, unsigned short* a2, atom** atoms, unsigned char* epairs) {
	//Exit and print error msg if either atom is null
	if (a1 == NULL || a2 == NULL) {
		fprintf(stderr, "%s", "Error atom uninitialized..\n");
		exit(1);
	}
	bond->atoms = *atoms;
	bond->a1 = *a1; //Store first atom to bond member
	bond->a2 = *a2; //Store second atom to bond member
	bond->epairs = *epairs; //Store electron pairs to bond member
	compute_coords(bond);
}

//Copy values of bond to location of pointers
void bondget(bond* bond, unsigned short* a1, unsigned short* a2, atom** atoms, unsigned char* epairs) {
	//Exit and print error msg if either bond atoms are null
	if (bond == NULL || bond->atoms == NULL) {
		fprintf(stderr, "%s", "Error bond uninitialized..\n");
		exit(1);
	}
	*a1 = bond->a1; //Store bond atom1 to atom variable
	*a2 = bond->a2; //Store bond atom2 to atom variable
	*epairs = bond->epairs; //Store bond epairs to epairs variable
	*atoms = bond->atoms; //Store array of atoms
}

//Compare bond z values
int bond_comp(const void* a, const void* b) {
	bond* const* b1 = a;
	bond* const* b2 = b;

	if ((*b1)->z < (*b2)->z) {
		return -1;
	}
	else if ((*b1)->z == (*b2)->z) {
		return 0;
	}
	else {
		return 1;
	}
}

//Compute coords for bond and set the values to the bond
void compute_coords(bond* bond) {
	bond->x1 = bond->atoms[bond->a1].x;
	bond->x2 = bond->atoms[bond->a2].x;

	bond->y1 = bond->atoms[bond->a1].y;
	bond->y2 = bond->atoms[bond->a2].y;

	bond->z = (bond->atoms[bond->a1].z + bond->atoms[bond->a2].z) / 2;
	//len will store the distance from a1 to a2
	bond->len = sqrt((bond->x2 - bond->x1) * (bond->x2 - bond->x1) + 
		(bond->y2 - bond->y1) * (bond->y2 - bond->y1));

	bond->dx = (bond->atoms[bond->a2].x - bond->atoms[bond->a1].x) / bond->len;
	bond->dy = (bond->atoms[bond->a2].y - bond->atoms[bond->a1].y) / bond->len;
}

//Initialize a molecule with empty values except max values which are passed in
molecule* molmalloc(unsigned short atom_max, unsigned short bond_max) {
	molecule* temp = (molecule*)malloc(sizeof(molecule)); //allocate memory for temp molecule
	//If malloc failed then return null with err msg
	if (temp == NULL) {
		fprintf(stderr, "%s", "molmalloc - Error allocating memory.\n");
		return NULL;
	}
	//Set atom max and atom number values
	temp->atom_max = atom_max;
	temp->atom_no = 0;

	temp->atoms = (atom*)malloc(sizeof(atom) * atom_max); //allocate memory for atoms array
	//If malloc failed then return null with err msg
	if (temp->atoms == NULL) {
		fprintf(stderr, "%s", "molmalloc - Error allocating memory.\n");
		//free previous malloc or else memory leak will occur
		free(temp);
		return NULL;
	}

	temp->atom_ptrs = (atom**)malloc(sizeof(atom*) * atom_max); //allocate memory for atom pointers array
	//If malloc failed then return null with err msg
	if (temp->atom_ptrs == NULL) {
		fprintf(stderr, "%s", "molmalloc - Error allocating memory.\n");
		//free previous malloc or else memory leak will occur
		free(temp->atoms);
		free(temp);
		return NULL;
	}
	//Set bond max and bond number values
	temp->bond_max = bond_max;
	temp->bond_no = 0;

	temp->bonds = (bond*)malloc(sizeof(bond) * bond_max); //allocate memory for bond array
	//If malloc failed then return null with err msg
	if (temp->bonds == NULL) {
		fprintf(stderr, "%s", "molmalloc - Error allocating memory.\n");
		//free previous malloc or else memory leak will occur
		free(temp->atom_ptrs);
		free(temp->atoms);
		free(temp);
		return NULL;
	}

	temp->bond_ptrs = (bond**)malloc(sizeof(bond*) * bond_max); //allocate memory for bond pointers array
	//If malloc failed then return null with err msg
	if (temp->bond_ptrs == NULL) {
		fprintf(stderr, "%s", "molmalloc - Error allocating memory.\n");
		//free previous malloc or else memory leak will occur
		free(temp->bonds);
		free(temp->atom_ptrs);
		free(temp->atoms);
		free(temp);
		return NULL;
	}

	return temp;
}

//Initialize a new molecule and copy the attributes of a molecule that was passed in
molecule* molcopy(molecule* src) {
	molecule* mTemp = molmalloc(src->atom_max, src->bond_max); //allocate memory for molecule and its members
	//If molmalloc returned null then return null
	if (mTemp == NULL) {
		return NULL;
	}
	//Copy values
	mTemp->atom_max = src->atom_max;
	mTemp->bond_max = src->bond_max;

	//Iterate through all of the src atoms
	for (int i = 0; i < src->atom_no; i++) {
		//Initialize temp vars
		atom aTemp;
		bond bTemp;

		atomset(&aTemp, src->atoms[i].element, &(src->atoms[i].x), &(src->atoms[i].y), &(src->atoms[i].z)); //Set values of temp atom using src atom
		molappend_atom(mTemp, &aTemp); //Append temp atom to new molecule

		//Conditional to append bonds in the same loop as atoms
		if (mTemp->bond_no != src->bond_no) {
			bondset(&bTemp, &src->bonds[i].a1, &src->bonds[i].a2, &src->bonds[i].atoms, &src->bonds[i].epairs); //Set values of temp bonds using src bond
			molappend_bond(mTemp, &bTemp); //Append temp bond to new molecule
		}
	}
	return mTemp;
}

//Free dynamically allocated memory of a molecule
void molfree(molecule* ptr) {
	//Free molecule members first
	free(ptr->atoms);
	free(ptr->atom_ptrs);
	free(ptr->bonds);
	free(ptr->bond_ptrs);
	//Free the molecule last
	free(ptr);
}

//Add an atom to molecule
void molappend_atom(molecule* molecule, atom* atom) {
	//Check if atoms are at max capacity
	if (molecule->atom_no == molecule->atom_max) {
		//If the max is 0 set it to 1, otherwise double it
		if (molecule->atom_max == 0) {
			molecule->atom_max = 1;
		}
		else {
			molecule->atom_max *= 2;
		}
		//Adjust the atom array to fit the new max
		molecule->atoms = (struct atom*)realloc(molecule->atoms, sizeof(struct atom) * molecule->atom_max);
		//If malloc failed, exit
		if (molecule->atoms == NULL) {
			fprintf(stderr, "%s", "Error allocating memory.. Exiting..\n");
			molfree(molecule);
			exit(1);
		}
		//Adjust the atom ptr array to fit the new max
		molecule->atom_ptrs = (struct atom**)realloc(molecule->atom_ptrs, sizeof(struct atom*) * molecule->atom_max);
		//If malloc failed, exit
		if (molecule->atom_ptrs == NULL) {
			fprintf(stderr, "%s", "Error allocating memory.. Exiting..\n");
			molfree(molecule);
			exit(1);
		}
		//Point the atom pointers to the new addresses
		for (int i = 0; i < molecule->atom_max; i++) {
			molecule->atom_ptrs[i] = &(molecule->atoms[i]);
		}
	}
	molecule->atoms[molecule->atom_no] = *atom; //Append the new atom
	molecule->atom_ptrs[molecule->atom_no] = &(molecule->atoms[molecule->atom_no]); //Append a pointer that points to the new atom address
	molecule->atom_no++; //Increment atom count
}

//Add a bond to molecule
void molappend_bond(molecule* molecule, bond* bond) {
	//Check if bonds are at max capacity
	if (molecule->bond_no == molecule->bond_max) {
		//If the max is 0 set it to 1, otherwise double it
		if (molecule->bond_max == 0) {
			molecule->bond_max = 1;
		}
		else {
			molecule->bond_max *= 2;
		}
		//Adjust the bond array
		molecule->bonds = (struct bond*)realloc(molecule->bonds, sizeof(struct bond) * molecule->bond_max);
		//If malloc failed, exit
		if (molecule->bonds == NULL) {
			fprintf(stderr, "%s", "Error allocating memory.. Exiting..\n");
			molfree(molecule);
			exit(1);
		}
		//Adjust the bond pointer array
		molecule->bond_ptrs = (struct bond**)realloc(molecule->bond_ptrs, sizeof(struct bond*) * molecule->bond_max);
		//If malloc failed, exit
		if (molecule->bond_ptrs == NULL) {
			fprintf(stderr, "%s", "Error allocating memory.. Exiting..\n");
			molfree(molecule);
			exit(1);
		}
		//Point the bond pointers to the new addresses
		for (int i = 0; i < molecule->bond_max; i++) {
			molecule->bond_ptrs[i] = &(molecule->bonds[i]);
		}
	}
	molecule->bonds[molecule->bond_no] = *bond; //Append the new bond
	molecule->bond_ptrs[molecule->bond_no] = &(molecule->bonds[molecule->bond_no]); //Append a pointer that points to the new bond address
	molecule->bond_no++; //Increment bond count

}

//Sorts atom z values and bond averge z values in increasing order
void molsort(molecule* molecule) {
	aQuicksort(molecule->atom_ptrs, 0, molecule->atom_no - 1); //Sort Atoms
	bQuicksort(molecule->bond_ptrs, 0, molecule->bond_no - 1); //Sort Bonds
}

//Returns a transformtion matrix rotation in the x-axis
void xrotation(xform_matrix xform_matrix, unsigned short deg) {
	double rad = deg * M_PI / 180; //Convert degrees to radians

	//Generate a 2D array that matches x-axis rotation matrix
	xform_matrix[0][0] = 1.00;
	xform_matrix[0][1] = 0.00;
	xform_matrix[0][2] = 0.00;
	xform_matrix[1][0] = 0.00;
	xform_matrix[1][1] = cos(rad);
	xform_matrix[1][2] = sin(rad) * -1.00;
	xform_matrix[2][0] = 0.00;
	xform_matrix[2][1] = sin(rad);
	xform_matrix[2][2] = cos(rad);
}

//Returns a transformtion matrix rotation in the y-axis
void yrotation(xform_matrix xform_matrix, unsigned short deg) {
	double rad = deg * M_PI / 180; //Convert degrees to radians

	//Generate a 2D array that matches y-axis rotation matrix
	xform_matrix[0][0] = cos(rad);
	xform_matrix[0][1] = 0.00;
	xform_matrix[0][2] = sin(rad);
	xform_matrix[1][0] = 0.00;
	xform_matrix[1][1] = 1.00;
	xform_matrix[1][2] = 0.00;
	xform_matrix[2][0] = sin(rad) * -1.00;
	xform_matrix[2][1] = 0.00;
	xform_matrix[2][2] = cos(rad);
}

//Returns a transformtion matrix rotation in the z-axis
void zrotation(xform_matrix xform_matrix, unsigned short deg) {
	double rad = deg * M_PI / 180; //Convert degrees to radians

	//Generate a 2D array that matches z-axis rotation matrix
	xform_matrix[0][0] = cos(rad);
	xform_matrix[0][1] = sin(rad) * -1.00;
	xform_matrix[0][2] = 0.00;
	xform_matrix[1][0] = sin(rad);
	xform_matrix[1][1] = cos(rad);
	xform_matrix[1][2] = 0.00;
	xform_matrix[2][0] = 0.00;
	xform_matrix[2][1] = 0.00;
	xform_matrix[2][2] = 1.00;
}

//Performs Matrix x Vector multiplication upon every atom in a molecule
void mol_xform(molecule* molecule, xform_matrix matrix) {
	//Iterate through every atom in the molecule
	for (int i = 0; i < molecule->atom_no; i++) {
		double x = molecule->atoms[i].x; //Store x value
		double y = molecule->atoms[i].y; //Store y value
		double z = molecule->atoms[i].z; //Store z value

		//Iterate through each row in the matrix/vector
		for (int j = 0; j < 3; j++) {
			switch (j) {
			case 0:
				molecule->atoms[i].x = matrix[0][0] * x + matrix[0][1] * y + matrix[0][2] * z; //Calculate new x value
				break;
			case 1:
				molecule->atoms[i].y = matrix[1][0] * x + matrix[1][1] * y + matrix[1][2] * z; //Calculate new y value
				break;
			case 2:
				molecule->atoms[i].z = matrix[2][0] * x + matrix[2][1] * y + matrix[2][2] * z; //Calculate new z value
				break;
			}
		}
	}
	//Compute every bond accordingly
	for (int i = 0; i < molecule->bond_no; i++) {
		compute_coords(&molecule->bonds[i]);
	}
}

//Helper function that performs aQuicksort algorithm
void aQuicksort(atom** arr, int low, int high) {
	//Base Case
	if (low < high) {
		int iPivot = aPartition(arr, low, high); //"Seperate" the aarray
		aQuicksort(arr, low, iPivot - 1); //Sort Left
		aQuicksort(arr, iPivot + 1, high); //Sort Right
	}
}

//Sorts a section of the array based off of the pivot location
int aPartition(atom** arr, int low, int high) {
	float pivot = arr[high]->z; //Initialize a "Pivot"
	int temp = low - 1; //Set lower bound
	//Iterate through subarray
	for (int i = low; i < high; i++) {
		//Swap with element on left of element if current value is less than the pivot
		if (arr[i]->z < pivot) {
			temp++; //Move right of the "left" element
			aSwap(arr, temp, i); //Swap positions
		}
	}
	aSwap(arr, temp + 1, high); //Swap upperbound if possible
	return (temp + 1);
}

//Helper function that aSwaps values of atom pointers in an array
void aSwap(atom** arr, int first, int second) {
	//Swap the variables if they are not equal
	if (first != second) {
		atom* temp = arr[first];
		arr[first] = arr[second];
		arr[second] = temp;
	}
}

//Helper function that performs aQuicksort algorithm
void bQuicksort(bond** arr, int low, int high) {
	//Base Case
	if (low < high) {
		int iPivot = bPartition(arr, low, high); //"Seperate" the aarray
		bQuicksort(arr, low, iPivot - 1); //Sort Left
		bQuicksort(arr, iPivot + 1, high); //Sort Right
	}
}

//Sorts a section of the array based off of the pivot location
int bPartition(bond** arr, int low, int high) {
	float pivot = arr[high]->z; //Initialize a "Pivot"
	int temp = low - 1; //Set lower bound
	//Iterate through subarray
	for (int i = low; i < high; i++) {
		//Swap with element on left of element if current value is less than the pivot
		if (arr[i]->z < pivot) {
			temp++; //Move right of the "left" element
			bSwap(arr, temp, i); //Swap positions
		}
	}
	bSwap(arr, temp + 1, high);
	return (temp + 1);
}

//Helper function that aSwaps values of atom pointers in an array
void bSwap(bond** arr, int first, int second) {
	//Swap the variables if they are not equal
	if (first != second) {
		bond* temp = arr[first];
		arr[first] = arr[second];
		arr[second] = temp;
	}
}
