"""The main screen of the application"""

import sys
import random
import pygame
import pgzero.screen
import pgzero.animation
import pgzero.ptext
import pgzero.actor
import pgzero.keyboard
import pgzero.clock
from pgzero.loaders import sounds
from pgzero import music

from game import statemachine
from game import button
from game import group
from game import text
from game import callout
from game import gauge
from game import textentry
from game import healthpanel
from game import rectangle
from game import scrolling
from game import tabbed
import game.clock
from game.settings import SETTINGS as S
import model.water
import model.person
import model.food
import model.conversation


class MainScreen(statemachine.StateMachine):

    """The main screen of the game"""

    initial_state = 'initial'

    def __init__(self, options):
        """Initialise the screen"""
        super(MainScreen, self).__init__()
        #
        self.options = options
        self.buttons_clicked = []
        self.objects = group.Group('group')
        self.out_of_game_objects = group.Group('out-of-game-group')

        #
        self.initialise_screen()
        self.initialise_health_model()
        self.initialise_conversation_model()
        #
        self.started = False

    def initialise_conversation_model(self):
        """Initialise the conversation model"""
        self.conversation = model.conversation.ConversationSystem()
        #
        # Set all as alive
        for name in 'abcde':
            self.conversation.addKnowledge(['{0}-alive'.format(name)])
        #
        # And set the requires
        self.conversation.convertPresentToRequires('{0}-alive')

    def initialise_health_model(self):
        """Initialise the health model"""
        self.water_container = model.water.WaterReserve(S['reserves-water'])
        self.food_container = model.food.FoodReserve(S['reserves-food'])
        #
        self.people = {}
        for person in 'abcde':
            property_name = 'person-{0}-properties'.format(person) if not self.options.alternate else \
                'person-{0}-alt-properties'.format(person)
            self.people[person] = model.person.Person(**S[property_name])

    def initialise_screen(self):
        """Initialise the main screen"""
        self.objects.append(
            pgzero.actor.Actor('screen_background', topleft=(-1, 0))
        )
        self.vessel = gauge.Gauge(
            name='vessel',
            foreground='vessel_front',
            back_colour=S['vessel-back-colour'],
            front_colour=S['vessel-water-colour'],
            size=S['vessel-size'],
            value=20,
            orientation=gauge.Gauge.VERTICAL,
            bar_offset=S['vessel-bar-offset'],
        )
        self.vessel.pos = S['vessel-position']
        self.objects.append(self.vessel)
        #
        # The panels showing the individual people
        self.health_panels = {}
        for idx, name in enumerate('abcde'):
            panel = healthpanel.HealthPanel(name, self)
            panel.pos = (S['panel-initial-x'] + idx * S['panel-dx'], S['panel-initial-y'])
            self.objects.append(panel)
            self.health_panels[name] = panel
        #
        self.tabbed = tabbed.Tabbed()
        self.objects.append(self.tabbed)
        #
        self.clock = game.clock.Clock('clock', self)
        self.clock.pos = S['clock-pos']
        self.objects.append(self.clock)
        self.end_of_day = None
        #
        self.awaiting_conversations = set()
        self.deaths = {}

    def draw(self, surface):
        """Draw the screen"""
        if self.started:
            self.objects.draw(surface)
        self.out_of_game_objects.draw(surface)

    def update(self, dt):
        """Update the screen"""
        self.objects.update(dt)
        #
        super(MainScreen, self).update(dt)
        self.buttons_clicked = []

    def initial(self):
        """The initial state of the game"""
        self.update_panel_displays()
        yield 0
        #
        if self.options.initial_state:
            self.started = True
            self.nextState(getattr(self, self.options.initial_state)())
        else:
            self.nextState(self.start_screen())

    def hide_give_buttons(self):
        """Hide all the give buttons"""
        #
        # Don't show the give buttons
        for panel in self.health_panels.values():
            panel.hide_button()

    def show_give_buttons(self):
        """Show all the give buttons"""
        #
        # Show the give buttons, but only if we have some water
        if self.vessel.value > 0:
            self.log.debug('Showing give buttons with vessel water at {0}'.format(self.water_container.amount))
            for panel in self.health_panels.values():
                panel.show_button()

    def hide_people(self):
        """Hide all the people"""
        for panel in self.health_panels.values():
            panel.hide_person()
            panel.set_drinking_state(healthpanel.S_OFF)

    def show_people(self):
        """Show all the people"""
        for panel in self.health_panels.values():
            panel.show_person()
            panel.clear_wants_to_talk()
            panel.set_drinking_state(healthpanel.S_OFF)
        self.awaiting_conversations.clear()

    def preamble(self):
        """The preamble to the game"""
        yield 1
        #
        self.log.debug('Showing preamble')
        for delay in self.show_callout_sequence('preamble', 'text', 'Foreword'):
            yield delay
        #
        yield 1
        #
        self.log.debug('Showing introduction')
        for delay in self.show_callout_sequence('introduction', 'text', 'Foreword'):
            yield delay
        #
        self.nextState(self.setup())

    def show_callout_sequence(self, state, situation, title):
        """Show a sequence of callouts"""
        #
        c = callout.Callout(
            state,
            'The world was destroyed by a terrorist state',
            'callout_back',
            ['callout_ok'],
            config=S['in-game-callout'],
            auto_remove=False,
            title=title
        )
        c.show()
        self.objects.append(c)
        #
        while True:
            next_item = self.conversation.getAndUseNext(state=state, situation=situation)
            if next_item:
                c.text.set_text(next_item.conversation_text)
                c.dismiss_button = None
                #
                while c.dismiss_button is None:
                    yield 0
            else:
                break
        #
        c.dismiss()

    def setup(self):
        """The setup loop"""
        yield 1
        #
        if not self.options.mute_music:
            music.play('outward_bound_intrenclant')
        #
        for delay in self.show_conversation_sequence('setup', 'main-story'):
            yield delay
        #
        yield 1
        for delay in self.show_callout_sequence('instruction', 'text', 'The Giving'):
            yield delay
        #
        self.nextState(self.water_giving())

    def show_conversation_sequence(self, state, situation):
        """Show a sequence of conversation"""
        self.hide_give_buttons()
        self.hide_people()
        #
        while True:
            next_item = self.conversation.getAndUseNext(state=state, situation=situation)
            if next_item:
                self.ready_to_talk(next_item)
            else:
                break
            #
            # Wait for the conversation to happen
            while next_item in self.awaiting_conversations:
                yield 0
            #
            yield len(next_item.conversation_text) * S['talking-time-per-letter']

    def water_giving(self):
        """Initial giving of water to people"""
        #
        self.clock.start()
        self.show_give_buttons()
        self.show_people()
        in_conversation = False
        last_delay = 0
        #
        while True:
            for button, mouse_button in self.buttons_clicked:
                if button.tag == 'give':
                    for delay in self.give_water_to(button.person):
                        yield delay
            #
            if not self.awaiting_conversations and not self.end_of_day:
                conversation_item = self.conversation.getAndUseNext(state='day-{0}'.format(self.clock.day + 1), situation='main-story')
                ###
                if conversation_item:
                    self.log.debug('Conversation item: {0}'.format(conversation_item))
                    guid = conversation_item.guid
                    other_item = self.conversation.getEntry(guid - 1)
                    self.log.debug('Previous item is {0}'.format(other_item))
                ###
                #
                if conversation_item:
                    in_conversation = True
                    #
                    # Pause so that talk button doesn't immediately appear - visually this confuses the user
                    yield last_delay
                    last_delay = len(conversation_item.conversation_text) * S['talking-time-per-letter']
                    #
                    self.hide_give_buttons()
                    self.ready_to_talk(conversation_item)
                elif in_conversation:
                    yield 1
                    self.show_give_buttons()
                    self.hide_people()
                    in_conversation = False
            #
            # Are we at the drinking
            if self.end_of_day:
                self.awaiting_conversations.clear()
                last_delay = 0
                #
                for delay in self.the_drinking():
                    yield delay
                self.clock.start()
                if self.clock.day == 7:
                    self.nextState(self.mid_point_onwards())
            #
            yield 0

    def mid_point_onwards(self):
        """From the mid point of the game onwards"""
        self.log.info('Starting the second half of the game now')
        #
        # Quick fix to make sure that the clock is running
        if self.options.initial_state == 'mid_point_onwards':
            self.clock.start()
        #
        in_conversation = False
        last_talker = None
        spoken_times = 0
        last_item = None
        #
        while True:
            for button, mouse_button in self.buttons_clicked:
                if button.tag == 'give':
                    for delay in self.give_water_to(button.person):
                        yield delay
            #
            if (not self.awaiting_conversations and spoken_times < 3) and not self.end_of_day:
                conversation_item = self.conversation.getAndUseNext(
                    person=last_talker,
                    state='day-7-onwards',
                    situation='single-commentary'
                )
                self.log.debug('Conversation item is {0}'.format(conversation_item))
                #
                if conversation_item and (last_item is None or conversation_item.order - last_item.order == 1):
                    in_conversation = True
                    self.hide_give_buttons()
                    self.ready_to_talk(conversation_item)
                    last_talker = conversation_item.person
                    last_item = conversation_item
                elif in_conversation:
                    yield 1
                    self.show_give_buttons()
                    self.hide_people()
                    #
                    # The following code ensures that we have two monologues
                    last_item = None
                    last_talker = None
                    spoken_times += 1
                    #
                    in_conversation = False
            #
            # Are we at the drinking
            if self.end_of_day:
                for delay in self.the_drinking():
                    yield delay
                #
                if self.clock.day == 12:
                    self.nextState(self.end_of_game())
                    yield 0
                else:
                    self.clock.start()
                #
                # Reset counter to make sure we have two monologues
                spoken_times = 0
                last_item = None
                last_talker = None
            #
            yield 0

    def handle_special_knowledge(self):
        """Look for special knowledge which causes things to happen"""
        if self.conversation.knowsAbout(['show-health-graph']):
            self.tabbed.tabs[2].image = 'health_graph'
            self.tabbed.change_tab(self.tabbed.buttons[2], None)
            self.conversation.removeKnowledge('show-health-graph')
        #
        if self.conversation.knowsAbout(['show-water-graph']):
            self.tabbed.tabs[3].image = 'water_graph'
            self.tabbed.change_tab(self.tabbed.buttons[3], None)
            self.conversation.removeKnowledge('show-water-graph')
        #
        if self.conversation.knowsAbout(['show-food-graph']):
            self.tabbed.tabs[4].image = 'food_graph'
            self.tabbed.change_tab(self.tabbed.buttons[4], None)
            self.conversation.removeKnowledge('show-food-graph')

    def the_drinking(self):
        """Move to the drinking"""
        self.log.info('The drinking starts')
        self.hide_give_buttons()
        self.show_people()

        #
        state = 'day-{0}'.format(self.end_of_day)
        conversation_item = self.conversation.getNext(situation='drinking', state=state)
        if conversation_item:
            if conversation_item.person == 'x':
                conversation = self.show_callout_sequence(situation='drinking', state=state, title='The Drinking')
            else:
                conversation = self.show_conversation_sequence(situation='drinking', state=state)
            for delay in conversation:
                yield delay
        #
        yield S['drinking-start-delay']
        #
        self.log.info('Performing the drinking')
        for name in sorted(self.people.keys()):
            person = self.people[name]
            if not person.isDead():
                #
                self.log.debug('{0} trying to drink'.format(name))
                conversation_item = None
                #
                try:
                    person.drinkWater()
                except model.person.NoWater:
                    self.log.debug('{0} has no water'.format(name))
                    self.health_panels[name].set_drinking_state(healthpanel.S_NOT_DRINKING)
                    if random.random() < S['drinking-talk-probability']:
                        conversation_item = self.conversation.getAndUseNext(person=name, situation='no-drink-at-drinking')
                    sounds.not_drinking.play()
                else:
                    self.health_panels[name].set_drinking_state(healthpanel.S_DRINKING)
                    if random.random() < S['drinking-talk-probability']:
                        conversation_item = self.conversation.getAndUseNext(person=name, situation='drink-at-drinking')
                    sounds.drink.play()
                #
                person.eatFood()
                person.newDay()
                #
                self.log.info('{0} finished day with health {1} and water {2}'.format(name, person.health, person.water))
                if person.isDead() and not self.health_panels[name].is_dead:
                    self.record_death(name)
                #
                if conversation_item:
                    self.show_conversation(conversation_item)
                self.update_panel_displays()
                #
                yield S['drinking-individual-delay']
                #
                self.health_panels[name].set_drinking_state(healthpanel.S_OFF)
        #
        yield S['drinking-end-delay']
        self.show_give_buttons()
        #
        self.end_of_day = None


    def ready_to_talk(self, conversation_item):
        """We are ready to talk about a conversation item"""
        self.health_panels[conversation_item.person].set_wants_to_talk(conversation_item)
        self.awaiting_conversations.add(conversation_item)
        #
        # Make sure the right people are visible
        for name, panel in self.health_panels.items():
            if name in conversation_item.present:
                panel.show_person()
                panel.set_drinking_state(healthpanel.S_TALKING)
            else:
                panel.hide_person()
                panel.set_drinking_state(healthpanel.S_OFF)

    def show_conversation(self, conversation_item):
        """Show a conversation item"""
        #
        # Handle any special knowledge which might arise
        self.handle_special_knowledge()
        #
        if conversation_item.conversation_text.strip():
            new_item = textentry.TextEntry(
                'person_{0}'.format(conversation_item.person),
                self.markup_text(conversation_item.conversation_text),
                width=S['text-entry-width'],
                fontname='computerfont',
                color=S['vdu-colour'],
            )
            self.tabbed.add_dialog_item(new_item)
            #
        try:
            self.awaiting_conversations.remove(conversation_item)
        except KeyError:
            pass

    def markup_text(self, text):
        """Markup text to replace names"""
        for moniker, name in S['names'].items():
            text = text.replace('${0}'.format(moniker.split('_')[1]), name)
        return text

    def day_to_day(self):
        """The day to day state"""
        while True:
            yield 0

    def update_panel_displays(self):
        """Update all the panel displays"""
        #
        # The individual gauges
        for name in self.people:
            person = self.people[name]
            panel = self.health_panels[name]
            panel.set_health(person.health)
            panel.set_water(person.water)
        #
        # The vessel of water
        self.vessel.new_value = self.water_container.amount

    def on_mouse_up(self, pos, mouse_button):
        """Check for mouse clicks"""
        for item in button.Button.all_buttons:
            if item.collidepoint(pos):
                self.buttons_clicked.append((item, mouse_button))
                item.on_click(mouse_button)

    def on_key_up(self, key):
        """A key was pressed"""
        if key == pgzero.keyboard.keys.G:
            if self.vessel.value == 20:
                pgzero.animation.Animation(self.vessel, value=100, tween='bounce_end')
            else:
                pgzero.animation.Animation(self.vessel, value=20, tween='bounce_end')
        if key == pgzero.keyboard.keys.P:
            for panel in self.health_panels.values():
                panel.set_wants_to_talk()
                pgzero.animation.Animation(panel.water_gauge, value=random.randrange(0, 100), tween='bounce_end')
        if key == pgzero.keyboard.keys.H:
            for panel in self.health_panels.values():
                panel.clear_wants_to_talk()
                pgzero.animation.Animation(panel.health_gauge, value=random.randrange(0, 100), tween='bounce_end')
        elif key == pygame.K_PAGEDOWN:
            self.tabbed.vdu_text.page_down()
        elif key == pygame.K_PAGEUP:
            self.tabbed.vdu_text.page_up()
        elif key == pygame.K_HOME:
            self.tabbed.vdu_text.home()
        elif key == pygame.K_END:
            self.tabbed.vdu_text.end()
        elif key == pygame.K_UP:
            self.tabbed.vdu_text.up()
        elif key == pygame.K_DOWN:
            self.tabbed.vdu_text.down()

    def give_water_to(self, person_name):
        """Give water to a particular person"""
        yield 0
        self.log.info('Giving water to {0}. Amount in vessel is {1}'.format(
            person_name, self.vessel.value))
        #
        sounds.pump_water.play()
        #
        amount = S['reserves-amount-to-give'] if not self.water_container.isEmpty() else 0
        self.water_container.useWater(amount * S['reserves-water-ratio'])
        self.people[person_name].giveWater(amount)
        #
        self.update_panel_displays()
        self.hide_give_buttons()
        #
        yield 1
        #
        self.show_give_buttons()

    def mark_end_of_day(self, day):
        """Mark the end of a day"""
        self.log.info('This is the end of day {0}'.format(day))
        self.end_of_day = day

    def record_death(self, name):
        """Record the death of a person"""
        self.log.info('{0} has died'.format(name))
        self.health_panels[name].set_dead()
        self.conversation.removeKnowledge('{0}-alive'.format(name))
        sounds.death.play()
        #
        self.deaths[name] = self.clock.day

    def end_of_game(self):
        """The game has ended"""
        self.log.info('The game has ended')
        #
        end_callout = callout.FinishCallout(
            'callout',
            'finish_callout',
            ['exit_button'],
            S['end-game-callout'],
            self.deaths,
        )
        end_callout.show()
        #
        self.objects.append(end_callout)
        #
        while True:
            if end_callout.dismiss_button:
                music.fadeout(2)
                yield 2
                break
            yield 0
        #
        sys.exit(0)

    def start_screen(self):
        """The main start screen"""
        overlay = rectangle.Rectangle((0, 0, 0), (S['screen-width'], S['screen-height']))
        self.out_of_game_objects.append(overlay)
        # #
        yield 1
        #
        the = pgzero.actor.Actor('logo_the', pos=(S['screen-width'] / 2, -100 + S['logo-y-offset']))
        self.out_of_game_objects.append(the)
        pgzero.animation.Animation(the,
                                   pos=(S['screen-width'] / 2, S['screen-height'] / 2 - 100 + S['logo-y-offset']),
                                   tween='bounce_end')
        #
        yield 2
        #
        godel = pgzero.actor.Actor('logo_godel', pos=(-100, S['screen-height'] / 2 + S['logo-y-offset']))
        self.out_of_game_objects.append(godel)
        pgzero.animation.Animation(godel,
                                   pos=(S['screen-width'] / 2, S['screen-height'] / 2 + S['logo-y-offset']),
                                   tween='bounce_end')
        #
        yield 2
        #
        sentence = pgzero.actor.Actor('logo_sentence', pos=(S['screen-width'] / 2, S['screen-height'] + 100 + S['logo-y-offset']))
        self.out_of_game_objects.append(sentence)
        pgzero.animation.Animation(sentence,
                                   pos=(S['screen-width'] / 2, S['screen-height'] / 2 + 100 + S['logo-y-offset']),
                                   tween='bounce_end')
        #
        yield 2
        #
        t1 = text.Text('A pyweek 20 entry by Paul Paterson',
                       center=(S['screen-width'] / 2, S['screen-height'] / 2 + 100),
                       fontname='computerfont', color='yellow',
                       )
        #
        t2 = text.Text('This game can only be played once and takes about 12 minutes '
                       'to complete.\n\nChoose wisely!',
                       center=(S['screen-width'] / 2, S['screen-height'] / 2 + 200),
                       fontname='computerfont', color='green',
                       )
        t3 = text.Text('v{0}'.format(S['version']),
                       center=(S['screen-width'] - 50, S['screen-height'] - 40),
                       fontname='computerfont', color='grey', fontsize=12,
                       )

        self.out_of_game_objects.extend([t1, t2, t3])
        #
        start = button.Button('start', 'start_button', center=(S['screen-width'] / 2, S['screen-height'] / 2 + 300))
        self.out_of_game_objects.append(start)
        credits_button = button.Button('credits', 'credits_button', center=(80, S['screen-height'] - 50))
        self.out_of_game_objects.append(credits_button)
        #
        credits_overlay = pgzero.actor.Actor('credits', center=(S['screen-width'] / 2, S['screen-height'] / 2))
        credits_overlay.visible = False
        self.out_of_game_objects.append(credits_overlay)
        #
        while True:
            if self.buttons_clicked:
                if self.buttons_clicked[0][0] == start:
                    break
                if self.buttons_clicked[0][0] == credits_button:
                    credits_overlay.visible = True
                    #
                    for i in range(5):
                        yield 1
                        if self.buttons_clicked:
                            break
                    #
                    credits_overlay.visible = False
            yield 0
#
        #
        self.log.info('Starting up')
        self.started = True
        self.out_of_game_objects.remove(t1)
        self.out_of_game_objects.remove(t2)
        self.out_of_game_objects.remove(t3)
        self.out_of_game_objects.remove(start)
        self.out_of_game_objects.remove(credits_button)
        self.out_of_game_objects.remove(credits_overlay)
        #
        pgzero.animation.Animation(overlay, pos=(S['screen-width'] / 2, -S['screen-height']), tween='accelerate')
        #
        yield 2
        #
        pgzero.animation.Animation(the, pos=(S['screen-width'] / 2, S['screen-height'] + 100), tween='accelerate')
        pgzero.animation.Animation(godel, pos=(S['screen-width'] / 2, S['screen-height'] + 100), tween='accelerate')
        pgzero.animation.Animation(sentence, pos=(S['screen-width'] / 2, S['screen-height'] + 100), tween='accelerate')
        #
        self.nextState(self.preamble())
