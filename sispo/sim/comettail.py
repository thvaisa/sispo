from org.orekit.orbits import KeplerianOrbit
import org.orekit.utils as utils # pylint: disable=import-error
import subprocess
from org.orekit.time import AbsoluteDate, TimeScalesFactory
import orekit

##Come tail simulation environment
class CometTail():

    ##location of the comettail
    def __init__(self, settings):
        self.dust_simulation = settings["tail"]["dust_simulator"]
        self.data_processing = settings["tail"]["data_processing"]


    ##Print arguments to file
    def create_parameters(self,env,settings):
        dust_sim = settings["tail"]

        mu = dust_sim["solar_radiation_coefficient"]
        maxDistFromComet = dust_sim["max_dist_from_comet"]
        nPartsPerStep = dust_sim["particles_per_each_step"]
        nSteps = dust_sim["n_time_steps"]
        coeff = dust_sim["k_coeff"]
        output_dir = dust_sim["tmp_output_dir"]        

        self.simulation_args_path = dust_sim["tmp_arg_path"]
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

            for (date, sssb_pos, sssb_rot) in zip(env.spacecraft.date_history,
                                                          env.sssb.pos_history,
                                                          env.sssb.rot_history):
                diff = str(date.durationFrom(sTime))
                f.write(str(diff+"\n"))
        


    def run(self,env,settings):
        self.create_parameters(env,settings)
        self.run_simulation()


    def run_simulation(self):
        subprocess.run([self.dust_simulation, self.simulation_args_path])
        pass


    def set_comet_tail(self,settings,name,dimensions,npoints,middle_point):
        model_file = Path(settings["model"]["file"])       
        tt = self.load_object(model_file,name,["SssbConstDist","SssbOnly"])
        obj = bpy.data.objects['Tail']
        for i in range(0,3):        
            obj.dimensions[i] = dimensions[i]        
            obj.location[i] = middle_point[i]
        

        # get the material
        mat = bpy.data.materials['volumeScatterer']
        tilingNode = mat.node_tree.nodes.get("nTiles")
        tilingNode.outputs[0].default_value = npoints[1]


        #pngfile = mat.node_tree.nodes.get("texture")
        #pngfile.inputs[0].default_value = npoints[1]

        bpy.data.images['52.png'].filepath = '/app/sispo/data/52.png'

        # change its parameters - example viewport diffuse color:
        #mat.diffuse_color = (1,0,0)
        #material = obj.material_slots[0]
        #material.use = True

        #print(dimensions)
        #print(middle_point)
        #print(npoints)
        pass





             





