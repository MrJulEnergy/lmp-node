from zntrack import Node, zn, dvc, meta
import subprocess

class lammpsnode(Node):
    lmp_exe = meta.Text("lmp_serial") #see: https://docs.lammps.org/Run_basics.html . either "lmp" or "lmp_<machine>"
    lmp_params = dvc.params("lammps.yaml") #parameters which can be changes by dvc in the template file
    lmp_input_file = dvc.deps("NPT.in") #input template for LAMMPS
    
    def run(self):
        #TODO
        #proc = subprocess.Popen([self.lmp_exe, "-in", self.lmp_input_file])
        pass


if __name__ == "__main__":
    lmp = lammpsnode()
    lmp.write_graph()
