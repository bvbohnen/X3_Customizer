'''
Obj file edits, broken out due to length.
'''
'''
Some general notes on obj editing:

A group of Russian modders wrote a disassembler for the obj files.
See this thread for a link (maybe with browser security settings turned up): 
https://forum.egosoft.com/viewtopic.php?t=92374.

The obj files contain KC psuedo-assembly code, which is fed to a lower 
level interpreter in the exe. Egosoft has some details on the X2 KC 
available at https://www.egosoft.com/X/questsdk/info/doxygen/index.html, 
which can give a general idea of what is in there.

The assembly is stack oriented, where operations generally pull some number
of items off the stack and put a result back on the stack.

Notepad++ does a reasonable job as a text viewer.
The .asm file can be used for general perusal, though the .out is handy 
for checking stack depth changes to help understand different operations.

'''
from .Seta import Adjust_Max_Seta
from .Seta import Adjust_Max_Speedup_Rate
from .Seta import Stop_Events_From_Disabling_Seta

from .Spaceflies import Kill_Spaceflies
from .Spaceflies import Prevent_Accidental_Spacefly_Swarms

from .Misc import Set_Max_Marines
from .Misc import Disable_Combat_Music
from .Misc import Stop_GoD_From_Removing_Stations
from .Misc import Disable_Asteroid_Respawn
from .Misc import Allow_Valhalla_To_Jump_To_Gates
from .Misc import Remove_Factory_Build_Cutscene
from .Misc import Keep_TLs_Hired_When_Empty
from .Misc import Disable_Docking_Music
from .Misc import _Disable_Friendly_Fire
from .Misc import Preserve_Captured_Ship_Equipment
from .Misc import Hide_Lasertowers_Outside_Radar
from .Misc import Force_Infinite_Loop_Detection
# This doesn't work sufficiently, so hide it; titles aren't available.
#from .Misc import _Show_Pirate_Yaki_Nororiety

from .Complex import _Prevent_Complex_Connectors
from .Complex import Remove_Complex_Related_Sector_Switch_Delay

# Fill in the default documentation category for the transforms.
# Use a dict copy, since this adds new locals.
for _attr_name, _attr in dict(locals()).items():
    if hasattr(_attr, '_category'):
        _attr._category = 'Obj_Code'
