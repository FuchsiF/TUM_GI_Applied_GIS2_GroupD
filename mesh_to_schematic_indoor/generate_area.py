import sys
import os
import math
import subprocess
from load_city_schematics import schematics_to_world

def setup():
    path_2km_input = input("Enter the path of your file: ")
    gen2km(path_2km_input)

def gen2km(path_2km, offsetx = 0, offsety = 0):
    assert os.path.exists(path_2km), "I did not find the file at, "+str(path_2km)
    folder_name = os.path.basename(path_2km)
    # remove the x2 from the name
    # up ycoord 000000a0-000000a2-000000b0-000000b2-001000a0
    # up xcoord 000000a0-000000a3-000000c0-000000c3-000001a0
    tile_base_name = folder_name[:-2]
        
    tiles = []
    #Goes through every 250m x 250m tile in the 2km x 2km tile and creates a schematic of them
    for y in range(8):
        tiles.append([])
        for x in range(8):
            #Figure out what is the name of the 250m x 250m tile that is in the local coordinates x,y (local to the 2km x 2km tile)
            new_tile_name = int(tile_base_name)
            new_tile_name += 1000 * math.floor(y / 4)
            new_tile_name += 1 * math.floor(x / 4)
            letterid = 1+math.floor(x%4/2)
            letterid += 2*math.floor(y%4/2)
            letter = "a"
            if letterid == 2:
                letter = "c"
            elif letterid == 3:
                letter = "b"
            elif letterid == 4:
                letter = "d"
            id_250m = 1
            if x%2!=0 and y%2==0:
                id_250m = 3
            elif x%2==0 and y%2!=0:
                id_250m = 2
            elif x%2!=0 and y%2!=0:
                id_250m = 4
            tile_250m_name = str(new_tile_name)+letter+str(id_250m)
            tiles[y].append(tile_250m_name)
            xcoord = x+offsetx
            ycoord = y+offsety
            print(tile_250m_name + ", X: " + str(xcoord) + ", Y:" + str(ycoord))
            path_to_250m_tile = path_2km + "\\"+tile_250m_name
            
            largest_file_size = 0
            largest_file = ""
            #In case there are many .obj files in the folder, pick the largest one
            if os.path.exists(path_to_250m_tile):
                for file in os.listdir(path_to_250m_tile):
                    if file.endswith(".obj"):
                        size = os.path.getsize( os.path.join(path_to_250m_tile,file))
                        if size > largest_file_size:
                            largest_file_size = size
                            largest_file = file
                #Create a .schematic from the chosen .obj file
                subprocess.run([os.path.realpath(__file__) + "\..\mesh_to_schematic.bat", os.path.join(path_to_250m_tile, largest_file), str(xcoord)+"-"+str(ycoord)+"-"+"ORIGIN_Y"])
                #Add the schematic to the city_map minecraft world using load_city_schematics.py script's schematics_to_world function
                schematics_to_world()