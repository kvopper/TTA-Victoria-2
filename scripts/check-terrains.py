import os
import sys

terrains_to_ignore = set([
    # Ignore continents
    'north_america', 'south_america', 'europe', 'africa', 'asia', 'oceania',
    # Ignore climates
    'arctic_polar_climate_plains', 'arctic_polar_climate_hills', 'arctic_polar_climate_woods',
    'cold_highlands_climate_plains', 'cold_highlands_climate_hills', 'cold_highlands_climate_woods',
    'cold_winter_climate_plains', 'cold_winter_climate_hills', 'cold_winter_climate_woods',
    'cold_humid_climate_plains', 'cold_humid_climate_hills', 'cold_humid_climate_woods',
    'temperate_oceanic_climate_plains', 'temperate_oceanic_climate_hills', 'temperate_oceanic_climate_woods',
    'temperate_drywinter_climate_plains', 'temperate_drywinter_climate_hills', 'temperate_drywinter_climate_woods',
    'temperate_drysummer_climate_plains', 'temperate_drysummer_climate_hills', 'temperate_drysummer_climate_woods',
    'temperate_subtropical_climate_plains', 'temperate_subtropical_climate_hills', 'temperate_subtropical_climate_woods',
    'semi_arid_cold_climate_plains', 'semi_arid_cold_climate_hills', 'semi_arid_cold_climate_woods',
    'arid_cold_climate_plains', 'arid_cold_climate_hills', 'arid_cold_climate_woods',
    'arid_climate_plains', 'arid_climate_hills', 'arid_climate_woods',
    'semi_arid_climate_plains', 'semi_arid_climate_hills', 'semi_arid_climate_woods',
    'tropical_savannah_drysummer_climate_plains', 'tropical_savannah_drysummer_climate_hills', 'tropical_savannah_drysummer_climate_woods',
    'tropical_savannah_climate_plains', 'tropical_savannah_climate_hills', 'tropical_savannah_climate_woods',
    'tropical_monsoon_climate_plains', 'tropical_monsoon_climate_hills', 'tropical_monsoon_climate_woods',
    'tropical_equatorial_climate_plains', 'tropical_equatorial_climate_hills', 'tropical_equatorial_climate_woods',
    # Ignore vanilla terrains
    'ocean', 'arctic', 'farmlands', 'forest', 'hills', 'woods', 'mountain', 'steppe', 'plains', 'jungle', 'marsh', 'desert', 'desert_hills'
])

terrain_loc_file = "localisation/terrain.csv"
terrain_workplace_file = "events/Work Place.txt"
terrain_interface_file = "interface/province_interface.gfx"
terrain_txt_file = "map/terrain.txt"
terrain_img_folder = "gfx/interface/terrain/"

"""
Get all terrains that are found in the localisation file
"""
def get_terrains_from_loc_file():
    terrains = set()
    with open(terrain_loc_file, 'r', encoding='windows-1252') as f:
        for line in f:
            # Ignore comments and blank lines
            if line.startswith('#') or not line.strip():
                continue
            parts = line.split(';')
            if len(parts) < 2:
                continue
            terrain = parts[0].strip()
            if terrain not in terrains_to_ignore:
                terrains.add(terrain)
    return terrains

"""
Get all terrains that are found in the work place file
"""
def get_terrains_from_work_place_file():
    terrains = set()
    found_start_line = False
    with open(terrain_workplace_file, 'r', encoding='windows-1252') as f:
        for line in f:
            line = line.strip()
            # Ignore comments and blank lines
            if line.startswith('#') or not line.strip():
                continue
            # Ignore all lines up till we find the event 12057
            if not found_start_line and 'id = 12057' not in line:
                continue
            found_start_line = True
            # Lines will be of the form "terrain = <name>", so split on '=' and take the second part
            if line.startswith('terrain ='):
                terrain = line.split('=')[1].strip()
                if terrain not in terrains_to_ignore:
                    terrains.add(terrain)
            # Next event is 12058, so stop processing after that
            if found_start_line and line.startswith('id = 12058'):
                break
    return terrains

"""
Get all terrains that are found in the interface file
"""
def get_terrains_from_interface_file():
    terrains = set()
    with open(terrain_interface_file, 'r', encoding='windows-1252') as f:
        for line in f:
            line = line.strip()
            # Ignore comments and blank lines
            if line.startswith('#') or not line.strip():
                continue
            # Lines will be of the form "name = "GFX_terrainimg_<name>", so check if line starts with "name = "GFX_terrainimg_" and if so extract the name
            if line.startswith('name = "GFX_terrainimg_'):
                terrain = line[len('name = "GFX_terrainimg_'):-1].strip()
                if terrain not in terrains_to_ignore:
                    terrains.add(terrain)
    return terrains

"""
Get all terrains that are found in the terrain.txt file
"""
def get_terrains_from_terrain_txt_file():
    terrains = set()
    found_start_line = False
    with open(terrain_txt_file, 'r', encoding='windows-1252') as f:
        for line in f:
            line = line.strip()
            # Ignore comments and blank lines
            if line.startswith('#') or not line.strip():
                continue
            # Ignore all lines up till we find the categories line
            if not found_start_line and 'categories = {' not in line:
                continue
            # Up until ocean1
            if found_start_line and line.startswith('ocean1'):
                break
            if not found_start_line:
                found_start_line = True
                continue
            # Lines will be of the form "<name> = {", so check if line ends with " = {"
            if line.endswith(' = {'):
                terrain = line[:-len(' = {')].strip()
                if terrain not in terrains_to_ignore and terrain != 'categories':
                    terrains.add(terrain)
    return terrains

"""
Get all terrains that are found in the terrain images folder
"""
def get_terrains_from_img_folder(folder=terrain_img_folder):
    terrains = set()
    for fn in os.listdir(folder):
        # If its a folder, look inside it for .tga files
        if os.path.isdir(os.path.join(folder, fn)):
            terrains.update(get_terrains_from_img_folder(os.path.join(folder, fn)))
        if fn.endswith('.tga'):
            if fn.startswith('terrain_'):
                terrain = fn[len('terrain_'):-4]
            else:
                terrain = fn[:-4]
            if terrain not in terrains_to_ignore:
                terrains.add(terrain)
    return terrains

def main():
    loc_terrains = get_terrains_from_loc_file()
    work_place_terrains = get_terrains_from_work_place_file()
    interface_terrains = get_terrains_from_interface_file()
    terrain_txt_terrains = get_terrains_from_terrain_txt_file()
    # img_folder_terrains = get_terrains_from_img_folder()

    all_terrains = loc_terrains | work_place_terrains | interface_terrains | terrain_txt_terrains # | img_folder_terrains

    missing_in_loc = all_terrains - loc_terrains
    missing_in_work_place = all_terrains - work_place_terrains
    missing_in_interface = all_terrains - interface_terrains
    missing_in_terrain_txt = all_terrains - terrain_txt_terrains
    # missing_in_img_folder = all_terrains - img_folder_terrains

    problems = False
    if missing_in_loc:
        problems = True
        print(f'\nTerrains missing in localisation file: {missing_in_loc}')
    if missing_in_work_place:
        problems = True
        print(f'\nTerrains missing in work place file: {missing_in_work_place}')
    if missing_in_interface:
        problems = True
        print(f'\nTerrains missing in interface file: {missing_in_interface}')
    if missing_in_terrain_txt:
        problems = True
        print(f'\nTerrains missing in terrain.txt file: {missing_in_terrain_txt}')
    # if missing_in_img_folder:
    #     problems = True
    #     print(f'\nTerrains missing in image folder: {missing_in_img_folder}')

    sys.exit(1 if problems else 0)

if __name__ == '__main__':
    main()
