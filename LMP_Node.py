from zntrack import Node, dvc, meta
import subprocess
from jinja2 import Environment, FileSystemLoader
import yaml


class lammpsnode(Node):
    """Can run LAMMPS Simulations.

    Args:
        lmp_exe: This is the name or path of the LAMMPS executable. Either path
            to executable, "lmp" or "lamp_<machine>". 
            See https://docs.lammps.org/Run_basics.html for more information
        lmp_params: To be able to change parameters with DVC and not have to change
            them manually in the input script, a params file in yaml format and
            corresponding template file must be provided.
        lmp_template: In combination with the params file this will be the input
            script for the lammps simulation

    Returns:
        #TODO
    """

    lmp_exe = meta.Text("lmp_serial")
    lmp_params = dvc.params("lammps.yaml")
    lmp_template = dvc.deps("NPT.in")


    def _post_init_(self):
        params = yaml.safe_load(self.lmp_params)
        #loader = FileSystemLoader()
        #env = Environment(loader=loader)
        print(params)

    def run(self):
                

        """
        proc = subprocess.Popen(
                [self.lmp_exe, "-in", self.lmp_input_file], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                )

        stdout, stderr = process.communicate()
        print(stdout)
        #print(stdout.decode("utf-8"))
        """
        pass

if __name__ == "__main__":
    lmp = lammpsnode()
    lmp.write_graph()
