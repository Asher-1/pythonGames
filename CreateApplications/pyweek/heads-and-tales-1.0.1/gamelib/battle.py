import pyglet
from pyglet.gl import *

from gamelib import app
from gamelib import interface
from gamelib import sound
import battlepanel
import team
import menu
import world
from vector import v

import random

from collections import defaultdict
from constants import *
from monsterparts import *
import genesis

def make_random_team():
    return team.Team(map(lambda n: genesis.make_random_monster(), xrange(3)))

class Gauge(interface.Panel):
    level = interface.Attribute(1.0)
    color = interface.Attribute((1.0, 0.0, 0.0, 1.0))
    def draw_content(self):
        cwidth, cheight = self.content_size
        right = self.level * cwidth
        vdata = [0, 0, right, 0, right, cheight, 0, cheight]
        cdata = 4 * [int(255 * c) for c in self.color]
        pyglet.graphics.draw(4, GL_QUADS, ('v2f', vdata), ('c4B', cdata))
        #x, y = self.frame_offset
        #x -= self.scroll_xoffset
        #y -= self.scroll_yoffset
        #w, h = self.frame_size
        #c = [c/3.0 for c in self.color[:3]] + [1.0]
        #glLineWidth(2.0)
        #pyglet.graphics.draw(4, GL_LINE_LOOP, ('v2f', (x, y, x + w, y, x + w,
        #    y + h, x, y + h)), ('c4f', c * 4))

class InfoPanel(interface.Grid):
    team = interface.Attribute(None)
    def init_panel(self):
        self.grid_width = 3
        self.spacing = 0.01
        self.column_widths = (0.2, 0.1, 0.1)

        self._mapping = {}
        for m in self.team:
            self._mapping[m] = (
                self.add(interface.Text,
                    font_size = 0.025,
                    halign = 'left',
                    align = 'left',
                    ),
                self.add(Gauge,
                    height = 0.025,
                    width = 0.1,
                    valign = 0.6,
                    color = (1, 0, 0, 1),
                    frame_color = (.5, 0, 0, 1),
                    frame_width = 0.005,
                    ),
                self.add(Gauge,
                    height = 0.025,
                    width = 0.1,
                    valign = 0.6,
                    color = (0, 1, 0, 1),
                    frame_color = (0, .5, 0, 1),
                    frame_width = 0.005,
                    ),
                )

class BattleScene(object):

    def __init__(self, friendly_team=None, enemy_team=None, reward=None):

        self.friendly_team = friendly_team
        self.enemy_team = enemy_team
        self.reward = reward

        if friendly_team is None:
            self.friendly_team = app.game().team
        if enemy_team is None:
            self.enemy_team = make_random_team()
        self.allmons = list(self.friendly_team) + list(self.enemy_team)

        # play it safe
        for m in self.friendly_team:
            m.friendly = True
            m.refresh()
        for m in self.enemy_team:
            m.friendly = False
            m.refresh()

        self.hp_disp = dict([(m, m.get_total_max_damage()) for m in self.allmons])
        self.full_hp = dict(self.hp_disp)

        self.times = dict([(m, random.randrange(1, DELAY_MAX)) for m in self.allmons])
        self.full_times = dict((m, DELAY_MAX) for m in self.allmons)

        self.message = ''
        self.message_queue = []
        for m in self.allmons:
            m.push_handlers(self)

        app.interface.add(interface.Panel,
            background_texture = pyglet.resource.texture('misc/labtile.png'),
            background_tiles = 8,
            )

        horiz = app.interface.add(interface.Horizontal,
            spacing=0.05,
            )

        leftvert = horiz.add(interface.Vertical,
            spacing = 0.05,
            valign = 'top',
            )

        rightvert = horiz.add(interface.Vertical,
            spacing = 0.05,
            valign = 'top',
            )

        self.leftpanel = leftvert.add(battlepanel.BattlePanel,
            width = 0.45,
            height = 0.6,
            team = self.friendly_team,
            frame_texture = pyglet.resource.texture('misc/labcorner.png'),
            frame_width = 0.1,
            scissor = True,
            )

        self.rightpanel = rightvert.add(battlepanel.BattlePanel,
            width = 0.45,
            height = 0.6,
            team=self.enemy_team,
            frame_texture = pyglet.resource.texture('misc/labcorner.png'),
            frame_width = 0.1,
            scissor = True,
            )

        self.leftinfo = leftvert.add(InfoPanel,
            team = self.friendly_team,
            )

        self.rightinfo = rightvert.add(InfoPanel,
            team = self.enemy_team,
            )

        self.messagearea = app.interface.add(interface.Text,
            font_size = 0.04,
            valign = 'bottom',
            )

        self.message_fade = app.interface.add(interface.Color,
                color = (0.0, 0.0, 0.0, 0.0),
                width = 1.0,
                height = 0.0,
                valign = "bottom",
                halign = "left",
                )
        self.message_display = app.interface.add(interface.Text,
                text = u'',
                font_size = 0.08,
                anchor_x = "right",
                halign = "left",
                valign = 'top',
                width = 1.0,
                color = (1.0, 1.0, 1.0, 1.0),
                )
        self.overlay = app.interface.add(interface.Panel,
            padding = 0.1,
            background_color = (0, 0, 0, .6),
            )
        self.overlay.add(interface.Text,
            font_size = 0.08,
            text = ESCAPE_TEXT,
            )
        self.overlay.visible = False

        self.menu = None
        self.menu_choice = None
        self.highlight_actor = None

        self.script = self.battle_script()
        self.script.next()

    def draw(self):
        pass

    @property
    def activemons(self):
        return filter(lambda m: not m.disabled, self.allmons)

    def on_key_press(self, sym, mods):
        from pyglet.window import key
        if self.overlay.visible and sym != key.ESCAPE:
            self.overlay.visible = False
        elif sym == pyglet.window.key.ESCAPE:
            if self.overlay.visible:
                from gamelib import menu
                app.control.switch(menu.MenuScene)
            else:
                self.overlay.visible = True
        elif DEBUG and sym == pyglet.window.key.W: # this is pretty sketchy, don't press at wrong time
            for m in self.enemy_team.active:
                m.disable()
        elif self.leftpanel.camera_queue or self.rightpanel.camera_queue:
            return
        elif self.menu:
            return
        elif self.message != '':
            self.message = ''
            self.message_ticks = BATTLE_MESSAGE_SPEED + 1
            self.message_timeout = 5
            self.script.next()
        else:
            return False
        return True

    def on_defeated(self, monster):
        self.message_queue.append("%s was defeated!" % monster.name)

    def on_part_disabled(self, part):
        # feel free to remove if disabled parts are shown graphically instead
        if not part.ancestor.disabled:
            self.message_queue.append("%s's %s was disabled!" % (part.ancestor.name, part.fullname))

    def on_receive_damage(self, part, amt):
        self.message_queue.append("%s was wounded!" % part.ancestor.name)

    def on_miss(self, user, ability, target):
        self.message_queue.append("%s missed!" % user.name)
        sound.miss()
        
    def on_temp_stat(self, target, stat, delta, duration):
        if delta < 0:
            self.message_queue.append("%s lost %s!" % (target.name, stat))
        else:
            self.message_queue.append("%s gained %s!" % (target.name, stat))

    def on_use_ability(self, user, ability, target):
        # user is the monster (=monster torso), ability is the singleton
        # ability object from AbilityMeta.classes
        # target is the specific part being targeted, but if you want the
        # monster being attacked you can use target.ancestor
        part = ability.attack_part(user)
        if user.friendly:
            self.leftpanel.show_attack(user, part)
        else:
            self.rightpanel.show_attack(user, part)
            
    message_ticks = BATTLE_MESSAGE_SPEED + 1
    def tick(self):
        if self.overlay.visible: return
        # these are ticked first so that can correctly report whether their
        # current shot is ambient or purposeful
        self.leftpanel.tick()
        self.rightpanel.tick()
        hp = dict([(m, m.get_total_max_damage() - m.get_total_damage()) for m in self.allmons])
        t = ''

        for m in self.friendly_team:
            name, _hp, atb = self.leftinfo._mapping[m]
            name.text = m.name
            name.color = (1, 1, 1, 1)
            _hp.level = float(self.hp_disp[m]) / self.full_hp[m]
            atb.level = 1.0 - float(self.times[m]) / self.full_times[m]
        if self.highlight_actor:
            idx = list(self.friendly_team).index(self.highlight_actor)
            self.leftinfo._mapping[self.friendly_team[idx]][0].color = (1, 1, 0, 1)
        for m in self.enemy_team:
            name, _hp, atb = self.rightinfo._mapping[m]
            name.text = m.name
            _hp.level = float(self.hp_disp[m]) / self.full_hp[m]
            atb.level = 1.0 - float(self.times[m]) / self.full_times[m]

        #for m in self.allmons:
        #    if m.disabled and self.hp_disp[m] == 0:
        #        t += "%s: defeated\n" % m.name
        #    else:
        #        t += "%s: %i HP (ATB=%i)\n" % (m.name, self.hp_disp[m], self.times[m])
        #self.leftinfo.text = '%s%s' % (t, self.message)
        self.message_ticks += 1
        self.message_timeout = max(0, self.message_timeout - 1)
        if self.message_timeout > 0:
            self.message_display.text = self.message
        else:
            self.message_display.text = u''
        f = lambda t: max(0, min(1, 1-(32*(t-.5)**5+.5)))
        self.message_display.xoffset = f(float(self.message_ticks) / BATTLE_MESSAGE_SPEED) * (app.interface.content_size[0] + self.message_display.content_size[0])
        f = lambda t: max(0, min(1, 1-64*(t-0.5)**6))
        self.message_fade.height = self.message_display.content_size[1] / app.interface.content_size[1]
        self.message_fade.yoffset = self.message_display.content_offset[1]
        self.message_fade.color = [0, 0, 0, .8*f(float(self.message_ticks) / BATTLE_MESSAGE_SPEED)]
        if self.menu or self.message_timeout or not self.leftpanel.camera.ambient or not self.rightpanel.camera.ambient:
            pass
        else:
            waiting = False
            for m in self.allmons:
                if self.hp_disp[m] > hp[m]:
                    self.hp_disp[m] = max(self.hp_disp[m] - HP_GAUGE_SPEED, hp[m])
                    waiting = True
                elif self.hp_disp[m] < hp[m]:
                    self.hp_disp[m] = min(self.hp_disp[m] + HP_GAUGE_SPEED, hp[m])
                    waiting = True
            if not waiting:
                self.script.next()

        
    def display_text(self, text):
        self.message = text
        self.message_timeout = BATTLE_MESSAGE_SPEED
        self.message_ticks = 0

    def update_counters(self):
        pass # done automatically in tick()

    def update_times(self):
        maxspeed = max(m.stats['speed'] + BASE_SPEED for m in self.activemons)
        for m in self.activemons:
            self.times[m] -= max(1, 30 * (m.stats['speed'] + BASE_SPEED) / maxspeed)
            self.times[m] = max(0, self.times[m])

    def battle_script(self):
        yield self.display_text("fight!")
        for m in self.allmons:
            m.begin_fight()
        while True:
            actor = None
            for m in self.activemons:
                if self.times[m] <= 0:
                    actor = m
            if actor is None:
                yield self.update_times()
                continue
            actor.begin_turn()
            
            # select ability
            if actor.friendly:
                opts = [('use ' + a.name.upper() + '!', (self.menu_choose, a)) for a in actor.abilities()]
                self.highlight_actor = actor
                yield self.display_menu(opts)
                a = self.menu_choice
            else:
                a = random.choice(actor.abilities())


            if actor.friendly:
                opts = [('attack ' + m.name.upper(), (self.menu_choose, m)) for m in self.enemy_team.active]
                self.highlight_actor = actor
                yield self.display_menu(opts)
                victim = self.menu_choice
            else:
                victim = random.choice(self.friendly_team.active)

            if a.precise:
                if actor.friendly:
                    opts = [('attack ' + p.fullname.upper(), (self.menu_choose, p)) for p in victim.active_parts()]
                    self.highlight_actor = actor
                    yield self.display_menu(opts)
                    target = self.menu_choice
                else:
                    target = random.choice(victim.active_parts())
                yield self.display_text("%s uses %s on %s!" % (actor.name.upper(), a.name.upper(), target.fullname))
                actor.use_ability(a, target)
                # dealing damage also dispatches one or more events
            else:
                yield self.display_text("%s uses %s!" % (actor.name.upper(), a.name.upper()))
                actor.use_ability(a, victim)
            yield self.update_counters()

            while len(self.message_queue) > 0:
                yield self.display_text(self.message_queue.pop(0))

            self.times[actor] = a.time_cost * BATTLE_ATB_SPEED
            self.full_times[actor] = a.time_cost * BATTLE_ATB_SPEED

            if self.friendly_team.defeated:
                yield self.display_text("Defeat ...")
                for m in self.allmons:
                    m.end_fight()
                app.control.switch(menu.MenuScene)

            if self.enemy_team.defeated:
                #app.music.stop(fadeout=1.0)
                #sound.victory()
                yield self.display_text("Victory!")
                self.loot_enemies()
                while len(self.message_queue) > 0:
                    yield self.display_text(self.message_queue.pop(0))
                for m in self.allmons:
                    m.end_fight()
                self.win_battle()
                
    def display_menu(self, opts):
        self.menu = app.interface.add(interface.TextMenu,
                halign = 0.4,
                valign = 0.2,
                padding = 0.02,
                background_color = (.2, .2, .2, 1),
                frame_color = (0, 0, 0, 1),
                frame_width = 0.01,
                item_options = dict(
                    font_size = 0.03,
                    align = 'left',
                    halign = 'left',
                ),
            )

        for o in opts:
            self.menu.add(interface.TextMenuItem, text=o[0], callback=o[1])

    def close_menu(self):
        self.menu.destroy()
        self.menu = None

    def menu_choose(self, choice):
        self.menu_choice = choice
        self.highlight_actor = None
        self.close_menu()
        
    def loot_enemies(self):
        loot = defaultdict(lambda: 0)
        if self.reward is not None:
            for p in self.reward:
                loot[p] += 1
        else:
            for m in self.enemy_team:
                for p in m.all_parts():
                    if random.random() < p.loot_chance:
                        loot[p.__class__] += 1
        for c, n in loot.items():
            text = "Gained %s%s!" % (c.fullname, (' x %i' % n) if n > 1 else '')
            self.message_queue.append(text)
            app.game().inventory[c] += n

    def win_battle(self):
        app.control.switch(world.WorldScene)

    def start(self):
        app.music.play_track(BATTLE_MUSIC, fadeout=0.5, looping=True)
