import pathlib
import subprocess

import yaml
from jinja2 import Environment, FileSystemLoader
from zntrack import Node, dvc, meta, utils


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

    lmp_exe: str = meta.Text("lmp_serial")
    lmp_params: str = dvc.params()
    lmp_template: str = dvc.deps()
    skiprun: bool = False

    lmp_directory: str = dvc.outs(utils.nwd / "lammps")

    def create_input_script(self):
        # Get parameter from yaml:
        with open(self.lmp_params, "r") as stream:
            params = yaml.safe_load(stream)

        # Resolve paths for input files
        input_dict = {}
        for key in params["files"]["inputs"]:
            input_dict[key] = (
                pathlib.Path(params["files"]["inputs"][key]).resolve().as_posix()
            )
        for key in params["files"]["outputs"]:
            input_dict[key] = params["files"]["outputs"][key]
        for key in params["sim_parameters"]:
            input_dict[key] = params["sim_parameters"][key]

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
        # TODO Find a Way to get live output from run or Popen
        # print(proc.stdout)


if __name__ == "__main__":
    lmp = LammpsSimulator(
        lmp_params="npt_params.yaml",
        lmp_template="templates/npt.lmp",
    )

    lmp.write_graph()
