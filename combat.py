from primarchs import *
from weapons import *
from rules import *
from calculations import *

####AI stuff

####Actual rolling
def isDefeated(primarch):
    return primarch.W <= 0 #or primarch.S <= 0 or primarch.T <= 0 #no more

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
        return hitRolls
    elif "Line of Effect" in attacker_weapon.rules:
        hitRolls = [Die(7) for i in range(numAttacks)]
        for hitRoll in hitRolls:
            hitRoll = Die(7)
            hitRoll.success = True
            hitRoll.evaluated = True
        print("Line of Effect: autohit!")
        print("Successes: %s" % str([die.value for die in hitRolls]))
        return hitRolls
    elif "Blast" in attacker_weapon.rules or "Large Blast" in attacker_weapon.rules: #only Pert atm
        print(numAttacks)
        hitRolls = [Die(7) for i in range(numAttacks)]
        for hitRoll in hitRolls:
            hitRoll = Die(7)
            hitRoll.success = True
            hitRoll.evaluated = True
        print("Blast: autohit!")
        print("Successes: %s" % str([die.value for die in hitRolls]))
        return hitRolls
    #calculate the thresholds, apply all rules
    if attackType == "Melee":
        if defender.name == "Angron": #TODO: See https://www.reddit.com/r/Warhammer30k/comments/v2jakj/has_anyone_crunched_the_numbers_on_primarch_duels/, debate(?) on Butcher's Nails' effect on Challenges
            threshold = thresholdToHit(attacker.WS, 3)
        else:
            threshold = thresholdToHit(attacker.WS, defender.WS)
    else:
        #2.0: All Primarch Snap Shots resolved at full BS
        threshold = thresholdToShoot(attacker.BS)
    rules = collectRules(attacker, attacker_weapon, defender, combat_round, "%sPreHitThreshold" % (attackType))
    for rule in rules:
        threshold = rule[1](attacker, defender, threshold)
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
            saveRolls = resolveSaves(attacker, attacker_weapon, attacker, combat_round, woundRolls, "Shooting") #note, cover cannot be taken, but those with cover saves don't have GetsHot anyway

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
    """
    if attacker.charge and attackType == "Melee":
        if "PLUS_ONE_S_ON_CHARGE" in attacker_weapon.rules:
            atkS = min(10, atkS + 1)
            print("%s has +1S on the charge! S:%d" % (attacker_weapon.name, atkS))
        elif "PLUS_THREE_S_ON_CHARGE" in attacker_weapon.rules:
            atkS = min(10, atkS + 3)
            print("%s has +3S on the charge! S:%d" % (attacker_weapon.name, atkS))
    """
    if defender.name == "Ferrus Manus" and attackType == "Shooting" and attacker != defender: #Gets Hot lul
        atkS = max(1, atkS - 1) #to avoid accessing chart[-1]
        print("Medusa's Scales: Shooting attacks have -1S against %s! S:%d" % (defender.name, atkS))
    if defender.name == "Horus Lupercal" and (attacker.charge or defender.charge) and attackType == "Melee":
        atkS = max(1, atkS - 1) #to avoid accessing chart[-1]
        print("Merciless Fighters: %s's melee attacks suffer -1S! S%d" % (attacker.name, atkS))
    threshold = thresholdToWound(atkS, defT)
    #apply threshold stuff, if any
    rules = collectRules(attacker, attacker_weapon, defender, combat_round, "%sPreWoundThreshold" % attackType)
    for rule in rules:
        threshold = rule[1](attacker, attacker_weapon, defender, threshold)

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
        #TODO: Decide whether to Overwatch or HtL (HtL seems to be the superior choice in duels unless the shot is AP2)
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

def chooseAndShootWeapons(attacker, defender, combat_round):
    #choose weapon(s)
    weapons = []
    if attacker.name == "Ferrus Manus": #assume this is what Firing Protocols do
        weapons.append(attacker.shooting_weapons[0])
        weapons.append(attacker.shooting_weapons[1])
        weapons.append(attacker.shooting_weapons[2])
    elif attacker.name == "Corvus Corax":
        weapons.append(attacker.shooting_weapons[0])
        weapons.append(attacker.shooting_weapons[1])
    elif attacker.name == "Jaghatai Khan" and len(attacker.shooting_weapons) > 1: #Mounted, assume this is what Firing Protocols do
        weapons.append(attacker.shooting_weapons[0])
        weapons.append(attacker.shooting_weapons[1])
        weapons.append(attacker.shooting_weapons[2])
    else:
        #just use the first one
        weapons.append(attacker.shooting_weapons[0])

    for weapon in weapons:
        shootWeapon(attacker, weapon, defender, combat_round)
        if isDefeated(attacker) or isDefeated(defender): #must check attacker too - e.g. Gets Hot
            return True
    return False

def shootingPhase(active_primarch, reactive_primarch, num_round):
    #check in combat
    if active_primarch.in_combat:
        assert(reactive_primarch.in_combat)
        print("Both primarchs locked in combat")
        return False
    #Evade reaction will not be implemented because it's not stackable with other Shroudeds and every daddy has an equiv or better Invuln
    ended = chooseAndShootWeapons(active_primarch, reactive_primarch, num_round)
    if ended:
        return ended
    if active_primarch.name != "Fulgrim": #Tactical Excellence
        #Fire back reaction
        print("%s is Firing Back!" % reactive_primarch.name)
        ended = chooseAndShootWeapons(reactive_primarch, active_primarch, num_round)
        if ended:
            return ended
    return False

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
    return

def resolveHammerOfWrath(attacker, defender, combat_round):
    #generate "hit" rolls, retrieve the dummy weapon
    numHits = 1
    attacker_weapon = HammerOfWrath()
    for rule in attacker.rules:
        if rule == "Hammer of Wrath(2)": #.____.
            numHits = 2
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
def allocateAttacks(attacker, defender, numAttacks, combat_round):
    assert (numAttacks >= 1)
    attacks = []
    if len(attacker.melee_weapons) == 1:
        attacks.append([attacker, attacker.melee_weapons[0], defender, combat_round, numAttacks])
    else: #should be 2
        assert (len(attacker.melee_weapons) == 2)
        if attacker.name == "Horus Lupercal":
            if (defender.I < 7 and defender.W <= 2):
                #attempt a quick kill
                attacks.append([attacker, attacker.melee_weapons[0], defender, combat_round, numAttacks])
            else:
                #Worldbreaker all the way for Brutal(2)
                attacks.append([attacker, attacker.melee_weapons[1], defender, combat_round, numAttacks])
        elif attacker.name == "Leman Russ":
            #Can Russ still split his attacks...?
            if defender.T <= 6 or defender.name == "Rogal Dorn": #TODO: Proper calculation esp. concerning Brutal
                attacks.append([attacker, attacker.melee_weapons[0], defender, combat_round, numAttacks])
            else:
                #use the Axe
                attacks.append([attacker, attacker.melee_weapons[1], defender, combat_round, numAttacks])
        elif attacker.name == "Sanguinius": #Spear config has more than one weapon
            if defender.psyker:
                #use Moonsilver
                attacks.append([attacker, attacker.melee_weapons[1], defender, combat_round, numAttacks])
            else:
                attacks.append([attacker, attacker.melee_weapons[0], defender, combat_round, numAttacks])
        elif attacker.name == "Roboute Guilliman":
            if (defender.I < 7 and defender.W <= 2) or ("Feel No Pain(4)" in defender.rules):
                #Gladius to 1. attempt a quick kill/draw or 2. overcome a significant FNP (e.g. Curze's psychic power, Horus Ascended) (do some math to see if it's worth it)
                attacks.append([attacker, attacker.melee_weapons[0], defender, combat_round, numAttacks])
            else:
                #HoD for brutal
                attacks.append([attacker, attacker.melee_weapons[1], defender, combat_round, numAttacks])
        elif attacker.name == "Ferrus Manus":
            attacks.append([attacker, attacker.melee_weapons[0], defender, combat_round, numAttacks])
            #then servo arm attacks
            attacks.append([attacker, attacker.melee_weapons[1], defender, combat_round, 1])
    attacker.allocated_attacks = True
    return attacks

def attackAtThisInitiative(primarch, init):
    #reaping blow and duellist's edge has been handled at start of round
    if len(primarch.melee_weapons) == 1 and "Unwieldy" in primarch.melee_weapons[0].rules: #this will skip Horus' Worldbreaker at init 1, which is expected because Horus will have already allocated
        return init == 0
    return primarch.I - 1 == init

def pushAttackIntoInitiativeQueue(initiative_queue,attack,primarch):
    weapon = attack[1]
    if "Unwieldy" in weapon.rules:
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
        if primarch1.charge and primarch1.how:
            resolveHammerOfWrath(primarch1, primarch2, combat_round)
            if isDefeated(primarch1) or isDefeated(primarch2):
                return True
        elif primarch2.charge and primarch2.how:
            resolveHammerOfWrath(primarch2, primarch1, combat_round)
            if isDefeated(primarch1) or isDefeated(primarch2):
                return True

    #initiative represented as an array of 11 arrays. Then, iterate backwards to resolve attacks
    initiative_queue = [[] for i in range(11)]

    #now traverse the initiative queue to resolve attacks
    i = 10 #Need more?
    while i >= 0:
        if attackAtThisInitiative(primarch1, i) and not primarch1.allocated_attacks:
            numattacks1 = primarch1.getAttacks(primarch2, combat_round)
            attacks1 = allocateAttacks(primarch1, primarch2, numattacks1, combat_round) #for ppl with multiple weapons at diff initiative, must decide now
            for attack in attacks1:
                pushAttackIntoInitiativeQueue(initiative_queue,attack,primarch1)
        if attackAtThisInitiative(primarch2, i) and not primarch2.allocated_attacks:
            numattacks2 = primarch2.getAttacks(primarch1, combat_round)
            attacks2 = allocateAttacks(primarch2, primarch1, numattacks2, combat_round)
            for attack in attacks2:
                pushAttackIntoInitiativeQueue(initiative_queue,attack,primarch2)
        attacks = initiative_queue[i]
        for attack in attacks:
            resolveMeleeAttacks(*attack)
        #resolve ALL attacks at the init before checking for dead
        if isDefeated(primarch1) or isDefeated(primarch2):
            return True
        i -= 1

    #nobody croaked?
    #resolve end-of-combat effects (IWND etc)

    primarch1.allocated_attacks = False
    primarch2.allocated_attacks = False

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

def assaultPhase(active_primarch, reactive_primarch, num_round, MODE_CHARGE):
    rules1 = getStartOfAssaultRules(active_primarch)
    for rule in rules1:
        rule[1](active_primarch, reactive_primarch, num_round)
    rules2 = getStartOfAssaultRules(reactive_primarch)
    for rule in rules2:
        rule[1](reactive_primarch, active_primarch, num_round)

    #Charge!
    if MODE_CHARGE:
        print("##Start of charge subphase##")
        if not active_primarch.in_combat: #primarch2 should not be in combat either
            active_primarch.charge = True
            print("%s is charging!" % active_primarch.name)
            if reactive_primarch.name == "Rogal Dorn": #Bulwark of the Imperium
                active_primarch.disordered = True
            if active_primarch.name != "Fulgrim": #Tactical Excellence from doc leak
                #TODO: Decide Charge reactions
                print("%s makes Overwatch!" % reactive_primarch.name)
                ended = chooseAndShootWeapons(reactive_primarch, active_primarch, num_round)
                if ended:
                    return ended
        print("##End of charge subphase##")
    #always assume charge success, so
    active_primarch.in_combat = True
    reactive_primarch.in_combat = True
    print("##Start of fight subphase##")
    ended = fightSubPhase(active_primarch, reactive_primarch, num_round, MODE_CHARGE)
    if ended:
        return ended
    print("#End of fight subphase#")
    #none of these really have an ordering
    
    if MODE_CHARGE:
        active_primarch.charge = False
        active_primarch.disordered = False
        reactive_primarch.charge = False
        reactive_primarch.disordered = False

    rules1 = getEndOfAssaultRules(active_primarch)
    for rule in rules1:
        rule[1](active_primarch, reactive_primarch, num_round)
    rules2 = getEndOfAssaultRules(reactive_primarch)
    for rule in rules2:
        rule[1](reactive_primarch, active_primarch, num_round)

    #Hit and Run
    if MODE_CHARGE:
        if "Hit and Run" in reactive_primarch.rules:
            attemptHitAndRun(reactive_primarch, active_primarch)

    return ended

def playerTurn(active_primarch, reactive_primarch, num_round, MODE_CHARGE):
    active_primarch.handleStartOfTurn()
    reactive_primarch.handleStartOfTurn()
    #movement phase #whatever
    #shooting phase
    if MODE_CHARGE:
        print("###Shooting phase###")
        active_primarch.handleStartOfPhase()
        reactive_primarch.handleStartOfPhase()
        ended = shootingPhase(active_primarch, reactive_primarch, num_round)
        if ended:
            return ended
        print("###End of shooting phase###")
    #assault phase
    print("###Assault phase###")
    active_primarch.handleStartOfPhase()
    reactive_primarch.handleStartOfPhase()
    ended = assaultPhase(active_primarch, reactive_primarch, num_round, MODE_CHARGE)
    if ended:
        return ended
    print("###End of assault phase###")

    #IWND
    IWNDTest(active_primarch)

def resolveGameTurnEnd(primarch1, primarch2):
    return

def duel(primarchA, primarchB, MODE_CHARGE):
    ended = False
    who_goes_first = decideFirstRound()
    if who_goes_first:
        primarchA.active = True
    else:
        primarchB.active = True
    player_turn = 0
    game_turn = 0
    combat_round = 0
    while not ended:
        print("Player Turn %d" % (player_turn + 1))
        #now actually do the turn!
        if primarchA.active:
            ended = playerTurn(primarchA, primarchB, combat_round, MODE_CHARGE)
        else:
            ended = playerTurn(primarchB, primarchA, combat_round, MODE_CHARGE)
        if primarchA.in_combat and primarchB.in_combat:
            combat_round += 1
        else:
            assert(not primarchA.in_combat and not primarchB.in_combat)
            combat_round = 0
        player_turn += 1
        if player_turn % 2 == 0:
            game_turn += 1
            resolveGameTurnEnd(primarchA, primarchB)
        if primarchA.active:
            primarchA.active = False
            primarchB.active = True
        else:
            primarchA.active = True
            primarchB.active = False
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
