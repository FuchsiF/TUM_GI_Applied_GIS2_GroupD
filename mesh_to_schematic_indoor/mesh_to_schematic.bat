@echo off
TITLE mesh_to_schematic
echo ===========================================
echo script created by Pietari Niinimäki - www.pietariniinimaki.com
echo ===========================================
::Get path to a mesh as an argument (This means that you have to call mesh_to_schematic.bat [C:/path/to/your/mesh.obj])
set i_obj=%1
set vendor_path=%~dp0vendor\
:beginning
::Make sure temporary files are cleared
if not exist "%~dp0TMP_outputfiles" (
	mkdir %~dp0TMP_outputfiles
)
if not exist "%~dp0result" (
	mkdir %~dp0result
)
del "%~dp0TMP_outputfiles\point_cloud_output.ply"
del "%~dp0TMP_outputfiles\point_cloud_output_WIP.ply"
del "%~dp0TMP_outputfiles\point_cloud_output_WIP2.ply"

::Make sure all necessary files and programs are found, if not, prompt the user to input the path to those
if exist %i_obj% (
	goto cc
)
:a
set /p i_obj="Enter input 3D mesh model path: "

if not exist %i_obj% (
	echo %i_obj% does not exist
	goto a
)
:cc

set i_cloudCompare=%ProgramFiles%\CloudCompare\CloudCompare.exe
echo %i_cloudCompare%
:c
if exist %i_cloudCompare% (
	echo CloudCompare located in %i_cloudCompare%
	goto b
)

echo CloudCompare not found in %i_cloudCompare%
set /p i_cloudCompare ="Enter path to CloudCompare.exe: "
goto c

:b
set i_fileToVox="%vendor_path%FileToVox\FileToVox.exe"
:e
if exist %i_fileToVox% (
	echo FileToVox located in %i_fileToVox%
	goto d
)

echo FileToVox not found in %i_fileToVox%
set /p i_fileToVox ="Enter path to FileToVox.exe: "
goto e

:d

set i_vox2schematic="%vendor_path%python_scripts\bin\_vox2schematic.py"

if exist %i_vox2schematic% (
	echo vox2schematic located in %i_vox2schematic%
	
) else (
	echo vox2schematic not found in %i_vox2schematic% !
	pause
	goto fail
)

echo please wait, converting mesh to point cloud
::Convert mesh to point cloud using density 20 and move up one meter (this is for coastline handling)
start cmd /c ""%i_cloudCompare%" -SILENT -AUTO_SAVE OFF -o -GLOBAL_SHIFT AUTO "%i_obj%" -SAMPLE_MESH DENSITY 20 -APPLY_TRANS "%~dp0settings/transformation_matrix.txt" -C_EXPORT_FMT PLY -NO_TIMESTAMP -SAVE_CLOUDS FILE %~dp0TMP_outputfiles/point_cloud_output_WIP.ply"
:wait0
if not exist "%~dp0TMP_outputfiles/point_cloud_output_WIP.ply" (
	timeout 1 > NUL
	echo "waiting0"
	goto wait0
)
::Crop out all water (assuming water is below 0.1 units in the up direction)
"%i_cloudCompare%" -SILENT -AUTO_SAVE OFF -o  "%~dp0TMP_outputfiles/point_cloud_output_WIP.ply" -CROP 0:0:1.2:999999:999999:10000 -C_EXPORT_FMT PLY -NO_TIMESTAMP -SAVE_CLOUDS FILE "%~dp0TMP_outputfiles/point_cloud_output.ply"
set waited_yet=false
:wait
if not exist "%~dp0TMP_outputfiles/point_cloud_output.ply" (
	if %waited_yet%==true (
		echo "area is most probably completely under sea level, skipping"
		goto fail
	)
	timeout 3 > NUL
	set waited_yet=true
	echo "waiting1"
	goto wait
)
::Try cropping out all the land, so only the water surface remains, and move it down one meter (based on the default setting of the transformation_matrix.txt)
"%i_cloudCompare%" -SILENT -AUTO_SAVE OFF -o  "%~dp0TMP_outputfiles/point_cloud_output_WIP.ply" -CROP 0:0:-10:999999:999999:1.2 -APPLY_TRANS "%~dp0settings/transformation_matrix2.txt"  -C_EXPORT_FMT PLY -NO_TIMESTAMP -SAVE_CLOUDS FILE "%~dp0TMP_outputfiles/point_cloud_output_WIP2.ply"
::If the resulting file is empty, e.g. there is no water surface, move on
set waited_yet=false
:wait1
if not exist "%~dp0TMP_outputfiles/point_cloud_output_WIP2.ply" (
	if %waited_yet%==true (
		echo no coastline, continuing
		goto skipcoast
	)
	timeout 3 > NUL
	set waited_yet=true
	echo "waiting1"
	goto wait1
)
::If there is water surface, combine the water surface and land surface models together This whole process is done, so that the water surface is separated from the land, and can be removed once the mesh is converted to a minecraft structure, and is being imported into the minecraft world. The water surface has to however be present for a few more steps, otherwise the structure can become misaligned- resulting in broken coastlines
echo separating coastline
"%i_cloudCompare%" -SILENT -AUTO_SAVE OFF -o "%~dp0TMP_outputfiles/point_cloud_output_WIP2.ply" -o "%~dp0TMP_outputfiles/point_cloud_output_WIP.ply" -MERGE_CLOUDS -C_EXPORT_FMT PLY -NO_TIMESTAMP -SAVE_CLOUDS FILE "%~dp0TMP_outputfiles/point_cloud_output.ply"

:skipcoast

echo point cloud located!
timeout 1 > NUL
::Converting point cloud to a vox file
echo please wait, converting point cloud to vox file
"%i_FileToVox%" -i "%~dp0TMP_outputfiles/point_cloud_output.ply" -o "%~dp0TMP_outputfiles/vox_output.vox" -p "%~dp0settings\minecraft_palette.png" --chunk-size=256
:wait2
if not exist "%~dp0TMP_outputfiles/vox_output.vox" (
	timeout 1 > NUL
	echo "waiting2"
	goto wait2
)

echo vox file located!
echo please wait, converting vox file to schematic
::FileToVox saves the vox file in a format that is unreadable by vox2schematic, so we run a VBS script that opens the vox file in a vox file editor, then sends the keypress F2 which is a custom hotkey for saving an opened file, in order to overwrite the vox file in a format readable by filetovox
wscript "%~dp0SaveVoxFile.vbs"
echo SAVED
python "%i_vox2schematic%" "%~dp0TMP_outputfiles/vox_output.vox" -o "%~dp0result/%2.schematic"
set output_name=%2
set waited_yet=false
:wait3
::If possible, include the origin y coordinate in the result schematic name, as this is required by the python script that imports each tile to minecraft.
for %%f in ("%~dp0result\*") do ( 
for %%r in ("%%f") do (
for /f "tokens=1,2 delims=-" %%a in ("%%~nr") do (
if %%a-%%b-ORIGIN_Y==%2 (
set output_name=%%~nr
goto continue
)
)
)
)
timeout 2 > NUL
	echo "Done"
	if %waited_yet%==true (
		goto beginning
	)
	set waited_yet=true
	goto wait3

:continue

echo Done!

:fail
