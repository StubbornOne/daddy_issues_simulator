from primarchs import *
from weapons import *
from rules import *
from calculations import *

####AI stuff

def SangCharged(defender):
    return defender.name == "Sanguinius" and defender.charge

"""
VERY rough metrics based on 1d4's math, which I do not know the exact algorithm
One attack from Sword of Balenight (assume WS9; for 3+ just 4/3 the final result)
1 * 1/2 * 3/4 / 2 = 0.1875
1 * 1/2 * 5/9 / 3 = 0.138
1 * 1/2 * 3/4 / 3 = 0.125
1 * 1/2 * 5/9 / 3 = 0.0926

Against T6 Sever Life will cause an additional 1.091 Wounds on average. (~0.5 after saves, ~-0.1 if I alloc 5 attacks)
Against T7 Sever Life will cause an additional 0.909 Wounds on average. (~0.45 after saves, ~-0.05 if I alloc 5 attacks)
Assume this is for 4++; if so, using very rough math for 3++ (*2 / 3):
Against T6 Sever Life will cause an additional 0.727 Wounds on average. (~0.242 after saves, ~0.04 if I alloc 5 attacks)
Against T7 Sever Life will cause an additional 0.606 Wounds on average. (~0.202 after saves, ~0.034 if I alloc 5 attacks)

One attack from Axe of Helwinter (assume WS9)
1.5 * 1/2 * 5/6 / 2 = 0.3125
1.5 * 1/2 * 2/3 / 2 = 0.25
1.5 * 1/2 * 5/6 / 3 = 0.208
1.5 * 1/2 * 2/3 / 3 = 0.167

More precisely calculations needed, but from the gist of it; T7/3++-equiv spend all on Axe; everyone else 5-1 split
Ok I crunched it against Ferrus; indeed, spent all on Axe if T7 and 3++
"""
def predictSeverLife(defender):
    if (defender.T <= 6 and defender.invuln_melee > 3) and not SangCharged(defender):
        return True
    return False

def needToConcuss(defender):
    return defender.name == "Fulgrim" or ("Hit and Run" in defender.rules and not defender.active)

####Actual rolling
def isDefeated(primarch):
    return primarch.W <= 0 or primarch.S <= 0 or primarch.T <= 0

def resolveHits(attacker, attacker_weapon, defender, combat_round, numAttacks, attackType):
    if "Template" in attacker_weapon.rules:
        if attacker.active:
            #auto... one hit?
            hitRoll = Die(7)
            hitRoll.success = True
            hitRoll.evaluated = True
            hitRolls = [hitRoll]
        else:
            hitRolls = [Die(7) for i in range(roll(3))]
            for hitRoll in hitRolls:
                hitRoll.success = True
                hitRoll.evaluated = True
        print("Template: autohit! %d hits" % len(hitRolls))
        print("Successes: %s" % str([die.value for die in hitRolls]))
        return hitRolls #some posthit may matter, e.g. if a template weapon has blind, but no such weap in daddy duels
    elif "Line of Effect" in attacker_weapon.rules:
        hitRolls = [Die(7) for i in range(numAttacks)]
        for hitRoll in hitRolls:
            hitRoll = Die(7)
            hitRoll.success = True
            hitRoll.evaluated = True
        print("Line of Effect: autohit!")
        print("Successes: %s" % str([die.value for die in hitRolls]))
        return hitRolls #some posthit may matter, e.g. if a template weapon has blind, but no such weap in daddy duels
    elif "Blast" in attacker_weapon.rules or "Large Blast" in attacker_weapon.rules: #only Pert atm
        print(numAttacks)
        hitRolls = [Die(7) for i in range(numAttacks)]
        for hitRoll in hitRolls:
            hitRoll = Die(7)
            hitRoll.success = True
            hitRoll.evaluated = True
        print("Blast: autohit!")
        print("Successes: %s" % str([die.value for die in hitRolls]))
        return hitRolls #some posthit may matter, e.g. if a template weapon has blind, but no such weap in daddy duels
    #calculate the thresholds, apply all rules
    if attackType == "Melee":
        threshold = thresholdToHit(attacker.WS, defender.WS)
    else:
        #should not be done like this...
        if not attacker.active: #then it's an Overwatch
            threshold = thresholdToShoot(1)
        else:
            threshold = thresholdToShoot(attacker.BS)
    rules = collectRules(attacker, attacker_weapon, defender, combat_round, "%sPreHitThreshold" % (attackType))
    for rule in rules:
        threshold = rule[1](threshold)
    #apply threshold stuff, if any

    print("%d+ to hit..." % threshold)
    
    #roll hit dice
    hitRolls = rollDice(numAttacks)
    print([die.value for die in hitRolls])
    
    #compare threshold
    compareThreshold(hitRolls, threshold)

    #for each preHit rule
        #execute rule
        #evaluate again
    rules = collectRules(attacker, attacker_weapon, defender, combat_round, "%sPreHitDie" % attackType)
    for rule in rules:
        for hitRoll in hitRolls:
            rule[1](attacker, attacker_weapon, defender, combat_round, hitRoll)
            hitRoll._compareThreshold(threshold)

    #if shooting and BS > 5, reroll
    if attackType == "Shooting" and attacker.BS > 5 and attacker.active:
        for hitRoll in hitRolls:
            if not hitRoll.rerolled and hitRoll.value == 1: #which should not be a success / 'faux' hitRolls should have some other value
                #by right we should recompute the threshold, however I cannot think of a scenario in this context that we can't just +4 to the existing one
                hitRoll.reroll()
                print("BS%d: Reroll 1 -> %d, require %d" % (attacker.BS, hitRoll.value, threshold+4))
                hitRoll._compareThreshold(threshold+4)

    #Resolve Gets Hot (I don't think there's a melee GetsHot)
    if "Gets Hot" in attacker_weapon.rules:
        getsHotRolls = list(filter(lambda roll: roll.value == 1, hitRolls))
        if len(getsHotRolls) > 0:
            print("Gets Hot!!!")
            woundRolls = resolveWounds(attacker, attacker_weapon, attacker, combat_round, getsHotRolls, "Shooting")
            saveRolls = resolveSaves(attacker, attacker_weapon, attacker, combat_round, woundRolls, "Shooting")

    hitRolls = discardFailedRolls(hitRolls)
    print("Successes: %s" % str([die.value for die in hitRolls]))

    #apply postHit rules to all dice that hit
    rules = collectRules(attacker, attacker_weapon, defender, combat_round, "%sPostHit" % attackType)
    for rule in rules:
        rule[1](attacker, attacker_weapon, defender, hitRolls)

    return hitRolls

def resolveWounds(attacker, attacker_weapon, defender, combat_round, hitRolls, attackType):
    #calculate the thresholds, apply all rules
    atkS = attacker_weapon.calculateAttackStrength(attacker.S)
    defT = defender.T
    #this is terrible, find a way to put them inside rules.py
    if attacker.charge and attackType == "Melee":
        if "PLUS_ONE_S_ON_CHARGE" in attacker_weapon.rules:
            atkS = min(10, atkS + 1)
            print("%s has +1S on the charge! S:%d" % (attacker_weapon.name, atkS))
        elif "PLUS_THREE_S_ON_CHARGE" in attacker_weapon.rules:
            atkS = min(10, atkS + 3)
            print("%s has +3S on the charge! S:%d" % (attacker_weapon.name, atkS))
    if attackType == "Shooting":
        if "Sire of the Iron Hands" in defender.rules and attacker != defender: #Gets Hot lul
            atkS = max(1, atkS - 1) #to avoid accessing chart[-1]
            print("Sire of the Iron Hands: Shooting attacks have -1S against %s! S:%d" % (defender.name, atkS))
        if "Draken Scale" in defender.rules and ("Plasma" in attacker_weapon.rules or "Flame" in attacker_weapon.rules or "Volkite" in attacker_weapon.rules):
            atkS = max(1, atkS // 2) #rounded down!
            print("Draken Scale: Plasma and Flamers are reduce to half strength! S:%d" % atkS)
    threshold = thresholdToWound(atkS, defT)
    #apply threshold stuff, if any
    rules = collectRules(attacker, attacker_weapon, defender, combat_round, "%sPreWoundThreshold" % attackType)
    for rule in rules:
        threshold = rule[1](defender, threshold)

    print("%d+ to wound..." % threshold)
    
    #roll wound dice
    woundRolls = rollWoundDice(len(hitRolls), attacker_weapon)
    print([die.value for die in woundRolls])

    #compare threshold
    compareThreshold(woundRolls, threshold)

    #evaluate
    #for each preWound rule
        #execute rule
        #evaluate again
    rules = collectRules(attacker, attacker_weapon, defender, combat_round, "%sPreWoundDie" % attackType)
    for rule in rules:
        for woundRoll in woundRolls:
            rule[1](attacker, attacker_weapon, defender, combat_round, woundRoll)
            woundRoll._compareThreshold(threshold)

    woundRolls = discardFailedRolls(woundRolls)
    print("Successes: %s" % str([die.value for die in woundRolls]))

    #apply postWound rules to all dice that wound

    rules = collectRules(attacker, attacker_weapon, defender, combat_round, "%sPostWound" % attackType)
    for rule in rules:
        rule[1](attacker, attacker_weapon, defender, woundRolls)

    return woundRolls

def resolveSaves(attacker, attacker_weapon, defender, combat_round, woundRolls, attackType):
    #apply threshold stuff, if any
    #because of Rending, we've to go through the wounds one-by-one and see which save is applicable
    armour_rules = collectRules(attacker, attacker_weapon, defender, combat_round, "%sPreSaveArmourThreshold" % attackType)
    cover_rules = collectRules(attacker, attacker_weapon, defender, combat_round, "%sPreSaveCoverThreshold" % attackType) #should be empty for melee
    invuln_rules = collectRules(attacker, attacker_weapon, defender, combat_round, "%sPreSaveInvulnThreshold" % attackType)
    #generate "unrolled" saveRolls first, with the appropriate save type and whatever
    saveRolls = [SaveDie(0,SAVE_ARMOUR) for roll in woundRolls]
    for i in range(len(woundRolls)):
        woundRoll = woundRolls[i]
        saveRoll = saveRolls[i]
        if "Lethal Precision" in woundRoll.effects:
            #hack to ensure it doesn't actually roll
            saveRoll.rerolled = True
            saveRoll.evaluated = True
        elif woundRoll.AP > defender.armour:
            #use armour. We can technically choose cover/invuln, but I don't think there's a case within daddy duels to NOT choose armour
            #ok there is a case: Precog Lorgar's rerollable 3++. Handle that if/when psychic is implemented
            #in daddy duels, there will never be AP3 (ignoring Sang's throw), so just chuck it below?
            threshold = defender.armour
            for rule in armour_rules:
                threshold = rule[1](attacker, attacker_weapon, defender, armour_threshold)
            saveRoll.saveType = SAVE_ARMOUR
            saveRoll.threshold = threshold
            print("w%d: Using armour save" % woundRoll.value)
        elif issubclass(type(attacker_weapon), ShootingWeapon):
            #compute cover and invuln, find the better threshold
            cover_threshold = defender.cover
            for rule in cover_rules:
                cover_threshold = rule[1](attacker, attacker_weapon, defender, cover_threshold)
            invuln_threshold = defender.invuln_shoot
            for rule in invuln_rules:
                invuln_threshold = rule[1](attacker, attacker_weapon, defender, invuln_threshold)
            if cover_threshold >= invuln_threshold or "Ignores Cover" in attacker_weapon.rules:
                saveRoll.threshold = invuln_threshold
                saveRoll.saveType = SAVE_INVULN
                print("w%d: Using invuln save" % woundRoll.value)
            else:
                saveRoll.threshold = cover_threshold
                saveRoll.saveType = SAVE_COVER
                print("w%d: Using cover save" % woundRoll.value)
        else:
            threshold = defender.invuln_melee
            for rule in invuln_rules:
                threshold = rule[1](attacker, attacker_weapon, defender, threshold)
            saveRoll.threshold = threshold
            saveRoll.saveType = SAVE_INVULN
    
    #roll save dice
    print("Rolling saves")
    for saveRoll in saveRolls:
        saveRoll.firstRoll()
        saveRoll._compareThreshold(saveRoll.threshold)
    print([die.value for die in saveRolls])

    rules = collectRules(attacker, attacker_weapon, defender, combat_round, "%sPreSaveDie" % attackType)
    for rule in rules:
        for saveRoll in saveRolls:
            rule[1](attacker, attacker_weapon, defender, combat_round, saveRoll)
            saveRoll._compareThreshold(saveRoll.threshold)

    print("Final:     %s" % str([die.value for die in saveRolls]))

    #Post-save, including the actual wounding
    assert (len(saveRolls) == len(woundRolls))
    rules = collectRules(attacker, attacker_weapon, defender, combat_round, "%sPostSave" % attackType)
    for rule in rules:
        rule[1](attacker, attacker_weapon, defender, woundRolls, saveRolls)
    print("%s has %d wounds left!" % (defender.name, defender.W))

    return saveRolls

###########SHOOTING################

def shootWeapon(attacker, weapon, defender, combat_round):
    #these should be in chooseAndShootWeapons
    if weapon.weapontype == "Salvo" and attacker.active:
        #don't shoot because we want to charge, though there's a case for shooting and doing nothing
        return
    if ("Blast" in weapon.rules or weapon.weapontype == "Ordnance") and not attacker.active:
        #can't shoot
        return
    if "One-Use" in weapon.rules:
        if weapon.used:
            return
        else:
            weapon.used = True
    #there is also "Heavy" and "Ordnance", but Ferrus and Pert has rules to handle those
    if attacker.active:
        print("%s is shooting %s with %s!" % (attacker.name, defender.name, weapon.name))
    else:
        print("Overwatch: %s is shooting %s with %s!" % (attacker.name, defender.name, weapon.name))
    
    #HITS
    hitRolls = resolveHits(attacker, weapon, defender, combat_round, weapon.getShots(), "Shooting")

    #WOUNDS (which, is a near repeat...)
    woundRolls = resolveWounds(attacker, weapon, defender, combat_round, hitRolls, "Shooting")

    #SAVES
    saveRolls = resolveSaves(attacker, weapon, defender, combat_round, woundRolls, "Shooting")
    #postshoot?

    #Deflagrate check
    if "Deflagrate" in weapon.rules:
        hitRolls = []
        for i in range(len(saveRolls)):
            if not saveRolls[i].success:
                hitRoll = Die(7)
                hitRoll.success = True
                hitRoll.evaluated = True
                hitRolls.append(hitRoll)
        if len(hitRolls) > 0:
            print("Deflagrate: Inflict %d new hits" % len(hitRolls))
            #I dunno if Ferrus will get -1S for this though
            woundRolls = resolveWounds(attacker, weapon, defender, combat_round, hitRolls, "Shooting")
            resolveSaves(attacker, weapon, defender, combat_round, woundRolls, "Shooting")
    return

def chooseAndShootWeapons(attacker, defender, combat_round): #nobody will snap shot except for Overwatch
    #choose weapon(s)
    weapons = []
    if "Medusan Carapace" in attacker.rules:
        if attacker.active:
            if "Draken Scale" in defender.rules:
                weapons.append(attacker.shooting_weapons[1]) #you can't hurt Vulkan with anything else
            else:
                print("Medusan Carapace: Ferrus can fire two weapons!")
                #for my sanity; just fire the plasma blaster and heavy flamer
                #TODO: when movement is implemented, use the graviton gun when to create difficult/dang terrain
                weapons.append(attacker.shooting_weapons[0])
                weapons.append(attacker.shooting_weapons[3])
        else:
            weapons.append(attacker.shooting_weapons[3]) #use the heavy flamer for 1d3 autohit overwatch
    elif attacker.name == "Corvus Corax" and len(attacker.shooting_weapons) > 1: #get the two Archaeotech pistols
        weapons.append(attacker.shooting_weapons[0])
        weapons.append(attacker.shooting_weapons[1])
    elif attacker.name == "Jaghatai Khan" and len(attacker.shooting_weapons) > 1: #Mounted
        if defender.name == "Angron" or defender.name == "Ferrus Manus":
            weapons.append(attacker.shooting_weapons[0]) #Angron has 3+ armour, Ferrus imposes -1S on top of T7 so 6+
        else:
            weapons.append(attacker.shooting_weapons[1]) #use the HB. -1strength overall but 4x shots
    #may be too optimistic to say Pert can't scatter the bombardment (onto himself!)
    #elif attacker.name == "Perturabo" and attacker.active:
    #    weapons.append(attacker.shooting_weapons[0])
    #    weapons.append(attacker.shooting_weapons[1]) #fire the bombardment
    else:
        #just use the first one
        weapons.append(attacker.shooting_weapons[0])

    for weapon in weapons:
        shootWeapon(attacker, weapon, defender, combat_round)
        if isDefeated(attacker) or isDefeated(defender): #must check attacker too - e.g. Gets Hot
            return True
    return False

def shootingPhase(primarch1, primarch2, num_round):
    #No rule that executes at the start of the shooting phase
    """
    rules1 = getStartOfShootingRules(primarch1)
    for rule in rules1:
        rule[1](primarch1, num_round)
    rules2 = getStartOfShootingRules(primarch2)
    for rule in rules2:
        rule[1](primarch2, num_round)
    """
    #check in combat
    if primarch1.in_combat:
        assert(primarch2.in_combat)
        print("Both primarchs locked in combat")
        return
    #check which primarch is active
    if primarch1.active:
        ended = chooseAndShootWeapons(primarch1, primarch2, num_round)
    else:
        ended = chooseAndShootWeapons(primarch2, primarch1, num_round)
    if ended:
        return ended
    
    #Blind tests
    if primarch1.takeBlindTest:
        BlindTest(primarch1)
    if primarch2.takeBlindTest:
        BlindTest(primarch2)

    #No rule that executes at the end of the shooting phase
    """
    rules1 = getEndOfAssaultRules(primarch1)
    for rule in rules1:
        rule[1](primarch1, num_round)
    rules2 = getEndOfAssaultRules(primarch2)
    for rule in rules2:
        rule[1](primarch2, num_round)
    """

###########ASSAULT################


def resolveMeleeAttacks(attacker, attacker_weapon, defender, combat_round, numAttacks):
    print("%s attacks with %s %d times!" %(attacker.name, attacker_weapon.name, numAttacks))
    #HITS
    hitRolls = resolveHits(attacker, attacker_weapon, defender, combat_round, numAttacks, "Melee")

    #WOUNDS
    woundRolls = resolveWounds(attacker, attacker_weapon, defender, combat_round, hitRolls, "Melee")

    #SAVES
    resolveSaves(attacker, attacker_weapon, defender, combat_round, woundRolls, "Melee")
    
    #POST ATTACK PHASE
    #TODO: Implement all these as a Post-Attack
    #all these can be post-save though?
    #Sever Life check
    if defender.sufferSeverLife and defender.W > 0:
        #do 2d6 for Toughness
        do_sever_life = roll() + roll()
        print("Sever Life: %s rolls 2d6 against Toughness %d: %d" % (defender.name, defender.T, do_sever_life))
        if do_sever_life > defender.T:
            #create new wound rolls
            newWoundRolls = rollWoundDice(roll(3), attacker_weapon)
            print("Inflict %d new wounds" % len(newWoundRolls))
            #we assume that because the AP of the wound is described, it means a save can be made for the new wounds
            resolveSaves(attacker, attacker_weapon, defender, combat_round, newWoundRolls, "Melee")
    defender.sufferSeverLife = False

def resolveHammerOfWrath(attacker, defender, combat_round):
    #generate "hit" rolls, retrieve the dummy weapon
    numHits = 1
    attacker_weapon = HammerOfWrath()
    for rule in attacker.rules:
        if rule == "Sojutsu Voidbike" or rule == "Nightmare Mantle":
            numHits = roll(3)
            break
        if rule == "Korvidine Pinions":
            numHits = roll(3)
            attacker_weapon = KorvidinePinions()
            break
        if rule == "Great Wings":
            attacker_weapon = GreatWings()
            break

    print("Hammer of Wrath: %s attacks with %s %d times!" %(attacker.name, attacker_weapon.name, numHits))
    hitRolls = rollDice(numHits)
    for hitRoll in hitRolls:
        hitRoll.value = 7
        hitRoll.success = True
        hitRoll.evaluated = True
    #WOUND PHASE
    woundRolls = resolveWounds(attacker, attacker_weapon, defender, combat_round, hitRolls, "Melee")

    #SAVE PHASE
    resolveSaves(attacker, attacker_weapon, defender, combat_round, woundRolls, "Melee")
    #done


#return an array with the attacker, weapon and attacks allocated, representing primarch1's attacks
#resolve init outside, for convenience
#TODO: Weapon Mastery and smarter choosing (need more context)
def allocateAttacks(attacker, defender, numAttacks, combat_round):
    assert (numAttacks >= 1)
    attacks = []
    if len(attacker.melee_weapons) == 1:
        attacks.append([attacker, attacker.melee_weapons[0], defender, combat_round, numAttacks])
    else: #should be 2
        assert (len(attacker.melee_weapons) == 2)
        #hardcode
        #since Hit & Run is not implemented, no need to consider is_own_combat_round (for Concussing)
        if attacker.name == "Horus Lupercal":
            if "IMMUNE_CONCUSS" in defender.rules or not needToConcuss(defender):
                #no reason to use Worldbreaker
                attacks.append([attacker, attacker.melee_weapons[0], defender, combat_round, numAttacks])
            else:
                #split X-1 Talon-Worldbreaker. Why? To maximise Master-crafted
                #though if you really need to concuss you should spend more on Worldbreaker...
                attacks.append([attacker, attacker.melee_weapons[0], defender, combat_round, numAttacks-1])
                attacks.append([attacker, attacker.melee_weapons[1], defender, combat_round, 1])
        elif attacker.name == "Leman Russ":
            if predictSeverLife(defender):
                attacks.append([attacker, attacker.melee_weapons[0], defender, combat_round, numAttacks-1])
                attacks.append([attacker, attacker.melee_weapons[1], defender, combat_round, 1])
            else:
                #use the Axe
                attacks.append([attacker, attacker.melee_weapons[1], defender, combat_round, numAttacks])
        elif attacker.name == "Roboute Guilliman":
            #TODO: Smarter strat to figure out when to switch based on initiative of next round. but this'll go into decision trees...?
            if defender.T >=7 or needToConcuss(defender) or (defender.I > attacker.I and defender.name != "Angron") or defender.name == "Horus":
                #use the HoD
                attacks.append([attacker, attacker.melee_weapons[1], defender, combat_round, numAttacks])
            else:
                attacks.append([attacker, attacker.melee_weapons[0], defender, combat_round, numAttacks])
        elif attacker.name == "Ferrus Manus":
            attacks.append([attacker, attacker.melee_weapons[0], defender, combat_round, numAttacks])
            #then servo arm attacks
            attacks.append([attacker, attacker.melee_weapons[1], defender, combat_round, 1])
    return attacks

def pushAttackIntoInitiativeQueue(initiative_queue,attack,primarch):
    weapon = attack[2]
    if "Sire of the White Scars" in primarch.rules:
        initiative_queue[10].append(attack) #Khan's special tier. May want to hardcode instead, in case a Khan vs Khan fight happens (then initiative matters)
    elif "Unwieldy" in weapon.rules:
        initiative_queue[0].append(attack)
    else:
        initiative = primarch.I-1
        #now handled by startOfCombatRules. Reason is I'm not sure if this modifies Initiative step or Initiative itself (affecting Sublime Swordsman), mathhammer suggests it does
        """
        if "Reaping Blow" in weapon.rules:
            initiative = max(0,initiative-1)
        if "Duellist's Edge" in weapon.rules:
            initiative = initiative+1        """
        initiative_queue[initiative].append(attack)

def fightSubPhase(primarch1, primarch2, combat_round, MODE_CHARGE):
    #resolve start-of-combat effects (e.g. Corax's modes, Sire of the Blood Angels)
    rules1 = getStartOfCombatRules(primarch1)
    if MODE_CHARGE:
        rules1.extend(getChargeRules(primarch1))
    for rule in rules1:
        rule[1](primarch1, primarch2, combat_round)
    rules2 = getStartOfCombatRules(primarch2)
    if MODE_CHARGE:
        rules2.extend(getChargeRules(primarch2))
    for rule in rules2:
        rule[1](primarch2, primarch1, combat_round)

    #Hammer of Wrath
    if MODE_CHARGE:
        if primarch1.charge and "Hammer of Wrath" in primarch1.rules:
            resolveHammerOfWrath(primarch1, primarch2, combat_round)
            if isDefeated(primarch1) or isDefeated(primarch2):
                return True
        elif primarch2.charge and "Hammer of Wrath" in primarch2.rules:
            resolveHammerOfWrath(primarch2, primarch1, combat_round)
            if isDefeated(primarch1) or isDefeated(primarch2):
                return True
    
    numattacks1 = primarch1.getAttacks(primarch2, combat_round)
    numattacks2 = primarch2.getAttacks(primarch1, combat_round)

    #initiative represented as an array of 11 arrays. Then, iterate backwards to resolve attacks
    initiative_queue = [[] for i in range(11)]
    #primarchs choose weapons and attacks
    attacks1 = allocateAttacks(primarch1, primarch2, numattacks1, combat_round)
    attacks2 = allocateAttacks(primarch2, primarch1, numattacks2, combat_round)
    for attack in attacks1:
        pushAttackIntoInitiativeQueue(initiative_queue,attack,primarch1)
    for attack in attacks2:
        pushAttackIntoInitiativeQueue(initiative_queue,attack,primarch2)

    #now traverse the initiative queue to resolve attacks
    i = 10 #Khan's special priority
    while i >= 0:
        attacks = initiative_queue[i]
        for attack in attacks:
            resolveMeleeAttacks(*attack)
        #resolve ALL attacks at the init before checking for dead
        if isDefeated(primarch1) or isDefeated(primarch2):
            return True
        i -= 1

    #nobody croaked?
    #resolve end-of-combat effects (IWND etc)

    rules1 = getEndOfCombatRules(primarch1)
    if MODE_CHARGE:
        rules1.extend(getChargeEndRules(primarch1))
    for rule in rules1:
        rule[1](primarch1, primarch2, combat_round)
    rules2 = getEndOfCombatRules(primarch2)
    if MODE_CHARGE:
        rules2.extend(getChargeEndRules(primarch2))
    for rule in rules2:
        rule[1](primarch2, primarch1, combat_round)

    #done! return False to indicate not ended
    return False

#primarch1 is the Hit and Runner
def attemptHitAndRun(primarch1, primarch2):
    #run on this turn
    print("Hit and Run: %s" % primarch1.name)
    success = InitiativeTest(primarch1)
    if success:
        print("Success!")
        primarch1.in_combat = False
        primarch2.in_combat = False
        if "Preternatural Strategy" in primarch2.rules:
            PreternaturalStrategyReset(primarch2)

def assaultPhase(primarch1, primarch2, num_round, MODE_CHARGE):
    rules1 = getStartOfAssaultRules(primarch1)
    for rule in rules1:
        rule[1](primarch1, num_round)
    rules2 = getStartOfAssaultRules(primarch2)
    for rule in rules2:
        rule[1](primarch2, num_round)

    #Charge!
    if MODE_CHARGE:
        print("##Start of charge subphase##")
        if not primarch1.in_combat: #primarch2 should not be in combat either
            if primarch1.active:
                primarch1.charge = True
                print("%s is charging!" % primarch1.name)
                print("%s makes Overwatch!" % primarch2.name)
                ended = chooseAndShootWeapons(primarch2, primarch1, num_round)
                if ended:
                    return ended
            else: #primarch2 should be active
                primarch2.charge = True
                print("%s is charging!" % primarch2.name)
                print("%s makes Overwatch!" % primarch1.name)
                ended = chooseAndShootWeapons(primarch1, primarch2, num_round)
                if ended:
                    return ended
        print("##End of charge subphase##")
    #always assume charge success, so
    primarch1.in_combat = True
    primarch2.in_combat = True
    print("##Start of fight subphase##")
    ended = fightSubPhase(primarch1, primarch2, num_round, MODE_CHARGE)
    if ended:
        return ended
    print("#End of fight subphase#")
    #none of these really has an ordering
    
    #handle Concuss
    if primarch1.underConcuss > 0:
        primarch1.underConcuss = primarch1.underConcuss - 1
        if primarch1.underConcuss == 0:
            print("%s is no longer concussed" % (primarch1.name))
            primarch1.restoreI()
    if primarch2.underConcuss > 0:
        primarch2.underConcuss = primarch2.underConcuss - 1
        if primarch2.underConcuss == 0:
            print("%s is no longer concussed" % (primarch2.name))
            primarch2.restoreI()

    #Blind tests
    if primarch1.takeBlindTest:
        BlindTest(primarch1)
    if primarch2.takeBlindTest:
        BlindTest(primarch2)

    if MODE_CHARGE:
            primarch1.charge = False
            primarch2.charge = False

    rules1 = getEndOfAssaultRules(primarch1)
    for rule in rules1:
        rule[1](primarch1, num_round)
    rules2 = getEndOfAssaultRules(primarch2)
    for rule in rules2:
        rule[1](primarch2, num_round)

    #Hit and Run
    if MODE_CHARGE:
        if "Hit and Run" in primarch1.rules and not primarch1.active:
            attemptHitAndRun(primarch1, primarch2)
        elif "Hit and Run" in primarch2.rules and not primarch2.active:
            attemptHitAndRun(primarch2, primarch1)

    return ended

def SoulBlazeTest(primarch1, num_round):
    if primarch1.sufferSoulBlaze:
        soulblaze_test = roll(6)
        if soulblaze_test <= 3:
            print("Soul Blaze: %s rolls %d, ended!" % (primarch1.name, soulblaze_test))
            primarch1.sufferSoulBlaze = False
        else:
            #D3 strength hits
            attacker_weapon = SoulBlazeAttack()
            hitRolls = rollDice(3)
            print("Soul Blaze: %s rolls %d, failed! %d hits!" % (primarch1.name, soulblaze_test, len(hitRolls)))
            for hitRoll in hitRolls:
                hitRoll.value = 7
                hitRoll.success = True
                hitRoll.evaluated = True
            woundRolls = resolveWounds(DummyPrimarch(), attacker_weapon, primarch1, num_round, hitRolls, "Shooting")
            resolveSaves(DummyPrimarch(), attacker_weapon, primarch1, num_round, woundRolls, "Shooting")
    return isDefeated(primarch1)

def playerTurn(primarch1, primarch2, num_round, MODE_CHARGE):
    primarch1.handleStartOfTurn()
    primarch2.handleStartOfTurn()
    #movement phase #whatever
    #shooting phase
    if MODE_CHARGE:
        print("###Shooting phase###")
        primarch1.handleStartOfPhase()
        primarch2.handleStartOfPhase()
        ended = shootingPhase(primarch1, primarch2, num_round)
        if ended:
            return ended
        print("###End of shooting phase###")
    #assault phase
    print("###Assault phase###")
    primarch1.handleStartOfPhase()
    primarch2.handleStartOfPhase()
    ended = assaultPhase(primarch1, primarch2, num_round, MODE_CHARGE)
    if ended:
        return ended
    print("###End of assault phase###")

    #blind
    resolveBlindEnd(primarch1)
    resolveBlindEnd(primarch2)

    #Soul Blaze
    ended = SoulBlazeTest(primarch1, num_round)
    if ended:
        return ended
    ended = SoulBlazeTest(primarch2, num_round)
    if ended:
        return ended

    #cleanup
    if primarch1.active:
        IWNDTest(primarch1)
    else:
        IWNDTest(primarch2)

def resolveBlindEnd(primarch1):
    if primarch1.underBlind > 0:
        primarch1.underBlind -= 1
        if primarch1.underBlind == 0:
            print("%s is no longer blinded" % (primarch1.name))
            primarch1.restoreWS()
            primarch1.restoreBS()

def resolveStasisEnd(primarch1):
    if primarch1.underStasis:
        primarch1.underStasis = False
        primarch1.restoreI()
        print("%s is no longer under stasis" % primarch1.name)

def resolveGameTurnEnd(primarch1, primarch2):
    #Stasis
    resolveStasisEnd(primarch1)
    resolveStasisEnd(primarch2)

def duel(primarchA, primarchB, MODE_CHARGE):
    ended = False
    who_goes_first = decideFirstRound(primarchA.mv, primarchB.mv)
    if who_goes_first:
        primarchA.active = True
    else:
        primarchB.active = True
    player_turn = 0
    game_turn = 0
    combat_round = 0
    while not ended:
        if primarchA.active:
            primarchA.active = False
            primarchB.active = True
        else:
            primarchA.active = True
            primarchB.active = False
        print("Player Turn %d" % (player_turn + 1))
        #now actually do the turn!
        ended = playerTurn(primarchA, primarchB, combat_round, MODE_CHARGE)
        if primarchA.in_combat and primarchB.in_combat:
            combat_round += 1
        else:
            assert(not primarchA.in_combat and not primarchB.in_combat)
            combat_round = 0
        player_turn += 1
        if player_turn % 2 == 0:
            game_turn += 1
            resolveGameTurnEnd(primarchA, primarchB)
        print()
    #check the primarch wounds and declare victor
    print("END OF DUEL")
    print("%s: %d wounds, %s: %d wounds" % (primarchA.name, primarchA.W, primarchB.name, primarchB.W))
    A_defeated = isDefeated(primarchA)
    B_defeated = isDefeated(primarchB)
    if A_defeated and B_defeated:
        print("Mutual defeat")
        return 2
    elif A_defeated:
        print("%s wins!" % primarchB.name)
        return 1
    elif B_defeated:
        print("%s wins!" % primarchA.name)
        return 0
    else:
        print("Hm?")
    return (A_defeated, B_defeated)

#MODE_CHARGE=True
#pert = Perturabo()
#pert.active = True
#shootingPhase(pert, Ferrus(), 0)
#duel(Alpharius(),Ferrus())
