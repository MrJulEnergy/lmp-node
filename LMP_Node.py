from zntrack import Node, dvc, meta


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

    def run(self):
        # TODO
        # proc = subprocess.Popen([self.lmp_exe, "-in", self.lmp_input_file])
        pass


if __name__ == "__main__":
    lmp = lammpsnode()
    lmp.write_graph()
