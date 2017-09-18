'''
Edits the sector backgrounds, view distance and fog effects.

In IEX, some sectors use a short fade distance even when not fogged,
 which looks iffy.

Note: base files have fade distances all over the place, generally not
 attached to fogging (probably considering fog more of a visual effect,
 and using fade distance to imply density), and with wide variations
 in fade in/out distance gaps (sometimes fade out is 2x fade in distance,
 sometimes they are equal).

Options:
1) Set fade distance based on fog density only.
2) Set fog density based on existing fade distance.
3) Try to keep old values, but limit the fade in proximity based on
 fog density (eg. 50 fog may allow fadein at 5k or later, 0 fog only at
 200km or later).
4) Find a way to edit sectors to hide stars in foggy sectors, and maybe
 any planets as well. This will be done outside of TBackgrounds.
 See notes on this issue further below.

There is generally more variation in fade distances than in fog densities.
Fade distance may have been set for performance reasons (eg. shorter in 
 sectors with more stuff or expecting more action) for older computers, and
 shouldn't be overly relied on.

0 fog density will always fix fade to 200km; select other data points
 based on scaling desired.


Note on stars/planets:

    The main issue with X3 foggy sectors is that they have a starfield and visible
    planets, which completely break immersion when asteroids or factories are faded
    out and then pop in in front of the stars/planets behind them (if stars are
    visible, a factory should be as well).
    Nearly every fogged sector in X3 has this problem, except perhaps the Hole.
    Fixing this issue would require one of the following:

    1) Edit the background files in objects/environments/nebulas and /planets to
    make the stars and planets used by foggy sectors effectively blank somehow,
    eg. black.
    -The drawback is that some non-foggy sectors may make use of the
    same backgrounds/stars or planets, which would mess up their visuals.
    --Eg. a foggy tbackgrounds and a non-foggy tbackgrounds may reference the
    same background image folder.
    --Can perhaps do an analysis pass to build a structure of background:image
    pairs and use that to determine which images are always used in foggy sectors,
    making them safer for star removal.
    -This is also messy to accomplish, since it requires extracting a large number
    of starfields from the appropriate background folders; likely all star fields
    need extracting so that this transform can freely select which to keep and
    which to replace with blank fields.
    --If just removing stars, this is pretty easy: using the name in tbackgrounds,
    create a path to where the stars file would be and create an empty file in
    its place.

    2) Edit the x3_universe.xml file, set "stars" to 1 to make that
    part of the background invisible, and remove any planet generation.
    -This likely requires a new game start, since this xml file is only used to set
    up sectors or to add new objects (if one is put into the file that is not
    already in the sector), but is not used when loading a save game since
    sectors are saved with their attributes (probably to make dynamic sector
    changes work out better, eg. with unfocused jumps).
    -The default map file for The Hole appears to already hide the stars, as do
    a few others (eg. the Xenon sector north of Getsu Fune, which also has a
    very heavy fogging effect, and has "nebula" set to 1, the only sector
    to set this).

    3) Use a script with various sector edit commands that can (hopefully) delete
    planets and stars.
    -This might need to sync up with x3_universe.xml, so that the planets are not
    re-added.
    -Requires manually running the script while in game to update the sectors.
    -Some complexity in generating the script text.
    -Need a way to determine which sectors are to be fogged (where tbackground
    entries may be used by multiple sectors), probably by parsing existing
    sector information to determine the background being referenced using
    the x3_universe.xml file.
    -There appears to be no documented way to remove planets, though there must
    be some method since unfocused jump sectors add planets and have to clear
    them somehow.
    -There is no command to remove stars; the best option would be to change
    the background to one that has a blank or missing star field.


Note:
    In game, the graphics setting for visual distance will override object fade
    options when set above Medium. Further, if set to Medium, lighting are further
    objects seems to have some reduced mode,
    
    This is most evident on solar panels which might have a bright sheen when 
    at a distance, only taking on proper shading when closer or when the 
    graphics option for visual distance is turned up.

    There is no good way around this issue if trying to allow for fade effects.
    In general, the fade effects are too cool in play to give them up.
    
'''
import os
from File_Manager import *


@Check_Dependencies('TBackgrounds.txt')
def Set_Minimum_Fade_Distance(distance_in_km = 3):
    '''
    Sets a floor to fade distance, so that object do not appear
     too closely. May be useful in some sectors with really short view
     distances, though may also want to keep those for variety.
    Note: max fade distance will be set to minimum fade distance if
     it would otherwise be lower. Recommend following this with a
     call to Adjust_Fade_Start_End_Gap.

    distance_in_km : 
        Minimum fade distance, in km.
    '''
    #Loop over the backgrounds.
    for this_dict in Load_File('TBackgrounds.txt'):
        #Look up existing fade.
        fade_start_km = int(this_dict['fadeout_start']) / 1000 / 500
        fade_end_km   = int(this_dict['fadeout_end'])   / 1000 / 500
        #Apply minimum fade distance.
        #Adjust start and end (to avoid end being closer than start).
        fade_start_km = max(fade_start_km, distance_in_km)
        fade_end_km   = max(fade_end_km, distance_in_km)
        #Put them back.
        #Convert to 1/500-m units.
        this_dict['fadeout_start'] = str(int(fade_start_km * 1000 * 500))
        this_dict['fadeout_end']   = str(int(fade_end_km * 1000 * 500))

        
        
@Check_Dependencies('TBackgrounds.txt')
def Adjust_Fade_Start_End_Gap(
    fade_gap_min_func = lambda x: x*1, 
    fade_gap_max_func = lambda x: 20):
    '''
    Adjust the gap between the start and end fade distance, changing how
    quickly objects will fade in.
    This will never affect fade_start, only fade_end.

    fade_gap_min_func, fade_gap_max_func:
        Functions which take fade_start as the argument, in km, and return
        the min and max gap allowed.
        Example: 
            Set fade gap to be as much as fade start:
                fade_gap_min_func = lambda start: start*1
            Require the fade gap be no longer than 20 km:
                fade_gap_max_func = lambda start: 20
    '''
    for this_dict in Load_File('TBackgrounds.txt'):
        #Look up existing fade.
        fade_start_km = int(this_dict['fadeout_start']) / 1000 / 500
        fade_end_km   = int(this_dict['fadeout_end'])   / 1000 / 500
        
        #Current gap may be 0 if a min was applied, but that is okay,
        # it gets increased here.
        gap = fade_end_km - fade_start_km
        #Apply minimum gap first.
        gap = max(gap, fade_gap_min_func(fade_start_km))
        #Now apply the max (may put a cap on the min if less than that min).
        gap = min(gap, fade_gap_max_func(fade_start_km))
        #Apply the gap to fade_end.
        fade_end_km = fade_start_km + gap

        #Put them back.
        #Convert to 1/500-m units.
        this_dict['fadeout_start'] = str(int(fade_start_km * 1000 * 500))
        this_dict['fadeout_end']   = str(int(fade_end_km * 1000 * 500))

        

        
@Check_Dependencies('TBackgrounds.txt')
def Adjust_Particle_Count(
    base_count = 10,
    fog_factor = 0.5
    ):
    '''
    Change the number of particles floating in space around the camera.
    Default game is 100, mods often set to 0, but can keep some small number
     for a feeling of speed.

    base_count:
        The base number of particles to use in all sectors.
        Default is 10, or 10% of the vanilla particle count.
    fog_factor:
        The portion of sector fog to add as additional particles.
        Eg. a fog factor of 0.5 will add 25 more particles in heavy fog.
    '''
    for this_dict in Load_File('TBackgrounds.txt'):
        density = int(this_dict['fog_density'])
        #Add the base value to the fog scaled value.
        num_particles = base_count + density * fog_factor
        this_dict['num_particles'] = str(int(num_particles))

                
        
@Check_Dependencies('TBackgrounds.txt')
def Remove_Stars_From_Foggy_Sectors(
    #The fog requirement for star removal; all backgrounds affected need a
    # fog above this much.
    #This is not as important as fade distance in general, it seems.
    # Set to 12, which is used by a background that shares images with the
    #  background used by Maelstrom, which should be faded.
    fog_requirement = 12,
    #The highest fade distance to allow; all backgrounds affected need a
    # fade_start under this value (to prevent star removal in high visibility
    # sectors). In km.
    fade_distance_requirement_km = 60,
    #Special flag to clean out old files.
    _cleanup = False
    ):
    '''
    Removes star backgrounds from sectors with significant fog and short fade
    distance. Fogged sectors sharing a background with an unfogged sector will
    not be modified, as the background needs to be edited for all sectors
    which use it. Fade is removed from sectors which will not have their
    stars removed.
    
    fog_requirement:
        The fog requirement for star removal; all backgrounds affected need a
         fog above this much.
        This is not as important as fade distance in general, it seems.
         Set to 12, which is used by a background that shares images with the
          background used by Maelstrom, which should be faded.
    fade_distance_requirement_km:
        The highest fade distance to allow; all backgrounds affected need a
         fade_start under this value (to prevent star removal in high visibility
         sectors). In km.
    '''
    #Define the nebulae directory, to which empty star files will be written.
    nebulae_directory = os.path.join('..','objects','environments','nebulae')

    #Nested function to clean up any old files.
    #Optionally, will not delete files in images_allowing_star_removal_list.
    def Cleanup(images_allowing_star_removal_list = []):

        #To avoid having to pull star images from all possible background images,
        # the Remove_stars_from_foggy_sectors transform will only create empty
        # star files. However, a previous run may have made such files which
        # will not be wanted on this run, so need to clean them out.
        #Check if the directory exists (if not, can return).
        if not os.path.exists(nebulae_directory):
            return

        #Get all folders in that directory.
        #This will get a list of all files and folders, and filter out non-folders.
        folder_list = [name for name in os.listdir(nebulae_directory) if os.path.isdir(
                                            os.path.join(nebulae_directory, name))]

        #Note: folder names should always match image names.
        #Loop over the folders.
        for image_name in folder_list:

            #Get the expected name of the star file.
            #This is always based on the image name, with some prefix and suffix.
            star_file_name = 'nebula_{}_stars_01.bob'.format(image_name)
            star_path = os.path.join(nebulae_directory, image_name, star_file_name)

            #Check if the star file exists, and is not one of those to be kept.
            if (os.path.exists(star_path) 
            and image_name not in images_allowing_star_removal_list):
                #Remove the file if it is size 0ish.  Maybe give a little slack for file
                # overhead; star files with content are around 40 kB.
                #Larger files will be left in place for now, to avoid accidental
                # deletion of something important.
                if os.path.getsize(star_path) < 10:
                    os.remove(star_path)
              
    #When being called for cleanup, run the Cleanup function and return.
    if _cleanup:
        Cleanup()
        return
    
    #Nested function to generate empty star files.
    #Placed here to keep code near Cleanup, since there is some overlap
    # in folder naming and such.
    def Make_Empty_Star_Files(images_allowing_star_removal_list):
        #Check if the directory exists (if not, make it).
        if not os.path.exists(nebulae_directory):
            os.makedirs(nebulae_directory)

        #Loop over the images to remove stars from.
        for image_name in images_allowing_star_removal_list:

            #Get the expected name of the star file.
            #This is always based on the image name, with some prefix and suffix.
            star_file_name = 'nebula_{}_stars_01.bob'.format(image_name)
            star_folder = os.path.join(nebulae_directory, image_name)
            star_path = os.path.join(star_folder, star_file_name)

            #Check if the folder exists; make it if not.
            if not os.path.exists(star_folder):
                os.makedirs(star_folder)

            #Check if the star file doesn't exists.
            #If it does exist, it may have actual data, so this will avoid
            # overwriting it. TODO: maybe do a size check, and throw a
            # warning if skipping replacement.
            if not os.path.exists(star_path):
                #Make a dummy file.
                with open(star_path, 'w') as file:
                    pass

    
    #Note: the following are a bunch of options tried out for various ways
    # of setting fade and fog values.
    #To avoid complicating the transform call, only the best options have
    # been selected to be function inputs, when using star removal from
    # foggy sectors.
    #TODO: clean all this up, maybe.
    
    #If star display should be disabled in heavily fogged sectors.
    #This will always remove display in any sector that has fade less than
    # Fade_removal_distance, after performing the above transform on fade amounts.
    #Note: this also makes use of the Remove_fade_unless_background_image_is_fog flag,
    # and will not remove stars unless the sector image has a 'fog' style name.
    #Remove_stars_from_foggy_sectors = True
    #Rename these to the same names that used to be used internally to this code,
    # in case this code is ever expanded in the future to keep naming clear.
    remove_stars_fog_requirement = fog_requirement
    remove_stars_fade_distance_requirement_km = fade_distance_requirement_km

    #Which adjustment to use.
    #0: Set fade distance by fog density (feels best so far).
    #1: Set fog density by fade distance (doesn't feel like enough fog for some distances).
    #2: Extend fade distance when fog density is <= some threshold; no other changes.
    #3: Remove fade entirely (fog effects otherwise unchanged).
    #4: Remove fade when the background image will have stars, otherwise no change.
    #   For use with Remove_stars_from_foggy_sectors.
    Fade_fog_adjustment_type = 4
    #Distance to use for fading when fade effects should be removed, in km.
    #This should be far enough that the player will never be further than this from
    # any object.
    Fade_removal_distance = 200
    #If fade should be disabled for sectors that don't have 'fog' in their image name,
    # to try to avoid fading occurring in front of a star field.
    # Note: 'fog' images may still have stars in them, so this is not perfect.
    Remove_fade_unless_background_image_is_fog = True

    #Per fade-type settings, keeping them split out for better organization.
    if Fade_fog_adjustment_type == 0:
        #Distance to start fading out when fog is 50 (highest value seen).
        Fade_Start_km_at_50_fog = 15
        #Distance to end fading out when fog is 50, if type 1.
        Fade_End_km_at_50_fog = 30
        #Distance to start fading as fog goes to 0.
        Fade_Start_km_near_0_fog = 100
    elif Fade_fog_adjustment_type == 1:
        Fade_Start_km_at_50_fog = 15
        Fade_End_km_at_50_fog = 30
        Fade_Start_km_near_0_fog = 100
        #Minimum difference between fade start and end to allow; end will get
        # boosted to meet this if needed.
        Min_distance_km_fade_start_to_end = 5
    elif Fade_fog_adjustment_type == 2:
        #The fog density at or above which fade will be kept, below which fade is removed.
        #Set 0 to only allow fade is sectors with at least some fog.
        #Can set negative to disable fade entirely, but Fade_fog_adjustment_type == 3 does
        # that more clearly.
        #Try out ~20 for now
        Min_fog_density_to_allow_fade = 0
    elif Fade_fog_adjustment_type == 3:
        pass
    elif Fade_fog_adjustment_type == 4:
        pass
    

    tbackgrounds_dict_list = Load_File('TBackgrounds.txt')
    
    #Go through tbackgrounds and figuring out which entries
    # share background images.
    #This will key by image name, and have a list of backgrounds using
    # that image.
    image_background_list_dict = {}
    #This will key by background name, and hold the basic properties
    # of interest.
    background_properties_dict_dict = {}
    for this_dict in tbackgrounds_dict_list:
        #Get the image string.
        image = this_dict['image']
        #Add the background to this image's list, making a new entry if needed.
        if image not in image_background_list_dict:
            image_background_list_dict[image] = []
        image_background_list_dict[image].append(this_dict['name'])

        #Record some background properties.
        background_properties_dict_dict[this_dict['name']] = {
            'image'        : image,
            'fog_density'  : int(this_dict['fog_density']),
            'fade_start_km': int(this_dict['fadeout_start']) / 1000 / 500,
            'fade_end_km'  : int(this_dict['fadeout_end'])   / 1000 / 500,
            }


    #Can now build a set of images which are candidates for star removal
    # based on fogging. Always make this list even if not removing stars,
    # since it is used for cleaning out old files as well.
    images_allowing_star_removal_list = []
    for image, background_list in image_background_list_dict.items():
        #Determine the minimum fog density and maximum fade_start out of all 
        # backgrounds using this image.
        min_fog = 100
        max_fade_start = 0
        for background in background_list:
            min_fog        = min(min_fog, 
                                    background_properties_dict_dict[background]['fog_density'])
            max_fade_start = max(max_fade_start, 
                                    background_properties_dict_dict[background]['fade_start_km'])

        #Allow star removal only if both fog is above a threshold and
        # fade is within a threshold.
        #Eg. don't remove stars if there is not enough fog effect to cover
        # for the dark background, and also don't remove if the sector
        # had full view distance.
        if min_fog >= remove_stars_fog_requirement:
            if max_fade_start <= remove_stars_fade_distance_requirement_km:
                #Also check for 'fog' in the image name, if requested.
                if Remove_fade_unless_background_image_is_fog == False or 'fog' in image:
                    images_allowing_star_removal_list.append(image)

                        

    #To avoid having to pull star images from all possible background images,
    # the Remove_stars_from_foggy_sectors transform will only create empty
    # star files. However, a previous run may have made such files which
    # will not be wanted on this run, so need to clean them out.
    #To save some file accesses, inform this of the list of images
    # to be kept.
    Cleanup(images_allowing_star_removal_list)                    
    #Generate the empty star files.
    Make_Empty_Star_Files(images_allowing_star_removal_list)


    #Loop over the backgrounds to handle fade.
    for this_dict in tbackgrounds_dict_list:
  
        #Look up existing fade.
        fade_start_km = int(this_dict['fadeout_start']) / 1000 / 500
        fade_end_km   = int(this_dict['fadeout_end'])   / 1000 / 500
        density = int(this_dict['fog_density'])

        if Fade_fog_adjustment_type == 0:
            #Calculate fade values.
            if density == 0:
                #Remove fade
                fade_start_km = Fade_removal_distance
                fade_end_km = Fade_removal_distance
            else:
                #Start at base value for 50 density, add more for density under 50,
                # up to +Fade_Start_km_near_0_fog km.
                fade_start_km  = Fade_Start_km_at_50_fog + Fade_Start_km_near_0_fog * (1 - density/50)
                fade_end_km    = Fade_End_km_at_50_fog   + Fade_Start_km_near_0_fog * (1 - density/50)
                                

        elif Fade_fog_adjustment_type == 1:
            start_density = density #For debug view

            #Calculate density based on fade start.
            #Over Fade_Start_km_near_0_fog, want density 0 (and to boost up fade).
            if fade_start_km >= Fade_Start_km_near_0_fog:
                density = 0
                #Remove fade
                fade_start_km = Fade_removal_distance
                fade_end_km   = Fade_removal_distance
            else:
                #Density is 50 at Fade_Start_km_at_50_fog, goes down as
                # the fade goes up.
                density = 50 * (1 - (fade_start_km - Fade_Start_km_at_50_fog) 
                                    / (Fade_Start_km_near_0_fog - Fade_Start_km_at_50_fog))
                #Keep density floored at 0.
                density = max(0, density)


            #Check if fade_end needs a boost.
            if fade_end_km < fade_start_km + Min_distance_km_fade_start_to_end:
                #This will keep a little variation by just adding on the
                # minimum amount.
                fade_end_km += Min_distance_km_fade_start_to_end
                this_dict['fadeout_end']   = str(int(fade_end_km * 1000 * 500))
                                   

        elif Fade_fog_adjustment_type == 2:
            #Only do fade boost on density 0.
            if density == 0:
                fade_start_km = Fade_removal_distance
                fade_end_km = Fade_removal_distance

        elif Fade_fog_adjustment_type == 3:
            #Remove fade entirely.
            fade_start_km = Fade_removal_distance
            fade_end_km = Fade_removal_distance
                
        elif Fade_fog_adjustment_type == 4:
            #Check if the background image will not have stars removed.
            if this_dict['image'] not in images_allowing_star_removal_list:
                #Remove fading in this case; treat sector as clear.
                fade_start_km = Fade_removal_distance
                fade_end_km = Fade_removal_distance

                    
        if Remove_fade_unless_background_image_is_fog:
            #Turn off any fading if the background image doesn't have 'fog' in it.
            if 'fog' not in this_dict['image']:
                fade_start_km = Fade_removal_distance
                fade_end_km = Fade_removal_distance
                
        #Put it all back.
        this_dict['fog_density']   = str(int(density))
        #Convert to 1/500-m units.
        this_dict['fadeout_start'] = str(int(fade_start_km * 1000 * 500))
        this_dict['fadeout_end']   = str(int(fade_end_km * 1000 * 500))
            
    return

