'''
Change Log:
 * 1.x :
   - Original project development for private use.
 * 2.0 :
   - Restructuring of project for general use, isolating individual
     transforms, separating out transform calls, adding robustness.
     Filling out documentation generation.
 * 2.01:
   - Added Convert_Beams_To_Bullets.
 * 2.02:
   - Added Adjust_Generic_Missions.
   - Added new arguments to Enhance_Mosquito_Missiles.
   - Adjusted default ignored weapons for Convert_Beams_To_Bullets.
 * 2.03:
   - Added Add_Ship_Life_Support.
   - Added Adjust_Shield_Regen.
   - Added Set_Weapon_Minimum_Hull_To_Shield_Damage_Ratio.
   - Added Standardize_Ship_Tunings.
   - New options added for Adjust_Weapon_DPS.
   - New option for Adjust_Ship_Hull to scale repair lasers as well.
   - Several weapon transforms now ignore repair lasers by default.
   - Command line call defaults to User_Transforms.py if a file not given.
 * 2.04:
   - Added Add_Ship_Equipment.
   - Added XRM_Standardize_Medusa_Vanguard.
   - Added Add_Ship_Variants, Add_Ship_Combat_Variants, Add_Ship_Trade_Variants.
 * 2.05:
   - Updates to Add_Ship_Variants to refine is behavior and options.
   - Added in-game script for adding generated variants to shipyards.
   - XRM_Standardize_Medusa_Vanguard replaced with Patch_Ship_Variant_Inconsistencies.
 * 2.06:
   - Updated scaling equation fitter to be more robust; functionality unchanged.
   - Update to Adjust_Missile_Damage to standardize the scaling function
     to support typical tuning paramaters.
   - Added Expand_Bomber_Missiles.
   - Added Add_Ship_Cross_Faction_Missiles.
   - Add_Ship_Boarding_Pod_Support.
   - Changed documentation generator to include more text in the readme file,
     and to categorize transforms.
 * 2.07:
   - Minor tweak to Add_Ship_Variants, allowing selection of which variant will
     be set to 0 when an existing variant is used as a base ship.
   - Adjust_Missile_Damage has new parameters to scale missile ware volume
     and price in line with the damage adjustment.
 * 2.08:
   - Added Adjust_Gate_Rings.
   - Removed Swap_Standard_Gates_To_Terran_Gates, which is replaced by an 
     option in the new transform.
 * 2.09:
   - Added Add_Job_Ship_Variants.
   - Added Change_Ware_Size.
   - Tweaked Add_Ship_Variants to specify shield_conversion_ratios in args.
'''
#Note: changes moved here for organization, and to make them easier to
#break out during documentation generation.
#TODO: think of a better way to version track than using a hand
# edit of the x3_customizer docstring.