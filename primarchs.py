from calculations import *
from weapons import *

#some rules are not recorded: E.g. EW because we only account for ID's anti-FNP effect, Fear-Fearless (negate each other) etc

class Primarch:
    def __init__(self, name, WS, BS, S, T, W, I, A, LD,
                 armour, invuln_shoot, invuln_melee, shooting_weapons, melee_weapons, rules):
        self.name = name
        self.WS = WS
        self.BS = BS
        self.S = S
        self.T = T
        self.W = W
        self.I = I
        self.A = A
        self.LD = LD
        #the shadow is to backup characteristics in the event of temporary changes, e.g. Blind, Concuss
        #shadow should always contain (original + permanent effects)
        #note: preternatural affects shadow_WS to handle Blind, will be reset if H&R using challenge_counter
        self.shadow_WS = WS
        self.shadow_BS = BS
        self.shadow_S = S
        self.shadow_T = T
        self.shadow_W = W #for IWND
        self.shadow_I = I
        self.shadow_A = A
        self.shadow_LD = LD
        self.armour = armour
        self.cover = 7
        self.how = False
        self.rerollIWND = False
        self.invuln_shoot = invuln_shoot
        self.invuln_melee = invuln_melee
        self.shooting_weapons = shooting_weapons
        self.melee_weapons = melee_weapons #melee_weapons have their own rules for those wielding two melee_weapons
        self.rules = rules  #misc combat-relevant rules

        #temporary values
        self.sufferSeverLife = False
        self.sufferSoulBlaze = False
        #self.underStrikedown = False   ##HH rulebbook: Strikedown NO LONGER HALVES INITIATIVE
        self.takeBlindTest = False
        #counter, substracts every End-Of-Assault-Phase (including the turn concussing turn)
        self.underConcuss = 0
        self.underBlind = 0
        self.underStasis = False #no need to be counter because it's easily trackable by game turn
        self.active = False #not your turn
        self.charge = False
        self.in_combat = False #setup during duel
        self.allocated_attacks = False

    def restoreWS(self):
        if not self.underBlind:
            self.WS = self.shadow_WS
    def restoreBS(self):
        if not self.underBlind:
            self.BS = self.shadow_BS
    def restoreS(self):
        self.S = self.shadow_S
    def restoreT(self):
        self.T = self.shadow_T
    def restoreI(self):
        if self.underConcuss <= 0 and not self.underStasis:
            self.I = self.shadow_I
    def restoreA(self):
        self.A = self.shadow_A
    def restoreLD(self):
        self.LD = self.shadow_LD

    def getAttacks(self, defender, combat_round):
        return self.A

    def handleStartOfTurn(self):
        for weapon in self.melee_weapons:
            if "Master-Crafted" in weapon.rules:
                weapon.mastercrafted_rerolled = False

    def handleStartOfPhase(self):
        return

class Lion(Primarch):
    def __init__(self, weapon="Wolf Blade"):
        super().__init__("Lion El'Jonson", 8,5,7,6,6,7,5,10,2,4,4,
            [FusilActinaeus()],
            [],
            [   "Stasis Grenades",
                "Leonine Panoply","An Absolute Focus"
            ]
        )
        if weapon == "Wolf Blade":
            self.melee_weapons.append(WolfBlade())
        else:
            self.melee_weapons.append(LionSword())
        self.invulnreroll = False

    def handleStartOfTurn(self):
        super().handleStartOfTurn()
        self.invulnreroll = False #refresh

    def getAttacks(self, defender, combat_round):
        #Lion's Choler
        if self.W <= 2:
            print("Lion's Choler: Lion at %d wounds, gains 2 attacks" % (self.W))
            return self.A + 2
        if self.W <= 4:
            print("Lion's Choler: Lion at %d wounds, gains 1 attack" % (self.W))
            return self.A + 1
        return self.A

class Fulgrim(Primarch):
    def __init__(self, weapon="Fireblade", childofterra=True):
        super().__init__("Fulgrim", 8,6,6,6,6,8,5,10,2,5,3, #sublime swordsman hardcoded
            [Firebrand(), KrakGrenade()], #krak is 8" so dubious to throw, stick to Firebrand
            [],
            ["Gilded Panoply"]
        )
        if weapon == "Fireblade":
            self.melee_weapons.append(Fireblade())
        else:
            self.melee_weapons.append(LaerBlade())
        if childofterra:
            self.rules.append("Child of Terra")

    def getAttacks(self, defender, combat_round):
        if self.I > defender.I:
            #Sublime Swordsman
            print("Sublime Swordsman: Fulgrim makes an additional %d attacks" % (self.I - defender.I))
            return self.A + (self.I - defender.I)
        return self.A

class Perturabo(Primarch):
    def __init__(self, weapon="Forgebreaker"):
        super().__init__("Perturabo",8,6,7,6,6,5,4,10,2,3,3,
            [Logos(), PrecisionBombardment()],
            [],
            [
                "Furious Charge", #this is only within the enemy deployment zone. But only affects the alt. loadout Fists so whatever
                "IMMUNE_CONCUSS", "IMMUNE_BLIND"
            ]
        )
        if weapon == "Forgebreaker":
            self.melee_weapons.append(Forgebreaker_Perturabo())
        else:
            self.melee_weapons.append(Fists_Perturabo())

#Fun stuff: RAW Khan has no invuln during Movement, Psyker, start-of-game... we'll assume this is a FW rule messup. Doesn't affect current implementation anyway
class Khan(Primarch):
    def __init__(self, mode="Mounted"):
        if mode == "Afoot":
            super().__init__("Jaghatai Khan",7,6,6,6,6,8,7,10,2,5,3, #+1A for pistol
                [ArchaeotechPistol()],
                [WhiteTigerDao()],
                [
                    "Hit and Run",
                    #"Sire of the White Scars", #hardcoded
                    "Wildfire Panoply",
                    #"AUTOPASS_DANGEROUS_TERRAIN",
                ])
        else:
            super().__init__("Jaghatai Khan",7,6,6,7,6,7,7,10,2,5,3,
                [ArchaeotechPistol(), SojutsuHeavyBolter(), SojutsuHeavyBolter()], #there are two heavy bolters, but rules are quite explicit 1-rider = 1-weapon, so no point adding the 2nd bolter
                [WhiteTigerDao()],
                [
                    "Hit and Run",
                    "Sojutsu Voidbike", #"Hammer of Wrath",
                    "Relentless",
                    #"Sire of the White Scars",
                    "Wildfire Panoply",
                    #"AUTOPASS_DANGEROUS_TERRAIN",
                ]
            )
            #Unmatched Rider. Just jink for everything, it'll reset on your turn. It's possible the opponent will H&R and you'll get to Overwatch, but Overwatch was Snap Shot anyway
            self.cover = 3
            self.how = True

class Russ(Primarch):
    def __init__(self):
        super().__init__("Leman Russ",9,6,6,6,6,7,6,10,2,4,4,
            [Scornspitter()],
          [SwordOfBalenight(),AxeOfHelwinter()],
            [
                "Armour of Elavagar",
                "Counter-Attack"
                #"Night Vision", "Preternatural Senses",
                #"Weapon Mastery"
            ]
        )

class Dorn(Primarch):
    def __init__(self):
        super().__init__("Rogal Dorn",8,5,6,6,6,5,4,10,2,4,4,
            [VoiceOfTerra()],
            [StormsTeeth()],
            [
                "Auric Armour",
                "Furious Charge"
                #"Sundering Blow", #unlikely to implement; mathhammer says Sundering is always strictly worse in daddy duels
            ]
        )

class Curze(Primarch):
    def __init__(self):
        super().__init__("Konrad Curze",8,6,6,6,6,7,6,10,2,4,4, #Paired has been added here
            [Widowmakers()],
            [MercyAndForgiveness()],
            [
                #"Night Vision", "Acute Senses",
                #"Sire of the Night Lords", #To impose Night Fighting
                "Hit and Run",
                "Nightmare Mantle",
            ]
        )
        self.cover = 4 #stealth, shrouded
        self.how = True

class Sanguinius(Primarch):
    def __init__(self, weapon="Encarmine"):
        super().__init__("Sanguinius",9,5,6,6,6,7,6,10,2,4,4,
            [Infernus(),
            #FragGrenade() #Ignore until Blast is implemented, but Sang of all Primarchs may actually throw Frag. Not really. If Sang gets a shooting it's Infernus and then there's no shooting phase left (Frags can't Overwatch)
            ],
            [],
            [
                "Sire of the Blood Angels",
                "Great Wings", #"Sky Strike",
                "Regalia Resplendent",
            ]
        )
        self.how = True
        if weapon == "Encarmine":
            self.melee_weapons.append(BladeEncarmine())
        else:
            self.melee_weapons.append(SpearOfTelesto()) #NEVER throw the Spear and use the AP3 Moonsilver blade...

class Ferrus(Primarch):
    def __init__(self, weapon="Forgebreaker"):
        super().__init__("Ferrus Manus",7,6,7,7,6,5,4,10,2,3,3,
            [PlasmaBlaster(), GravitonGun(), GrenadeHarness(), HeavyFlamer()], #RAW technically Ferrus DOESN'T have these and can't overwatch???
            [],
            [
                "Sire of the Iron Hands", "Medusan Carapace", #"Relentless",
            ]
        )
        if weapon == "Forgebreaker":
            self.melee_weapons.append(Forgebreaker_Ferrus())
        else:
            self.melee_weapons.append(Fists_Ferrus())
        self.melee_weapons.append(ServoArm())

class Angron(Primarch):
    def __init__(self):
        super().__init__("Angron",9,5,7,6,5,7,6,10,3,4,4,
            [SpiteFurnace()],
            [GorefatherAndGorechild()],
            [
                "Hatred", "Feel No Pain",
                #"Butcher's Nails",
                "Furious Charge"
            ]
        )

class Guilliman(Primarch):
    def __init__(self):
        super().__init__("Roboute Guilliman",7,6,6,6,6,6,5,10,2,4,4, #Two specialist weaps has been added here
            [Arbitrator()],
            [GladiusIncandor(), HandOfDominion()],
            [
                #"Unyielding Will", "REROLL_DTW",
                "Armour of Reason", "Preternatural Strategy", "IMMUNE_CONCUSS"
            ]
        )
        self.invulnreroll = False #Armour of Reason
        self.challenge_counter = -1

    def handleStartOfPhase(self):
        super().handleStartOfPhase()
        self.invulnreroll = False #refresh

class Mortarion(Primarch):
    def __init__(self):
        super().__init__("Mortarion",7,5,6,7,7,5,5,10,2,4,4,
            [Lantern(), PhosphexBomb()],
          [Silence()],
          [
                #"AUTOPASS_TOUGHNESS", "AUTOPASS_DANGEROUS_TERRAIN",
                "Preternatural Resilience"
          ]
        )
        self.rerollIWND = True

class Magnus(Primarch):
    def __init__(self):
        super().__init__("Magnus the Red",7,5,7,6,6,6,4,10,2,4,4,
            [PsyfireSerpenta()],
          [AhnNunurta()],
          [
                #"Eye of the Crimson King", "Infernal Bargain", "Mind Wrath", "Horned Raiment"
                "Phantasmal Aura"
          ]
        )

class Horus(Primarch):
    def __init__(self):
        super().__init__("Horus Lupercal",8,5,7,6,6,6,6,10,2,3,3, #+1A for two weapons added
        [TalonGun()],
          [Talon(), Worldbreaker()],
          [
                #"Weapon Mastery", just hardcoded based on name. need specific analysis on how to split anyway
                "Serpent's Scales"
          ]
        )
    def getAttacks(self, defender, combat_round):
        if defender.WS <= 4:
            #Sire of the SoH
            extra_attacks = roll(3)
            print("Sire of the Sons of Horus: Opponent WS%d, Horus gains %d attacks" % (defender.WS, extra_attacks))
            return self.A + extra_attacks
        return self.A

class Lorgar(Primarch):
    def __init__(self):
        super().__init__("Lorgar Aurelian",6,6,6,6,5,6,5,10,2,4,4, #+1A for pistol
            [ArchaeotechPistol()],
          [Illuminarum()],
          [
                "Dark Fortune",
                "Armour of the Word"
          ]
        )

class Vulkan(Primarch):
    def __init__(self):
        super().__init__("Vulkan",7,5,7,7,6,5,4,10,2,3,3,
            [FurnacesHeart(), HeavyFlamer()],
          [Dawnbringer()],
          [
                "Draken Scale",
          ]
        )
        #Vulkan's heavy flamer is S6
        self.shooting_weapons[1].str_modifier = lambda s: 6
        self.rerollIWND = True #Blood of Fire

class Corax(Primarch):
    def __init__(self, time=""):
        super().__init__("Corvus Corax",7,6,6,6,6,7,6,10,2,5,5,
            [],
          [PanoplyOfTheRavenLord()],
          [
                "Fighting Style",
                "Sire of the Raven Guard", "Shroud Bombs", #"Shadowed Lord",
                "Hit and Run"
          ]
        )
        if time == "Post-Isstvan":
            self.W = 5
            self.shadow_W = 5
            self.A = 5
            self.shadow_A = 5
            self.armour = 3
            self.shooting_weapons.append(SalvagedHeavyBolter())
        else:
            self.shooting_weapons.append(ArchaeotechPistol())
            self.shooting_weapons.append(ArchaeotechPistol())
            self.how = True
            self.rules.append("Korvidine Pinions")
        
    def getAttacks(self, defender, combat_round):
        if "FIGHTING_STYLE_SCOURGE" in self.rules:
            extra_attacks = roll(3)
            print("Fighting Style (Scourge): Corax gains %d attacks" % extra_attacks)
            return self.A + extra_attacks
        return self.A

class Alpharius(Primarch):
    def __init__(self):
        super().__init__("Alpharius",7,7,6,6,6,6,5,10,2,4,4,
            [PlasmaBlaster()], #ignore assault grenades
          [PaleSpear()],
          [
                "Preferred Enemy",
                "Counter-Attack",
                "Pythian Scales"
          ]
        )
        #this should be done by modifying the constructor of PlasmaBlaster
        self.shooting_weapons[0].rules.append("Master-Crafted")
        self.shooting_weapons[0].mastercrafted_rerolled = False
        self.how = True

class DummyPrimarch(Primarch):
    def __init__(self):
        super().__init__("",0,0,0,0,0,0,0,0,0,0,0,
            [],
          [],
          []
        )

def createPrimarchFromName(name):
    if name == "Lion":
        return Lion()
    elif name == "Fulgrim":
        return Fulgrim()
    elif name == "Perturabo":
        return Perturabo()
    elif name == "Khan":
        return Khan()
    elif name == "Russ":
        return Russ()
    elif name == "Dorn":
        return Dorn()
    elif name == "Curze":
        return Curze()
    elif name == "Sanguinius":
        return Sanguinius()
    elif name == "Ferrus":
        return Ferrus()
    elif name == "Angron":
        return Angron()
    elif name == "Guilliman":
        return Guilliman()
    elif name == "Mortarion":
        return Mortarion()
    elif name == "Magnus":
        return Magnus()
    elif name == "Horus":
        return Horus()
    elif name == "Lorgar":
        return Lorgar()
    elif name == "Vulkan":
        return Vulkan()
    elif name == "Corax":
        return Corax()
    elif name == "Alpharius":
        return Alpharius()
    elif name == "Lion_Sword":
        return Lion("Lion Sword")
    elif name == "Fulgrim_Laer":
        return Fulgrim("Blade of the Laer")
    elif name == "Perturabo_Fists":
        return Perturabo("Fists")
    elif name == "Khan_Afoot":
        return Khan("Afoot")
    elif name == "Sanguinius_Spear":
        return Sanguinius("Spear of Telesto")
    elif name == "Ferrus_Fists":
        return Ferrus("Fists")
    elif name == "Corax_PostIsstvan":
        return Corax("Post-Isstvan")
    return None #what

primarch_names = ["Lion", "Fulgrim", "Perturabo", "Khan",
                  "Russ", "Dorn", "Curze", "Sanguinius",
                  "Ferrus", "Angron", "Guilliman", "Mortarion",
                  "Magnus", "Horus", "Lorgar", "Vulkan",
                  "Corax", "Alpharius",
                  #"Lion_Sword", "Fulgrim_Laer", "Perturabo_Fists", "Khan_Afoot", "Sanguinius_Spear", "Ferrus_Fists", "Corax_PostIsstvan"
                  ]