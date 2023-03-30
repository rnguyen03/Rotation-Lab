#ifndef _mol_h
#define _mol_h
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#ifndef M_PI
#define M_PI 3.141592653589793238462643383279502884
#endif

/*****************************************************************************
 * This defines a struct that describes an atom and its 3 dimensional space. *
 *****************************************************************************/
typedef struct atom {
    char element[3]; //Name of element
    double x; //Coordinate of atom along x axis
    double y; //Coordinate of atom along y axis
    double z; //Coordinate of atom along z axis
} atom;

/******************************************************************************
 * This defines a struct that represents the covalent bond between two atoms. *
 ******************************************************************************/
typedef struct bond {
    unsigned short a1; //Stores Index of the first atom
    unsigned short a2; //Stores Index of the second atom
    unsigned char epairs; //Stores the amount of electron pairs
    atom* atoms; //Stores the address of the atoms
    double x1; //Atom 1 x coordinate
    double x2; //Atom 2 x coordinate
    double y1; //Atom 1 y coordinate
    double y2; //Atom 2 y coordinate
    double z; //Average z value of Atom 1 and Atom 2
    double len; //Store length of the array
    double dx; //Difference of both atoms in x direction
    double dy; //Difference of both atoms in y direction
} bond;

/*******************************************************************************
 * This defines a struct that represents a molecule made up of atoms and bonds *
 *******************************************************************************/
typedef struct molecule {
    unsigned short atom_max; //Records the Dimensionality of an array pointed to by atoms
    unsigned short atom_no; //Number of Atoms currently stored in the array (can't be larger than max)
    atom* atoms; // Points to an array of atoms
    atom** atom_ptrs; //Array of pointers to atoms (To sort atoms)
    unsigned short bond_max; //Records the Dimensionality of an array pointed to by bonds
    unsigned short bond_no; //Number of Bonds currently stored in the arry(can't be larger than max)
    bond* bonds; // Points to an array of bonds (To sort bonds)
    bond** bond_ptrs; //Array of pointers to bonds
} molecule;

/***********************************************
 * reprents a 3-d affine transformation matrix *
 ***********************************************/
typedef double xform_matrix[3][3];

//Sets values of atom equal to arguments.
void atomset(atom* atom, char element[3], double* x, double* y, double* z);
//Gets values of atom and copies them to the locations of the argument
void atomget(atom* atom, char element[3], double* x, double* y, double* z);
//Sets values of bond equal to arguments.
void bondset(bond* bond, unsigned short* a1, unsigned short* a2, atom** atoms, unsigned char* epairs);
//Gets values of bond and copies them to the locations of the argument
void bondget(bond* bond, unsigned short* a1, unsigned short* a2, atom** atoms, unsigned char* epairs);
//return address of dynamically allocated memory and set values given as arguments
molecule* molmalloc(unsigned short atom_max, unsigned short bond_max);
//return address of dynamically allocated memory and copy values of an existing molecule
molecule* molcopy(molecule* src);
//Frees dynamically allocated memory of a molecule
void molfree(molecule* ptr);
//Appends an atom to atoms array of a molecule
void molappend_atom(molecule* molecule, atom* atom);
//Appends a bond to bonds array of a molecule
void molappend_bond(molecule* molecule, bond* bond);
//Sorts atom/bond ptr arrays of a molecule by increasing value of z (Low to High). Take average of both atoms for bonds.
void molsort(molecule* molecule);
//Rotate matrix in x axis
void xrotation(xform_matrix xform_matrix, unsigned short deg);
//Rotate matrix in y axis
void yrotation(xform_matrix xform_matrix, unsigned short deg);
//Rotate matrix in z axis
void zrotation(xform_matrix xform_matrix, unsigned short deg);

void compute_coords(bond* bond);
int bond_comp(const void* a, const void* b);

//Vector matrix multiplication to x, y, z coordinates to all atoms
void mol_xform(molecule* molecule, xform_matrix matrix);

/********************
 * Helper Functions *
 ********************/

//Quicksort atoms in a molecule
void aQuicksort(atom** arr, int low, int high);
int aPartition(atom** arr, int low, int high);
void aSwap(atom** arr, int first, int second);

//Quicksort bonds in a molecule
void bQuicksort(bond** arr, int low, int high);
int bPartition(bond** arr, int low, int high);
void bSwap(bond** arr, int first, int second);

#endif
