import collections

import pyglet
from pyglet.gl import *

from gamelib import app
from gamelib import interface
from gamelib import vector
from gamelib.constants import *
from vector import v

import gamestate # must do this to set app.game
import game
import battle
import menu
import worldmap

MESSAGE_TIME = 250

class World(interface.Panel):

    world_height = interface.Attribute(1000.0)
    world_pan = interface.Attribute(vector.zero)
    draw_world = interface.Attribute(lambda: None)
    image = interface.Attribute(None)
    target_pan = vector.zero

    def tick(self):
        delta = self.target_pan - self.world_pan
        self.world_pan += delta * 0.1

    def draw_content(self):
        width, height = self.content_size
        scale = height / self.world_height
        self.world_pan = v(self.image.width, self.image.height) / 2
        panx, pany = self.world_pan
        glPushMatrix()
        glTranslatef(width / 2, height / 2, 0.0)
        glScalef(scale, scale, 1.0)
        glTranslatef(-panx, -pany, 0.0)
        self.draw_world()
        glPopMatrix()

    def on_mouse_release(self, x, y, btn, mods):
        width, height = self.content_size
        scale = height / self.world_height
        panx, pany = self.world_pan
        vec = v((x, y))
        vec -= (width/2, height/2)
        vec /= scale
        vec += (panx, pany)
        app.control.scene.click(vec)

# Portrait graphics.

portnames = {
    'Becka' : ('becka', 'Becka'),
    'Becka#facepalm' : ('beckafacepalm', 'Becka'),
    'Heinrich' : ('heinrich', 'Heinrich'),
    'Heinrich#point' : ('heinrichpoint', 'Heinrich'),
    'Heinrich#laugh' : ('heinrichlaugh', 'Heinrich'),
    'Igor' : ('igor', 'Igor'),
    'Igor#fryingpan' : ('igorpan', 'Igor'),
    'Assistant' : ('igor', 'Assistant'),
    'Cat Lady' : ('mcl', 'Cat Lady'),
    'Peasant': ('peasantm', 'Peasant'),
    'Peasants': ('peasants', 'Peasants'),
    'Alchemist': ('scientistm', 'Alchemist'),
    'Engineer': ('scientistf', 'Engineer'),
    'Commodore': ('admiral', 'Commodore'),
    'Shadow': ('shadowyfigure', 'Shadowy Figure'),
    }

def get_left_portrait(name):
    name, rname = portnames.get(name, ('dummy', name))
    try:
        img = pyglet.resource.image('portraits/%s.png' % name)
    except pyglet.resource.ResourceNotFoundException:
        img = pyglet.resource.image('portraits/dummy.png')
    tex = img.get_texture().get_region(1, 1, img.width-2, img.height-2)
    return tex, rname
def get_right_portrait(name):
    name, rname = portnames.get(name, ('dummy', name))
    try:
        img = pyglet.resource.image('portraits/%s.png' % name, flip_x=True)
    except pyglet.resource.ResourceNotFoundException:
        img = pyglet.resource.image('portraits/dummy.png', flip_x=True)
    img.anchor_x = 0
    tex = img.get_texture().get_region(1, 1, img.width-2, img.height-2)
    return tex, rname
## Load portraits as we need them to save on video memory.
#def get_portraits(name):
#    left = pyglet.resource.image('portraits/%s.png' % name)
#    right = pyglet.resource.image('portraits/%s.png' % name, flip_x=True)
#    right.anchor_x = 0
#    return left, right
#portraits = collections.defaultdict(lambda: portraits[None], {
#    'Becka' : get_portraits('becka'),
#    'Heinrich' : get_portraits('heinrich'),
#    'Igor' : get_portraits('igor'),
#    'Assistant' : get_portraits('igor'),
#    'Mad Cat Lady' : get_portraits('mcl'),
#    None : get_portraits('dummy'),
#    })

# Location graphics.

def get_location(name):
    image = pyglet.resource.image('locations/%s.png' % name)
    image.anchor_x = image.width / 2
    image.anchor_y = image.height / 2
    return image

locations = collections.defaultdict(lambda: locations[None], {
    'town' : get_location('town'),
    'lab' : get_location('lab'),
    'dungeon' : get_location('volcano'),
    'secret' : get_location('house'),
    
    # tower
    'workbench': get_location('workbench'),
    'centre': get_location('lab'),
    'igor': get_location('igor_icon'),
    'floor2': get_location('cage'),
    'floor1': get_location('bookshelf'),
    'exit': get_location('door'),
    
    # act 1 map
    'tower': get_location('tower'), 
    'outsidetower': get_location('bigrock'),
    'forest1': get_location('bigtree'),
    'forest2': get_location('bigtree'),
    'forest3': get_location('bigtree'),
    'clearing': get_location('bridge'),
    'act1lab': get_location('sparelab'),
    'field1': get_location('farm'),
    'field2': get_location('farm'),
    'field3': get_location('farm'),
    'village' : get_location('village'),
    'portlab' : get_location('sparelab'),
    'port' : get_location('port'),
    
    # act 2 map
    'prairie': get_location('farm'),
    'prairielab': get_location('sparelab'),
    'hills1': get_location('lake'),
    'hills2': get_location('grove'),
    'hills3': get_location('tree'),
    'outcrop': get_location('house'),
    'outcroplab': get_location('sparelab'),
    'cabin': get_location('nest'),
    'nests1': get_location('nest'),
    'nests2': get_location('nest'),
    'mountain1': get_location('mountain'),
    'mountain2': get_location('mountain'),
    'mountainlab': get_location('sparelab'),
    'volcano': get_location('volcano'),
    
    # act 3 map
    'beach' : get_location('palmtree'),
    'beachlab' : get_location('sparelab'),
    'shore1' : get_location('beach2'),
    'shore2' : get_location('palmtrees'),
    'shore3' : get_location('beach1'),
    'jungle1' : get_location('bush'),
    'jungle2' : get_location('cave'),    
    'junglelab' : get_location('sparelab'),
    'shore4' : get_location('beach4'),
    'shore5' : get_location('beach3'),
    'shore6' : get_location('beach5'),
    'shorelab' : get_location('sparelab'),
    'marina' : get_location('blank'),
    
    # locations only swapped in dynamically
    'dummy_warehouse': get_location('warehouse'),
    'dummy_admiral' : get_location('admiral'),
    'dummy_eviltower' : get_location('eviltower'),
    
    None: get_location('dummy'),
    })

# Player graphics.
fixed_player = pyglet.resource.image('misc/player1.png')
fixed_player.anchor_x = fixed_player.width / 2
fixed_player.anchor_y = fixed_player.height / 2
frame_images = pyglet.resource.image('misc/player1.png'), \
               pyglet.resource.image('misc/player2.png'), \
               pyglet.resource.image('misc/player1.png', flip_x=True), \
               pyglet.resource.image('misc/player2.png', flip_x=True)
for image in frame_images:
    image.anchor_x = image.width / 2
    image.anchor_y = image.height / 2
frame_durations = .1, .1, .1, .1
frames = []
for image, duration in zip(frame_images, frame_durations):
    frames.append(pyglet.image.AnimationFrame(image, duration))
anim_player = pyglet.image.Animation(frames)

class Cutscene(interface.Panel):

    def init_panel(self):

        self.leftportrait = self.add(interface.Image,
            width = 0.4,
            height = 0.8,
            margin = 0.02,
            halign = 'left',
            valign = 'top',
            image = None,
            )

        self.rightportrait = self.add(interface.Image,
            width = 0.4,
            height = 0.8,
            margin = 0.02,
            halign = 'right',
            valign = 'top',
            image = None,
            )

        lower = self.add(interface.Panel,
            width = 1.0,
            height = 0.4,
            margin = 0.02,
            padding = 0.02,
            valign = 'bottom',
            background_color = (0, 0, 0, 1),
            )

        self.dialogue = lower.add(interface.Text,
            halign = 'left',
            valign = 'top',
            padding = 0.08,
            font_size = 0.04,
            align = 'left',
            text = u'',
            )

        self.speaker = lower.add(interface.Text,
            halign = 'left',
            valign = 'top',
            anchor_x = 'left',
            anchor_y = -0.4,
            padding = 0.04,
            font_size = 0.04,
            align = 'left',
            text = u'',
            background_color = (.4, .4, .4, 1),
            )

        self.left_speaker = u''
        self.right_speaker = u''

    def set_dialogue(self, dialogue, speaker=None, side=None):

        if side is not None:
            self.speaker.align = side
            self.speaker.halign = side
            self.speaker.anchor_x = side
            self.dialogue.align = side
            self.dialogue.halign = side
            self.dialogue.anchor_x = side

        if self.speaker.align == 'left':
            self.speaker.text = self.left_speaker
            portrait = self.leftportrait
        elif self.speaker.align == 'right':
            self.speaker.text = self.right_speaker
            portrait = self.rightportrait

        if speaker is not None:
            if self.speaker.align == 'left':
                self.leftportrait.image, self.left_speaker = \
                        get_left_portrait(speaker)
                self.speaker.text = self.left_speaker
            elif self.speaker.align == 'right':
                self.rightportrait.image, self.right_speaker = \
                        get_right_portrait(speaker)
                self.speaker.text = self.right_speaker

        self.speaker.visible = True
        if len(self.speaker.text) == 0:
            self.speaker.visible = False

        self.dialogue.text = dialogue

    def set_portrait(self, name, side):
        if name is not None:
            if side == 'left':
                self.leftportrait.image, self.left_speaker = get_left_portrait(name)
            elif side == 'right':
                self.rightportrait.image, self.right_speaker = get_right_portrait(name)
        else:
            if side == 'left':
                self.left_speaker = u''
                self.leftportrait.image = None
            if side == 'right':
                self.right_speaker = u''
                self.rightportrait.image = None

    def clear(self):
        self.set_dialogue(u'', side='left')
        self.leftportrait.image = None
        self.rightportrait.image = None
        self.left_speaker = u''
        self.right_speaker = u''
        self.visible = False

class WorldScene(object):

    def __init__(self):

        g = app.game()

        self.world = app.interface.add(World,
            draw_world = self.draw_world,
            )

        cutscene_alpha = 0.6
        if g.current_map_name == 'credits': # what a hack!
            cutscene_alpha = 0.0

        self.cutscene = app.interface.add(Cutscene,
            padding = 0.02,
            background_color = (0, 0, 0, cutscene_alpha),
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
                font_size = 0.04,
                anchor_x = "right",
                halign = "left",
                valign = 0.0,
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

        self.cutscene.visible = False

        self.themap = worldmap.Map.load(g.current_map_name)
        self.theimage = pyglet.resource.image('maps/%s.png' % self.themap.realname)
        self.world.image = self.theimage

        imagedata = self.theimage.get_image_data()
        self.clear_color = [c / 255.0 for c in imagedata._current_data[:4]]

        # Paths.
        self.path_vlists = {}
        for key, path in self.themap.paths.items():
            self.path_vlists[key] = self._path_vlist(path)

        # Locations.
        self.location_sprites = []
        self.location_map = {}
        for key, pos in self.themap.locations.items():
            if locations[key] is not None:
                image = locations[key]
                sprite = pyglet.sprite.Sprite(image)
                sprite.scale = LOCATION_SIZE / sprite.image.height
                sprite.x, sprite.y = pos
                self.location_sprites.append(sprite)
                self.location_map[key] = sprite

        # Player.
        self.player_sprite = pyglet.sprite.Sprite(fixed_player)
        self.player_sprite.scale = PLAYER_SIZE / self.player_sprite.height
        self.world.world_pan = self.update_pos()

        # Script.
        self.script = None
        self.script_state = None
        self.script_input = None
        
        app.control.scene = self
        if self.themap.mapscript is not None:
            self.script = self.themap.mapscript(g)

    def changeimage(self, a, b):
        self.location_map[a].image = locations[b]
        s = self.location_map[a]
        s.scale = LOCATION_SIZE / s.image.height

    def advance_script(self):
        if self.script is not None:
            # Check the script state.
            if self.script_state == 'keypress':
                if self.script_input is None:
                    return False
            # Advance the script.
            try:
                result = self.script.send(self.script_input)
                self.script_input = None
            except StopIteration:
                self.script = None
                self.script_state = None
                self.script_input = None
                return False
            # Process the result.
            code, args = result[0], result[1:]
            if code == 'dialogue':
                self.cutscene.visible = True
                self.cutscene.set_dialogue(*args)
                self.script_state = 'keypress'
            elif code == 'setportrait':
                self.cutscene.set_portrait(*args)
            elif code == 'endcutscene':
                self.cutscene.visible = False
                self.cutscene.clear()
                self.script_state = None
            elif code == 'battle':
                app.control.switch(battle.BattleScene, enemy_team=args[0],
                        reward=args[1])
                self.script_state = None
            elif code == 'enterlab':
                app.control.switch(game.GameScene, args[0], args[1])
                self.script_state = None
            elif code == 'changemap':
                app.game().current_map_name = args[0]
                app.game().current_world_node = args[1]
                app.control.switch(WorldScene)
                self.script_state = None
            elif code == 'win':
                app.control.switch(menu.MenuScene)
            elif code == 'help':
                self.set_message(args[0], args[1])
                self.script_state = None
            elif DEBUG:
                print 'unknown script code:', code
            # Script advanced successfully.
            return True

    message_ticks = MESSAGE_TIME + 1
    def update_message(self):
        self.message_ticks += 1
        f = lambda t: max(0, min(1, 1-(32*(t-.5)**5+.5)))
        self.message_display.xoffset = f(float(self.message_ticks) / MESSAGE_TIME) * (app.interface.content_size[0] + self.message_display.content_size[0])
        f = lambda t: max(0, min(1, 1-64*(t-0.5)**6))
        self.message_fade.height = self.message_display.content_size[1] / app.interface.content_size[1]
        self.message_fade.yoffset = self.message_display.content_offset[1]
        self.message_fade.color = [0, 0, 0, .8*f(float(self.message_ticks) / MESSAGE_TIME)]
    def set_message(self, message, delay=None):
        if delay:
            pyglet.clock.schedule_once(lambda dt: self.set_message(message), delay)
        else:
            self.message_display.text = message
            self.message_ticks = 0

    def tick(self):
        self.update_message()
        self.update_pos()
        self.advance_script()
        self.world.tick()

        g = app.game()
        if g.travelling:
            fight = g.travel()
            if g.dest_world_node is None:
                self.start_script()
                self.player_sprite.image = fixed_player
            if fight is not None:
                # time for a fight!
                #app.control.switch(battle.BattleScene)
                pass

    def start_script(self):
        g = app.game()
        self.script = self.themap.scripts[g.current_world_node]
        if self.script is not None:
            self.script = self.script(g)

    def on_key_press(self, symbol, modifiers):
        from pyglet.window import key
        if self.overlay.visible and symbol != key.ESCAPE:
            self.overlay.visible = False
        elif self.script_state == 'keypress' and symbol == key.ENTER:
            self.script_input = True
        elif not app.game().travelling and not self.cutscene.visible and symbol in (key.LEFT, key.RIGHT, key.UP, key.DOWN):
            v = {key.LEFT: -vector.unit_x, key.RIGHT: vector.unit_x,
                    key.UP: vector.unit_y, key.DOWN: -vector.unit_y}[symbol]
            opts = []
            k1 = app.game().current_world_node
            for k2 in self.themap.graph[k1]:
                path = self.themap.paths[k1, k2]
                value = (path[1] - path[0]).normalised().dot(v)
                opts.append((k2, value))
            dest, value = max(opts, key=lambda x: x[1])
            if value*value > 0.0:
                app.game().start_travel(dest, self.themap.distance(app.game().current_world_node, dest))
                self.player_sprite.image = anim_player
        elif symbol == key.ESCAPE:
            if self.overlay.visible:
                from gamelib import menu
                app.control.switch(menu.MenuScene)
            else:
                self.overlay.visible = True
        else:
            return False
        return True

    def on_mouse_release(self, x, y, button, modifiers):
        if self.script_state == 'keypress':
            self.script_input = True
            return True

    def click(self, pos):
        g = app.game()
        if g.travelling: return
        node_idx = self.themap.nearest_node(pos)
        if node_idx in self.themap.graph[g.current_world_node]:
            app.game().start_travel(node_idx, self.themap.distance(app.game().current_world_node, node_idx))
            self.player_sprite.image = anim_player

    def on_close_link(self, mapname, start, end):
        if mapname == self.themap.name:
            self.themap.graph[start].discard(end)
            self.themap.graph[end].discard(start)

    def on_open_link(self, mapname, start, end):
        if mapname == self.themap.name:
            self.themap.graph[start].add(end)
            self.themap.graph[end].add(start)

    def update_pos(self):
        currpos = app.game().current_world_node
        destpos = currpos
        progress = 0.0
        if app.game().travelling:
            destpos = app.game().dest_world_node
            progress = float(app.game().world_map_distance) / app.game().travel_distance
        progress = 3 * progress ** 2 - 2 * progress ** 3
        pos = self.themap.find_pos(currpos, destpos, progress)
        self.world.target_pan = pos
        self.player_sprite.x, self.player_sprite.y = pos
        return pos

    def _path_vlist(self, path):
        segs = zip(path, path[1:])
        remaining = PATH_STEP_LENGTH
        show = False
        points = [path[0]]
        for p1, p2 in segs:
            l = tl = (p2 - p1).length
            while l > remaining:
                l -= remaining
                show = not show
                if show:
                    remaining = PATH_STEP_LENGTH
                else:
                    remaining = PATH_UNSTEP_LENGTH
                t = l / tl
                points.append(p1 * t + p2 * (1-t))
            remaining -= l
        vdata = []
        points = points[2:]
        for idx in xrange(len(points)/2):
            p1 = points[2*idx]
            p2 = points[2*idx+1]
            dir = (p2 - p1).normalised().perpendicular()
            a = p1 + dir * PATH_WIDTH / 2
            b = p1 - dir * PATH_WIDTH / 2
            c = p2 + dir * PATH_WIDTH / 2
            d = p2 - dir * PATH_WIDTH / 2
            vdata.extend(a)
            vdata.extend(c)
            vdata.extend(d)
            vdata.extend(b)
        cdata = [0, 0, 0, 127] * (len(vdata) / 2)
        return pyglet.graphics.vertex_list(len(vdata) / 2, ('v2f', vdata),
                ('c4B', cdata))

    def draw_world(self):
        glClearColor(*self.clear_color)
        glClear(GL_COLOR_BUFFER_BIT)
        glColor4ub(255, 255, 255, 255)
        self.theimage.blit(0, 0)
        # Paths.
        for (k1, k2), path in self.themap.paths.items():
            if k1 < k2 and not app.game().link_closed(self.themap.name, k1, k2):
                self.path_vlists[k1, k2].draw(GL_QUADS)
        # Locations.
        for sprite in self.location_sprites:
            sprite.draw()
        # Avatar.
        self.player_sprite.draw()

    def start(self):
        app.music.play_track(MAP_MUSIC, fadeout=0.5, looping=True)
