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
        #counter, substracts every End-Of-Assault-Phase (including the turn concussing turn)
        self.underConcuss = 0
        self.active = False #not your turn
        self.charge = False
        self.in_combat = False #setup during duel
        self.allocated_attacks = False

    def restoreWS(self):
        self.WS = self.shadow_WS
    def restoreBS(self):
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
    def __init__(self, weapon="Lion Sword"):
        super().__init__("Lion El'Jonson", 8,6,7,6,6,7,7,10,2,4,4,
            [FusilActinaeus()],
            [],
            [   "Legiones Astartes (Dark Angels)", #will always be Deathwing, can't see anything more impactful in duels
                #"Stasis Grenades", //All primarchs are no longer affected by negative modifiers
                "Leonine Panoply",
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
        super().__init__("Perturabo",7,7,6,7,6,5,6,10,2,3,3,
            [LogosArray()],
            [],
            [
                "Firing Protocols(2)"
            ]
        )
        if weapon == "Forgebreaker":
            self.melee_weapons.append(Forgebreaker_Desecrated())
        else:
            self.melee_weapons.append(Logos_Melee())

class Khan(Primarch):
    def __init__(self, mode="Mounted"):
        if mode == "Afoot":
            super().__init__("Jaghatai Khan",7,6,6,6,6,8,7,10,2,4,3, #+1A for pistol
                [StormsVoice()],
              [WhiteTigerDao()],
              [
                  "Hit and Run",
                  "Furious Charge(3)", #assume supposed to be cumulative with the Dao...
                  "Wildfire Panoply",
              ])
        else:
            super().__init__("Jaghatai Khan",7,6,6,7,6,8,7,10,2,4,3, #+1A for pistol
                [StormsVoice(), SojutsuHeavyBolter(), SojutsuHeavyBolter()],
              [WhiteTigerDao()],
              [
                  "Hit and Run",
                  "Furious Charge(1)",
                  "Wildfire Panoply",
                  "Hammer of Wrath(2)", #._________.
                  "Antigrav",
                  "Firing Protocols(3)"
              ]
            )
            self.how = True

class Russ(Primarch):
    def __init__(self):
        super().__init__("Leman Russ",8,6,7,6,6,7,8,10,2,4,4, #+1A for two weaps
            [Scornspitter()],
          [SwordOfBalenight(),AxeOfHelwinter()],
          [
            "Furious Charge(1)", #It's technically Sire of the SW...
            "Armour of Elavagar",
            "Counter-Attack(2)"
            #"Night Vision", "Preternatural Senses",
            #"Weapon Mastery"
          ]
        )

class Dorn(Primarch):
    def __init__(self):
        super().__init__("Rogal Dorn",8,6,6,6,7,6,6,10,2,4,4,
            [VoiceOfTerra()],
          [StormsTeeth()],
          [
            "Legiones Astartes (Imperial Fists)",
            "Auric Armour",
            "Furious Charge(2)",
            "Bulwark of the Imperium",
          ]
        )

class Curze(Primarch):
    def __init__(self):
        super().__init__("Konrad Curze",8,7,6,6,6,7,8,10,2,4,4, #+1A for claws
            [Widowmakers()],
          [MercyAndForgiveness()],
            [
            "Hit and Run",
            "Glimpse of Death", #TODO, no idea how Perils work yet
            ]
        )
        #self.how = True #?

class Sanguinius(Primarch):
    def __init__(self, weapon="Encarmine"):
        super().__init__("Sanguinius",8,6,6,6,6,6,6,10,2,4,4,
            [Infernus(),
             #FragGrenade() #Ignore until Blast is implemented, but Sang of all Primarchs may actually throw Frag. Not really. If Sang gets a shooting it's Infernus and then there's no shooting phase left (Frags can't Overwatch)
             ],
            [],
            [
                "Sire of the Blood Angels",
                "Encarmine Fury",
                "Regalia Resplendent",
            ]
        )
        #self.how = True #?
        if weapon == "Encarmine":
            self.melee_weapons.append(BladeEncarmine())
        else:
            self.melee_weapons.append(SpearOfTelesto())
            self.melee_weapons.append(MoonsilverBlade())

class Ferrus(Primarch):
    def __init__(self):
        super().__init__("Ferrus Manus",7,6,7,7,6,6,6,10,2,3,3,
            [PlasmaBlaster(), GravitonGun(), HeavyFlamer(), GrenadeHarness()], #idk what is a Graviton shredder
            [Forgebreaker_Ferrus(), ServoArm()],
            [
                "Legiones Astartes (Iron Hands)",
                "Feel No Pain(6)" #Is "Sire of the Iron Hands"
            ]
        )
        #this should be done by modifying the constructor of PlasmaBlaster
        self.shooting_weapons[0].rules.append("Master-Crafted")
        self.shooting_weapons[0].mastercrafted_rerolled = False
        self.shooting_weapons[1].rules.append("Master-Crafted")
        self.shooting_weapons[1].mastercrafted_rerolled = False

class Angron(Primarch):
    def __init__(self):
        super().__init__("Angron",8,5,6,6,6,6,6,10,2,4,4, #+1 for Gores but -1 to compensate for the 'turn-0' Butcher's Nails increment
            [SpiteFurnace()],
            [GorefatherAndGorechild()],
            [
                "Legiones Astartes (World Eaters)",
                "Hatred", "Feel No Pain(6)",
                "Furious Charge(2)"
            ]
        )
    
    def handleStartOfTurn(self):
        super().handleStartOfTurn()
        self.A = min(10, self.A+1)
        print("Butcher's Nails: Angron has %d attacks!" % self.A)

class Guilliman(Primarch):
    def __init__(self):
        super().__init__("Roboute Guilliman",7,6,6,6,6,6,7,10,2,4,4, #Two specialist weaps has been added here
            [Arbitrator()],
            [GladiusIncandor(), HandOfDominion()],
            [
                "Armour of Reason",
                #"Preternatural Strategy",
                "Calculating Swordsman"
            ]
        )
        self.invulnreroll = False #Armour of Reason
        self.previous_preter_choice = 3 #0: Fleet, 1: Counter, 2: FC, 3: Stubborn (dummy)
    
    def handleStartOfTurn(self):
        super().handleStartOfTurn()
        if self.active:
            #Preternatural Strategy
            #the no-successive rule is so irritating
            if self.previous_preter_choice == 1:
                self.rules.remove("Counter-Attack(1)")
            elif self.previous_preter_choice == 2:
                self.rules.remove("Furious Charge(1)")
            #what to choose?
            if self.in_combat:
                #nothing matters except for preparing for H&R
                if self.previous_preter_choice == 1:
                    #too bad, can't get Counter again
                    self.previous_preter_choice = 3
                else:
                    self.previous_preter_choice = 1
                    self.rules.append("Counter-Attack(1)")
            else:
                #active and not in combat: Charge!
                if self.previous_preter_choice == 2:
                    #too bad, can't get FC again
                    self.previous_preter_choice = 3
                else:
                    self.previous_preter_choice = 2
                    self.rules.append("Furious Charge(1)")
    
    def handleStartOfPhase(self):
        super().handleStartOfPhase()
        self.invulnreroll = False #refresh

class Mortarion(Primarch):
    def __init__(self):
        super().__init__("Mortarion",7,6,7,7,7,5,6,10,2,4,4,
            [Lantern()], #Seven phosphex bombs...
            [Silence()],
            [
                "Preternatural Resilience",
                "Hatred(Psykers)"
            ]
        )
        #self.rerollIWND = True

class Magnus(Primarch):
    def __init__(self):
        super().__init__("Magnus the Red",7,6,6,6,6,6,6,10,2,4,4,
            [PsyfireSerpenta()],
          [AhnNunurta()],
          [
              #LOL
              #TODO: Cult Arcanas when psychic rules are known
          ]
        )
        self.cover = 5

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
              "Counter-Attack", "Hammer of Wrath",
              "Pythian Scales"
          ]
        )
        #this should be done by modifying the constructor of PlasmaBlaster
        self.shooting_weapons[0].rules.append("Master-Crafted")
        self.shooting_weapons[0].mastercrafted_rerolled = False

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
    elif name == "Lion_Blade":
        return Lion("Wolf Blade")
    elif name == "Fulgrim_Laer":
        return Fulgrim("Blade of the Laer")
    elif name == "Perturabo_Fists":
        return Perturabo("Fists")
    elif name == "Khan_Afoot":
        return Khan("Afoot")
    elif name == "Sanguinius_Spear":
        return Sanguinius("Spear of Telesto")
    elif name == "Corax_PostIsstvan":
        return Corax("Post-Isstvan")
    return None #what

primarch_names = ["Lion", "Fulgrim", "Perturabo", "Khan",
                  "Russ", "Dorn", "Curze", "Sanguinius",
                  "Ferrus", "Angron", "Guilliman", "Mortarion",
                  "Magnus", "Horus", "Lorgar", "Vulkan",
                  "Corax", "Alpharius",
                  "Lion_Blade", "Fulgrim_Laer", "Perturabo_Fists", "Khan_Afoot", "Sanguinius_Spear", "Corax_PostIsstvan"
                  ]