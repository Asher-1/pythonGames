import collections
import textwrap

class Upgrade(object):

    name = "[Unknown]"
    spell_name = "[Unknown]"
    prereqs = []
    caption = "[Unknown]"
    spell_caption = "[Unknown]"
    text = "[Unknown]"
    spell_text = "[Unknown]"
    image = "red.png"
    category = None
    attribs = {}
    index = collections.defaultdict(list)
    name_index = {None: None}

    def __init__(self,
            name=None,
            prereqs=None,
            caption=None,
            spell_caption=None,
            text=None,
            spell_text=None,
            image=None,
            category=None,
            attribs=None):
        if name:
            self.name = name
            if category == 'spell':
                assert name.startswith('Spell: ')
                self.spell_name = name[7:]
            else:
                self.spell_name = name
        if prereqs:
            self.prereqs = prereqs
        if caption:
            self.caption = caption
            self.spell_caption = caption
        if spell_caption:
            self.spell_caption = spell_caption
        if text:
            text = textwrap.dedent(text)
            text = text.strip().replace('\n', ' ')
            self.text = text
            self.spell_text = text
        if spell_text:
            spell_text = textwrap.dedent(spell_text)
            spell_text = spell_text.strip().replace('\n', ' ')
            self.spell_text = spell_text
        if image:
            self.image = image
        if category:
            self.category = category
            self.index[category].append(self)
        if attribs:
            self.attribs = attribs
        self.index[None].append(self)
        assert self.name not in self.name_index, repr(self)
        self.name_index[self.name] = self

    def __repr__(self):
        return "<Upgrade : %r>" % self.name

s_missile = Upgrade(
        name = "Spell: Ptolemaic Projectile",
        prereqs = [],
        caption = "Fires a single shot.",
        text = """
            Grants access to the Ptolemaic Projectile spell, which fires a
            shot capable of damaging a single enemy.
            """,
        spell_text = """
            The workhorse of combat-minded wizards, this spell Fires a shot
            capable of damaging a single enemy.
            """,
        image = "magicmissle_icon.png",
        category = "spell",
        )

s_shield = Upgrade(
        name = "Spell: Brilliant Shield",
        prereqs = [],
        caption = "Protects you from enemies.",
        text = """
            Grants access to the Brilliant Shield spell.
            """,
        spell_text = """
            Protects you with swirling lights which deflect enemies.
            """,
        category = "spell",
        image = "sheild_icon.png",
        )

run10 = Upgrade(
        name = "Celerity",
        prereqs = [s_missile],
        caption = "10% increased movement speed.",
        text = """
            You can run 10% faster.
            """,
        attribs = {'run_speed': 1.1},
        image = "scroll.png",
        )

run20 = Upgrade(
        name = "Enhanced Celerity",
        prereqs = [run10],
        caption = "20% increased movement speed.",
        text = """
            You can run 20% faster.
            """,
        attribs = {'run_speed': 1.2},
        image = "scroll.png",
        )

s_summon = Upgrade(
        name = "Spell: Faerie Mage",
        prereqs = [s_shield],
        caption = "Summons a tiny faerie.",
        text = """
            Grants access to the Faerie Mage spell, which summons a tiny
            faerie to attack your enemies.
            """,
        spell_text ="""
            Summons a tiny faerie who will float around attacking your
            enemies for a short time.
            """,
        image = "summon_icon.png",
        category = "spell",
        )

shieldt = Upgrade(
        name = "Enduring Shield",
        prereqs = [s_shield, s_summon],
        caption = "Shield lasts longer.",
        text = """
            Increases the duration of Brilliant Shield by 50%.
            """,
        attribs = {'shield_time': 360},
        image = "sheild_icon.png",
        )

ward1 = Upgrade(
        name = "Weird Warding",
        prereqs = [shieldt],
        caption = "Protects you from being stunned by enemies.",
        text = """
            Decreases the time for which you are stunned when you collide with
            an enemy by 25%.
            """,
        attribs = {'stun_time': 30},
        image = "scroll.png",
        )
        
shieldc = Upgrade(
        name = "Triforce Shield",
        prereqs = [s_shield],
        caption = "Three shields rather than two.",
        text = """
            The Brilliant Shield spell creates three swirling lights
            rather than two.
            """,
        attribs = {'shield_count': 3},
        image = "sheild_icon.png",
        )

ward2 = Upgrade(
        name = "Holy Warding",
        prereqs = [ward1, shieldc],
        caption = "Protects you further from being stunned by enemies.",
        text = """
            Decreases the time for which you are stunned when you collide with
            an enemy by 40%.
            """,
        attribs = {'stun_time': 24},
        image = "scroll.png",
        )

missile2 = Upgrade(
        name = "Wrathful Projectiles",
        prereqs = [s_missile],
        caption = "Increases damage.",
        text = """
            Your Ptolemaic Projectile spell deals double damage to enemies.
            """,
        attribs = {'missile_damage': 2},
        image = "magicmissle_icon.png",
        )

steadfast = Upgrade(
        name = "Steadfastness",
        prereqs = [ward1],
        caption = "Decreases knockback.",
        text = """
            Decreases the amount by which you are knocked by when colliding
            with an enemy by 20%.
            """,
        attribs = {'knockback': 20},
        image = "scroll.png",
        )

missile4 = Upgrade(
        name = "Devastating Projectiles",
        prereqs = [missile2, steadfast],
        caption = "Further increases damage.",
        text = """
            Your Ptolemaic Projectile spell deals quadruple damage to enemies.
            """,
        attribs = {'missile_damage': 4},
        image = "magicmissle_icon.png",
        )

s_vortex = Upgrade(
        name = "Spell: Vortex of the Void",
        prereqs = [run10],
        caption = "Sucks enemies in.",
        text = """
            Grants access to the Vortex of the Void spell, which summons
            a vortex which sucks enemies towards it.
            """,
        spell_text = """
            Fires a moving portal to the nether void, which will suck
            all nearby enemies towards it until the portal dissipates.
            """,
        image = "vortex_icon.png",
        category = "spell",
        )

s_arrows = Upgrade(
        name = "Spell: Magic Arrows",
        prereqs = [shieldc],
        caption = "Fire a hail of arrows at enemies.",
        text = """
            Grants access to the Magic Arrows spell, which summons a
            swarm of magical arrows which pass through walls on their way
            to your enemies.
            """,
        spell_text = """
            Summons a swarm of magical arrows which will fly through walls
            towards the point at which the spell was aimed.
            """,
        image = "burst.png",
        category = "spell",
        )

arrows11 = Upgrade(
        name = "Magic Arrow Multiplicity",
        prereqs = [s_arrows],
        caption = "Increases the quantity of arrows to 11.",
        text = """
            Your Magic Arrows spell produces eleven arrows rather than five.
            """,
        attribs = {'num_arrows': 11},
        image = "burst.png",
        )

run30 = Upgrade(
        name = "Greater Celerity",
        prereqs = [run20, s_arrows],
        caption = "30% increased movement speed.",
        text = """
            You can run 30% faster.
            """,
        attribs = {'run_speed': 1.3},
        image = "scroll.png",
        )

s_firebomb = Upgrade(
        name = "Spell: Dante's Firebomb",
        prereqs = [s_arrows, missile4],
        caption = "Throw an explosive projectile.",
        text = """
            Grants access to the Firebomb spell, which enables you to throw
            a firebomb which detonates with a small explosion.
            """,
        spell_text = """
            Throws a firebomb which detonates when it strikes the ground,
            damaging all enemies within the blast radius.
            """,
        image = "firebomb_icon.png",
        category = "spell",
        )

s_repel = Upgrade(
        name = "Spell: Arcane Repulsion",
        prereqs = [ward2, run20],
        caption = "Pushes enemies away",
        text = """
            Grants access to the Arcane Repulsion spell, which pushes away
            all nearby enemies when it is cast.
            """,
        spell_text = """
            When cast, pushes all nearby enemies away from you.
            """,
        image = "repel_icon.png",
        category = "spell",
        )

firebomb1 = Upgrade(
        name = "Enhanced Firebombs",
        prereqs = [s_firebomb],
        caption = "Firebombs have larger explosions.",
        text = """
            Increases the blast radius of your firebombs by 25% and causes
            them to inflict double damage to enemies.
            """,
        attribs = {'firebomb_radius': 250, 'firebomb_damage': 8},
        image = "firebomb_icon.png",    
        )

djump = Upgrade(
        name = "Boots of Hermes",
        prereqs = [run20],
        caption = "Allows double jump.",
        text = """
            The wings on these boots enable you to jump for a second time
            while in the air.
            """,
        attribs = {'max_jumps': 2},
        image = "scroll.png",
        )

tjump = Upgrade(
        name = "Boots of Trismegistus",
        prereqs = [djump, s_vortex],
        caption = "Allows triple jump.",
        text = """
            These divinely- and alchemically-enhanced boots enable you to
            jump for a third time while in the air.
            """,
        attribs = {'max_jumps': 3},
        image = "scroll.png",
        )

dist1 = Upgrade(
        name = "Advanced Start",
        prereqs = [s_summon, missile2],
        caption = "Start at a greater distance.",
        text = """
            Start at a distance of 500m.
            """,
        attribs = {'start_dist': 500},
        image = "scroll.png",
        )
        
dist2 = Upgrade(
        name = "Elite Start",
        prereqs = [dist1, djump],
        caption = "Start at an even greater distance.",
        text = """
            Start at a distance of 1337m.
            """,
        attribs = {'start_dist': 1337},
        image = "scroll.png",
        )

dist3 = Upgrade(
        name = "Olympic Start",
        prereqs = [dist2, run30, s_firebomb],
        caption = "Start at an even greater distance still.",
        text = """
            Start at a distance of 2012m.
            """,
        attribs = {'start_dist': 2012},
        image = "scroll.png",
        )
                
s_teleport = Upgrade(
        name = "Spell: Teleport",
        prereqs = [s_vortex, steadfast],
        caption = "Move short distances in a flash.",
        text = """
            Grants access to the Teleport spell, which enables you to move to
            a new visible location instantaneously.
            """,
        spell_text = """
            Moves you instantaneously to the point on the ground closest to
            your mouse cursor.
            """,
        image = "teleport_icon.png",
        category = "spell",
        )
        
cheaptele = Upgrade(
        name = "Effortless Gateway",
        prereqs = [s_teleport, tjump],
        caption = "Teleporting is cheaper.",
        text = """
            Teleporting only consumes one-third as much energy as before.
            """,
        attribs = {'teleport_cost': 500},
        image = "teleport_icon.png",
        )
        
victory = Upgrade(
        name = "Pactbreaker",
        prereqs = [s_teleport, s_repel, s_firebomb],
        caption = "Allows you to defeat Mephistopheles.",
        text = """
            After travelling 3000m, Mephistopheles ceases to be invulnerable
            and can be damaged by your spells.
            """,
        image = "scroll.png",
        )
