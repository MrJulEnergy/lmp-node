import ase.io
from ase.io import lammpsdata
import pathlib

atoms = ase.io.read(pathlib.Path("NaCl.xyz").resolve().as_posix())
print(len(atoms.get_atomic_numbers()))

#atoms.set_initial_charges([1]*500 + [-1]*500)
#print(atoms)
#print(atoms[499])
#print(atoms[500])
#ase.io.lammpsdata.write_lammps_data("output_file2", atoms, atom_style="charge")
