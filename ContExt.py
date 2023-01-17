
import sys
import os
import re
from scipy.spatial import KDTree

ATOMSPATTERN = re.compile(r"^(#(([0-9]+)(_([0-9]+))?)?)?"+\
                          r"(\/([\w]*))?"+\
                          r"(:([A-Za-z0-9]+)?((_(-?[0-9]+))(_(-?[0-9]+))?)?)?"+\
                          r"(@([A-Za-z0-9]+'?)?((_(-?[0-9]+))(_(-?[0-9]+))?)?)?$")

    
def ParseAtomsFormat(kw,pattern=ATOMSPATTERN):

    regsearch = re.findall(ATOMSPATTERN, kw)[0]
    
    modelmin   = regsearch[2]
    modelmax   = regsearch[4]
    chain      = regsearch[6]
    residue    = regsearch[8]
    resnummin  = regsearch[11]
    resnummax  = regsearch[13]
    atom       = regsearch[15]
    atomnummin = regsearch[18]
    atomnummax = regsearch[20]

    return {'MODELMIN':   int(modelmin)   if modelmin   else None,
            'MODELMAX':   int(modelmax)   if modelmax   else None,
            'CHAIN':      chain   if chain   else None,
            'RESIDUE':    residue if residue else None,
            'RESNUMMIN':  int(resnummin)  if resnummin  else None,
            'RESNUMMAX':  int(resnummax)  if resnummax  else None,
            'ATOM':       atom    if atom    else None,     
            'ATOMNUMMIN': int(atomnummin) if atomnummin else None,
            'ATOMNUMMAX': int(atomnummax) if atomnummax else None}


def ParseAtoms(inpfile,mask):
    pass


def Atompairs(n1,n2,limit):

    tree1 = KDTree(n1)
    tree2 = KDTree(n2)

    dist = tree1.sparse_distance_matrix(
        tree2,
        limit,
        p=2,
        output_type='ndarray'
    )

    dist.sort()

    return dist


def ContactExtractor(inpfile1, inpfile2=None, Range=10.0, mask1="#", mask2=None):

    if inpfile2 is None:
        inpfile2 = inpfile1
    if mask2 is None:
        mask2 = mask1

    mask1 = [ParseAtomsFormat(kw) for kw in mask1]
    mask2 = [ParseAtomsFormat(kw) for kw in mask2]

    if not mask1:
        mask1 = [ParseAtomsFormat(''),]
    if not mask2:
        mask2 = [ParseAtomsFormat(''),]

    atoms1 = ParseAtoms(inpfile1,mask1) ###

    if inpfile1!=inpfile2 or mask1!=mask2:
        atoms2 = ParseAtoms(inpfile2,mask2)
    else:
        atoms2 = atoms1

    contacts = Atompairs([(a1['X'],a1['Y'],a1['Z']) for a1 in atoms1],
                         [(a2['X'],a2['Y'],a2['Z']) for a2 in atoms2],
                         Range)

    PrintContacts(contacts,atoms1,atoms2) ###
    

if __name__ == "__main__":

    def PrintUsage():
        print()
        print("Usage:")
        print()
        print("pathto/python3 pathto/ContExt.py input=pathto/coordfile [OPTIONS]")
        print()
        print("try --help for a detailed description")
        print()
        exit(1)

    INPFILE1 = None
    INPFILE2 = None
    RANGE    = 10.0
    ATOMS1   = "#"
    ATOMS2   = None

    args = sys.argv[1:]

    if "--help" in args or "-help" in args or "help" in args or\
       "--h" in args or "-h" in args or "h" in args or\
       "--H" in args or "-H" in args or "H" in args:
        with open("README.md") as helpfile:
            print(helpfile.read())
        exit(0)

    for arg in args:

        if arg.startswith("input="):
            INPFILE1 = arg[6:]
            if not os.path.exists(INPFILE1):
                print("ERROR: something is wrong with your input file")
                exit(1)

        elif arg.startswith("input2="):
            INPFILE2 = arg[7:]
            if not os.path.exists(INPFILE2):
                print("ERROR: something is wrong with your input2 file")
                exit(1)

        elif arg.startswith("range="):
            try:
                RANGE = float(arg[6:])
            except:
                print("ERROR: something is wrong with your range value")
                exit(1)

        elif arg.startswith("atoms="):
            ATOMS1 = arg[6:].split()
            for kw in ATOMS1:
                if not ATOMSPATTERN.match(kw):
                    print("ERROR: something is wrong with your atoms value")
                    exit(1)

        elif arg.startswith("atoms2="):
            ATOMS2 = arg[7:].split()
            for kw in ATOMS2:
                if not ATOMSPATTERN.match(kw):
                    print("ERROR: something is wrong with your atoms2 value")
                    exit(1)

    if INPFILE1 is None:
        PrintUsage()

    ContactExtractor(INPFILE1, INPFILE2, RANGE, ATOMS1, ATOMS2)


