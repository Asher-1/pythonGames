class ProtagonistCondition(object):
    """A condition on the protagonist that can be checked.
    """

    def check(self, protagonist):
        """Check if this condition applies.
        """
        raise NotImplementedError()


class YesCondition(ProtagonistCondition):
    """Condition that is always met.
    """
    def check(self, protagonist):
        return True


class AllConditions(ProtagonistCondition):
    """Condition that is met if all provided conditions are met.

    Conditions are evaluated lazily, so the first condition to fail stops
    processing.
    """
    def __init__(self, *conditions):
        self.conditions = conditions

    def check(self, protagonist):
        for condition in self.conditions:
            if not condition.check(protagonist):
                return False
        return True


class AnyCondition(ProtagonistCondition):
    """Condition that is met if any provided condition is met.

    Conditions are evaluated lazily, so the first condition to pass stops
    processing.
    """
    def __init__(self, *conditions):
        self.conditions = conditions

    def check(self, protagonist):
        for condition in self.conditions:
            if condition.check(protagonist):
                return True
        return False


class WolfFormCondition(ProtagonistCondition):
    """Condition that is met if the protagonist is in wolf form.
    """
    def check(self, protagonist):
        return protagonist.in_wolf_form()


class HumanFormCondition(ProtagonistCondition):
    """Condition that is met if the protagonist is in human form.
    """
    def check(self, protagonist):
        return protagonist.in_human_form()


class ItemRequiredCondition(ProtagonistCondition):
    """Condition that is met if the protagonist has the required item.
    """
    def __init__(self, required_item):
        self.required_item = required_item

    def check(self, protagonist):
        return protagonist.has_item(self.required_item)


class FunctionCondition(ProtagonistCondition):
    """Condition that is met if the provided function returns `True`.
    """
    def __init__(self, func):
        self.func = func

    def check(self, protagonist):
        return self.func(protagonist)


class PuzzleStateCondition(ProtagonistCondition):
    """Condition that is met if the provided function returns `True`.
    """
    def __init__(self, puzzler):
        self.puzzler = puzzler

    def check(self, protagonist):
        return self.puzzler.get_state()


class Action(object):
    """Representation of an action that can be performed.

    If the (optional) condition is met, the provided function will be called
    with the protagonist as a parameter. It is assumed that the function
    already knows about the target.
    """
    def __init__(self, func, condition=None):
        self.func = func
        self.condition = condition

    def check(self, protagonist):
        if self.condition is None:
            return True
        return self.condition.check(protagonist)

    def perform(self, protagonist):
        if not self.check(protagonist):
            raise ValueError("Attempt to perform invalid action.")
        return self.func(protagonist)


class Interactible(object):
    """The property of interactibility on a thing.
    """

    def __init__(self, *actions):
        self.actions = actions

    def set_game_object(self, game_object):
        self.game_object = game_object

    def select_action(self, protagonist):
        """Select a possible action given the protagonist's state.
        """
        for action in self.actions:
            if action.check(protagonist):
                return action
        return None
