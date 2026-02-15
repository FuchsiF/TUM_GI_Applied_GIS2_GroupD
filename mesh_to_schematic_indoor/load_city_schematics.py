import amulet
from amulet.api.selection import SelectionGroup, SelectionBox
import os

def schematics_to_world():

    level = amulet.load_level( os.path.realpath(__file__) + "\..\city_map")
    baseFolder = (os.path.realpath(__file__) + "/../")
    schematics = []
    #Goes throuhg every .schematic in the result folder, and adds them to the city_map minecraft world at the coordinates specified in the filenames
    for filename in os.listdir(baseFolder + "result"): 
        parsed_filename = filename.split(".")[0].split("-")
        if (len(parsed_filename) < 2):
            continue
        x = int(parsed_filename[1])*-250
        y = int(parsed_filename[0])*-250
        y_origin = int(parsed_filename[2])
        structure = amulet.load_level(os.path.join(baseFolder + "result/"+filename))
        water_fill = amulet.load_level(os.path.join(baseFolder + "settings/water_fill.construction"))
        boundingbox = structure.bounds(structure.dimensions[0])
        selection_box = boundingbox.selection_boxes[0]
        #If the tile has some coast in it, remove the the bottom layer of blocks to make way for actual minecraft water
        if (y_origin == 0):
            boundingbox = SelectionGroup([SelectionBox((selection_box.point_1[0],1,selection_box.point_1[2]),(selection_box.point_2[0], selection_box.point_2[1], selection_box.point_2[2]))])
        #Copy the city model .schematic file into the world in the correct position and rotation
        level.paste(
        structure, 
        structure.dimensions[0], 
        boundingbox, 
        level.dimensions[0], 
        (x,10+(selection_box.point_2[1])/2+y_origin,y), 
        scale=(1.0, 1.0, -1.0), 
        rotation=(0.0, 90.0, 0.0), 
        include_blocks=True, 
        include_entities=False, 
        skip_blocks=(), 
        copy_chunk_not_exist=False)
    
        #If coast line, paste water under
        if (y_origin == 0):
            level.paste(
            water_fill,
            water_fill.dimensions[0],
            water_fill.bounds(water_fill.dimensions[0]),
            level.dimensions[0],
            (x,water_fill.bounds(water_fill.dimensions[0]).selection_boxes[0].point_2[1]/2,y),
            scale=(1.0, 1.0, 1.0), 
            rotation=(0.0, 0.0, 0.0),
            include_blocks=True, 
            include_entities=False, 
            skip_blocks=(), 
            copy_chunk_not_exist=False
            )


    # save the changes to the world
    level.save()

    # close the world
    level.close()
    for filename in os.listdir(baseFolder + "result"): 
        if os.path.exists(baseFolder+ "result/"+filename):
            os.remove(baseFolder+"result/"+filename)