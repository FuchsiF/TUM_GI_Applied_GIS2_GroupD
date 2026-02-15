# Generating-Minecraft-Worlds-from-Indoor-Point-Clouds
**Felix Fuchsloch, Noel Henke, Sofia F. Vyshnevska, 2026**

This repository contains the adapted workflow and tools used to convert high-density **Indoor Mobile Laser Scan (MLS)** data into playable Minecraft worlds. The Workflow has been created for the project Generating Minecraft Worlds from Indoor Point Clouds in the course Applied Geoinformatics 2, by the Chair of Geoinformatics at the Technical University of Munich.   

Originally based on the [City of Helsinki's mesh_to_schematic](https://github.com/City-of-Helsinki/mesh_to_schematic) tool, this pipeline has been decoupled and modified to handle the specific challenges of indoor environments, including removal of furniture to ensure navigability in the World.



## Prerequisites
To reproduce this workflow, you will need the following software:

1.  **[CloudCompare](https://www.danielgm.net/cc/)** (v2.12+): For preprocessing, subsampling, and RANSAC plane detection.
2.  **[Minecraft Java Edition](https://www.minecraft.net/)**: Version 1.20.
3.  **Python 3.x**: To run the conversion script.
4.  **Minecraft WorldEdit** or **Amulet Editor**: To import the final schematic into the desired World.

## Setup
We utilize conda to manage dependencies.
### Step 1: Clone the repository:
```
git clone https://github.com/FuchsiF/TUM_GI_Applied_GIS2_GroupD.git
cd TUM_GI_Applied_GIS2_GroupD
```
### Step 2: Create the environment:
```
conda env create -f environment.yml
conda activate minecraft-pipeline
```

## Step-by-Step Workflow
### Step 1: Preprocess the Point Cloud in Cloud Compare
Open the raw dataset in CloudCompare and perform following steps:
1. Subsampling: Use Edit > Subsample, choose the Spatial method in the dropdown.  
2. Grid alignment: Use Edit > Translate/Rotate to rotate the point cloud along the Z-Axis until the building's primary walls are paralell to the X and Y axis.  
3. Manual Cleanup: Remove any apparent scanning artefacts, such as reflections or floating points using the tool Edit > Segment.
4. Use the same Segment tool to extract any staircases in the point cloud and merge them into one cloud using Edit > merge
5. Apply the RANSAC Shape Detection plugin (Plugins > RANSAC Shape Detection) in two passes, once for the staircases and once for the remainder. In both cases the option to set random colors per primitive needs to diabled:
   + Pass A: Walls & Floors (The Main Cloud)
      + Select the main point cloud (excluding the extracted stairs).
      + Primitives: Plane
      + Min support points: 1250 
      + Max distance to primitive: 0.05 
   + Pass B: Staircases
      + Select the isolated staircase cloud.
      + Primitives: Plane
      + Min support points: 100 
      + Max distance to primitive: 0.05
        
### Step 2: Voxelization
Copy your preprocessed Point cloud into the parent folder:
and run the ```FileToVox``` tool: 
   + ```--scale 1,9```: Maps 1 meter to ~1.9 blocks to increase the resolution of the reconstruction.
   + ```color-limit 20```: Snaps colors to dominant hues to reduce noise.
```
.\mesh_to_schematic_indoor\vendor\FileToVox\FileToVox.exe -i "cleaned_cloud.ply" -o "model.vox" -p .\mesh_to_schematic_indoor\vendor\FileToVox\minecraft_palette.png --scale 1,9 --color-limit 20
```
### Step 3: Open the .vox file in Magica Voxel
1. Open ```model.vox``` using the included MagicaVoxel executable.
2. Edit > Select > All
3. Edit > Boolean > Union
4. Save (Ctrl + S)

### Step 4: Format Conversion
Run the ```vox2schematic.py``` conversion script, wich uses our modified dictionary in its ```vox.py``` dependency:
```
python mesh_to_schematic_indoor\vendor\python_scripts\bin\_vox2schematic.py model.vox -o level.schematic
```
### Step 5: Format Conversion
Use either WorldEdit (in-game) or Amulet Editor (external) to place the Schematic-file intothe desired level.

## Summary
1. Preprocess in CloudCompare
2. Run FileToVox
3. Re-save in MagicaVoxel
4. Run vox2schematic
5. Import into Minecraft
