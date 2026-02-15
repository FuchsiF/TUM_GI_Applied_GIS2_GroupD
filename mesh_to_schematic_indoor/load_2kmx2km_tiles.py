import sys
import os
import math
import subprocess
import requests
import zipfile
from generate_area import gen2km
import shutil
print("By default this program will start generating the city model starting from the coordinates specified in settings/current_generation_coords.txt [X,Y].\nThis means that if the program crashes, the next time you run it, the program will continue from where it left off. However, if you wish to start generating the whole city from the origin, delete current_generation_coords.txt\n")

print("For this program to work, you have to place a copy of your minecraft world in this folder, and rename it city_map\n")

print("This program can overwrite existing creations in your chosen minecraft world, if you have anything you'd like to save, create a backup!\n\n")

data_set_url = input("Enter the URL that contains 2kmx2km tiles (for example: http://3d.hel.ninja/data/mesh/Helsinki3D-MESH_2015_OBJ_2km-250m_ZIP/): ")

#Used mainly for debugging colors, not in use currently
def debug():
    src_tile = '672496x2'
    end_tile = '686514x2'

    src_tile_int = int(src_tile[:-2])
    end_tile_int = int(end_tile[:-2])

    diff = end_tile_int - src_tile_int

    xdiff = int(int(str(diff)[3:])/2+1)
    ydiff = int(int(str(diff)[:-3])/2+1)

    for y in range(ydiff):
        for x in range(xdiff):
            current_tile_name = str(src_tile_int + 2000*y + 2*x)+"x2"
            url = data_set_url + "Helsinki3D_OBJ_"+current_tile_name+".zip"
            pathToTile = os.path.realpath(__file__) + '/../src_3D_files/' + current_tile_name
            
            gen2km(pathToTile, x*8, y*8) #2km x 2km consists of 8*8 250m x 250m tiles
            print("2km x 2km tile processed, removing TMP files and moving to next.")

def main():
    #Bottom left (Southwest) corner of the city area you want to bring to minecraft
    src_tile = '668490x2'
    #Top right (Northeast) corner of the city area you want to bring to minecraft
    end_tile = '686514x2'

    src_tile_int = int(src_tile[:-2])
    end_tile_int = int(end_tile[:-2])

    diff = end_tile_int - src_tile_int
    #Calculate the local coordinate difference between the city corner tiles
    xdiff = int(int(str(diff)[3:])/2+1)
    ydiff = int(int(str(diff)[:-3])/2+1)
    #Preparing and clearing folders for downloading city models from datasets
    if os.path.exists(os.path.realpath(__file__) + '/../src_3D_files/'):
        try:
            shutil.rmtree(os.path.realpath(__file__) + '/../src_3D_files/')
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))
    
    os.mkdir(os.path.realpath(__file__) + '/../src_3D_files/')
    start_coords = ""
    if os.path.exists(os.path.realpath(__file__) + "/../settings/current_generation_coords.txt"):
        f= open(os.path.realpath(__file__) +"/../settings/current_generation_coords.txt",mode='r')
        start_coords = f.read()
    
    #If the program last exited mid-generation, the program will continue from the point where the program left off
    xstartoffset = 0
    ystartoffset = 0
    if start_coords:
        ystartoffset = int(start_coords.split(",")[1])
        xstartoffset = int(start_coords.split(",")[0])
        f.close()
    #Go through every tile in the city that is inside the start and end corners specified
    for y in range(ystartoffset, ydiff):
        for x in range(xstartoffset, xdiff):
            
            print(str(x) + ", " + str(y))
            #Update current coordinates to current_generation_coords.txt, so if generation stops, we can continue from there
            f= open(os.path.realpath(__file__) +"/../settings/current_generation_coords.txt","w+")
            f.truncate(0)
            f.write(str(x) + ","+str(y))
            f.close()
            
            #Download a single 2km x 2km tile from dataset
            current_tile_name = str(src_tile_int + 2000*y + 2*x)+"x2"
            url = data_set_url + "Helsinki3D_OBJ_"+current_tile_name+".zip"
            print("Downloading "+url)
            r = requests.get(url, allow_redirects=True)
            pathToTile = os.path.realpath(__file__) + '/../src_3D_files/' + current_tile_name
            open(pathToTile +'.zip', 'wb').write(r.content)
            #Check if download is successfull

            #If download is not successfull, move on to next tile
            if not zipfile.is_zipfile(pathToTile+'.zip'):
                continue
            if not os.path.exists(pathToTile):
                os.mkdir(pathToTile)
            with zipfile.ZipFile(pathToTile+'.zip', 'r') as zip_ref:
                zip_ref.extractall(pathToTile)
            
            #Call function from another python file, that generates the 2km x 2km tile to minecraft .schematic files, and adds them to the city_map minecraft world
            gen2km(pathToTile, x*8, y*8) #2km x 2km consists of 8*8 250m x 250m tiles
            
            #Clear temporary and unnecessary files
            print("2km x 2km tile processed, removing TMP files and moving to next.")
            if os.path.exists(pathToTile):
                try:
                    shutil.rmtree(pathToTile)
                except OSError as e:
                    print("Error: %s - %s." % (e.filename, e.strerror))
            if os.path.exists(pathToTile+'.zip'):
                os.remove(pathToTile+'.zip')
        xstartoffset = 0
    if os.path.exists(os.path.realpath(__file__) + "/../settings/current_generation_coords.txt"):
        os.remove(os.path.realpath(__file__) + "/../settings/current_generation_coords.txt")

main()