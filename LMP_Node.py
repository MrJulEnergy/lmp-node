import subprocess

import yaml
from jinja2 import Environment, FileSystemLoader
from zntrack import Node, dvc, meta, utils


class lammpsnode(Node):
    """Can run LAMMPS Simulations.

    Args:
        lmp_exe: This is the name or path of the LAMMPS executable. Either path
            to executable, "lmp" or "lamp_<machine>".
            See https://docs.lammps.org/Run_basics.html for more information
        lmp_params: Path to file. To be able to change parameters with DVC and not
            have to change them manually in the input script, a params file in yaml
            format and corresponding template file must be provided.
        lmp_template: Path to file. In combination with the params file this will
            be the input script for the LAMMPS simulation

    Returns:
        #TODO
    """

    lmp_exe = meta.Text("lmp_serial")
    lmp_params = dvc.params()
    lmp_template = dvc.deps()

    lmp_directory = dvc.outs(utils.nwd / "lammps")
    
    def _post_init_(self):
        # Get parameter from yaml:
        with open(self.lmp_params, "r") as stream:
            params = yaml.safe_load(stream)

        # Get template
        loader = FileSystemLoader(".")
        env = Environment(loader=loader)#, trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(self.lmp_template)

        # Render Template
        self.lmp_input_script = template.render(params)

    def run(self):
        self.lmp_directory.mkdir(exist_ok=True) #create output directory
        with open(f"{self.lmp_directory}/input.script", "w") as file:
            file.write(self.lmp_input_script) #write input script to output directory

        proc = subprocess.run(
                [self.lmp_exe, "-in", "input.script"],
                cwd=self.lmp_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                )
        #TODO Find a Way to get live output from run or Popen
        #print(proc.stdout)


if __name__ == "__main__":
    lmp = lammpsnode(lmp_params="npt_params.yaml", lmp_template="templates/npt.lmp")
    lmp.write_graph()
