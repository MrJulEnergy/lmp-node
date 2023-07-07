import ase.io
from ase.io import lammpsdata
import pathlib

atoms = ase.io.read(pathlib.Path("NaCl.xyz").resolve().as_posix())
atomic_masses = atoms.get_masses()
atomic_numbers = atoms.get_atomic_numbers()
atomic_symbol = atoms.get_chemical_symbols()
i = 1
atom_map = {}
for k in range(len(atomic_numbers)):
    if atomic_numbers[k] not in atom_map:
        atom_map[atomic_numbers[k]] = (i, atomic_masses[k], atomic_symbol[k])
        i += 1

atom_type = [atom_map[num][0] for num in atomic_numbers]
print(atom_map)
print([tup[1] for tup in list(atom_map.values())])

print([tup[2] for tup in list(atom_map.values())])

#atoms.set_initial_charges([1]*500 + [-1]*500)
#print(atoms)
#print(atoms[499])
#print(atoms[500])
#ase.io.lammpsdata.write_lammps_data("output_file2", atoms, atom_style="charge")
