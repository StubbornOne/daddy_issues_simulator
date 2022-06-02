from calculations import *

#No plan to evolve this past daddy fights, just include +1attack into profile

#HANDS_NONE = 0
#HANDS_SPECIALIST = 1
#HANDS_TWO_HANDED = 2  #it's on paper not mutually exclusive (Laerblade), but effectively is
#HANDS_PAIRED = 3

class Weapon:
    def __init__(self, name, _str, AP, rules):
        self.name = name
        self.str_modifier = _str     #expected: lambda S: X. Stick with this even for shooting
        self.AP = AP                 #expected: int
        self.rules = rules
        if "Master-Crafted" in self.rules:
            self.mastercrafted_rerolled = False
        if "One-Use" in self.rules:
            self.used = False

    def calculateAttackStrength(self, attacker_strength):
        return min(10, self.str_modifier(attacker_strength))

class MeleeWeapon(Weapon):
    def __init__(self, name, _str, AP, rules):
        super().__init__(name, _str, AP, rules)

class ShootingWeapon(Weapon):
    def __init__(self, name, _str, AP, _range, weapontype, shots, rules):
        super().__init__(name, _str, AP, rules)
        self.shooting_range = _range
        self.shots = shots #has to be a string because of Psyfire Serpenta...
        self.weapontype = weapontype

    def getShots(self):
        if "D" in self.shots:
            return roll(int(self.shots[1]))
        else:
            return int(self.shots)

class LionSword(MeleeWeapon):
    def __init__(self):
        super().__init__(
            "Lion Sword",
            lambda s: s,
            1,
            ["Master-Crafted","Fleshbane", "Instant Death"]
        )

class WolfBlade(MeleeWeapon):
    def __init__(self):
        super().__init__(
            "Wolf Blade",
            lambda s: s+2,
            3,
            ["Shred", "Breaching(4)", "Reaping Blow(2)", "Master-Crafted"],
        )

class Fireblade(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Fireblade",
                lambda s: s+1,
                    2,
                    ["Master-Crafted", "Murderous Strike (5+)"],
                    )

class LaerBlade(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Blade of the Laer",
                    lambda s: s,
                    2,
                    ["Rending"]
                    )

class Logos_Melee(MeleeWeapon):
    def __init__(self):
        super().__init__(
            "Logos",
            lambda s: s+1,
            2,
            []
        )

class Forgebreaker_Desecrated(MeleeWeapon):
    def __init__(self):
        super().__init__(
            "Forgebreaker",
            lambda s: 12,
            1,
            ["Unwieldy", "Master-Crafted", "Brutal(2)"]
        )

class WhiteTigerDao(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "White Tiger Dao",
    lambda s: s+1,
    2,
    ["Master-Crafted", "Duellist's Edge(1)", "Murderous Strike(5)", "Furious Charge(2)"] #assume this only applies to the Dao's attacks thus excluding HoW. TODO: Fix it, still affects HoW
    )

class SwordOfBalenight(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Sword of Balenight",
    lambda s: s + 1,
    2,
    ["Master-Crafted", "Shred", "Murderous Strike(4)", "Brutal(2)"]
    )

class AxeOfHelwinter(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Axe of Helwinter",
    lambda s: s+2,
    2,
    ["Master-Crafted"] #Sunder
    )

class StormsTeeth(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Storm's Teeth",
    lambda s: s+2,
    2,
    ["Shred", "Murderous Strike(6)"]
    )

class MercyAndForgiveness(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Mercy & Forgiveness",
    lambda s: s,
    2,
    ["Shred", "Murderous Strike(4)"]
    )

class BladeEncarmine(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Blade Encarmine",
    lambda s: s+1,
    2,
    ["Master-Crafted", "Shred", "Rage(2)", "Murderous Strike(5)"] #No idea what Rage(2) is...
    )

class SpearOfTelesto(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Spear of Telesto",
    lambda s: 10,
    1,
    ["Master-Crafted"]
    )

class MoonsilverBlade(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Moonsilver Blade",
    lambda s: s,
    2,
    ["Master-Crafted", "Moonsilver"]
    )

class Forgebreaker_Ferrus(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Forgebreaker",
                        lambda s: s * 2,
                        1,
                        ["Strikedown", "Concussive"]
                    )

class Fists_Ferrus(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Bare Hands",
                    lambda s: s,
                    2,
                    ["Smash"]
                    )

class ServoArm(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Servo-arm",
    lambda s: 8,
    2,
    ["Unwieldy"]
    )

class GorefatherAndGorechild(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Gorefather & Gorechild",
    lambda s: s + 1,
    2,
    ["Murderous Strike"] #"Armourbane"
    )

class GladiusIncandor(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Gladius Incandor",
    lambda s: s + 1,
    2,
    ["Shred", "Murderous Strike"]
    )

class HandOfDominion(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Hand of Dominion",
    lambda s: 10,
    1,
    ["Concussive", "Unwieldy"]
    )

class Silence(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Silence",
    lambda s: s+1,
    2,
    ["Instant Death", "Reaping Blow"]
    )

class AhnNunurta(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Ahn-Nunurta",
    lambda s: s+2,
    1,
    ["Force"]
    )

class Worldbreaker(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Worldbreaker",
    lambda s: 10,
    2,
    ["Master-Crafted", "Concussive", "Unwieldy"]
    )

class Talon(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Warmaster's Talon",
    lambda s: s,
    2,
    ["Shred", "Disabling Strike"]
    )

class Illuminarum(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Illuminarum",
    lambda s: s+2,
    2,
    ["Master-Crafted", "Concussive", "Smash"]
    )

class Dawnbringer(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Dawnbringer",
    lambda s: 10,
    1,
    ["Concussive", "Instant Death"]
    )

class PanoplyOfTheRavenLord(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Panoply of the Raven Lord",
    lambda s: s,
    1,
    ["Shred"]
    )

class PaleSpear(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Pale Spear",
    lambda s: s,
    1,
    ["Instant Death"]
    )

#####HOW#####

class HammerOfWrath(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Hammer of Wrath",
    lambda s: s,
    7,
    []
    )

class KorvidinePinions(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Korvidine Pinions",
    lambda s: 5,
    3,
    []
    )

class GreatWings(MeleeWeapon):
    def __init__(self):
        super().__init__(
    "Great Wings",
    lambda s: 10,
    2,
    []
    )

###SHOOTAS###

#At present, we're never not going to charge, so this will not be shot during the Shooting Phase
#TODO: add a firedSalvo to prevent charging, then review what happens during Overwatch
#and see if it's worth skipping a charge to shoot and do nothing
class FusilActinaeus(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Fusil Actinaeus",
            lambda s: 7,
            3,
            18,
            "Assault",
            "2",
            ["Twin-linked", "Plasma", "Rending(3)"]
        )

#we assume we'll never throw frag (S3 AP-) and plasma (S4 AP4)
#EDIT: Sanguinius DOES want to have Frag Grenades! ._.
class FragGrenade(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Frag grenade",
            lambda s: 3,
            7, #AP-
            8,
            "Assault",
            "1",
            ["Blast"]
        )

class Firebrand(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Firebrand",
            lambda s: 5,
            5,
            15,
            "Assault",
            "2",
            ["Master-Crafted", "Deflagrate", "Volkite"]
        )

class KrakGrenade(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Krak grenade",
            lambda s: 6,
            4,
            8,
            "Assault",
            "1",
            []
        )

class LogosArray(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Logos Array",
            lambda s: 6,
            3,
            30,
            "Assault",
            "6",
            ["Twin-linked", "Shred", "Shell Shock(1)"]
        )

class StormsVoice(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Storm's Voice",
            lambda s: 6,
            4,
            12,
            "Pistol",
            "2",
            ["Rending(5)", "Master-Crafted"]
        )

class ArchaeotechPistol(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Archaeotech Pistol",
            lambda s: 6,
            3,
            12,
            "Pistol",
            "1",
            ["Master-Crafted"]
            )

class SojutsuHeavyBolter(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Sojutsu Voidbike's Heavy Bolter",
            lambda s: 5,
            4,
            36,
            "Heavy",
            "3",
            ["Master-Crafted"]
            )

class Scornspitter(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Scornspitter",
            lambda s: 4,
            3,
            12,
            "Assault",
            "3",
            ["Rending(6)"]
            )

class PsyfireSerpenta(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Psyfire Serpenta",
            lambda s: 8,
            2,
            15,
            "Assault",
            #shit
            "D3",
            ["Soul Blaze", "Plasma"],
            )

class VoiceOfTerra(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Voice of Terra",
            lambda s: 5,
            3,
            24,
            "Assault",
            "3",
            ["Rending(5)"],
            )

class Widowmakers(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Widowmakers",
            lambda s: 4,
            5,
            12,
            "Assault",
            "3",
            ["Rending(4)"],
            )

class Infernus(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Infernus",
            lambda s: 8,
            1,
            18,
            "Assault",
            "2",
            ["One-Use", "Melta"],
            )

class PlasmaBlaster(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Plasma blaster",
            lambda s: 7,
            2,
            18,
            "Assault",
            "2",
            ["Gets Hot", "Plasma"],
            )

class GravitonGun(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Graviton gun",
            lambda s: s, #placeholder, check Graviton
            4,
            18,
            "Heavy",
            "1",
            ["Haywire","Concussive","Graviton Pulse"]
            )

#this is really crap and I cannot think of when Ferrus would use
class GrenadeHarness(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Grenade harness",
            lambda s: 3,
            7,
            8,
            "Assault",
            "2",
            ["Blast"] #technically it has one use but Ferrus' version doesn't
            )

class HeavyFlamer(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Heavy Flamer",
            lambda s: 5,
            4,
            7, #Template
            "Heavy",
            "1",
            ["Template", "Ignores Cover", "Flamer"]
            )

class SpiteFurnace(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Spite Furnace",
            lambda s: 7,
            2,
            12,
            "Pistol",
            "1",
            ["Master-Crafted", "Gets Hot", "Plasma"]
            )

class Arbitrator(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Arbitrator",
            lambda s: 6,
            3,
            18,
            "Assault",
            "2",
            ["Rending"]
            )

class Lantern(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Lantern",
            lambda s: 8,
            2,
            18,
            "Assault",
            "1",
            [] #Sunder
            )

class PhosphexBomb(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Phosphex bomb",
            lambda s: 5,
            2,
            6, #ok this makes it a hard argument to be used
            "Assault",
            "1",
            ["Poison 3", "Blast"] #Crawling Fire, Lingering Death. Matters because dangerous terrain! Even if run, will Crawl and Linger on Mort
            #ignore One-Shot because Mort has unlimited supply
            )

class TalonGun(ShootingWeapon):
    def __init__(self):
        super().__init__(
        "Talon",
        lambda s: 5,
        3,
        24,
        "Assault",
        "3",
        ["Twin-linked"]
        )

class PrecisionBombardment_Horus(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Precision Bombardment",
            lambda s: 10,
            2,
            255,
            "Ordnance",
            "1",
            ["Twin-linked", "One-Use", "Large Blast"] #Unlike Pert, Horus does not explicitly have "don't count as shooting"
            )

class SalvagedHeavyBolter(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Salvaged Heavy Bolter",
            lambda s: 5,
            4,
            36,
            "Assault",
            "3",
            []
            )

class FurnacesHeart(ShootingWeapon):
    def __init__(self):
        super().__init__(
    "Furnace's Heart",
    lambda s: 6,
    2,
    18,
    "Assault",
    "1",
    ["Rending", "Line of Effect"]
    )

class SoulBlazeAttack(ShootingWeapon):
    def __init__(self):
        super().__init__(
            "Soul Blaze",
            lambda s: 4,
            5,
            255,
            "Whee",
            "D3",
            ["Ignores Cover"],
            )
