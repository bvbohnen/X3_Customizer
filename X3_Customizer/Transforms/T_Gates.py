'''
Transforms to gates.
'''

'''
Aim is to find a solution to the issue of the default gate rings causing
large ships to suicide on the projecting pylons.
 
Files of interest:
/objects
    /others
        argon_gate.bod
        argon_gate_destroyed.bod
        argon_gate_effect.bod
        argon_gate_scene.bod
        terraformer_gate.bod
        terraformer_gate_scene.bod
        terraformer_gate_inactive_scene.bod
        terran_catapult_gate.bod
        terran_catapult_gate_scene.bod
    /patch20
        argon_inactivegate.bod
        terran_gate.pbd
        terran_gate_construction.pbd
        terran_gate_scene.bod

    The terraformer gates appear to be the ones in the Hub.
    On one side these are the same as standard argon gates, but the 
    backside has shortened stubs, plus some minor details are
    changed (eg. orange instead of blue ring glow).

    The patch20 terran gate appears to be the one used for the Aldrin
    expansion plot.

    Note: bod files are text, and somewhat suitable for direct editing.
    The scene file puts together bod files, with some placement
    information.
    The pbd files are just gzipped bod files.


Some possible options:
    1) Rotate the ring in the scene file, to move the pylons to top/bottom.

    2) Reverse the terraformer ring so the stubs are on the active side, and 
       use this reversed ring for the argon gates.  Side effect is that the 
       pylons may run into the side of the hub walls; need to watch for
       this.  Also should reverse the inactive gates to be consistent.
       Could also use the reversed gates only for standard gates, and then
       set the hub gates themselves to not have rings since the hub walls
       already give an okay superstructure.

    3) Remove the ring entirely by writing an empty bod file for it.
       Don't touch the scene. 
       This is the old method, which works okay but is rather ugly.

    4) Rescale the gate, ring and portal, if possible.  There does not seem
       to be a way to do this in the scene file, however.

    5) Swap terran gates (from the Aldrin expansion plot) in for the normal
       gates, as they don't have pylons that project as far, though they do
       have more mass in general for ships to collide with.

    6) See update further below on a pylonless gate model.

Any of these options could work.
A generalized transform may seek to apply any of them.
To mix rotation and resizing with swaps and such, it is probably best to
do it in one transform instead of over several.


Scene file notes (taken partially from playing with cockpit positions):

    '/' is the comment character.

    Of interest:
    http://www.argonopedia.org/wiki/BOD_scene_syntax

    Example line:
    P 0; B others\argon_gate; N Bothers\argon_gate; b
    { 0x2002;  209; -2632; 2136;  0.000000; 0.000000; 0.000000; 0.000000;  -1;  -1; }

    The first line appears to be source file and a unique name
    to use locally. The second line has to do with placement.
    "P #" is an index for the path, which can be referenced later using F
     for relative paths, but isn't used in the files sampled.
    "B [path]" is the base path of the object being placed, or an integer
     which paths implicitly to objects/v.
    "N [name]" is a name for 3dmax to give to a node, and can be ignored.
    "b" prefix before a set of flags, not used in files sampled.

    Elements:
        0: flags, always 0x2002.
           This appears to mean 'rotation is present' and 'rotation is absolute'.
        1: int, x, left/right offset from center.
        2: int, y, vertical offset from center.
        3: int, z, forward/back offset from center.
        4: float, 0 to 1, base angle, 0 to 360 degrees.
        5: float, x axis multiplier on (4). When >1, also scales size.
        6: float, y axis 
        7: float, z axis 
        8: unknown, always -1
        9: unknown, always -1

    Experimentation gets really weird results in some cases with scaling terms,
    eg. setting (.25,1,1,1) causes the ring to be tremendously warped and enlarged
    and partly rotated.  Maybe the x/y/z terms are added, and their total is
    used to determine scaling?

    Useful points:
    (.25,0,0,1)  will do the pylon rotation to the top/bottom of the gate.
    (.125,0,0,1) will do a half rotation, so the pylons are in the corners.
    (.5,0,1,0) will flip the ring around. (.5,1,0,0) also works.

    Notes:
        (.5,0,1.0,0) flips around the gate
        (.5,0,0.9,0) shrinks the gate around y axis and z axis.
        (.5,0,0.8,0) shrinks the gate even more
        (.5,0,0.71,0) shrinks to be very tiny
        (.5,0,0.70,0) still tiny, but now the gate is not flipped. Purely squishes now.
        (.5,0,0.6,0) unshrinking, no rotation.
        (.5,0,0.1,0) nearly done unsrhinking
        (.5,0,0.0,0) no effect.

        What is happening here?  The start and end points make sense assuming the
        angle is multiplied by an axis scaler.  The rest of the terms, though,
        make no sense, as the rotation does not change (except being completely
        lost between .71 and .70), and the size shink has a weird inflection
        point at the same ~.70x spot.

        If the axis term is a square root of the real term, it makes slightly
        more sense, since sqrt(0.5) = 0.707. Hence, the actual value is the
        one given squared.
        If this actual value is then rounded to determine a binary choice to
        apply the angle or not, the angle aspect somewhat makes sense.
        The size scaling (and being applied to y/z but not x) does not make
        sense, however.

        TODO: maybe figure this out. Scaling may just be a bug and not 
        actually intentionally usable.

        
    To minimize the need to overwrite existing bod files, new scenes can
    be created, and in TGates they can be pointed to.

        The new scenes can be placed in the objects/others folder for some
        consistency.
        Can either grab, copy, and edit the original files, or just create
        new ones from scratch.
        
        The latter is a little less safe against other mods, but probably 
        good enough for now, and requires the user to pull fewer files.
        (Plus there is no mechanism in place for editing object files from 
        one folder up, since the source files are assumed to start from 
        the addon directory.)

    The original scenes, with comments stripped off, are:

    argon_gate_scene:
        VER: 3;
        P 0; B others\argon_gate; N Bothers\argon_gate; b
          { 0x2002;  209; -2632; 2136;  0.000000; 0.000000; 0.000000; 0.000000;  -1;  -1; }
        P 1; B others\argon_gate_effect; N Bothers\argon_gate_effect; b
          { 0x2002;  0; 0; 49802;  0.000000; 0.000000; 0.000000; 0.000000;  -1;  -1; }

    terraformer_gate_scene:
        VER: 3;
        P 0; B others\terraformer_gate; N Bothers\terraformer_gate; b
          { 0x2002;  0; 0; 0;  0.000000; 0.000000; 0.000000; 0.000000;  -1;  -1; }
        P 1; B others\argon_gate_effect; N Bothers\argon_gate_effect; b
          { 0x2002;  0; 0; 47500;  0.000000; 0.000000; 0.000000; 0.000000;  -1;  -1; }

    terraformer_gate_scene_inactive:
        VER: 3;
        P 0; B others\terraformer_gate; N Bothers\terraformer_gate; b
          { 0x2002;  5000; 0; 0;  0.000000; 0.500000; 0.500000; 0.500000;  -1;  -1; }

    terran_catapult_scene:
        VER: 3;
        P 0; B others\terran_catapult_gate; N Bothers\terran_catapult_gate; b
          { 0x2002;  0; 0; 1793560;  0.000000; 0.000000; 0.000000; 0.000000;  3333;  1; }
          { 0x2002;  0; 0; 1793560;  0.000000; 0.000000; 0.000000; 0.000000;  -1;  -1; }

        (Side note: there are two entries here, and there is no info on what the
         last two fields (the only that differ) mean. In testing, commenting out
         either entry produces a scene that looks exactly the same, indicating
         these duplicate entries may be redundant. Generated files will just
         create the -1;-1 line unless problems arise.)

    terran_gate_scene:
        VER: 3;
        P 0; B 100000; N Particle View 01;
          { 0x2002;  0; 0; 0;  0.000000; 0.000000; 0.000000; 0.000000;  -1;  -1; }
        P 1; B others\argon_gate_effect; N Bothers\argon_gate_effect; b
          { 0x2002;  0; 0; 53844;  0.000000; 0.000000; 0.000000; 0.000000;  -1;  -1; }
        P 2; B patch20\terran_gate; N Bpatch20\terran_gate; b
          { 0x2002;  209; -2632; 2136;  0.000000; 0.000000; 0.000000; 0.000000;  -1;  -1; }

    Note: for argon_inactivegate has no scene file to edit, and is not
    referenced directly in tgates.  It is, however, used in the
    TSpecial.txt file, under the SS_SPECIAL_GATE_INACTIVE item, which references
    argon_inactivegate directly. This could be replaced with a scene file
    reference, created to have a matched argon gate without the portal.

    Similarly, SS_SPECIAL_GATE_CONSTRUCTION references a raw terran_gate_construction,
    which could similarly be replaced with a scene.

Update:
    Found another ring option:
        stations\others\terraformer_gate
    In this case, the ring is plain with no projections, and in quick testing it is
    the proper size for the portal. This appears to be the best option, though the
    hub gate was working well regardless, and could be kept for the Hub itself.

    The front side of this gate has dim spots where the normal top/bottom protrusions
    would go, but the back side has a clean ring. As such, the gate should be flipped
    around, similar to the hub, to look slightly better.

'''
from .. import File_Manager
import copy 

# -Removed; Adjust_Gate_Rings is a more powerful version that can
#  do this as well.
# @File_Manager.Transform_Wrapper('types/TGates.txt')
# def Swap_Standard_Gates_To_Terran_Gates():
#     '''
#     Changes standard gates into Terran gates, possibly helping reduce
#     large ship suicides when entering a system.
#     '''
#     #Step through each line.
#     for this_dict in File_Manager.Load_File('types/TGates.txt'):
#         #Check if this is one of the standard gates.
#         #Separate versions for each direction, though all use the same model.
#         if this_dict['name'] in ['SS_WG_NORTH','SS_WG_EAST','SS_WG_SOUTH','SS_WG_WEST']:
#             #Swap the scene file.
#             this_dict['model_scene'] = r'patch20\terran_gate_scene'
            

@File_Manager.Transform_Wrapper('types/TGates.txt', 'types/TSpecial.txt')
def Adjust_Gate_Rings(
    standard_ring_option = 'use_plain_ring',
    hub_ring_option = 'use_reversed_hub',
    ):
    '''
    Various options to modify gate rings, with the aim of reducing
    capital ship suicides when colliding with the pylons shortly
    after the player enters a sector. Includes ring removal, 
    rotation, reversal, and model swaps. Inactive versions of
    gates will also be updated for consistency. When applied to
    an existing save, gate changes will appear on a sector change.

    * standard_ring_option:
      - String, one of the following options to be applied to the
        standard gates.
        - 'use_plain_ring': Replaces the gate ring with a plain
          version lacking projecting pylons on either side. Default.
        - 'use_reversed_hub': Replaces the gate ring with the Hub
          ring reversed 180 degrees, resulting in pylons only being
          on the back side.
        - 'rotate_45': Rotates the gate 45 degrees, offsetting the
          pylons to be in corners.
        - 'rotate_90': Rotates the gate 90 degrees, offsetting the
          pylons to be at the top and bottom.
        - 'remove': Removes the gate ring entirely, leaving only
          a portal. This will not affect disabled gates.
        - 'use_terran': Replaces the gate ring with the Terran gate
          from the Aldrin expansion plot.
        - None: no change.
    * hub_ring_option:
      - String, one of the options for standard_ring_option, defaulting
        to 'use_reversed_hub', along with a new option:
        - 'use_standard_ring_option': The Hub ring will match the
          option used for the standard ring.
    '''
    
    # If 'use_standard_ring_option' was selected for the hub option,
    #  do the copy here.
    if hub_ring_option == 'use_standard_ring_option':
        hub_ring_option = standard_ring_option
        
    # Names of all gates of interest.
    base_gate_names = [
                'argon_gate',
                'terraformer_gate',
                'argon_gate_inactive',
                'terraformer_gate_inactive',
                # Don't change terran gates for now; no particular
                #  need for it.
                # 'terran_catapult_gate',
                # 'terran_gate',
                # 'terran_gate_inactive',
            ]
            
    # Since there are multiple options for each gate, the approach here will
    #  be to build a small data structure representing the fields needed
    #  per gate scene file, and then to made edits to it based on the
    #  input args.
    # Create the base scenes items.  There will be multiple portal objects
    #  to represent the portal offset needed.
    base_gates = {
        'argon_gate' : {
            'gate' : _Scene_Item(
                base_object = r'others\argon_gate',
                position = (209,-2632,2136),
                rotation = (0,0,0,0)
            ),
            'portal' : _Scene_Item(
                base_object = r'others\argon_gate_effect',
                position = (0,0,49802),
                rotation = (0,0,0,0)
            )},

        'terraformer_gate' : {
            'gate' : _Scene_Item(
                base_object = r'others\terraformer_gate',
                position = (0,0,0),
                rotation = (0,0,0,0)
            ),
            'portal' : _Scene_Item(
                base_object = r'others\argon_gate_effect',
                position = (0,0,47500),
                rotation = (0,0,0,0)
            )},
    
        # No portal on the catapult.
        'terran_catapult_gate' : {
            'gate' : _Scene_Item(
                base_object = r'others\terran_catapult_gate',
                position = (0,0,1793560),
                rotation = (0,0,0,0)
            )},

        'terran_gate' : {
            'particle' : _Scene_Item(
                base_object = r'100000',
                position = (0,0,0),
                rotation = (0,0,0,0)
            ),
            'gate' : _Scene_Item(
                base_object = r'patch20\terran_gate',
                position = (209,-2632,2136),
                rotation = (0,0,0,0)
            ),
            'portal' : _Scene_Item(
                base_object = r'others\argon_gate_effect',
                position = (0,0,53844),
                rotation = (0,0,0,0)
            )},
    
    }

    # Set up a default output gate dict. This one should be safe
    #  for direct editing.
    edited_gates = copy.deepcopy(base_gates)


    # Loop over the options for the different gate types.
    for option, gate_name in zip(
            [standard_ring_option, hub_ring_option],
            ['argon_gate', 'terraformer_gate']
            ):
        # Grab the gate scene dict, from the editable versions.
        gate_scene = edited_gates[gate_name]

        # Do rotations. These don't change position or portal.
        if option == 'rotate_45':
            gate_scene['gate'].rotation = (.125,0,0,1)
        elif option == 'rotate_90':
            gate_scene['gate'].rotation = (.25,0,0,1)

        # Do terran replacement.
        elif option == 'use_terran':
            # Clear the existing items and grab the terran
            #  gate scene, copied for now in case later development
            #  will support chaining transforms.
            gate_scene.clear()
            gate_scene.update(copy.deepcopy(base_gates['terran_gate']))

        # Do rotated hub replacement.
        elif option == 'use_reversed_hub':
            # Start with a copy.
            gate_scene.clear()
            gate_scene.update(copy.deepcopy(base_gates['terraformer_gate']))
            # Do the 180 degree rotation.
            gate_scene['gate'].rotation = (.5,0,1,0)

        # Do plain ring replacement.
        elif option == 'use_plain_ring':
            # This will do a direct drop-in of the model file.
            gate_scene['gate'].base_object = r'stations\others\terraformer_gate'
            # Do the 180 degree rotation, to get the clean side of
            #  the gate facing the system.
            gate_scene['gate'].rotation = (.5,0,1,0)

        # Remove the ring.
        elif option == 'remove':
            # Can either point to a dummy empty file, or delete the
            #  line for the ring. Go with the latter.
            # Note that this does not affect the inactive gates, since
            #  otherwise they would just be invisible.
            del(gate_scene['gate'])

        elif option == None:
            continue

        else:
            # If here, something went wrong.
            print('Adjust_Gate_Rings error, gate option {} not understood'.format(
                option))
            # Stop the transform.
            return

            
    # Inactive versions are just the gates from above with the
    #  portals removed (and the particle effect on the terran
    #  gate removed as well for now).
    # In case a gate was removed, these will grab from the base gates.
    for gate_name in ['argon_gate', 'terraformer_gate', 'terran_gate']:
        inactive_gate_name = gate_name + '_inactive'
        try:
            edited_gates[inactive_gate_name] = {
                'gate' : edited_gates[gate_name]['gate']}
        except KeyError:
            edited_gates[inactive_gate_name] = {
                'gate' : base_gates[gate_name]['gate']}
            

    # Create the new scene files for all of these, regardless of which ones
    #  were changed for now.
    for gate_name, gate_dict in edited_gates.items():
        
        # Skip if the gate not in base_gate_names.
        # This will skip terran gates.
        if gate_name not in base_gate_names:
            continue

        # Create the lines for the file.
        output_lines = [
            # Start with version.
            'VER: 3;',
            ]

        # Loop over the scene items. Order doesn't particularly matter,
        #  but can sort for consistency.
        for index, (name, scene_item) in enumerate(sorted(gate_dict.items())):

            # Create the object path line.
            # Example: 'P 0; B others\argon_gate; N Bothers\argon_gate; b'
            output_lines.append(
                'P {}; B {}; b'.format(
                    index,
                    scene_item.base_object
                    ))

            # Create the animation frame.
            # Example: { 0x2002; 0; 0; 0; 0.000000; 0.000000; 0.000000; 0.000000; -1; -1; }
            output_lines.append(
                # Note: format requires doubled {{ and }} to put in a single
                #  one.
                '{{ 0x2002; {}; {}; -1; -1; }}'.format(
                    # Can directly string the position offsets.
                    '; '.join([str(x) for x in scene_item.position]),
                    # Format the rotations into floats with a few decimals,
                    #  no more than 6 to limit to existing formats seen.
                    '; '.join(['{:.3f}'.format(x) for x in scene_item.rotation]),
                    ))

        # Make the file.
        File_Manager.Add_File(File_Manager.Misc_File(
            # Put in the objects/others folder for now; these don't have to
            #  go here, but it seems a good spot.
            virtual_path = 'objects/others/x3c_{}_scene.bod'.format(gate_name),
            text = '\n'.join(output_lines)))


    # With the scene files created, now need to point the existing gates
    #  to use these scenes.
    # Make a dict matching the old scene to new scene, which can be used
    #  for matching when doing edits on tgates and tspecial.
    # These references are all relative to the objects folder.
    scene_replacement_dict = {
        r'others\argon_gate_scene'                : r'others\x3c_argon_gate_scene',
        r'patch20\argon_inactivegate'             : r'others\x3c_argon_gate_inactive_scene',
        r'others\terraformer_gate_active_scene'   : r'others\x3c_terraformer_gate_scene',
        r'others\terraformer_gate_inactive_scene' : r'others\x3c_terraformer_gate_inactive_scene',
        # No changes to terran gates for now.
        # r'others\terraformer_gate_inactive_scene' : r'others\x3c_terraformer_gate_inactive_scene',
        # r'others\terran_catapult_gate_scene'      : r'others\x3c_terran_catapult_gate_scene',
        # r'patch20\terran_gate_scene'              : r'others\x3c_terran_gate_scene',
        }


    # Do tgates changes.
    for this_dict in File_Manager.Load_File('types/TGates.txt'):
        # Check for a scene to be replaced, and replace it.
        if this_dict['model_scene'] in scene_replacement_dict:
            this_dict['model_scene'] = scene_replacement_dict[this_dict['model_scene']]
    
    # Do tspecial changes.
    for this_dict in File_Manager.Load_File('types/TSpecial.txt'):
        if this_dict['model_scene'] in scene_replacement_dict:
            this_dict['model_scene'] = scene_replacement_dict[this_dict['model_scene']]
    

    # That should be it.
    return


class _Scene_Item:
    '''
    Convenience class to hold data for one item in a scene file, with
    position offset and rotation.
    Members:
        base_object
            String with path to the name of the object being placed in the scene,
            relative to the objects directory.
            May be a number in a special case, which is in the objects/v
            directory implicitly.
        position 
            3-item tuple of ints.
        rotation
            4-item tuple of floats.
    '''
    def __init__(s,
        base_object,
        position,
        rotation
        ):
        s.base_object = base_object
        s.position = position
        s.rotation = rotation