# Licensed under the terms of http://www.apache.org/licenses/LICENSE-2.0
# Author/s (©): Alvaro del Castillo

from math import sqrt

import chunk
import logging
import colorsys
import mcpi.block
from mcpi.vec3 import Vec3

from mcthings.thing import Thing


class Voxel:
    def __init__(self, bytes):
        self.x = bytes[0]
        self.z = bytes[1]
        self.y = bytes[2]
        self.color_index = bytes[3] - 1


class Color:
    """ RGBA format palette """
    _color2minecraft = {}  # Cache to convert a color to minecraft color

    def __init__(self, hex_str):
        self.hex_str = hex_str

    def rgb(self):
        red = int(self.hex_str[0:2], 16)
        green = int(self.hex_str[2:4], 16)
        blue = int(self.hex_str[4:6], 16)

        return red, green, blue
    
    def hex_brightness(self, brightness):
        red = max(min(self.rgb()[0]+brightness,255),0)
        green = max(min(self.rgb()[1]+brightness,255),0)
        blue = max(min(self.rgb()[2]+brightness,255),0)
        
        return '%02x%02x%02x' % (red, green, blue)

    def hex_levels(self, dark, bright):
        dist = float(bright-dark)
        red = self.rgb()[0] - max(dark,0)
        green = self.rgb()[1] - max(dark,0)
        blue = self.rgb()[2] - max(dark,0)
        red=min(int(float(red)/dist*255),255)
        green=min(int(float(green)/dist*255),255)
        blue=min(int(float(blue)/dist*255),255) 
        return '%02x%02x%02x' % (red, green, blue)

    def compare(self, color):
        # https://www.compuphase.com/cmetric.htm
        r1, g1, b1 = self.rgb()
        r2, g2, b2 = color.rgb()
        read_mean = (r1 + r2) / 2
        r = r1 - r2
        g = g1 - g2
        b = b1 - b2
        return sqrt((round((512 + read_mean) * r * r) >> 8) + 4.0 * g * g + (round((767 - read_mean) * b * b) >> 8))

    def minecraft(self):
        """ Convert this color to the nearest Minecraft block color """
        
        # This maps colors to Stone, Concrete, etc.
        mc_colors_hex = {
           # --- ORES & MINERALS
            "26619c": (22, 0),   # Lapis Lazuli Block

            # --- STONE 
            "7d7d7d": (1, 0),    # Stone
            "5e5e5e": (1, 0),    # Stone 
            "666666": (98, 0),   # Stone Bricks
            "392923": (159, 15), # Black Terracotta
            
            
            # --- CONCRETE
            "cfd5d6": (251, 0),  # White Concrete
            "e06100": (251, 1),  # Orange Concrete
            "a9309f": (251, 2),  # Magenta Concrete
            "2389c6": (251, 3),  # Light Blue Concrete
            "f1af15": (251, 4),  # Yellow Concrete
            "5ea818": (251, 5),  # Lime Concrete
            "d5658f": (251, 6),  # Pink Concrete
            "36393d": (251, 7),  # Grey Concrete
            "7d7d73": (251, 8),  # Light Grey Concrete
            "157788": (251, 9),  # Cyan Concrete
            "2c2e8f": (251, 11), # Blue Concrete
            "603b1f": (251, 12), # Brown Concrete
            "495b24": (251, 13), # Green Concrete
            "8e2020": (251, 14), # Red Concrete
            "080a0f": (251, 15), # Black Concrete

            # --- TERRACOTTA 
            "d1b1a1": (159, 0),  # White Terracotta
            "a05325": (159, 1),  # Orange Terracotta
            "95576c": (159, 2),  # Magenta Terracotta
            "706c8a": (159, 3),  # Light Blue Terracotta 
            "ba8523": (159, 4),  # Yellow Terracotta
            "677534": (159, 5),  # Lime Terracotta
            "a07651": (159, 6),  # Pink Terracotta 
            "392923": (159, 7),  # Grey Terracotta
            "876b62": (159, 8),  # Light Grey Terracotta
            "565b5b": (159, 9),  # Cyan Terracotta
            "764556": (159, 10), # Purple Terracotta 
            "4a3b5b": (159, 11), # Blue Terracotta   
            "4d3323": (159, 12), # Brown Terracotta
            "4c532a": (159, 13), # Green Terracotta
            "8e3c2e": (159, 14), # Red Terracotta
            "251610": (159, 15), # Black Terracotta

            # --- WOODS & EARTH 
            "8f7748": (3, 0),    # Dirt
            "a67839": (5, 0),    # Oak Planks
            "745734": (5, 1),    # Spruce Planks
            "cbb685": (5, 2),    # Birch Planks
            "a2705a": (5, 3),    # Jungle Planks
            "8e4c27": (5, 4),    # Acacia Planks
            "403120": (5, 5),    # Dark Oak Planks
            "fffbf2": (155, 0),  # Quartz Block (Smoother white)
        }
        # Get the Hex string of the current voxel
        rgb = self.hex_str[0:6]
        
        # 2. CHECK EXACT MATCH
        if rgb in mc_colors_hex:
            color = rgb
            
        # 3. CHECK CACHE (Optimization)
        elif rgb in Color._color2minecraft:
            color = Color._color2minecraft[rgb]
            
        # 4. CALCULATE NEAREST NEIGHBOR
        else:
            dist = float('inf')
            color = "7d7d7d" # Default fallback (Stone)
            
            # Loop through our dictionary keys
            for palette_hex in mc_colors_hex.keys():
                # Compare mathematical distance
                cdist = self.compare(Color(palette_hex))
                
                if cdist < dist:
                    dist = cdist
                    color = palette_hex
            
            # Save the winner to cache
            Color._color2minecraft[rgb] = color

        # Return the Block ID and Data (e.g., 1, 0)
        return mc_colors_hex[color]


class VoxDefaultPalette:
    # Removed first "0x00000000" (it does not appear in MV)
    # Reverse order: ABGR
    palette = [
        "0xffffffff", "0xffccffff", "0xff99ffff", "0xff66ffff", "0xff33ffff", "0xff00ffff", "0xffffccff",
        "0xffccccff",
        "0xff99ccff", "0xff66ccff", "0xff33ccff", "0xff00ccff", "0xffff99ff", "0xffcc99ff", "0xff9999ff",
        "0xff6699ff", "0xff3399ff", "0xff0099ff", "0xffff66ff", "0xffcc66ff", "0xff9966ff", "0xff6666ff", "0xff3366ff",
        "0xff0066ff",
        "0xffff33ff", "0xffcc33ff", "0xff9933ff", "0xff6633ff", "0xff3333ff", "0xff0033ff", "0xffff00ff",
        "0xffcc00ff", "0xff9900ff", "0xff6600ff", "0xff3300ff", "0xff0000ff", "0xffffffcc", "0xffccffcc", "0xff99ffcc",
        "0xff66ffcc",
        "0xff33ffcc", "0xff00ffcc", "0xffffcccc", "0xffcccccc", "0xff99cccc", "0xff66cccc", "0xff33cccc",
        "0xff00cccc", "0xffff99cc", "0xffcc99cc", "0xff9999cc", "0xff6699cc", "0xff3399cc", "0xff0099cc", "0xffff66cc",
        "0xffcc66cc",
        "0xff9966cc", "0xff6666cc", "0xff3366cc", "0xff0066cc", "0xffff33cc", "0xffcc33cc", "0xff9933cc",
        "0xff6633cc", "0xff3333cc", "0xff0033cc", "0xffff00cc", "0xffcc00cc", "0xff9900cc", "0xff6600cc", "0xff3300cc",
        "0xff0000cc",
        "0xffffff99", "0xffccff99", "0xff99ff99", "0xff66ff99", "0xff33ff99", "0xff00ff99", "0xffffcc99",
        "0xffcccc99", "0xff99cc99", "0xff66cc99", "0xff33cc99", "0xff00cc99", "0xffff9999", "0xffcc9999", "0xff999999",
        "0xff669999",
        "0xff339999", "0xff009999", "0xffff6699", "0xffcc6699", "0xff996699", "0xff666699", "0xff336699",
        "0xff006699", "0xffff3399", "0xffcc3399", "0xff993399", "0xff663399", "0xff333399", "0xff003399", "0xffff0099",
        "0xffcc0099",
        "0xff990099", "0xff660099", "0xff330099", "0xff000099", "0xffffff66", "0xffccff66", "0xff99ff66",
        "0xff66ff66", "0xff33ff66", "0xff00ff66", "0xffffcc66", "0xffcccc66", "0xff99cc66", "0xff66cc66", "0xff33cc66",
        "0xff00cc66",
        "0xffff9966", "0xffcc9966", "0xff999966", "0xff669966", "0xff339966", "0xff009966", "0xffff6666",
        "0xffcc6666", "0xff996666", "0xff666666", "0xff336666", "0xff006666", "0xffff3366", "0xffcc3366", "0xff993366",
        "0xff663366",
        "0xff333366", "0xff003366", "0xffff0066", "0xffcc0066", "0xff990066", "0xff660066", "0xff330066",
        "0xff000066", "0xffffff33", "0xffccff33", "0xff99ff33", "0xff66ff33", "0xff33ff33", "0xff00ff33", "0xffffcc33",
        "0xffcccc33",
        "0xff99cc33", "0xff66cc33", "0xff33cc33", "0xff00cc33", "0xffff9933", "0xffcc9933", "0xff999933",
        "0xff669933", "0xff339933", "0xff009933", "0xffff6633", "0xffcc6633", "0xff996633", "0xff666633", "0xff336633",
        "0xff006633",
        "0xffff3333", "0xffcc3333", "0xff993333", "0xff663333", "0xff333333", "0xff003333", "0xffff0033",
        "0xffcc0033", "0xff990033", "0xff660033", "0xff330033", "0xff000033", "0xffffff00", "0xffccff00", "0xff99ff00",
        "0xff66ff00",
        "0xff33ff00", "0xff00ff00", "0xffffcc00", "0xffcccc00", "0xff99cc00", "0xff66cc00", "0xff33cc00",
        "0xff00cc00", "0xffff9900", "0xffcc9900", "0xff999900", "0xff669900", "0xff339900", "0xff009900", "0xffff6600",
        "0xffcc6600",
        "0xff996600", "0xff666600", "0xff336600", "0xff006600", "0xffff3300", "0xffcc3300", "0xff993300",
        "0xff663300", "0xff333300", "0xff003300", "0xffff0000", "0xffcc0000", "0xff990000", "0xff660000", "0xff330000",
        "0xff0000ee",
        "0xff0000dd", "0xff0000bb", "0xff0000aa", "0xff000088", "0xff000077", "0xff000055", "0xff000044",
        "0xff000022", "0xff000011", "0xff00ee00", "0xff00dd00", "0xff00bb00", "0xff00aa00", "0xff008800", "0xff007700",
        "0xff005500",
        "0xff004400", "0xff002200", "0xff001100", "0xffee0000", "0xffdd0000", "0xffbb0000", "0xffaa0000",
        "0xff880000", "0xff770000", "0xff550000", "0xff440000", "0xff220000", "0xff110000", "0xffeeeeee", "0xffdddddd",
        "0xffbbbbbb",
        "0xffaaaaaa", "0xff888888", "0xff777777", "0xff555555", "0xff444444", "0xff222222", "0xff111111"
    ]


class Vox(Thing):
    file_path = None
    """ file path for the MagicaVoxel vox file """

    def parse_vox_file(self):
        if not self.file_path:
            RuntimeError("Missing file_path param")

        self.voxels = []
        self.palette = []
        self.materials = []

        # Read the vox data in RIFF format
        # https://github.com/python/cpython/blob/3.8/Lib/chunk.py
        vox_file = open(self.file_path, "rb")
        vox_chunk = chunk.Chunk(vox_file, bigendian=False)
        chunk_name = vox_chunk.getname().decode("utf-8")
        if chunk_name != 'VOX ':
            raise RuntimeError('File %s is not a VOX file' % self.file_path)
        version = vox_chunk.chunksize
        if version != 150:
            raise RuntimeError('File %s has a not supported VOX version %i' % (self.file_path, version))
        # Let's read chunks
        """
        2. Chunk Structure
        -------------------------------------------------------------------------------
        # Bytes  | Type       | Value
        -------------------------------------------------------------------------------
        1x4      | char       | chunk id
        4        | int        | num bytes of chunk content (N)
        4        | int        | num bytes of children chunks (M)      
        N        |            | chunk content
        M        |            | children chunks
        -------------------------------------------------------------------------------
        """
        # MAIN Chunk
        main_chunk = chunk.Chunk(vox_file, bigendian=False)
        # Pass last 4 bytes for MAIN Chunk with children chunks
        vox_file.seek(vox_file.tell() + 4)

        # SIZE CHUNK
        """
        -------------------------------------------------------------------------------
        # Bytes  | Type       | Value
        -------------------------------------------------------------------------------
        4        | int        | size x
        4        | int        | size y
        4        | int        | size z : gravity direction
        -------------------------------------------------------------------------------
        """
        size_chunk = chunk.Chunk(vox_file, bigendian=False)
        vox_file.seek(vox_file.tell() + 4)  # number of children chunks
        x = size_chunk.read(4)
        y = size_chunk.read(4)
        z = size_chunk.read(4)

        # XYZI voxels
        """
        -------------------------------------------------------------------------------
        # Bytes  | Type       | Value
        -------------------------------------------------------------------------------
        4        | int        | numVoxels (N)
        4 x N    | int        | (x, y, z, colorIndex) : 1 byte for each component
        -------------------------------------------------------------------------------
        """
        xyzi_chunk = chunk.Chunk(vox_file, bigendian=False)
        vox_file.seek(vox_file.tell() + 4)  # number of children chunks
        n_voxels_bytes = xyzi_chunk.read(4)
        n_voxels = int.from_bytes(n_voxels_bytes, "little")
        for i in range(0, n_voxels):
            self.voxels.append(Voxel(xyzi_chunk.read(4)))
        # Transform or palette chunk or no more chunk if default palette
        try:
            transform_chunk = chunk.Chunk(vox_file, bigendian=False)
        except EOFError:
            transform_chunk = None
            logging.info("Legacy vox file with default palette")
        if transform_chunk and transform_chunk.chunkname.decode("utf-8") == "nTRN":
            vox_file.seek(vox_file.tell() + 4)  # number of children chunks
            transform_chunk.skip()

            group_chunk = chunk.Chunk(vox_file, bigendian=False)
            vox_file.seek(vox_file.tell() + 4)  # number of children chunks
            group_chunk.skip()

            transform_chunk = chunk.Chunk(vox_file, bigendian=False)
            vox_file.seek(vox_file.tell() + 4)  # number of children chunks
            # transform_chunk.skip()  # it is skipping 1 byte in the next chunk
            vox_file.read(transform_chunk.getsize())

            shape_chunk = chunk.Chunk(vox_file, bigendian=False)
            vox_file.seek(vox_file.tell() + 4)  # number of children chunks
            vox_file.read(shape_chunk.getsize())

            # Layers chunk
            NUM_LAYERS = 8  # By default
            for i in range(0, NUM_LAYERS):
                layer_chunk = chunk.Chunk(vox_file, bigendian=False)
                vox_file.seek(vox_file.tell() + 4)  # number of children chunks
                vox_file.read(layer_chunk.getsize())
            """
            7. Chunk id 'RGBA' : palette
            -------------------------------------------------------------------------------
            # Bytes  | Type       | Value
            -------------------------------------------------------------------------------
            4 x 256  | int        | (R, G, B, A) : 1 byte for each component
                                  | * <NOTICE>
                                  | * color [0-254] are mapped to palette index [1-255], e.g :
                                  |
                                  | for ( int i = 0; i <= 254; i++ ) {
                                  |     palette[i + 1] = ReadRGBA();
                                  | }
            -------------------------------------------------------------------------------
            """
            rgba_chunk = chunk.Chunk(vox_file, bigendian=False)
            vox_file.seek(vox_file.tell() + 4)  # number of children chunks
        else:
            rgba_chunk = transform_chunk
            vox_file.seek(vox_file.tell() + 4)  # notice
        if rgba_chunk:
            if rgba_chunk.getname().decode("utf-8") != 'RGBA':
                raise RuntimeError('VOX format not supported (multimodel?)')
            for i in range(0, round(rgba_chunk.getsize() / 4)):
                # RGBA
                color_bytes = rgba_chunk.read(1) + rgba_chunk.read(1) + rgba_chunk.read(1) + rgba_chunk.read(1)
                self.palette.append(Color(color_bytes.hex()))
        else:
            # Default palette
            for i in range(0, len(VoxDefaultPalette.palette)):
                color = VoxDefaultPalette.palette[i].replace('0x', '')
                # Convert ABGR to RGBA
                color = color[::-1]
                self.palette.append(Color(color))

        # Read the materials palette
        """
        (4) Material Chunk : "MATL"

        int32    : material id
        DICT    : material properties
                    (_type : str) _diffuse, _metal, _glass, _emit
                    (_weight : float) range 0 ~ 1
                    (_rough : float)
                    (_spec : float)
                    (_ior : float)
                    (_att : float)
                    (_flux : float)
                    (_plastic)
        """
        # One material per each color
        for i in range(0, len(self.palette)):
            try:
                materials_chunk = chunk.Chunk(vox_file, bigendian=False)
                if materials_chunk.getname().decode("utf-8") != 'MATL':
                    logging.info("Material data not found")
                    break
                else:
                    vox_file.seek(vox_file.tell() + 4)  # number of children chunks
                    material_id = int.from_bytes(materials_chunk.read(4), "little")
                    dict_entries_len = int.from_bytes(materials_chunk.read(4), "little")
                    # Read the _type key from dict
                    key_str_len = int.from_bytes(materials_chunk.read(4), "little")
                    key_str = materials_chunk.read(key_str_len).decode('utf-8')
                    value_str_len = int.from_bytes(materials_chunk.read(4), "little")
                    value_str = materials_chunk.read(value_str_len).decode('utf-8')
                    self.materials.append(value_str)
                    materials_chunk.skip()
                    if materials_chunk.tell() > materials_chunk.getsize():
                        vox_file.seek(vox_file.tell() - 1)  # Hack: not sure why skip goes 1 byte more
            except EOFError:
                logging.info("Material data not found")
                break

    @classmethod
    def find_minecraft_material(cls, material):
        mc_material = None
        if material == '_glass':
            mc_material = mcpi.block.GLASS
        elif material == '_metal':
            mc_material = mcpi.block.IRON_BLOCK
        return mc_material

    def create(self):

        self.parse_vox_file()

        for voxel in self.voxels:
            voxel_color = self.palette[voxel.color_index]
            print(voxel.color_index, voxel_color.hex_str)
            minecraft_material = None
            if self.materials:
                minecraft_material = self.find_minecraft_material(self.materials[voxel.color_index])
            minecraft_color = voxel_color.minecraft()

            # y, z are the reverse in vox format
            pos = Vec3(self.position.x + voxel.x,
                       self.position.y + voxel.z,
                       self.position.z + voxel.y
                      )

            if self.block == self._block_empty:
                self.set_block(pos, self._block_empty)
            elif minecraft_material:
                self.set_block(pos, minecraft_material.id)
            else:
                self.set_block(pos, minecraft_color[0], minecraft_color[1])

        init_pos, end_pos = self._blocks_memory.find_init_end_pos()
        self._end_position = end_pos