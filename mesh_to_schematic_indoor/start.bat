@Echo off
echo mesh_to_schematic created by Pietari Niinimäki - www.pietariniinimaki.com
echo -
echo 3rd party software and scripts used are MagickaVoxel, Voxelers- mcthings, CloudCompare, Amulet API
echo -
echo With this program, you can either generate a minecraft map from a dataset of an entire city (as long as the dataset is readable by the program), or a single minecraft .schematic from a single 3D mesh, which can be imported into minecraft using mods, or a world editor such as Amulet.
:prompt
set /p inputtext="Do you want to generate an entire city? y/n "

IF "%inputtext%"=="y" (

	python %~dp0load_2kmx2km_tiles.py
) ELSE (

	IF "%inputtext%"=="n" (
		python %~dp0create_single_schematic.py
	) ELSE (
		echo Input must be either y or n
		goto prompt
	)

)
pause