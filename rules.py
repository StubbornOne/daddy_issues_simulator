### For rules that require a specific function ###

#Note: re-rerolls will be blocked by rerollDie(), so you can run it without worry

from calculations import *
from primarchs import *

"""
The assumption is all rules can just function without needing external, specific info
If specific info is needed e.g. only executes in the first round, immunity, saves,
this can be toggled outside so the phase
will not even add the rule in to be executed
"""

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

def WildfirePanoplyStart(primarch, combat_round):
    primarch.invuln_shoot = 3
    print("Wildfire Panoply: %s's invuln grows to 3++!" % primarch.name)

#####START OF COMBAT: CHARGE

def ChargeBonus(primarch, defender, combat_round):
    if primarch.charge and "Shroud Bombs" not in defender.rules:
        primarch.A += 1
        print("%s gets +1A for the charge!" % primarch.name)

def CounterAttack(primarch, defender, combat_round):
    if defender.charge:
        primarch.A += 1
        print("Counter-Attack: %s gets +1A for being charged!" % primarch.name)

def StasisGrenades(primarch, defender, combat_round):
    if primarch.charge or defender.charge:
        if "Serpent's Scales" in defender.rules:
            if SerpentScalesSave():
                return
        defender.I = 1
        defender.underStasis = True
        print("%s is under stasis!" % defender.name)

def FuriousCharge(primarch, defender, combat_round):
    if primarch.charge:
        primarch.S = min(primarch.S + 1, 10)
        print("Furious Charge: %s gains +1S!" % primarch.name)

def SireOfTheRavenGuard(primarch, defender, combat_round):
    if primarch.charge:
        primarch.S = min(10, primarch.S + 1)
        primarch.I = min(10, primarch.I + 1)
        print("Sire of the Raven Guard: %s gains +1S +1I!" % primarch.name)

#####START OF COMBAT

def SireOfTheBloodAngelsStart(primarch, defender, combat_round):
    if combat_round == 0:
        primarch.A += 1
        primarch.I = min(10, primarch.I + 1)
        print("Sire of the Blood Angels: %s gains +1A +1I!" % primarch.name)

def PreternaturalStrategyIncrement(primarch, defender, combat_round):
    #not sure how Preter is supposed to work with Blind
    #Based on wording, assume Blind's temporary WS1 supercedes and does not grow, but after Blind will turn into the 'grown' WS, which only resets when Challenge ends
    if primarch.shadow_WS == 10:
        return
    primarch.challenge_counter += 1
    if primarch.challenge_counter > 0:
        primarch.shadow_WS = primarch.shadow_WS + 1
        if primarch.underBlind <= 0:
            primarch.WS = primarch.shadow_WS
            print("Preternatural Strategy: %s's WS increases to %d!" % (primarch.name, primarch.shadow_WS))

def FightingStyle(primarch, defender, combat_round):
    #first, delete existing FIGHTING_STYLES
    if "FIGHTING_STYLE_SCOURGE" in primarch.rules: #._. abuse append/pop maybe?
        primarch.rules.remove("FIGHTING_STYLE_SCOURGE")
    #if "FIGHTING_STYLE_DEATH_STRIKE" in primarch.rules:
    #primarch.rules.remove("FIGHTING_STYLE_DEATH_STRIKE")
    if (primarch.active) and "FIGHTING_STYLE_SHADOW_WALK" in primarch.rules:
        primarch.rules.remove("FIGHTING_STYLE_SHADOW_WALK")
    #you will never use Death Strike until IA Magnus is implemented
    #stick to: if your own turn, shadow-walk (for 2 rounds' worth)
    #then, Scourge
    #it's ok to shadow-walk against e.g. the Lion because he hits you on 3+ so nerf to 4+. Even if he's blinded, you don't want to risk getting caught unblinded next turn
    if (primarch.active or combat_round==0):
        print("Fighting Style: Chose Shadow-Walk")
        primarch.rules.append("FIGHTING_STYLE_SHADOW_WALK")
    else:
        print("Fighting Style: Chose Scourge")
        primarch.rules.append("FIGHTING_STYLE_SCOURGE")

#technically it should be during attack selection?
#also: does this actually modify the Init value? People assume so, but DEdge says "score" and RB says "fights at -1 Init", not change the value
def DuellistsEdgeStart(primarch, defender, combat_round):
    if not (primarch.underConcuss > 0 or primarch.underStasis): #we assume these take precedence
        primarch.I = min(10, primarch.I + 1)
        print("Duellist's Edge: %s gains +1I!" % primarch.name)

def ReapingBlowStart(primarch, defender, combat_round):
    if not (primarch.underConcuss > 0 or primarch.underStasis): #we assume these take precedence
        primarch.I = max(1, primarch.I - 1)
        print("Reaping Blow: %s has -1I!" % primarch.name)

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

def DarkFortuneHit(attacker, attacker_weapon, defender, combat_round, hitRoll):
    if not hitRoll.rerolled and hitRoll.value >= 5:
        old_value = hitRoll.value
        rerollDie(hitRoll)
        print("Dark Fortune: %d -> %d" % (old_value, hitRoll.value))

#Threshold rules

def AbsoluteFocus(threshold):
    print("Absolute Focus sets the threshold to at least 4+")
    return min(4,threshold) #hits on minimum 4+; if 3+ all the better

def ArmourOfElavagar(threshold):
    print("Armour of Elavagar applies -1 to hit: new threshold %d" % (threshold+1))
    return threshold + 1

def PhantasmalAura(threshold):
    print("Phantasmal Aura applies -1 to hit: new threshold %d" % (threshold+1))
    return threshold + 1

def FightingStyleShadowWalk(threshold):
    print("Fighting-Style: Shadow-walk applies -1 to hit: new threshold %d" % (threshold+1))
    return threshold + 1

####################POSTHIT#########################
def Blind(attacker, attacker_weapon, defender, hitRolls):
    if "IMMUNE_BLIND" in defender.rules:
        print("Blind: %s is immune to Blind" % defender.name)
    elif len(hitRolls) > 0:
        print("Blind: %s must take a Blind test!" % defender.name)
        defender.takeBlindTest = True

####################PREWOUND####################

def Fleshbane(defender, threshold):
    if "Preternatural Resilience" in defender.rules:
        #So this is the funny part; unlike immunity, Preternatural Resilience is written to hijack flat rolls, as with the DG's intent to spam rad and phosphex
        #However, unlike Poison, Fleshbane has no "use strength's higher threshold"
        #Therefore, it seems Resilience should output 6+ because of its deliberate design to honeypot Fleshbane
        #coding really brings out the need to be specific eh :) see if 40k rulings ever go to the lengths of MtG
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

def DarkFortuneWound(attacker, attacker_weapon, defender, combat_round, woundRoll):
    if not woundRoll.rerolled and woundRoll.value >= 5:
        old_value = woundRoll.value
        rerollDie(woundRoll)
        print("Dark Fortune: %d -> %d" % (old_value, woundRoll.value))

#needs this to ensure any normal roll is also blocked
def AuricArmour(defender, threshold):
    print("Auric Armour limits wound threshold to 3+")
    return max(threshold, 3) #so 2+ to wound gets rejected

def Rending(defender, threshold):
    print("Rending: 6s always wound")
    return min(threshold, 6)

#POSTWOUND
def GravitonPulse(attacker, attacker_weapon, defender, woundRolls):
    print("Graviton Pulse: Compare against Strength instead")
    for woundRoll in woundRolls:
        if woundRoll.value == 6 or woundRoll.value > defender.S:
            print("w%d: success" % woundRoll.value)
            woundRoll.success = True

def MurderousStrike(attacker, attacker_weapon, defender, woundRolls):
    for woundRoll in woundRolls:
        if woundRoll.value == 6:
            print("Murderous Strike: %d has Instant Death" % woundRoll.value)
            woundRoll.effects.append("Instant Death")

#kind of bad lol, use a HoF maybe
def MurderousStrike5(attacker, attacker_weapon, defender, woundRolls):
    for i in range(len(woundRolls)):
        if woundRolls[i].value >= 5:
            print("Murderous Strike (5+): %d has Instant Death" % woundRolls[i].value)
            woundRolls[i].effects.append("Instant Death")

#If psychic is added, then force needs to check for toggle
def Force(attacker, attacker_weapon, defender, woundRolls):
    print("Force: All wounds have Instant Death")
    for woundRoll in woundRolls:
        woundRoll.effects.append("Instant Death")

def InstantDeath(attacker, attacker_weapon, defender, woundRolls):
    #print("Instant Death: All wounds have Instant Death")
    for woundRoll in woundRolls:
        woundRoll.effects.append("Instant Death")

def WrathOfAngels(attacker, attacker_weapon, defender, woundRolls):
    new_woundRolls = []
    for woundRoll in woundRolls:
        if woundRoll.value == 6 and woundRoll.success == True:
            print("Wrath of Angels: %d results in two wounds!" % woundRoll.value)
            new_woundRoll = WoundDie(6,attacker_weapon.AP)
            new_woundRoll.success = True
            new_woundRoll.evaluated = True
            #clone the effects over?
            new_woundRolls.append(new_woundRoll)
    woundRolls.extend(new_woundRolls)

def RendingPost(attacker, attacker_weapon, defender, woundRolls):
    for woundRoll in woundRolls:
        if woundRoll.value == 6:
            woundRoll.success = True
            woundRoll.AP = min(woundRoll.AP, 2)
            print("Rending: 6 -> auto-Wound at AP2")

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
    if "Plasma" in attacker_weapon.rules or "Flamer" in attacker_weapon.rules: #no melta
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

#POSTSAVE

def reduceWounds(attacker, attacker_weapon, defender, woundRolls, saveRolls):
    for i in range(len(saveRolls)):
        if not saveRolls[i].success:
            defender.W -= 1

#Strikedown no longer halves Init by HH rulebook (but still forces attacks at Init 1 if charge, todo)
"""
def Strikedown(attacker, attacker_weapon, defender, woundRolls, saveRolls):
    #at least one wound, saved or not
    if len(woundRolls) > 0:
        print("Applying Strikedown")
        if "Serpent's Scales" in defender.rules:
            if SerpentScalesSave():
                print("Strikedown: saved!")
                return #done, Strikedown triggers once for "one or more Wounds"
        #this exploits that only concussive and strikedown reduce I
        new_I = min(defender.I, (defender.shadow_I + 1) // 2)
        print("Strikedown: %s is struck down!" % defender.name)
        defender.I = new_I #immediately apply effect
        defender.underStrikedown = True
"""

def Concussive(attacker, attacker_weapon, defender, woundRolls, saveRolls):
    if "IMMUNE_CONCUSS" in defender.rules:
        #print("Concussive: %s is immune to Concussive" % defender.name)
        return
    for i in range(len(saveRolls)):
        if not saveRolls[i].success:
            if "Serpent's Scales" in defender.rules:
                if SerpentScalesSave():
                    print("Concussive: saved!")
                    return #done, Concuss triggers once for "one or more Wounds"
            defender.I = 1 #immediately apply effect
            defender.underConcuss = 2 #subtract 1 end of this assault phase; subtract 1 end of next assault phase and restore
            print("Concussive: %s is concussed!" % defender.name)
            break #just one is enough

def LethalPrecision(attacker, attacker_weapon, defender, woundRolls, saveRolls):
    for i in range(len(woundRolls)):
        if woundRolls[i].value == 6 and saveRolls[i].saveType != SAVE_COVER:
            saveRolls[i].success = False
            print("Lethal Precision: w%d ignores armour and invuln saves" % woundRolls[i].value)

def SoulBlaze(attacker, attacker_weapon, defender, woundRolls, saveRolls):
    for i in range(len(saveRolls)):
        if not saveRolls[i].success:
            defender.sufferSoulBlaze = True
            break #just one is enough

def SeverLife(attacker, attacker_weapon, defender, woundRolls, saveRolls):
    for i in range(len(saveRolls)):
        if not saveRolls[i].success:
            #not actually necessary because the sever test is not recursive, but it avoids printing confusing messages
            if not defender.sufferSeverLife:
                print("Sever Life activated")
                defender.sufferSeverLife = True
            break #just one is enough

def FeelNoPain(attacker, attacker_weapon, defender, woundRolls, saveRolls):
    for i in range(len(saveRolls)):
        if not saveRolls[i].success:
            if "Instant Death" in woundRolls[i].effects:
                print("FNP: w%d has Instant Death" % woundRolls[i].value)
                continue
            fnp = roll()
            print("w%d: %s rolls Feel No Pain: %d" % (woundRolls[i].value, defender.name, fnp))
            if fnp >= 5:
                print("Wound counted as saved!")
                saveRolls[i].success = True #"treat it as having been saved"

def GildedPanoply(attacker, attacker_weapon, defender, woundRolls, saveRolls):
    for saveRoll in saveRolls:
        if saveRoll.value == 6:
            if ("IMMUNE_BLIND" in attacker.rules):
                print("Gilded Panoply: %s is immune to Blind" % attacker.name)
                return
            print("Gilded Panoply: %s must take a blind test!" % attacker.name)
            attacker.takeBlindTest = True
            break #one will do

def DisablingStrike(attacker, attacker_weapon, defender, woundRolls, saveRolls):
    for i in range(len(saveRolls)):
        if not saveRolls[i].success:
            if "Serpent's Scales" in defender.rules:
                if SerpentScalesSave():
                    print("Disabling Strike: saved!")
                    continue #this is per wound!
            print("w%d: Disabling Strike!" % woundRolls[i].value)
            defender.WS = max(1, defender.WS - 1) #NOTE: I'm not sure if WS can drop to 0
            defender.S = max(0, defender.S - 1)
            defender.shadow_WS = max(1, defender.shadow_WS - 1)
            defender.shadow_S = max(1, defender.shadow_S - 1)
            print("Disabling Strike: %s now at WS%d S%d" % (defender.name, defender.WS, defender.S))

#######END OF COMBAT
def SireOfTheBloodAngelsEnd(primarch, opponent, combat_round):
    if combat_round == 0:
        primarch.I = max(1,primarch.I - 1)
        primarch.A -= 1
        #print("Sire of the Blood Angels: %s's I and A reset to %d, %d" % (primarch.name, primarch.I, primarch.A))

def DuellistsEdgeEnd(primarch, opponent, combat_round):
    if not (primarch.underConcuss > 0 or primarch.underStasis):
        primarch.I = max(1,primarch.I - 1)
        #print("Duellist's Edge: %s returns to I%d" % (primarch.name, primarch.I))

def ReapingBlowEnd(primarch, opponent, combat_round):
    if not (primarch.underConcuss > 0 or primarch.underStasis):
        primarch.I += 1
        #print("Reaping Blow: %s returns to I%d" % (primarch.name, primarch.I))

def ChargeBonusEnd(primarch, opponent, combat_round):
    if primarch.charge and "Shroud Bombs" not in opponent.rules:
        primarch.A -= 1

def CounterAttackEnd(primarch, opponent, combat_round):
    if opponent.charge:
        primarch.A -= 1

def FuriousChargeEnd(primarch, opponent, combat_round):
    if primarch.charge and "Shroud Bombs" not in opponent.rules:
        primarch.S = max(0, primarch.S - 1)
        #print("Furious Charge: %s loses the +1S" % primarch.name)

def SireOfTheRavenGuardEnd(primarch, defender, combat_round):
    if primarch.charge:
        primarch.S = max(0, primarch.S - 1)
        primarch.I = max(1,primarch.I - 1)
        #print("Sire of the Raven Guard: %s loses the +1S +1I" % primarch.name)

###END OF ASSAULT
def WildfirePanoplyEnd(primarch, combat_round):
    primarch.invuln_shoot = 5
    #print("Wildfire Panoply: %s's invuln returns to 5++" % primarch.name)

def DarkFortuneRemoval(primarch, combat_round):
    primarch.rules.remove("Dark Fortune")

###############################RULE CATEGORIES###############################

###############SHOOTING###############
#modifiers, flat-threshold
ShootingPreHitThresholdAttackerRules = {
    }

ShootingPreHitThresholdDefenderRules = {
    "Phantasmal Aura": (1, PhantasmalAura),
    }

ShootingPreHitDieAttackerRules = {
    "Master-Crafted": (1, MasterCrafted),
    "Twin-linked": (1, TwinLinked),
    "Preferred Enemy": (1, PreferredEnemyHit),
    }

ShootingPreHitDieDefenderRules = {
    "Dark Fortune": (1, DarkFortuneHit),
    }

ShootingPostHitAttackerRules = {
    "Blind": (1, Blind),
    }

ShootingPostHitDefenderRules = {
    }

ShootingPreWoundDieAttackerRules = {
    "Preferred Enemy": (1, PreferredEnemyWound),
    }

ShootingPreWoundDieDefenderRules = {
    "Dark Fortune": (1, DarkFortuneWound),
}

ShootingPreWoundThresholdAttackerRules = {
    "Fleshbane": (1, Fleshbane),
    }

ShootingPreWoundThresholdDefenderRules = {
    "Auric Armour": (0, AuricArmour), #supercede
    "Rending": (1, Rending),
    }

ShootingPostWoundAttackerRules = {
    "Graviton Pulse": (2, GravitonPulse),
    "Murderous Strike": (1, MurderousStrike),
    "Murderous Strike (5+)": (1, MurderousStrike5),
    #"Force": (1, Force),
    "Instant Death": (1, InstantDeath),
    "Rending": (1, RendingPost),
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
    }

ShootingPostSaveAttackerRules = {
    "Concussive": (1, Concussive), #Ferrus' Graviton Gun
    "Lethal Precision": (4, LethalPrecision),
    #"Deflagrate": (1, Deflagrate), #hardcoded test
    "Soul Blaze": (1, SoulBlaze),
    }

ShootingPostSaveDefenderRules = {
    "Feel No Pain": (3, FeelNoPain), #want this to happen BEFORE reducing wounds
    }

###############MELEE###############

#modifiers, flat-threshold
MeleePreHitThresholdAttackerRules = {
    "An Absolute Focus": (0, AbsoluteFocus), #0 to execute latest, thus "superceding" (remember -1 to hit still affects Lion's 3+)
    }

MeleePreHitThresholdDefenderRules = {
    "Armour of Elavagar": (1, ArmourOfElavagar),
    "Phantasmal Aura": (1, PhantasmalAura),
    "FIGHTING_STYLE_SHADOW_WALK": (1, FightingStyleShadowWalk),
    }

MeleePreHitDieAttackerRules = {
    "Master-Crafted": (1, MasterCrafted),
    "Hatred": (1, Hatred),
    "CoraxHatred": (1, CoraxHatred),
    "Preferred Enemy": (1, PreferredEnemyHit),
    }

MeleePreHitDieDefenderRules = {
    "Dark Fortune": (1, DarkFortuneHit),
    }

MeleePostHitAttackerRules = {
    "Blind": (1, Blind),
    }

MeleePostHitDefenderRules = {
    }

MeleePreWoundDieAttackerRules = {
    "Child of Terra": (1, ChildOfTerra),
    "Shred": (1, Shred),
    "Preferred Enemy": (1, PreferredEnemyWound),
    }

MeleePreWoundDieDefenderRules = {
    "Dark Fortune": (1, DarkFortuneWound),
}

MeleePreWoundThresholdAttackerRules = {
    "Fleshbane": (1, Fleshbane),
    }

MeleePreWoundThresholdDefenderRules = {
    "Auric Armour": (0, AuricArmour), #supercede
    "Rending": (1, Rending),
    }

MeleePostWoundAttackerRules = {
    "Murderous Strike": (1, MurderousStrike),
    "Murderous Strike (5+)": (1, MurderousStrike5),
    "Force": (1, Force),
    "Instant Death": (1, InstantDeath),
    "Wrath of Angels": (2, WrathOfAngels), #hack to ensure the new rolls have Instant Death
    "Rending": (1, RendingPost),
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
    }

MeleePostSaveAttackerRules = {
    #"Strikedown": (1, Strikedown),
    "Concussive": (1, Concussive),
    "Sever Life": (1, SeverLife),
    "Disabling Strike": (1, DisablingStrike),
    }

MeleePostSaveDefenderRules = {
    "Feel No Pain": (3, FeelNoPain), #want this to happen BEFORE reducing wounds
    "Gilded Panoply": (1, GildedPanoply),
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
    }

ChargeRules = {
    "Furious Charge": (1, FuriousCharge),
    "Sire of the Raven Guard": (1, SireOfTheRavenGuard),
    "Stasis Grenades": (1,StasisGrenades),
    "Counter-Attack": (1,CounterAttack),
    }

StartOfCombatRules = {
    "Sire of the Blood Angels": (1,SireOfTheBloodAngelsStart),
    "Preternatural Strategy": (1, PreternaturalStrategyIncrement),
    "Fighting Style": (1, FightingStyle),
    "Duellist's Edge": (1,DuellistsEdgeStart),
    "Reaping Blow": (1,ReapingBlowStart),
    }

EndOfCombatRules = {
    "Sire of the Blood Angels": (1,SireOfTheBloodAngelsEnd),
    "Duellist's Edge": (1,DuellistsEdgeEnd),
    "Reaping Blow": (1,ReapingBlowEnd),
    }

ChargeEndRules = {
    "Furious Charge": (1, FuriousChargeEnd),
    "Sire of the Raven Guard": (1, SireOfTheRavenGuardEnd),
    "Counter-Attack": (1,CounterAttackEnd),
    }

EndOfAssaultRules = {
    "Wildfire Panoply": (1, WildfirePanoplyEnd),
    "Dark Fortune": (1, DarkFortuneRemoval), #hack to ensure Dark Fortune is only used once
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

def PreternaturalStrategyReset(primarch):
    primarch.shadow_WS -= primarch.challenge_counter
    primarch.challenge_counter = -1
    #don't reset WS here; in case Guilliman is blinded
    if primarch.underBlind == 0:
        primarch.WS = primarch.shadow_WS
    print("Preternatural Strategy: %s resets WS%d (before Blind)" % (primarch.name, primarch.WS))

def BlindTest(primarch):
    #if you're immune, you should not have reached this
    print("Blind test: %s" % primarch.name)
    success = InitiativeTest(primarch)
    if not success:
        #blind test failed
        if "Serpent's Scales" in primarch.rules:
            if SerpentScalesSave():
                return
        print("%s is blinded!" % (primarch.name))
        if primarch.active == True:
            primarch.underBlind = 3
        else:
            primarch.underBlind = 2
        primarch.WS = 1
        primarch.BS = 1
    primarch.takeBlindTest = False

def IWNDTest(primarch1):
    IWND_roll = roll()
    print("%s rolls It Will Not Die: %d" % (primarch1.name, IWND_roll))
    if IWND_roll < 5:
        if primarch1.rerollIWND:
            new_roll = roll()
            print("Reroll: %s -> %s" % (IWND_roll, new_roll))
            IWND_roll = new_roll
    if IWND_roll >= 5:
        primarch1.W = min(primarch1.W + 1, primarch1.shadow_W)
        print("%s regains a wound to %d!" % (primarch1.name, primarch1.W))
