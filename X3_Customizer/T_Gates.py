'''
Transforms to gates.
'''
'''
Aim is to find a solution to the issue of the default gate rings causing
 large ships to suicide on the projecting pylons.
-Former solution was to use an empty file for the gate ring model, so that it simply
 doesn't show up in game, though this generally looks bad.
-May also consider swapping in a different ring type, other options being the
 terran orbital accelerator, or the terran style gate from the ATF expansion plot.
-Swapping gates may have secondary problems with the hub gates, which are a very
 tight fit by default.
 
TODO: Think about how to make removing the ring optional in a nice way.
Removal requires placing dummy files where the gate scene files would be,
 so that the ring doesn't get loaded. This would not be done in Tgates,
 but with file moving/renaming (though generating/deleting dummy files
 may work just as well).

TODO: Attempt to rotate the gate so that pylons are on top/bottom, since big
 ships turn left/right and could then avoid hitting the pylons.
This appears as if it cannot be done here, and may need to modify either every single
 instance of gate creation, or the gate model/scene file itself.
'''
from File_Manager import *

@Check_Dependencies('TGates.txt')
def Swap_Standard_Gates_To_Terran_Gates():
    '''
    Changes standard gates into Terran gates, possibly helping reduce
    large ship suicides when entering a system.
    '''            
    #Step through each line.
    for this_dict in Load_File('TGates.txt'):
        #Check if this is one of the standard gates.
        #Separate versions for each direction, though all use the same model.
        if this_dict['name'] in ['SS_WG_NORTH','SS_WG_EAST','SS_WG_SOUTH','SS_WG_WEST']:
            #Swap the scene file.
            this_dict['model_scene'] = r'patch20\terran_gate_scene'

