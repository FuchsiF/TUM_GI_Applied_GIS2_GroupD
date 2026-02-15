import subprocess
from load_city_schematics import schematics_to_world
import os
print("Your resulting .schematic minecraft creation will be stored in the results folder")
print("For best results, please make sure your input 3D mesh has no points with negative coordinates. If it has, consider moving it.") #since the program is created specifically for bringing city models to Minecraft, it tries to crop out areas where y<0
obj_path = input("Please input path to your 3D mesh: " )

subprocess.run([os.path.realpath(__file__) + "\..\mesh_to_schematic.bat", obj_path, "result"])