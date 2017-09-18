'''
Desired transforms are declared here, along with pathing to
the X3/addon folder and the specifying the source file folder.
'''

#Import all transform functions.
from Transforms import *

#Select if this is modifying vanilla or XRM.
XRM = True
Vanilla = not XRM

if Vanilla:
    Set_Path(
        path_to_addon_folder = r'D:\Steam\SteamApps\common\x3 terran conflict vanilla\addon',
        source_folder = 'vanilla_source'
    )
elif XRM:
    Set_Path(
        path_to_addon_folder = r'C:\Base\x3 terran conflict xrm\addon',
        source_folder = 'xrm_source'
    )

    


#####################################################
#Background

#Do a first pass to adjust fade minimum and gap.
#These should not have much affect on later transforms, since they are
# mainly concerned with high fade_start values.
#Sets a floor to fade distance, so that object do not appear
# too closely. May be useful in some sectors with really short view
# distances, though may also want to keep those for variety.
#5 or 10 km might be needed; it depends somewhat on object size, since the
# distance is maybe to object center and not the nearest point, which can
# project out some ways (eg. for asteroids).
#Keep low for now, tweak up later as needed.
Set_Minimum_Fade_Distance(distance_in_km = 3)

#Adjust system fade distances.
#Set fade gap to be as much as fade start.
#Require the fade gap be no longer than 20 km, which should be plenty.
Adjust_Fade_Start_End_Gap(
    fade_gap_min_func = lambda start: start*1, 
    fade_gap_max_func = lambda start: 20)


#Add some particles around the ship.
#10 feels good as a base (10% of vanilla), upscaling by
# 0.5 of the fog amount (up to +25 in heavily fogged sectors).
Adjust_Particle_Count(
    base_count = 10,
    fog_factor = 0.5)


#Remove stars from foggy sectors, and remove fade from other sectors.
Remove_Stars_From_Foggy_Sectors(
    #Set fog req to 12, which is used by a background that shares images with the
    # background used by Maelstrom, which should be faded.
    fog_requirement = 12,
    #Set fade distance req to 60, based on some hand adjustment to what
    # feels good for the game files.
    fade_distance_requirement_km = 60
    )


#####################################################
#Director

#Set standardized tuning counts.
Standardize_Tunings(
    enging_tuning_crates = 4,
    rudder_tuning_crates = 4,
    engine_tunings_per_crate = 4,
    rudder_tunings_per_crate = 3)

#Avoid dynamic convoys being mixed race for ships.
Convoys_made_of_race_ships()

#Set 70% of max overtuning for ships.
Standardize_Start_Plot_Overtunings(
    fraction_of_max = 0.70)


#####################################################
#Gates

#If the standard gate model should swap to the terran gate model.
#Disable for now; maybe turn on if losing too many ships to standard
# gates to try it out.
if Vanilla:
    pass
    #Swap_Standard_Gates_To_Terran_Gates()
elif XRM:
    pass
    #Swap_Standard_Gates_To_Terran_Gates()

    
#####################################################
#Universe

if XRM:
    #Color sector names.
    Color_Sector_Names()

    #Restore the aldrin rock for new games.
    Restore_Aldrin_rock()

    #Set Hub music to be restored.
    #XRM breaks it by setting the track to 0.
    #Restore_Hub_Music(apply_to_existing_save = True)
    
    #Set Argon Sector M148 music to be restored.
    #XRM changes this to the argon prime music.
    #Restore_M148_Music(apply_to_existing_save = True)


#####################################################
#Globals

Set_Missile_Swarm_Count(swarm_count = 4)
Set_Communication_Distance(distance_in_km = 75)
Set_Complex_Connection_Distance(distance_in_km = 100)
Set_Dock_Storage_Capacity(
    #Amount to increase player dock capacity; default is 3.
    player_factor = 4,
    #Amount to increase npc dock capacity; default is 1.
    #Fluff this up a bunch, since npc docks are generally way too small for high value
    # goods, eg. only holding 2 ppcs or similar, when an m2 requires 24+.
    npc_factor = 4,
    #Amount to increase hub storage; default is 6.
    hub_factor = 6
    )

#####################################################
#Jobs

if XRM:
    Adjust_Job_Count(
        job_count_factors = [
            #Too many khaak invaders (eg. 15 TM led groups).
            ('owner_khaak', 1/5),
            #Cut down pirates by a bit less.
            #Maybe go down to 1/4; 2/3 was not enough (pirate sectors still flooded.)
            #(This may not work well, as there appears to be many dedicated pirate
            # jobs for patrolling each pirate sector. Try to adjust respawn timers
            # instead.)
            ('owner_pirate', 2/3),
            #Similar redunction in yaki.
            ('owner_yaki', 2/3),
            #Cut down xenon a little bit while here, though they might
            # be a little more okay (haven't noticed flooding yet).
            ('owner_xenon', 2/3),

            #Can generally limit flavor drones by a bit (default is 10 per sector).
            #('Freight Drones', 2/3),

            #Can reduce civilian ships in general by a bit, if needed.
            #('classification_civilian', 2/3),
            #Can reduce trade ships in general by a bit, if needed.
            #('classification_trader', 2/3),

            #Everything else gets this factor.
            ('*', 1),
        ])

    #Khaak in particular respawn extremely fast (a few minutes), but
    # battle groups in general respawn too often, so aim to do general
    # nerfs to respawn times.
    Adjust_Job_Respawn_Time(
        time_adder_list = [
            #Just add a few minutes to everything for now.
            ('*', 15),
            ],
        time_multiplier_list = [
            #Generic boost.
            ('*', 2),
            ]
        )
    
#####################################################
#Ships

if Vanilla:
    Fix_Pericles_Pricing()
    Boost_Truelight_Seeker_Shield_Reactor()
    Adjust_Ship_Speed(
        adjustment_factors_dict = {
            #Bump up interceptors about 30%, to better distinguish their role from
            # fighters (which otherwise have a lot of speed overlap).
            #Could also bump up to 50% and still be in about the right range.
            'SG_SH_M4': 1.3,
            })


if XRM:
    #Can remove engine trails if they cause slowdown.
    #Simplify_Engine_Trails()

    Adjust_Ship_Pricing(
        #The XRM costs include eg. a 2-4x upscale on scouts, which combined with scouts being
        # easier to shoot down (due to laser changes) makes them even more terrible.
        #The rescale would bring costs in line with vanilla, which had pretty reasonable
        # prices.
        #This may only be applied to scouts themselves; other ships are more in line with
        # their usefulness.
        adjustment_factors_dict = {
            #A vanilla disco is 0.13x the price of a buster; in xrm this is 0.37x.
            #Can multiply by 0.35 to roughly bring scout prices in line, but a more conservative
            # 0.5 should do okay as well.
            'SG_SH_M5': 1/2,
        })
    

    #Increase laser recharge on corvettes in XRM, which uses TC style low values about
    # 1/2 of AP. Can use a generalized table for all ship subtypes for future scaling,
    # similar to what is done for hull and speed.
    Adjust_Ship_Laser_Recharge(
        adjustment_factors_dict = {
            #Recharge and capacitor have somewhat different scalings vanilla to Xrm.
            #This will just apply to the recharge factor.
            #AP centaurs have 0.6x the capacitor and 2.1x the recharge of Xrm centaurs.
            #Note: there is some overlap between this transform and reducing the
            # energy usage of weapons. See X3_Weapons for some notes on that.
            # The general decision is to adjust ships recharge for bigger ships to
            # account for XRM giving big weapons severe efficiency penalties compared
            # to vanilla, eg. 1/3 efficiency for PPC being balanced by 3x recharge
            # for capital ships.
            #Generally, can adjust these based on the energy efficiency ratio of
            # vanilla vs XRM for the typical best weapon of the ship class.
            
            #Ratios will be given as (vanilla damage / energy) / (xrm damage / energy),
            # eg. if vanilla is 2x more efficient, boost xrm ship laser recharge by 2x.
            #A second ratio will be (vanilla ship recharge / xrm ship recharge) for a
            # typical ship of the class.
            #This should bring xrm in line with vanilla overall.
        
            #M5 will use IRE, discoverer. -40%.
            'SG_SH_M5': (220/4) / (180/2) * (25 / 25),
            #M4 will use PAC, buster. -20%.
            'SG_SH_M4': (1155/23) / (640/10) * (51 / 51),
            #M3 will use HEPT, nova. -10%.
            'SG_SH_M3': (1995/40) / (1330/26) * (140 / 155),
            #Leave bombers alone for now.
            #'SG_SH_M8': 1.0,
            #M6 will use CIG, centaur. +30%.
            'SG_SH_M6': (7845/246) / (8050/153) * (1050 / 493),
            #M7 will use IBL, cerberus. +200%.
            # This may be too high with IBL, or too low with CIG.
            # Try averaging the two, for +95%.
            'SG_SH_M7': ((50860/526) / (14400/400)
                         #Cig damage/energy from above.
                         +(7845/246) / (8050/153))/2 * (2200 / 1925),
            #M2 will use PPC, titan. +150%.
            'SG_SH_M2': (63778/536) / (27000/900) * (4145 / 6581),
            #M1 will use PPC, colossus. +125%.
            'SG_SH_M1': (63778/536) / (27000/900) * (797 / 2817),
            #M0 will use PPC, megalodan. +450%.
            # TODO: Does any ship really use M0 classification?
            'SG_SH_M0': (63778/536) / (27000/900) * (7500 / 5405),
            #Transports will be left alone for now.
            #These could use a general buff to make them more capable of
            # defending themselves.
            #'SG_SH_TS': 1.0,
            #'SG_SH_TM': 1.0,
            #'SG_SH_TP': 1.0,
            #'SG_SH_TL': 1.0,
            #'SG_SH_GO': 1.0,
        })
    
    Adjust_Ship_Shield_Regen(    
        #Xrm makes many transports too tough, such that pirate/xenon groups cannot crack
        # their shields and just sit there pecking away forever as the transport
        # flies in circles without energy to use its guns.
        #The fix can be a mixture of reducing shield recharge rates on the buffed
        # transports (which are normally closer to 600, but in xrm go up to 2000+), and
        # reducing their total shields (in Adjust_shield_slots below). 
        #-For transport ships should have their shield recharge nerfed.
        #-Also needed for capital ships, otherwise they can't break shields on OOS combat
        # with the weak XRM weaponry.
        adjustment_factors_dict = {        
            #Ignore lighter ships for now. TODO: special scouts might have too much shield
            # regen, eg. Arrow has more than M3s.
            #'SG_SH_M5': (0, 1, None),
            #'SG_SH_M4': (0, 1, None),
            #'SG_SH_M3': (0, 1, None),
            #'SG_SH_M8': (0, 1, None),
            #M6s appear lightly buffed, around 15%-20%.
            # For a centaur, 2500 in vanilla and 3000 in xrm, if assuming
            #  a 1k base, then (2.5k-1k)/(3k-1k) = 0.75 to adjust it back.
            'SG_SH_M6': (1000, 0.75, None),
            #M7 are often unchanged. In the skirnir case, it was actually cut in about half.
            #'SG_SH_M7': (0, 1, None),
            #M2s were buffed by 21% on the low end (titan, 14400 in vanilla).
            # Megalodan is buffed 44% (14200 in vanilla), which might be okay.
            # Phoenix is buffed 112%, 8k to 17k, though it was oddly low in vanilla.
            # Assuming 10k base, then (14.4k-10k)/(14.4k*1.21-10k) = 0.6 to adjust
            #  the titan back to vanilla.
            'SG_SH_M2': (10000, 0.6, None),
            #M1s were buffed by 25% on the low end (colossus, 8200 in vanilla).
            # Assuming 5k base, then (8.2k-5k)/(8.2k*1.25-5k) = 0.6 to adjust the
            #  colossus back to vanilla, treating similar M1s the same but buffer M1s
            #  with a bigger nerf.
            # OWPs are classified as M1 and were buffed by 10x, and could use a big nerf.
            # Apply a max of ~25k for limit OWPs.
            'SG_SH_M1': (5000, 0.6, 20000),
            #'SG_SH_M0': (0, 1, None),
            #Greatly reduce transports, and personel transports, which were increased by
            # up to ~10x in some cases. Assumg vanilla base regen is around 500 for
            # trade ships and 400 for personel transports, and just go with a 90% reduction
            # on anything above that.
            'SG_SH_TS': (500, 0.1, None),
            'SG_SH_TP': (400, 0.1, None),
            #Military transports appear largely unchanged.
            #'SG_SH_TM': (0, 1, None),
            #Big transports were buffed by ~25%; can probably leave this alone, though they
            # may need a shield slot reduction (since they are overshielded).
            #'SG_SH_TL': (0, 1, None),
            #'SG_SH_GO': (0, 1, None),
        })
    
    #Reduce all shield regen by a global factor, in addition to what
    # is given above. This is applied after other adjustments.
    Adjust_Ship_Shield_Regen(scaling_factor = 0.5)

    Adjust_Ship_Shield_Slots(
        adjustment_factors_dict = {
            #For over-shielded transports, in addition to reducing recharge rates,
            # the other part of the fix is to reduce shielding,
            # particularly those that were given multiple 200 mj shields.
            #They can likely just have their shield slots dropped down to 1-2, from
            # the 5-6 currently.
            'SG_SH_TS': (200, 0.2),
            'SG_SH_TP': (200, 0.2),
            #Big transports were given a ~5x increase in shield slots;
            # drop them down as well, closer to 1 GJ.
            #This is a little dull since they will all end up at 1 GJ, but there
            # is no good way around that without swapping them to 200 mj shields.
            #Some transports had 6GJ of shields; a factor >0.1 should round them
            # up to 2GJ, to add a little variety at least.
            'SG_SH_TL': (1000, 0.12),
        })
    
    Adjust_Ship_Speed(
        #In XRM, many ships were greatly sped up in the m4-6 tiers, which has a general
        # effect of making the universe feel smaller, as well as making scouts less
        # distinctive when m4s can reach 400+.
        #Generally apply slowdowns, though keep some speed boosts selectively.
        adjustment_factors_dict = {
            #Bring scouts back down based on kestrel (drop 715 to 600).
            'SG_SH_M5': 600 / 715,
            #Bring intercepters back down based on buster, but still keeping a boost
            # over vanilla.  Go with 40% boost.
            'SG_SH_M4': 175 / 301 * 1.4,
            #Bring fighters down based on nova, and retain about half the boost
            # of the intercepter.
            'SG_SH_M3': 150 / 237 * 1.2,
            #Bombers are often unchanged.
            #'SG_SH_M8': 1.0,
            #Base corvette speed on skiron. Centaur seems sped up more than others,
            # so don't use it as base point.
            #Keep modest boost, to try to stay ahead of the faster frigates.
            'SG_SH_M6': 149 / 214 * 1.15,
            #Some M7s are exceptionally fast (faster than many vanilla corvettes), but
            # many were unchanged, so a global reduction isn't safe.
            #'SG_SH_M7': 1.0,
            #Capital ships are often unchanged.
            #'SG_SH_M2': 1.0,
            #'SG_SH_M1': 1.0,
            #'SG_SH_M0': 1.0,
            #Transports are often unchanged.
            #'SG_SH_TS': 1.0,
            #'SG_SH_TM': 1.0,
            #'SG_SH_TP': 1.0,
            #'SG_SH_TL': 1.0,
            #Goner classifier appears unused (goner ships given other subtypes).
            #'SG_SH_GO': 1.0,
        })

    Adjust_Ship_Hull(
        #Do a custom ship hull multiplier instead of using XRM's hull packs, for finer
        # control (eg. 2x fighters, 10x capitals).
        #Save games may need a script to update existing hull values if this is changed
        # mid game (can use the script from the xrm hull pack).
        adjustment_factors_dict = {
            #Base XRM hulls are generally from TC style values.
            #Use the TC to AP ratio for each class of ship for this scaling, generally
            # using basic argon ships from the wiki.
            'SG_SH_M5': 2,
            'SG_SH_M4': 2,
            'SG_SH_M3': 2,
            #Bombers were added in AP, and XRM uses roughly the AP hull already, so no change.
            #'SG_SH_M8': 1,
            'SG_SH_M6': 4,
            'SG_SH_M7': 4,
            'SG_SH_M2': 10,
            'SG_SH_M1': 10,
            'SG_SH_M0': 10,
            'SG_SH_TS': 3,
            #Military transports are like bombers, with no change.
            #'SG_SH_TM': 1,
            'SG_SH_TP': 3,
            'SG_SH_TL': 10,
            #Goner classifier appears unused (goner ships given other subtypes).
            #'SG_SH_GO': 1,
        })


#####################################################
#Weapons

if Vanilla:
    #Give a mild weapon range increase.
    Adjust_Weapon_Range(
        lifetime_scaling_factor = 1.2,
        speed_scaling_factor = 1.0,
        )
    
    Adjust_Beam_Weapon_Duration(
        bullet_name_adjustment_dict = {
            #Adjust palcs to fire shorter bursts, due to lag issues.
            #Base beams last 3 seconds, but fire over 2x/second, causing a 
            # single weapon to put out many beams, causing excess slowdown.
            'SS_BULLET_PAL': (None, 0.2, None),
            #Give no default; other weapons will be unchanged.
        })

    Adjust_Weapon_Fire_Rate(
        #Maybe reduce fire rates in general for performance.
        #scaling_factor = 0.5,
        laser_name_adjustment_dict = {
            #Cut the PAL down to every 2 seconds to reduce its
            # excessive performance impact somewhat.
            'SS_LASER_PAL': 30,
            })

    
    #Reduce OOS damage by 40%.
    Adjust_Weapon_OOS_Damage(scaling_factor = 0.6)
        

if XRM:
    
    #Adjust weapon damage, to increase it in general.
    '''
    It is unclear how best to go about this, since the XRM nerfs are not a 
    consistent % across weapons.
     Examples (for shield damage):
        IRE  is at 80% damage (compared to vanilla)
        Hept is at 33% (as well as similar tier weapons)
        CIG  is at 54%
        Flak is at 23%
        PBC  is at 156% (but also heavily role swapped, so maybe leave alone)
        PPC  is at 19%
    A flat 3x increase might be safe.
    However, dps of small guns and dps of heavy guns is very similar (eg. ppc is only around
     2-3x that of hept), so it might be more interesting to to an increasing returns 
     formula that give bigs guns more of a boost.
    Note also that XRM sets beam weapon damage way too high, similar to other weapons
    even though they have instant hit. Those really need to be brought down.

    TODO: use a scaling equation which gives a bigger boost to capital tier weapons,
     since otherwise capital combat takes ages (and doesn't resolve OOS against shield
     recharge rates).
    '''    
    Adjust_Weapon_DPS(
        #Goal is to boost the high end, where XRM PPC has a base dps
        # of 9000 vs shields, when the vanilla PPC is closer to 46k.
        # This is a 46/9= 5x difference.
        #On this step, aim to just bring up heavy weapon dps relative
        # to lighter weapon dps, and do the overall scaling later.
        #Vanilla ppc/hept = 46 / 9.4 = 4.9
        #XRM ppc/hept = 9 / 3.1 = 2.9
        #Use a 1.7x boost here.
        scaling_factor = 1.7,

        #If a scaling equation should be used for the damage adjustment.
        use_scaling_equation = True,
        #Set the tuning points.
        damage_to_adjust_kdps = 9,
        #The damage to pin in place on the low end.
        damage_to_keep_static_kdps = 3,
        
        #Special dict entries will override the above formula and factor.
        bullet_name_adjustment_dict = {
            #Tractor bullet should do little damage.
            'SS_BULLET_TUG': 1,
            #Don't adjust repair lasers.
            'SS_BULLET_REPAIR': 1,
            'SS_BULLET_REPAIR2': 1,
        },
        print_changes = True
        )

    #A flat factor to use for damage adjustment.
    #This is applied after the scaling equation below, so that that
    # equation can be configured to the base xrm numbers.
    #Go with 2.5 to be conservative, or even 2 since some ships have more
    # turret gun mounts than in vanilla.
    #This helps bring up energy drain as well.
    Flat_damage_adjustment_factor = 2.5
    Adjust_Weapon_DPS(scaling_factor = Flat_damage_adjustment_factor)

    #Extra scaling to apply to beam weapons, on top of the above factor
    # or equation scaling, to bring beam power back down.
    #This can be applied before or after the scaling equation; it will be
    # placed after for now (such that beam weapons get upscaled along with
    # other cap weapons, then reduced here).
    #Note: this reduces dps, but not energy efficiency, so in long fights where
    # both ships are limited by energy regeneration, beams may need a separate
    # nerf to keep them weaker (in return for nearly always hitting).
    #Unfortunately, cannot just drop this really low to get ships to not use
    # beam weapons, since many ships are very constrained on weapon choice 
    # such that their only long range weapon is a beam weapon,
    # which they will be stuck using at those ranges.
    Adjust_Weapon_DPS(
        bullet_name_adjustment_dict = {
            #Give other beams a nerf.
            #Try out a 40% beam reduction.
            'flag_beam': 0.6,
            #XRM has an extra nerfed mass driver, probably because it uses
            # the TC damage when AP increased it 4x. XRM MD is about 1/7th of vanilla.
            #Drop an extra 2x on this (2*2.5=5x), to put back in about the right
            # ballpark, but don't buff too much because it is no longer ammo limited.
            'SS_BULLET_MASS': 2,
            #Give IREs a smaller boost, since they are a bit too close to PACs and similar,
            # and they are too strong on fighter drones when OOS.
            #(Note: IREs also have much higher hull damage than vanilla, but leave that
            # alone for now.) TODO: maybe split into separate transform step.
            'SS_BULLET_IRE': .5,
            #An oddity exists with GPBC, in that it has a dps value far higher than
            # anything else (4x of PPC), which gets ballooned up due to the scaling
            # equation. TODO: tweak the scaling equation to not baloon this, but
            # otherwise leave the relative damage buff.
            #This is the lasertower beam weapon.
            #'SS_BULLET_GPBC': 1,
            #Don't adjust repair lasers.
            'SS_BULLET_REPAIR': 1,
            'SS_BULLET_REPAIR2': 1,
            #Leave the Khaak weapons without the beam nerf, to keep them scary.
            'SS_BULLET_KH_ALPHA': 1,
            'SS_BULLET_KH_BETA': 1,
            'SS_BULLET_KH_GAMMA': 1,
            })
    

    #Rescale OOS damage values to reflects actual weapon DPS, and adjust
    # the damage in general.
    #XRM has much weaker weapons in general than vanilla, such that this needs to be
    # increased, otherwise issues with perpetual OOS combat that doesn't break shielding
    # has been observed.
    #The XRM oos damage values are around 1/4 of vanilla, so if
    # vanilla needs a 0.6 factor, then xrm needs a 4 * 0.6 = 2.4x factor.
    #Since the weapon damage adjustment may have been applied in general, affecting
    # OOS damage as well, that should be included here as a correction.
    #After the correction, apply a scaling similar to that used in vanilla,
    # eg. around 40% reduction.
    Adjust_Weapon_OOS_Damage(scaling_factor = 0.6 * 2.4 / Flat_damage_adjustment_factor)

    

    Adjust_Weapon_Shot_Speed(
        #Set how much fast should be slowed by, eg. 0.5 for half speed.
        #Slow fast bullets by 40%, still leaving them faster than vanilla.
        scaling_factor = 0.6,
        #Use the formula for adjustments (only alternative is the table of overrides below).
        use_scaling_equation = True,

        #Set the tuning points:
        #The target speed to adjust, in m/s.
        #Can either: drop 2000 m/s IREs closer to vanilla 1100 m/s, or
        #            drop 1400 m/s PACs closer to vanilla 700 m/s.
        #The latter is a stronger slowdown, though fast shot weapons largely
        # go away until special overrides are put in place for them.
        #Try out PAC slowdown for now.
        target_speed_to_adjust = 1400,
        #The speed to pin in place.
        speed_to_keep_static = 500,

        #Special dict entries will override the above formula.
        #Note: formula will not touch beam, areal, or flak weapons for now.
        bullet_name_adjustment_dict = {
            #Leave IREs fairly fast.
            'SS_BULLET_IRE' : 1100 / 2000,
            },       
        print_changes = True
        )


    #Maybe swap mass drivers or other weapons back to the ammo system.
    #Leave off for now, since many npc ships appear to spawn with a full
    # load of such weapons, and may have ammo problems.
    #Convert_Weapon_To_Ammo(
    #    bullet_name_ammo_dict = {
    #    'SS_BULLET_MASS': 'Mass Driver Ammunition',
    #    })

    Adjust_Beam_Weapon_Duration(
        #The excessive amount of capital beam weapons causes issues in xrm,
        # particularly with anti-missle and anti-fighter effectiveness being
        # too high.
        #Making beams last longer will spread their damage out, and against fighters
        # will mean less time on target, essentially a nerf.
        #TODO: make duration based on dps, though that would require laser level
        # analysis rather than just a bullet tweak.
        bullet_name_adjustment_dict = {
            #Don't adjust repair lasers or tractor laser.
            'SS_BULLET_TUG':     (None, 1, None),
            'SS_BULLET_REPAIR':  (None, 1, None),
            'SS_BULLET_REPAIR2': (None, 1, None),
            #Try out a large increase. This may need more tweaks.
            # 5x was a bit too much; a xenon m2 had trouble killing anything.
            'default': (None, 4, 4),
        })
    
    
    Adjust_Beam_Weapon_Width(
        #Some xrm beams are far too wide, eg. 4x4 when vanilla beams are all 1x1, a
        # 16x increase in hit area (this mostly affects a Xenon capital weapon).
        #Also apply a min, since some XRM beams are too narrow, eg. khaak having trouble
        # hitting because they were reduces from 1x1 to 0.1x0.1.
        bullet_name_adjustment_dict = {
            #Capping at 1x1 was maybe too low; a xenon m2 had trouble landing hits
            # on fighters even when they were right next to it.
            #Maybe cap at 2x2.
            #Floor at 0.5x0.5 for now, maybe bring up to 1x1.
            '*': (0.5, 1, 2),
        })

    #Scale bullet energy.
    Adjust_Weapon_Energy_Usage(
        #Vanilla has efficiency around shield_damage = 50x energy for HEPT, up to 100x for PPC.
        #XRM is similar for HEPT, but 30x for PPC, a very large nerf.
        #The scaling equation should seek to rebalance efficiencies around weapon dps, with
        # both really low and really high dps getting efficiency bonuses.
        #Alternatively, could up the laser generator on bigger ship classes to power
        # their big weapons, up to around 3x (to bring PPCs in line), which will have
        # the general effect of making ships trade off between high DPS weapons that
        # drain their laser cap, or lower DPS weapons that are sustainable, but with
        # a better balance than in default XRM.
        #-Going with ship adjustment for now, since it is more straightforward;
        # see TShips changes.

        #TODO: extra nerf to beam weapon energy usage.
        #TODO: maybe bump up energy use by 2x, as xrm makes weapon damage/energy
        # much higher than vanilla, leading to m3s that never run out of laser
        # energy and similar issues. This mostly seems to affect light weapons,
        # eg. pacs. Heavy weapons flip this around, having about 1/2 energy
        # efficiency, so this would be a complex issue to unroll.
        #TODO: maybe force some sort of balance into this using a planned out equation,
        # eg. a curve that gives higher efficiency for really weak (IRE) and really
        # strong (PPC) weapons, the former to help out scouts, the latter to justify
        # capital weapons being limited to capital ships. Maybe think about how to
        # adjust for shot speed (faster shots = more energy). Maybe get a tuned
        # equation based on vanilla weapons. Maybe consider letting cap weapons be
        # less efficient, to give cap ships a reason to mount smaller weapons and
        # get in close (also plays better with the turret laser switching logic
        # in game which often switches to smaller weapons at close range).
        bullet_name_multiplier_dict = {
            #Reduce energy used by mass driver in XRM.
            #Go with 1/4 or so, since AP boosted MD shot damage by 4x from TC/XRM style values.
            #Getting an exact benchmark for this is difficult, since the shield-ignoring
            # property of MD is unique, but PACs generally consume 10 energy for 120 hull
            # damage in XRM (over double the energy is used in vanilla), while MD is at 
            # 65 energy for 38 hull damage.
            # Can set MD to double or more that, to represent the energy PAC
            # will have spent going through shielding, assuming PAC spends equal time
            # on shields and hull.
            #This may not matter if MD is converted back into an ammo weapon.
            'SS_BULLET_MASS': 1/4,
            #Leave IRE alone; generally, it should have a high damage/energy ratio
            # at the cost of using a slot to not do much damage, so that it plays
            # a role in small ship and transport weapons.
            #'SS_BULLET_IRE': 1,
            #Bump up pac energy a little bit, otherwise they are somewhat out of line
            # with similar weapons. -Removed, on double check they are only some 27%
            # higher efficiency than hept (which has 44% more dps), so the efficiency
            # is probably fine as-is.
            #'SS_BULLET_PAC': 1.5,
        })
    

    #XRM bullets are already quite fast and decent range.
    #Maybe give a range bump anyway.
    Adjust_Weapon_Range(
        lifetime_scaling_factor = 1.2,
        speed_scaling_factor = 1.0,
        )
    
    #XRM already seems to address problems with beam weapon slowdown, so nothing
    # to adjust here for now.
    #Maybe retool Split beams, which have very high fire rates.
    #Adjust_Weapon_Fire_Rate(scaling_factor = 0.5)
    

#####################################################
#Missiles

#Beef up mosquitos for better intercept.
Enhance_Mosquito_Missiles()

#Apply general missile damage nerfs.
Adjust_Missile_Damage(
    scaling_factor = 1,
    use_diminishing_returns = True,
    print_changes = True)

if XRM:
    #XRM gives ships much larger missile loadouts, compounding problems
    # with missile spam.  Apply additional nerfs.
    Adjust_Missile_Range(
        #The adjustment factor. Cut in half for now.
        #-Half feels about right in game.
        scaling_factor = 0.5,
        #If diminishing returns should be used, so that short range
        # missiles are less affected.
        use_diminishing_returns = True,
        #Set the tuning points.
        #The target range to adjust, in km. About 50km+ and longer missiles.
        target_range_to_adjust_km = 50,
        #The range to pin in place on the low end, about 10km.
        range_to_keep_static_km = 10,
        print_changes = True
        )
    
    Adjust_Missile_Speed(
        #The adjustment factor. -25% felt like too little, so try -50%.
        scaling_factor = 0.5,
        #If diminishing returns should be used, so that short range
        # missiles are less affected.
        use_diminishing_returns = True,
        #Set the tuning points.
        #The target speed to adjust, in dps. About 700+ on fast missiles.
        target_speed_to_adjust = 700,
        #The speed to pin in place on the low end.
        speed_to_keep_static = 150,
        print_changes = True
        )
    
    #Restore the trail effect on the bomber missiles,
    # which XRM removed but were good for seeing where the dangerous
    # missiles are.
    Restore_heavy_missile_trail()

    #Make missiles a little easier to shoot down.
    Adjust_Missile_Hulls(0.5)


#####################################################
#Wares
if XRM:
    #Restore tuning prices such that they have increasing cost again,
    #by just resetting to vanilla pricing.
    Restore_Vanilla_Tuning_Pricing()
