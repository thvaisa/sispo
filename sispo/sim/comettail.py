from pathlib import Path
import subprocess
import orekit
import bpy
import json
from org.orekit.time import AbsoluteDate, TimeScalesFactory
from org.orekit.orbits import KeplerianOrbit
import org.orekit.utils as utils # pylint: disable=import-error





##Come tail simulation environment
class CometTail():

    ##location of the comettail
    def __init__(self, settings):
        self.dust_simulation = settings["dust_simulator"]
        self.data_processing = settings["data_processing"]
        self.settings = settings


    ##Print arguments to file
    def create_parameters(self,env,date0):

        dust_sim = self.settings

        mu = dust_sim["solar_radiation_coefficient"]
        maxDistFromComet = dust_sim["max_dist_from_comet"]
        nPartsPerStep = dust_sim["particles_per_each_step"]
        nSteps = dust_sim["n_time_steps"]
        coeff = dust_sim["k_coeff"]
        output_dir = dust_sim["tmp_output_dir"]        
        output_fname = dust_sim["tmp_output_fname"]  

        self.dke_std = dust_sim["dke_std"]
        self.dke_scale = dust_sim["dke_scale"]
        self.dke_nPs = dust_sim["dke_nPs"]
        self.dke_output_path= dust_sim["dke_output_path"]

        self.simulation_args_path = dust_sim["tmp_s_arg_path"]

        trajectory = env.sssb_settings["trj"]
 
        with(open(self.simulation_args_path,"w")) as f:
            f.write(str(trajectory['a']* utils.Constants.IAU_2012_ASTRONOMICAL_UNIT)+"\n")
            f.write(str(trajectory['e'])+"\n")
            f.write(str(trajectory['omega'])+"\n")
            f.write(str(trajectory['Omega'])+"\n")
            f.write(str(trajectory['i'])+"\n")
            date = trajectory["date"]
            sTime = AbsoluteDate(int(date["year"]),
                                         int(date["month"]),
                                         int(date["day"]),
                                         int(date["hour"]),
                                         int(date["minutes"]),
                                         float(date["seconds"]),
                                         TimeScalesFactory.getTDB())
            f.write(str(0.0)+"\n")
            f.write(str(trajectory['M'])+"\n")

            f.write(str(mu)+"\n")
            f.write(str(maxDistFromComet)+"\n")
            f.write(str(nPartsPerStep)+"\n")
            f.write(str(nSteps)+"\n")
            f.write(str(coeff)+"\n")
            ##For some reason json parser removes character '/'
            f.write(str(output_dir)+"/"+"\n")
            f.write(str(output_fname)+"\n")
            ##replace to more simple robust approach later
            diff = date0.durationFrom(sTime)
            f.write(str(diff-1)+"\n")
            f.write(str(diff)+"\n")


    ##Run the simulation and process data to blender
    ##suitable format
    def run(self,env,date):
        settings = self.settings
        self.create_parameters(env,date)
        data_file = self.run_simulation(self.dust_simulation, self.simulation_args_path)

        self.process_data(data_file,
                            self.data_processing,
                            self.dke_std, self.dke_scale, 
                            self.dke_nPs, self.dke_output_path)
        

    ##Tell to use the executable (dust_simulation) and read arguments from
    ##(simulation args paths)
    def run_simulation(self,dust_simulation,simulation_args_path):
        print("Run dust particle simulation")
        cmd = [dust_simulation, simulation_args_path]
        output =subprocess.run(cmd, capture_output=True)
        output = output.stdout.decode("utf-8").strip().split()
        print("simulation ready")
        return output[-1]
        


    ##Convert point cloud data to voxel data
    def process_data(self,input_fname,
                    data_processor,
                    std,scale,nPs,
                    output_file):

        print("processing data")
        self.output_store = []
        ##executable,point cloud data, input, 
        cmd = [data_processor,input_fname,str(0),
                        str(std),str(scale),str(nPs),str(Path(output_file).resolve())]
        output = subprocess.run(cmd, capture_output=True)
        print(output)
        output = output.stdout.decode("utf-8").strip().split()
        png_file = Path(output[2]).resolve()
        aux_file = Path(output[3]).resolve()
        output = [False,png_file,aux_file]
        png_file = Path(output[1]).resolve()
        aux_file = Path(output[2]).resolve()
        print(png_file)
        print(aux_file)
        self.output_store.append(png_file)
        with open(aux_file, "r") as f:
            person_dict = json.load(f)
        self.output_store.append(person_dict)
        print("finished")
  
    ##Set parameters to the renderer
    def prepare_renderer(self,renderer):
        dust_sim = self.settings
        model_file = Path(dust_sim["model"])
        self.model_name = dust_sim["model_name"]
        layers = ["SssbConstDist","SssbOnly"]
        tt = renderer.load_object(model_file,self.model_name,layers)


    ##Needs refactoring
    def modify_renderer(self):
        model_name = self.model_name
        obj = bpy.data.objects[model_name]
        png_file = self.output_store[-2]
        json_file = self.output_store[-1]
        print(png_file)
        print(json_file)
        ##Set dimensions and the location of the cloud
        for i in range(0,3):   
            print(json_file["1"]["dimension"][i] )     
            obj.location[i] = json_file["1"]["origin"][i]
        obj.dimensions = json_file["1"]["dimension"]

        #Set shader parameters
        mat = bpy.data.materials['volumeScatterer']
        tilingNode = mat.node_tree.nodes.get("nTiles")
        tilingNode.outputs[0].default_value = json_file["1"]["indices"][1]
        bpy.data.images['52.png'].filepath = str(png_file)
        bpy.data.scenes["SssbOnly"].cycles.volume_step_size = 10
        bpy.data.scenes["SssbConstDist"].cycles.volume_step_size = 10
        mat.node_tree.nodes["Math.005"].inputs[1].default_value=0.5


        bpy.data.scenes["SssbConstDist"].cycles.volume_bounces=3
        bpy.data.scenes["SssbOnly"].cycles.volume_bounces=3
        bpy.data.scenes["SssbOnly"].cycles.volume_samples=2
        bpy.data.scenes["SssbConstDist"].cycles.volume_samples=2

        bpy.data.scenes["SssbOnly"].cycles.progressive = "BRANCHED_PATH"
        bpy.data.scenes["SssbConstDist"].cycles.progressive = "BRANCHED_PATH"
        bpy.data.scenes["SssbConstDist"].cycles.aa_samples = 128
        bpy.data.scenes["SssbOnly"].cycles.aa_samples = 128

        #pngfile = mat.node_tree.nodes.get("texture")
        #pngfile.inputs[0].default_value = npoints[1]

        # change its parameters - example viewport diffuse color:
        #mat.diffuse_color = (1,0,0)
        #material = obj.material_slots[0]
        #material.use = True

        #print(dimensions)
        #print(middle_point)
        #print(npoints)
        pass





             





