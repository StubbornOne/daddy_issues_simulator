### For rules that require a specific function ###

#Note: re-rerolls will be blocked by rerollDie(), so you can run it without worry

from calculations import *
from primarchs import *

"""
class Rule:
    def __init__(self, priority):
        self.priority = priority #this is for "supercede all other rules" rules

    def exec():
        return

class RollRule(Rule):
    def __init__(self, priority, rolls):
        super().__init__(priority)
        self.rolls = rolls
"""
#####START OF ASSAULT

def WildfirePanoplyStart(primarch, defender, combat_round):
    primarch.invuln_shoot = 3
    print("Wildfire Panoply: %s's invuln grows to 3++!" % primarch.name)

#####START OF COMBAT: CHARGE

def ChargeBonus(primarch, defender, combat_round):
    if primarch.charge and not primarch.disordered:
        primarch.A += 1
        print("%s gets +1A for the charge!" % primarch.name)

def LA_WE(primarch, defender, combat_round):
    if primarch.charge:
        primarch.A += 1
        print("Legiones Astartes (World Eaters): %s gets +1A for the charge!" % primarch.name)

def CounterAttack(num):
    def func(primarch, defender, combat_round):
        if defender.charge:
            primarch.A += num
            print("Counter-Attack: %s gets +%dA for being charged!" % (primarch.name, num))
    return func

def FuriousCharge(num):
    def func(primarch, defender, combat_round):
        if primarch.charge and not primarch.disordered: #assume this is the case
            primarch.S = primarch.S + num
            print("Furious Charge: %s gains +%dS!" % (primarch.name, num))
    return func

def Rage(num):
    def func(primarch, defender, combat_round):
        if primarch.charge and not primarch.disordered: #assume this is the case
            primarch.A = primarch.A + num
            print("Rage: %s gains +%dA!" % (primarch.name, num))
    return func

def SuddenStrike(num):
    def func(primarch, defender, combat_round):
        if primarch.charge and not primarch.disordered: #assume this is the case
            primarch.I = primarch.I + num
            print("Sudden Strike: %s gains +%dI!" % (primarch.name, num))
    return func

def FlawlessExecution(primarch, defender, combat_round):
    if primarch.charge:
        primarch.I = primarch.I + num
        print("Flawless Execution: %s gains +%dI!" % (primarch.name, num))

def SireOfTheSpaceWolves(primarch, defender, combat_round):
    if primarch.charge:
        primarch.WS = min(10, primarch.S + 1)
        print("Sire of the Space Wolves: %s gains +1S!" % primarch.name)

def SireOfTheBloodAngels(primarch, defender, combat_round):
    if primarch.charge:
        primarch.WS = min(10, primarch.WS + 1)
        print("Sire of the Blood Angels: %s gains +1WS!" % primarch.name)

#####START OF COMBAT

def FightingStyle(primarch, defender, combat_round):
    if primarch.active and not primarch.in_combat:
        #gonna charge
        if (primarch.I <= defender.I and defender.W <= 2): #try to kill off at faster Init
            primarch.rules.append("Sudden Strike(3)")
        else:
            primarch.rules.append("Rage(4)")
    else:
        primarch.rules.append("Murderous Strike(4)")
    return

#technically it should be during attack selection?
#also: does this actually modify the Init value? DEdge says "score" and RB says "fights at -1 Init", not change the value
def DuellistsEdgeStart(num):
    def func(primarch, defender, combat_round):
        primarch.I = min(10, primarch.I + num)
        print("Duellist's Edge: %s gains +1I!" % primarch.name)
    return func

########################PREHIT#############################

#Die rules
#TODO: MasterCrafted can actually choose the die to reroll. Matters for e.g. Plasma Blaster
def MasterCrafted(attacker, attacker_weapon, defender, combat_round, hitRoll):
    if not attacker_weapon.mastercrafted_rerolled:
        if not hitRoll.rerolled and not hitRoll.success:
            old_value = hitRoll.value
            rerollDie(hitRoll)
            print("Master-Crafted: %d -> %d" % (old_value, hitRoll.value))
            attacker_weapon.mastercrafted_rerolled = True

def TwinLinked(attacker, attacker_weapon, defender, combat_round, hitRoll):
    if not hitRoll.rerolled and not hitRoll.success:
        old_value = hitRoll.value
        rerollDie(hitRoll)
        print("Twin-linked: %d -> %d" % (old_value, hitRoll.value))

def Hatred(attacker, attacker_weapon, defender, combat_round, hitRoll):
    if combat_round == 0:
        if not hitRoll.rerolled and not hitRoll.success:
            old_value = hitRoll.value
            rerollDie(hitRoll) #although this checks for reroll, we still check above to avoid printing messages
            print("Hatred: %d -> %d" % (old_value, hitRoll.value))

def HatredPsykers(attacker, attacker_weapon, defender, combat_round, hitRoll): #.____.
    if combat_round == 0 and defender.psyker:
        if not hitRoll.rerolled and not hitRoll.success:
            old_value = hitRoll.value
            rerollDie(hitRoll) #although this checks for reroll, we still check above to avoid printing messages
            print("Hatred: %d -> %d" % (old_value, hitRoll.value))

def CoraxHatredTarget(defender):
    return type(defender) is Fulgrim or type(defender) is Perturabo or type(defender) is Horus or type(defender) is Curze or type(defender) is Alpharius or type(defender) is Mortarion or type(defender) is Angron

def CoraxHatred(attacker, attacker_weapon, defender, combat_round, hitRoll):
    if combat_round == 0 and CoraxHatredTarget(defender):
        if not hitRoll.rerolled and not hitRoll.success:
            old_value = hitRoll.value
            rerollDie(hitRoll) #although this checks for reroll, we still check above to avoid printing messages
            print("Hatred: %d -> %d" % (old_value, hitRoll.value))

def PreferredEnemyHit(attacker, attacker_weapon, defender, combat_round, hitRoll):
    if not hitRoll.rerolled and hitRoll.value == 1:
        rerollDie(hitRoll)
        print("Preferred Enemy: 1 -> %d" % hitRoll.value)

def CalculatingSwordsman(attacker, attacker_weapon, defender, combat_round, hitRoll):
    if combat_round > 0:
        if not hitRoll.rerolled and hitRoll.value == 1:
            rerollDie(hitRoll)
            print("CalculatingSwordsman: 1 -> %d" % hitRoll.value)

#Threshold rules

def LA_DA(attacker, defender, threshold):
    #Always Deathwing
    print("Legiones Astartes (Dark Angels): Deathwing adds +1 to hit")
    return threshold - 1

def ArmourOfElavagar(attacker, defender, threshold):
    if defender.charge:
        threshold = min(threshold+1,6)
        print("Armour of Elavagar applies -1 to hit: new threshold %d" % threshold)
    return threshold

def MasterOfWeapons(attacker, defender, threshold):
    print("MasterOfWeapons limits hit threshold to 4+")
    return max(threshold, 4)

def LA_IF(attacker, defender, threshold):
    print("Legiones Astartes (Imperial Fists): Add +1 to hit with Bolt weapons")
    return max(2, threshold - 1)

####################POSTHIT#########################

def BurstD6(attacker, attacker_weapon, defender, hitRolls):
    #assume only one roll in hitRolls
    if len(hitRolls) > 0 and hitRolls[0].success:
        mult = roll()
        print("Burst(D6): %s hits!" % mult)
        for i in range(1,mult):
            new_hitRoll = Die(hitRolls[0].value)
            new_hitRoll.success = True
            new_hitRoll.evaluated = True
            hitRolls.append(new_hitRoll)

####################PREWOUND####################

def EncarmineFury(attacker, attacker_weapon, defender, threshold):
    if attacker.charge:
        return max(2, threshold-1)
    return threshold

def Fleshbane(attacker, attacker_weapon, defender, threshold):
    if "Preternatural Resilience" in defender.rules:
        #So this is the funny part; unlike immunity, Preternatural Resilience is written to hijack flat rolls, as with the DG's intent to spam rad and phosphex
        #However, unlike Poison, Fleshbane has no "use strength's higher threshold"
        #Therefore, it seems Resilience should output 6+ because of its deliberate design to honeypot Fleshbane
        print("Fleshbane: Preternatural Resilience sets threshold to 6+")
        return 6
    #can just set Auric Armour to lower priority
    #if "Auric Armour" in defender.rules:
    #    print("Fleshbane: Auric Armour sets threshold to 3+")
    #    return 3
    elif "Pythian Scales" in defender.rules:
        #Unlike Preter.Resilience, immunity = "ignore rule completely and so use strength" seems to be the logical flow
        #Has precedence too: https://its-changemod.tumblr.com/post/119679268478/okay-so-skitarii-ruststalkers-can-have-two-kit
        print("Fleshbane: Pythian Scales is immune...")
        return threshold
    print("Fleshbane sets threshold to 2+")
    return 2

#needs this to ensure any normal roll is also blocked
def AuricArmour(attacker, attacker_weapon, defender, threshold):
    print("Auric Armour limits wound threshold to 4+")
    return max(threshold, 4)

def RendingThreshold(num):
    def func(attacker, attacker_weapon, defender, threshold):
        print("Rending: %d is success" % num)
        return min(threshold, num)
    return func

def BloodOfFire(attacker, attacker_weapon, defender, threshold):
    if "Flame" in attacker_weapon.rules or "Melta" in attacker_weapon.rules or "Plasma" in attacker_weapon.rules or "Volkite" in attacker_weapon.rules:
        print("Blood of Fire: -1 to Wound!")
        threshold = threshold + 1
    return threshold

def ChildOfTerra(attacker, attacker_weapon, defender, combat_round, woundRoll):
    if not woundRoll.rerolled and woundRoll.value == 1:
        rerollDie(woundRoll)
        print("Child of Terra: 1 -> %d" % woundRoll.value)

def Shred(attacker, attacker_weapon, defender, combat_round, woundRoll):
    if not woundRoll.rerolled and not woundRoll.success:
        old_value = woundRoll.value
        rerollDie(woundRoll)
        print("Shred: %d -> %d" % (old_value, woundRoll.value))

def PreferredEnemyWound(attacker, attacker_weapon, defender, combat_round, woundRoll):
    if not woundRoll.rerolled and woundRoll.value == 1:
        rerollDie(woundRoll)
        print("Preferred Enemy: 1 -> %d" % woundRoll.value)

#POSTWOUND
def GravitonPulse(attacker, attacker_weapon, defender, woundRolls):
    print("Graviton Pulse: Compare against Strength instead")
    for woundRoll in woundRolls:
        if woundRoll.value == 6 or woundRoll.value > defender.S:
            print("w%d: success" % woundRoll.value)
            woundRoll.success = True

def MurderousStrike(num):
    def func(attacker, attacker_weapon, defender, woundRolls):
        for woundRoll in woundRolls:
            if woundRoll.value >= num:
                print("Murderous Strike: %d has Instant Death" % woundRoll.value)
                woundRoll.effects.append("Instant Death")
    return func

def Brutal(num):
    def func(attacker, attacker_weapon, defender, woundRolls):
        new_woundRolls = []
        for woundRoll in woundRolls:
            if woundRoll.success == True:
                print("Brutal: w%d results in %d wounds!" % (woundRoll.value, num))
                for i in range(1,num):
                    new_woundRoll = WoundDie(woundRoll.value,attacker_weapon.AP)
                    new_woundRoll.success = True
                    new_woundRoll.evaluated = True
                    #clone the effects over?
                    new_woundRolls.append(new_woundRoll)
        woundRolls.extend(new_woundRolls)
    return func

#If psychic is added, then force needs to check for toggle
def Force(attacker, attacker_weapon, defender, woundRolls):
    print("Force: All wounds have Instant Death")
    for woundRoll in woundRolls:
        woundRoll.effects.append("Instant Death")

def InstantDeath(attacker, attacker_weapon, defender, woundRolls):
    #print("Instant Death: All wounds have Instant Death")
    for woundRoll in woundRolls:
        woundRoll.effects.append("Instant Death")

def Rending(num):
    def func(attacker, attacker_weapon, defender, woundRolls):
        for woundRoll in woundRolls:
            threshold = num
            if "Preternatural Resilience" in defender.rules: #not sure if considered "flat" roll
                threshold = 6
            if woundRoll.value >= threshold:
                #woundRoll.success = True #this is already determined by RendingThreshold
                woundRoll.AP = min(woundRoll.AP, 2)
                print("Rending: %s and above -> AP2" % num)
                #Suspicion: this isn't working as intended
    return func

def Breaching(num):
    def func(attacker, attacker_weapon, defender, woundRolls):
        for woundRoll in woundRolls:
            if woundRoll.value >= num:
                woundRoll.AP = min(woundRoll.AP, 2)
                print("Breaching: %s -> AP2" % num)
    return func

##############PRESAVE##############
#note: in practice you can decide the order of wounds to save against and then roll 1-by-1, e.g. in the case of Guilliman gaining FNP for some reason against ID
#however this doesn't happen in daddy duels, so iterating to the first failed save is just as good

#threshold
def ArmourOfTheWord(attacker, attacker_weapon, defender, threshold):
    if "Force" in attacker_weapon.rules:
        print("Armour of the Word: 3++ against %s which has Force" % (attacker_weapon.name))
        return 3
    return threshold

def ArmourOfElavagarShooting(attacker, attacker_weapon, defender, threshold):
    if "Plasma" in attacker_weapon.rules or "Flame" in attacker_weapon.rules: #no melta
        print("Armour of Elavagar: 3++ against %s" % attacker_weapon.name)
        return 3
    return threshold

#roll
def LeoninePanoply(attacker, attacker_weapon, defender, combat_round, saveRoll):
    if defender.invulnreroll:
        return
    if not saveRoll.rerolled and not saveRoll.success and saveRoll.saveType == SAVE_INVULN:
        old_value = saveRoll.value
        rerollDie(saveRoll)
        print("Leonine Panoply: %d -> %d" % (old_value, saveRoll.value))
        defender.invulnreroll = True

def ArmourOfReason(attacker, attacker_weapon, defender, combat_round, saveRoll):
    if defender.invulnreroll:
        return
    if not saveRoll.rerolled and not saveRoll.success and saveRoll.saveType == SAVE_INVULN:
        old_value = saveRoll.value
        rerollDie(saveRoll)
        print("Armour of Reason: %d -> %d" % (old_value, saveRoll.value))
        defender.invulnreroll = True

def RegaliaResplendent(attacker, attacker_weapon, defender, combat_round, saveRoll):
    if defender.charge:
        if not saveRoll.rerolled and not saveRoll.success and saveRoll.saveType == SAVE_INVULN:
            old_value = saveRoll.value
            rerollDie(saveRoll)
            print("Regalia Resplendent: %d -> %d" % (old_value, saveRoll.value))

def DrakenScale(attacker, attacker_weapon, defender, combat_round, saveRoll):
    if "Flame" in attacker_weapon.rules or "Volkite" in attacker_weapon.rules:
        if not saveRoll.rerolled and not saveRoll.success and saveRoll.saveType == SAVE_ARMOUR:
            old_value = saveRoll.value
            rerollDie(saveRoll)
            print("Draken Scale: %d -> %d" % (old_value, saveRoll.value))

#POSTSAVE

def reduceWounds(attacker, attacker_weapon, defender, woundRolls, saveRolls):
    for i in range(len(saveRolls)):
        if not saveRolls[i].success:
            defender.W -= 1

def Moonsilver(attacker, attacker_weapon, defender, woundRolls, saveRolls):
    #check for 'Psyker' done in combat.py
    new_woundRolls = []
    new_saveRolls = []
    for i in range(len(saveRolls)):
        if not saveRolls[i].success:
            print("Moonsilver: Unsaved roll results in two wounds!")
            new_woundRoll = WoundDie(woundRolls[i].value,attacker_weapon.AP)
            new_woundRoll.success = True
            new_woundRoll.evaluated = True
            #clone the effects over?
            new_woundRolls.append(new_woundRoll)
            new_saveRoll = SaveDie(saveRolls[i].value,saveRolls[i].saveType)
            new_saveRoll.success = False
            new_saveRoll.evaluated = True
            new_saveRolls.append(new_saveRoll)
    woundRolls.extend(new_woundRolls)
    saveRolls.extend(new_saveRolls)

def FeelNoPain(num):
    def func(attacker, attacker_weapon, defender, woundRolls, saveRolls):
        for i in range(len(saveRolls)):
            if not saveRolls[i].success:
                if "Instant Death" in woundRolls[i].effects:
                    print("FNP: w%d has Instant Death" % woundRolls[i].value)
                    continue
                fnp = roll()
                print("w%d: %s rolls Feel No Pain(%d): %d" % (woundRolls[i].value, defender.name, num, fnp))
                if fnp >= num:
                    print("Wound counted as saved!")
                    saveRolls[i].success = True #"treat it as having been saved"
    return func

#######END OF COMBAT
def DuellistsEdgeEnd(num):
    def func(primarch, opponent, combat_round):
        primarch.I = max(1,primarch.I - num)
    return func

def ChargeBonusEnd(primarch, defender, combat_round):
    if primarch.charge and not primarch.disordered:
        primarch.A -= 1

def LA_WEEnd(primarch, defender, combat_round):
    if primarch.charge:
        primarch.A -= 1

def CounterAttackEnd(num):
    def func(primarch, opponent, combat_round):
        if opponent.charge:
            primarch.A -= num
    return func

def FuriousChargeEnd(num):
    def func(primarch, defender, combat_round):
        if primarch.charge and not primarch.disordered:
            primarch.S = max(0, primarch.S - num) #I don't think we need the max safety anymore
    return func

def RageEnd(num):
    def func(primarch, defender, combat_round):
        if primarch.charge and not primarch.disordered:
            primarch.A = primarch.A - num
    return func

def FlawlessExecutionEnd(primarch, defender, combat_round):
    if primarch.charge:
        primarch.I = primarch.I - num

def SuddenStrikeEnd(num):
    def func(primarch, defender, combat_round):
        if primarch.charge and not primarch.disordered:
            primarch.I = primarch.I - num
    return func

def SireOfTheSpaceWolvesEnd(primarch, defender, combat_round):
    if primarch.charge:
        primarch.WS = max(0, primarch.S - 1)

def SireOfTheBloodAngelsEnd(primarch, defender, combat_round):
    if primarch.charge:
        primarch.WS = max(0, primarch.WS - 1)

###END OF ASSAULT
def WildfirePanoplyEnd(primarch, defender, combat_round):
    primarch.invuln_shoot = 5
    #print("Wildfire Panoply: %s's invuln returns to 5++" % primarch.name)

def FightingStyleEnd(primarch, defender, combat_round):
    if "Sudden Strike(3)" in primarch.rules:
        primarch.rules.remove("Sudden Strike(3)")
    elif "Rage(4)" in primarch.rules:
        primarch.rules.remove("Rage(4)")
    elif "Murderous Strike(4)" in primarch.rules:
        primarch.rules.remove("Murderous Strike(4)")

###############################RULE CATEGORIES###############################

###############SHOOTING###############
#modifiers, flat-threshold
ShootingPreHitThresholdAttackerRules = {
    "Legiones Astartes (Imperial Fists)": (1, LA_IF),
    }

ShootingPreHitThresholdDefenderRules = {
    }

ShootingPreHitDieAttackerRules = {
    "Master-Crafted": (1, MasterCrafted),
    "Twin-linked": (1, TwinLinked),
    "Preferred Enemy": (1, PreferredEnemyHit),
    }

ShootingPreHitDieDefenderRules = {
    }

ShootingPostHitAttackerRules = {
    "Burst(D6)": (1, BurstD6),
    }

ShootingPostHitDefenderRules = {
    }

ShootingPreWoundDieAttackerRules = {
    "Preferred Enemy": (1, PreferredEnemyWound),
    }

ShootingPreWoundDieDefenderRules = {
}

ShootingPreWoundThresholdAttackerRules = {
    "Fleshbane": (1, Fleshbane),
    }

ShootingPreWoundThresholdDefenderRules = {
    "Auric Armour": (0, AuricArmour), #supercede
    "Blood of Fire": (1, BloodOfFire),
    "Rending(3)": (1, RendingThreshold(3)), #.______.
    "Rending(4)": (1, RendingThreshold(4)), #.______.
    "Rending(5)": (1, RendingThreshold(5)), #.______.
    "Rending(6)": (1, RendingThreshold(6)), #.______.
    }

ShootingPostWoundAttackerRules = {
    "Graviton Pulse": (2, GravitonPulse),
    "Murderous Strike(5)": (1, MurderousStrike(5)),
    #"Force": (1, Force),
    "Instant Death": (1, InstantDeath),
    "Rending(3)": (1, Rending(3)), #.______.
    "Rending(4)": (1, Rending(4)), #.______.
    "Rending(5)": (1, Rending(5)), #.______.
    "Rending(6)": (1, Rending(6)), #.______.
    "Breaching(4)": (1, Breaching(4)), #.______.
    }

ShootingPostWoundDefenderRules = {
    }

ShootingPreSaveArmourThresholdAttackerRules = {
    }

ShootingPreSaveArmourThresholdDefenderRules = {
    }

ShootingPreSaveCoverThresholdAttackerRules = {
    }

ShootingPreSaveCoverThresholdDefenderRules = {
    }

ShootingPreSaveInvulnThresholdAttackerRules = {
    }

ShootingPreSaveInvulnThresholdDefenderRules = {
    #"Armour of the Word": (1, ArmourOfTheWord), #No force shooter I believe
    "Armour of Elavagar": (1, ArmourOfElavagarShooting)
    }

ShootingPreSaveDieAttackerRules = {
    }

ShootingPreSaveDieDefenderRules = {
    "Leonine Panoply": (1, LeoninePanoply),
    "Armour of Reason": (1, ArmourOfReason),
    "Regalia Resplendent": (1, RegaliaResplendent),
    "Draken Scale": (1, DrakenScale),
    }

ShootingPostSaveAttackerRules = {
    #"Deflagrate": (1, Deflagrate), #hardcoded test
    }

ShootingPostSaveDefenderRules = {
    "Feel No Pain(4)": (3, FeelNoPain(4)),
    "Feel No Pain(6)": (3, FeelNoPain(6)), #want this to happen BEFORE reducing wounds
    }

###############MELEE###############

#modifiers, flat-threshold
MeleePreHitThresholdAttackerRules = {
    "Legiones Astartes (Dark Angels)": (1, LA_DA),
    }

MeleePreHitThresholdDefenderRules = {
    "Armour of Elavagar": (1, ArmourOfElavagar),
    "Master of Weapons": (0, MasterOfWeapons), #supercede?
    }

MeleePreHitDieAttackerRules = {
    "Master-Crafted": (1, MasterCrafted),
    "Hatred": (1, Hatred),
    "Hatred(Psykers)": (1, HatredPsykers),
    "CoraxHatred": (1, CoraxHatred),
    "Preferred Enemy": (1, PreferredEnemyHit),
    "Calculating Swordsman": (1, CalculatingSwordsman),
    }

MeleePreHitDieDefenderRules = {
    }

MeleePostHitAttackerRules = {
    }

MeleePostHitDefenderRules = {
    }

MeleePreWoundDieAttackerRules = {
    "Child of Terra": (1, ChildOfTerra),
    "Shred": (1, Shred),
    "Preferred Enemy": (1, PreferredEnemyWound),
    }

MeleePreWoundDieDefenderRules = {
}

MeleePreWoundThresholdAttackerRules = {
    "Encarmine Fury": (1, EncarmineFury),
    "Fleshbane": (1, Fleshbane),
    }

MeleePreWoundThresholdDefenderRules = {
    "Auric Armour": (0, AuricArmour), #supercede
    "Rending(3)": (1, RendingThreshold(3)), #.______.
    "Rending(4)": (1, RendingThreshold(4)), #.______.
    "Rending(5)": (1, RendingThreshold(5)), #.______.
    "Rending(6)": (1, RendingThreshold(6)), #.______.
    #"Blood of Fire": (1, BloodOfFire), #Flame melee weapon...?
    }

MeleePostWoundAttackerRules = {
    "Murderous Strike(6)": (1, MurderousStrike(6)), #._____.
    "Murderous Strike(5)": (1, MurderousStrike(5)),
    "Murderous Strike(4)": (1, MurderousStrike(4)),
    "Murderous Strike(3)": (1, MurderousStrike(3)),
    "Force": (1, Force),
    "Instant Death": (1, InstantDeath),
    "Rending(3)": (1, Rending(3)), #.______.
    "Rending(4)": (1, Rending(4)), #.______.
    "Rending(5)": (1, Rending(5)), #.______.
    "Rending(6)": (1, Rending(6)), #.______.
    "Breaching(4)": (1, Breaching(4)), #.______.
    "Brutal(2)": (2, Brutal(2)),
    "Brutal(3)": (2, Brutal(3)),
    }

MeleePostWoundDefenderRules = {
    }

MeleePreSaveArmourThresholdAttackerRules = {
    }

MeleePreSaveArmourThresholdDefenderRules = {
    }

MeleePreSaveCoverThresholdAttackerRules = {
    }

MeleePreSaveCoverThresholdDefenderRules = {
    }

MeleePreSaveInvulnThresholdAttackerRules = {
    }

MeleePreSaveInvulnThresholdDefenderRules = {
    "Armour of the Word": (1, ArmourOfTheWord), #nothing it needs to supercede
    #Khan's 3++ against Overwatch
    }

MeleePreSaveDieAttackerRules = {
    #nothing, but an example is Sigismund's reroll-successful-saves
    }

MeleePreSaveDieDefenderRules = {
    "Leonine Panoply": (1, LeoninePanoply),
    "Armour of Reason": (1, ArmourOfReason),
    "Regalia Resplendent": (1, RegaliaResplendent),
    #"Draken Scale": (1, DrakenScale), #Flame melee weapon...?
    }

MeleePostSaveAttackerRules = {
    "Moonsilver": (3, Moonsilver),
    }

MeleePostSaveDefenderRules = {
    "Feel No Pain(4)": (3, FeelNoPain(4)), #want this to happen BEFORE reducing wounds
    "Feel No Pain(6)": (3, FeelNoPain(6)),
    }

#ugggh
#basically categorises the use of rules at specific points
#have to split into attacker and defender, so e.g. hatred when Angron's defending won't be used
#all things in the same category must accept the same arguments
rules_categories = {
    "ShootingPreHitThreshold": [ShootingPreHitThresholdAttackerRules, ShootingPreHitThresholdDefenderRules],
    "ShootingPreHitDie": [ShootingPreHitDieAttackerRules, ShootingPreHitDieDefenderRules],
    "ShootingPreWoundThreshold": [ShootingPreWoundThresholdAttackerRules, ShootingPreWoundThresholdDefenderRules],
    "ShootingPreWoundDie": [ShootingPreWoundDieAttackerRules, ShootingPreWoundDieDefenderRules],
    "ShootingPreSaveArmourThreshold": [ShootingPreSaveArmourThresholdAttackerRules, ShootingPreSaveArmourThresholdDefenderRules],
    "ShootingPreSaveCoverThreshold": [ShootingPreSaveCoverThresholdAttackerRules, ShootingPreSaveCoverThresholdDefenderRules],
    "ShootingPreSaveInvulnThreshold": [ShootingPreSaveInvulnThresholdAttackerRules, ShootingPreSaveInvulnThresholdDefenderRules],
    "ShootingPreSaveDie": [ShootingPreSaveDieAttackerRules, ShootingPreSaveDieDefenderRules],
    "ShootingPostHit": [ShootingPostHitAttackerRules, ShootingPostHitDefenderRules],
    "ShootingPostWound": [ShootingPostWoundAttackerRules, ShootingPostWoundDefenderRules],
    "ShootingPostSave": [ShootingPostSaveAttackerRules, ShootingPostSaveDefenderRules],
    "MeleePreHitThreshold": [MeleePreHitThresholdAttackerRules, MeleePreHitThresholdDefenderRules],
    "MeleePreHitDie": [MeleePreHitDieAttackerRules, MeleePreHitDieDefenderRules],
    "MeleePreWoundThreshold": [MeleePreWoundThresholdAttackerRules, MeleePreWoundThresholdDefenderRules],
    "MeleePreWoundDie": [MeleePreWoundDieAttackerRules, MeleePreWoundDieDefenderRules],
    "MeleePreSaveArmourThreshold": [MeleePreSaveArmourThresholdAttackerRules, MeleePreSaveArmourThresholdDefenderRules],
    "MeleePreSaveCoverThreshold": [MeleePreSaveCoverThresholdAttackerRules, MeleePreSaveCoverThresholdDefenderRules],
    "MeleePreSaveInvulnThreshold": [MeleePreSaveInvulnThresholdAttackerRules, MeleePreSaveInvulnThresholdDefenderRules],
    "MeleePreSaveDie": [MeleePreSaveDieAttackerRules, MeleePreSaveDieDefenderRules],
    "MeleePostHit": [MeleePostHitAttackerRules, MeleePostHitDefenderRules],
    "MeleePostWound": [MeleePostWoundAttackerRules, MeleePostWoundDefenderRules],
    "MeleePostSave": [MeleePostSaveAttackerRules, MeleePostSaveDefenderRules],
}

StartOfAssaultRules = {
    "Wildfire Panoply": (1, WildfirePanoplyStart),
    "Fighting Style": (1, FightingStyle),
    }

ChargeRules = {
    "Legiones Astartes (World Eaters)": (1, LA_WE),
    "Furious Charge(1)": (1, FuriousCharge(1)), #.___.
    "Furious Charge(2)": (1, FuriousCharge(2)), #.___.
    "Sire of the Space Wolves": (1, SireOfTheSpaceWolves),
    "Sire of the Blood Angels": (1, SireOfTheBloodAngels),
    "Counter-Attack(1)": (1,CounterAttack(1)),
    "Counter-Attack(2)": (1,CounterAttack(2)),
    "Rage(2)": (1, Rage(2)),
    "Rage(4)": (1, Rage(4)),
    "Sudden Strike(1)": (1, SuddenStrike(1)),
    "Sudden Strike(3)": (1, SuddenStrike(3)),
    "Flawless Execution": (1, FlawlessExecution),
    }

StartOfCombatRules = {
    "Duellist's Edge(1)": (1,DuellistsEdgeStart(1)),
    }

EndOfCombatRules = {
    "Duellist's Edge(1)": (1,DuellistsEdgeEnd(1)),
    }

ChargeEndRules = {
    "Legiones Astartes (World Eaters)": (1, LA_WEEnd),
    "Furious Charge(1)": (1, FuriousChargeEnd(1)),
    "Furious Charge(2)": (1, FuriousChargeEnd(2)),
    "Sire of the Space Wolves": (1, SireOfTheSpaceWolvesEnd),
    "Sire of the Blood Angels": (1, SireOfTheBloodAngelsEnd),
    "Counter-Attack(1)": (1,CounterAttackEnd(1)),
    "Counter-Attack(2)": (1,CounterAttackEnd(2)),
    "Rage(2)": (1, RageEnd(2)),
    "Rage(4)": (1, RageEnd(4)),
    "Sudden Strike(1)": (1, SuddenStrikeEnd(1)),
    "Sudden Strike(3)": (1, SuddenStrikeEnd(3)),
    "Flawless Execution": (1, FlawlessExecutionEnd),
    }

EndOfAssaultRules = {
    "Wildfire Panoply": (1, WildfirePanoplyEnd),
    "Fighting Style": (1, FightingStyleEnd),
    }

def getStartOfAssaultRules(primarch):
    rules = []
    for rulename in primarch.rules:
        if rulename in StartOfAssaultRules:
            rules.append(StartOfAssaultRules[rulename])
    return rules

def getEndOfAssaultRules(primarch):
    rules = []
    for rulename in primarch.rules:
        if rulename in EndOfAssaultRules:
            rules.append(EndOfAssaultRules[rulename])
    return rules

#assume no such rule on weapons: DAMMIT

def getChargeRules(primarch):
    rules = [(1,ChargeBonus)]
    for rulename in primarch.rules:
        if rulename in ChargeRules:
            rules.append(ChargeRules[rulename])
    for rulename in primarch.melee_weapons[0].rules: #Spear of Telesto, White Tiger Dao
        if rulename in ChargeRules:
            rules.append(ChargeRules[rulename])
    return rules

def getStartOfCombatRules(primarch):
    rules = []
    for rulename in primarch.rules:
        if rulename in StartOfCombatRules:
            rules.append(StartOfCombatRules[rulename])
    for rulename in primarch.melee_weapons[0].rules: #for init-modifying weapons; not good implementation!
        if rulename in StartOfCombatRules:
            rules.append(StartOfCombatRules[rulename])
    return rules

def getChargeEndRules(primarch):
    rules = [(1,ChargeBonusEnd)]
    for rulename in primarch.rules:
        if rulename in ChargeEndRules:
            rules.append(ChargeEndRules[rulename])
    for rulename in primarch.melee_weapons[0].rules: #Spear of Telesto, White Tiger Dao
        if rulename in ChargeEndRules:
            rules.append(ChargeEndRules[rulename])
    return rules


def getEndOfCombatRules(primarch):
    rules = []
    for rulename in primarch.rules:
        if rulename in EndOfCombatRules:
            rules.append(EndOfCombatRules[rulename])
    for rulename in primarch.melee_weapons[0].rules: #for init-modifying weapons; not good implementation!
        if rulename in EndOfCombatRules:
            rules.append(EndOfCombatRules[rulename])
    return rules

def collectRules(attacker, attacker_weapon, defender, combat_round, ruletype):
    rules_to_execute = [] #this should be a priority queue instead
    if ruletype.endswith("PostSave"):
        #always actually do damage first
        rules_to_execute.append((2, reduceWounds))
    attackerRules, defenderRules = rules_categories[ruletype]
    for rule in attacker.rules:
        if rule in attackerRules:
            rules_to_execute.append(attackerRules[rule])
    for rule in attacker_weapon.rules:
        if rule in attackerRules:
            rules_to_execute.append(attackerRules[rule])
    for rule in defender.rules:
        if rule in defenderRules:
            rules_to_execute.append(defenderRules[rule])
    rules_to_execute.sort(key=lambda x: x[0],reverse=True) #we want 0 to be slowest (supercede)
    return rules_to_execute

#####################MISC RULES#######################

def InitiativeTest(testee):
    return characteristicTest(testee.I)

def SerpentScalesSave():
    save = roll()
    print("Serpent's Scales: %d" % (save))
    return save >= 3

def IWNDTest(primarch):
    IWND_roll = roll()
    threshold = 5
    if primarch.name == "Mortarion" or primarch.name == "Lorgar" or primarch.name == "Vulkan":
        threshold = 4
    print("%s rolls It Will Not Die: %d" % (primarch.name, IWND_roll))
    """
    if IWND_roll < threshold:
        if primarch1.rerollIWND:
            new_roll = roll()
            print("Reroll: %s -> %s" % (IWND_roll, new_roll))
            IWND_roll = new_roll
    """
    if IWND_roll >= threshold:
        primarch.W = min(primarch.W + 1, primarch.shadow_W)
        print("%s regains a wound to %d!" % (primarch.name, primarch.W))
