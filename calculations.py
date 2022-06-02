import random

def roll(x=6):
    return random.randint(1,x)

#To append effects like Strikedown, Concuss, ID, Disabling Strike
class Die:
    def __init__(self, value):
        self.value = value
        self.effects = []
        self.success = False #to be manually set after comparing thresholds/rules
        self.rerolled = False
        self.evaluated = False

    def reroll(self):
        if not self.rerolled:
            self.value = roll()
            self.rerolled = True
            self.evaluated = False

    def _compareThreshold(self, threshold):
        if 1 < self.value and self.value >= threshold:
            self.success = True
        else:
            self.success = False
        self.evaluated = True

class WoundDie(Die):
    def __init__(self, value, AP):
        super().__init__(value)
        self.AP = AP

SAVE_ARMOUR = 0
SAVE_COVER = 1
SAVE_INVULN = 2

class SaveDie(Die):
    def __init__(self, value, saveType):
        super().__init__(value)
        self.saveType = saveType

    def firstRoll(self):
        if not self.evaluated: #value has been deliberately fixed
            self.value = roll()

def rollDie():
    return Die(roll())

def rollDice(numAtks):
    return [rollDie() for i in range(numAtks)]

def rollWoundDice(numHits, weapon):
    return [WoundDie(roll(),weapon.AP) for i in range(numHits)]

"""
def rollSaveDice(numWounds, saveType):
    return [SaveDie(roll(), saveType) for i in range(numWounds)]
"""

#derp make it a class method
def rerollDie(die):
    if not die.rerolled:
        die.value = roll()
        die.rerolled = True
        die.evaluated = False #realert them to recheck

hitChart = [
    #horizontal: target WS, vertical: attacking WS
    # 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
    [ 4, 6, 6, 6, 6, 6, 6, 6, 6, 6], #1
    [ 2, 4, 5, 6, 6, 6, 6, 6, 6, 6], #2
    [ 2, 3, 4, 5, 5, 6, 6, 6, 6, 6], #3
    [ 2, 2, 3, 4, 5, 5, 5, 6, 6, 6], #4
    [ 2, 2, 3, 3, 4, 5, 5, 5, 5, 6], #5
    [ 2, 2, 2, 3, 3, 4, 5, 5, 5, 5], #6
    [ 2, 2, 2, 3, 3, 3, 4, 5, 5, 5], #7
    [ 2, 2, 2, 2, 3, 3, 3, 4, 5, 5], #8
    [ 2, 2, 2, 2, 3, 3, 3, 3, 4, 5], #9
    [ 2, 2, 2, 2, 2, 3, 3, 3, 3, 4], #10
]

woundChart = [
    #horizontal: Toughness, vertical: strength
    #9 is a safe placeholder because daddy duels don't have anything that adds +3 to wound (yet...)
    # 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
    [ 4, 5, 6, 6, 9, 9, 9, 9, 9, 9], #1
    [ 3, 4, 5, 6, 6, 9, 9, 9, 9, 9], #2
    [ 2, 3, 4, 5, 6, 6, 9, 9, 9, 9], #3
    [ 2, 2, 3, 4, 5, 6, 6, 9, 9, 9], #4
    [ 2, 2, 2, 3, 4, 5, 6, 6, 9, 9], #5
    [ 2, 2, 2, 2, 3, 4, 5, 6, 6, 9], #6
    [ 2, 2, 2, 2, 2, 3, 4, 5, 6, 6], #7
    [ 2, 2, 2, 2, 2, 2, 3, 4, 5, 6], #8
    [ 2, 2, 2, 2, 2, 2, 2, 3, 4, 5], #9
    [ 2, 2, 2, 2, 2, 2, 2, 2, 3, 4], #10
]

#apply modifier/special rules outside
def thresholdToShoot(atkBS):
    return max(2, 7 - atkBS)
    return threshold

def thresholdToHit(atkWS, tgtWS):
    threshold = hitChart[atkWS-1][tgtWS-1]
    return threshold

def thresholdToWound(atkS, tgtT):
    threshold = woundChart[atkS-1][tgtT-1]
    return threshold

def compareThreshold(dice, threshold):
    for die in dice:
        die._compareThreshold(threshold)

def discardFailedRolls(dice):
    return list(filter(lambda die: die.success, dice))

def characteristicTest(threshold):
    if threshold <= 0: #autofail
        return False
    res = roll()
    print("Require %d or less, roll: %d" %(min(5,threshold),res))
    if res == 1: #autopass
        return True
    if res == 6: #autofail
        return False
    return res <= threshold

def decideFirstRound():
    #res = random.randint(1, mv1+mv2)
    #return res <= mv1
    return roll(2) < 2
