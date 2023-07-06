import ase.io
from ase.io import lammpsdata
import pathlib

atoms = ase.io.read(pathlib.Path("NaCl.xyz").resolve().as_posix())
atomic_numbers = atoms.get_atomic_numbers()

i = 1
atom_map = {}
for num in atomic_numbers:
    if num not in atom_map:
        atom_map[num] = i
        i += 1

atom_type = [atom_map[num] for num in atomic_numbers]
print(atom_type)

#atoms.set_initial_charges([1]*500 + [-1]*500)
#print(atoms)
#print(atoms[499])
#print(atoms[500])
#ase.io.lammpsdata.write_lammps_data("output_file2", atoms, atom_style="charge")
