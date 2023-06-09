import pathlib
import subprocess

import ase
import ase.io
import yaml
import zntrack
from jinja2 import Environment, FileSystemLoader
from zntrack import Node, dvc, meta, zn


class LammpsSimulator(Node):
    """Can perform LAMMPS Simulations.

    Parameters
    ----------
        lmp_exe: str
            This is the name or path of the LAMMPS executable. Either path
            to executable, "lmp" or "lamp_<machine>".
            See https://docs.lammps.org/Run_basics.html for more information
        lmp_params: str
            Path to file. To be able to change parameters with DVC and not
            have to change them manually in the input script, a params file in yaml
            format and corresponding template file must be provided.
        lmp_template: str
            Path to file. In combination with the params file this will
            be the input script for the LAMMPS simulation
        skiprun: bool, optional
            Whether to skip running LAMMPS or not, by default False

    Returns
    -------
    None
        This function does not return anything. Instead, it creates a LAMMPS input
        script based on the specified template and parameter files, runs the
        LAMMPS simulation using the specified executable, and saves the simulation
        output to the specified directory.

    """

    """A few remarks for future programmers:
    -If there is the error, that NPT.lammpstraj doesnt exist: 
        that means there is an error in the inputscript. 
        look at log.lammps in the nwd to see whats wrong
    - dont forget to "dvc init"...
    """
    lmp_directory: str = dvc.outs(zntrack.nwd / "lammps")
    lmp_exe: str = meta.Text("lmp_serial")
    skiprun: bool = False

    # inputs
    atoms: ase.Atoms = zn.deps(None)
    atoms_file = dvc.deps(None)  # input trajectory

    # outputs
    dump_file = dvc.outs(zntrack.nwd / "NPT.lammpstraj")
    log_file = dvc.outs(zntrack.nwd / "NPT.log")

    lmp_params: str = dvc.params()
    lmp_template: str = dvc.deps()

    def _post_init_(self):
        # Check if atoms were provided:
        if self.atoms is None and self.atoms_file is None:
            raise TypeError("Both atoms and atoms_file mustn't be None")
        if self.atoms is not None and self.atoms_file is not None:
            raise TypeError(
                "Atoms and atoms_file are mutually exclusive. Please only provide one"
            )

    def get_atoms(self):
        # look where to get the input_trajectory (either ase.Atoms or file)
        if self.atoms is None:
            self.atoms_file = pathlib.Path(self.atoms_file).resolve().as_posix()
        if self.atoms_file is None:
            # if not atoms_file is provided,
            # input_trajectory has to come from ase.Atoms,
            # which have to be written to a file.
            ase.io.write(self.lmp_directory / "atoms.xyz", self.atoms)
            self.atoms_file = (
                pathlib.Path(self.lmp_directory / "atoms.xyz").resolve().as_posix()
            )

    def fill_atoms_with_life(self):
        # Give LAMMPS more information about the Atoms provided.
        # (e.g. Mass or Type (LAMMPS specific)).
        # This Function has to be executed after get_atoms has been executed,
        # otherwise there might not be a xyz file to read.
        # Charges have to be set by Hand in the LAMMPS-inputscript-Template.
        data = ase.io.read(self.atoms_file)

        # Atomic Number
        self.atomic_numbers = data.get_atomic_numbers()
        # Atomic Mass
        self.atomic_masses = data.get_masses()
        # Atom Symbol
        self.atomic_symbols = data.get_chemical_symbols()

        i = 1
        atom_map = {}
        for k in range(len(self.atomic_numbers)):
            if self.atomic_numbers[k] not in atom_map:
                atom_map[self.atomic_numbers[k]] = (
                    i,
                    self.atomic_masses[k],
                    self.atomic_symbols[k],
                )
                i += 1
        self.atomic_type = [atom_map[num][0] for num in self.atomic_numbers]
        self.atomic_masses = [tup[1] for tup in list(atom_map.values())]
        self.atomic_symbols = [tup[2] for tup in list(atom_map.values())]

    def create_input_script(self):
        # Get parameter from yaml:
        with open(self.lmp_params, "r") as stream:
            params = yaml.safe_load(stream)

        # Resolve paths for input files
        input_dict = {}
        input_dict["log_file"] = self.log_file.resolve().as_posix()
        input_dict["dump_file"] = self.dump_file.resolve().as_posix()
        input_dict["input_trajectory"] = self.atoms_file

        for key in params["sim_parameters"]:
            input_dict[key] = params["sim_parameters"][key]

        # Fill input dict with information about the atoms
        # (all infos are gathered from the xyz file except charges)
        input_dict["atomic_type"] = self.atomic_type
        input_dict["atomic_masses"] = self.atomic_masses
        input_dict["atomic_symbols"] = self.atomic_symbols

        # Get template
        loader = FileSystemLoader(".")
        env = Environment(loader=loader)  # , trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(self.lmp_template)

        # Render Template
        self.lmp_input_script = template.render(input_dict)
        with open(f"{self.lmp_directory}/input.script", "w") as file:
            file.write(self.lmp_input_script)  # write input script to output directory

    def run(self):
        self.lmp_directory.mkdir(exist_ok=True)  # create output directory
        self.get_atoms()
        self.fill_atoms_with_life()
        self.create_input_script()
        if self.skiprun:
            print("Skipping simulation ...")
            cmd = [self.lmp_exe, "-sr" "-in", "input.script"]
        else:
            print("Simulating ...")
            cmd = [self.lmp_exe, "-in", "input.script"]

        subprocess.run(
            cmd,
            cwd=self.lmp_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )


class AseAtomsReader(Node):
    atoms_file = dvc.deps()
    atoms = zn.outs()

    def run(self):
        self.atoms = ase.io.read(pathlib.Path(self.atoms_file).resolve().as_posix())


if __name__ == "__main__":
    with zntrack.Project() as project:
        at = AseAtomsReader(atoms_file="NaCl.xyz")
        lmp = LammpsSimulator(
            atoms=at.atoms,
            lmp_params="npt_params.yaml",
            lmp_template="templates/npt.lmp",
        )
    project.run(repro=False)
