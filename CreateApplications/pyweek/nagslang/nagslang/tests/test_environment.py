from unittest import TestCase

from nagslang import environment


class YesCondition(environment.ProtagonistCondition):
    def check(self, protagonist):
        return True


class NoCondition(environment.ProtagonistCondition):
    def check(self, protagonist):
        return False


class ErrorCondition(environment.ProtagonistCondition):
    def check(self, protagonist):
        raise Exception()


class FakeProtagonist(object):
    def __init__(self, wolf=False, human=False, item=False):
        self._wolf = wolf
        self._human = human
        self._item = item

    def in_wolf_form(self):
        return self._wolf

    def in_human_form(self):
        return self._human

    def has_item(self, item):
        return self._item


class TestConditions(TestCase):
    def assert_met(self, condition, protagonist=None):
        self.assertTrue(condition.check(protagonist))

    def assert_not_met(self, condition, protagonist=None):
        self.assertFalse(condition.check(protagonist))

    def assert_error(self, condition, protagonist=None):
        self.assertRaises(Exception, condition.check, protagonist)

    def test_test_conditions(self):
        self.assert_met(YesCondition())
        self.assert_not_met(NoCondition())
        self.assert_error(ErrorCondition())

    def test_all_conditions(self):
        yes = YesCondition()
        no = NoCondition()
        err = ErrorCondition()
        self.assert_met(environment.AllConditions(yes, yes))
        self.assert_not_met(environment.AllConditions(yes, no))
        self.assert_not_met(environment.AllConditions(no, err))
        self.assert_error(environment.AllConditions(err, yes))
        self.assert_error(environment.AllConditions(yes, err))

    def test_any_condition(self):
        yes = YesCondition()
        no = NoCondition()
        err = ErrorCondition()
        self.assert_met(environment.AnyCondition(no, yes))
        self.assert_not_met(environment.AnyCondition(no, no))
        self.assert_met(environment.AnyCondition(yes, err))
        self.assert_error(environment.AnyCondition(err, yes))
        self.assert_error(environment.AnyCondition(no, err))

    def test_wolf_form_condition(self):
        wolf = environment.WolfFormCondition()
        self.assert_met(wolf, FakeProtagonist(wolf=True, human=True))
        self.assert_met(wolf, FakeProtagonist(wolf=True, human=False))
        self.assert_not_met(wolf, FakeProtagonist(wolf=False, human=True))
        self.assert_not_met(wolf, FakeProtagonist(wolf=False, human=False))

    def test_human_form_condition(self):
        human = environment.HumanFormCondition()
        self.assert_met(human, FakeProtagonist(human=True, wolf=True))
        self.assert_met(human, FakeProtagonist(human=True, wolf=False))
        self.assert_not_met(human, FakeProtagonist(human=False, wolf=True))
        self.assert_not_met(human, FakeProtagonist(human=False, wolf=False))

    def test_item_required_condition(self):
        item = environment.ItemRequiredCondition('item')
        self.assert_met(item, FakeProtagonist(item=True))
        self.assert_not_met(item, FakeProtagonist(item=False))

    def test_function_condition(self):
        condition = environment.FunctionCondition(lambda p: p.startswith('x'))
        self.assert_met(condition, 'xxx')
        self.assert_not_met(condition, 'yyy')


class TestActions(TestCase):
    def setUp(self):
        self.state = {}

    def make_action_func(self, name):
        self.state.setdefault(name, [])

        def action_func(protagonist, target):
            self.state[name].append((protagonist, target))
            return len(self.state[name])

        return action_func

    def make_action(self, name, condition=None):
        return environment.Action(self.make_action_func(name), condition)

    def assert_state(self, **kw):
        self.assertEqual(self.state, kw)

    def assert_action_selected(self, action, interactible, protagonist):
        self.assertEqual(action, interactible.select_action(protagonist))

    def test_unconditional_action(self):
        action = self.make_action('action')
        self.assert_state(action=[])
        self.assertTrue(action.check(None))
        self.assert_state(action=[])
        self.assertEqual(1, action.perform('p', 't'))
        self.assert_state(action=[('p', 't')])
        self.assertEqual(2, action.perform('p2', 't2'))
        self.assert_state(action=[('p', 't'), ('p2', 't2')])

    def test_conditional_action(self):
        yes_action = self.make_action('yes_action', YesCondition())
        no_action = self.make_action('no_action', NoCondition())
        self.assert_state(yes_action=[], no_action=[])
        self.assertTrue(yes_action.check(None))
        self.assert_state(yes_action=[], no_action=[])
        self.assertFalse(no_action.check(None))
        self.assert_state(yes_action=[], no_action=[])
        self.assertEqual(1, yes_action.perform('p', 't'))
        self.assert_state(yes_action=[('p', 't')], no_action=[])

    def test_perform_bad_action(self):
        action = self.make_action('action', NoCondition())
        self.assert_state(action=[])
        self.assertFalse(action.check(None))
        self.assert_state(action=[])
        self.assertRaises(ValueError, action.perform, 'p', 't')

    def test_interactible_no_actions(self):
        interactible = environment.Interactible()
        self.assert_action_selected(None, interactible, None)

    def test_interactible_unconditional_action(self):
        action = self.make_action('action')
        interactible = environment.Interactible(action)
        self.assert_action_selected(action, interactible, None)

    def test_interactible_conditional_actions(self):
        wolf_action = self.make_action('wolf', environment.WolfFormCondition())
        item_action = self.make_action(
            'item', environment.ItemRequiredCondition('item'))
        interactible = environment.Interactible(wolf_action, item_action)
        self.assert_action_selected(
            wolf_action, interactible, FakeProtagonist(wolf=True))
        self.assert_action_selected(
            item_action, interactible, FakeProtagonist(item=True))
        self.assert_action_selected(
            wolf_action, interactible, FakeProtagonist(wolf=True, item=True))
