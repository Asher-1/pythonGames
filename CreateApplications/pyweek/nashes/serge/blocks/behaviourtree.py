"""Implementation of behaviour trees for AI"""

import inspect
import logging
import serge.common


class Tree(serge.common.Loggable):
    """A behaviour tree implementation"""

    def __init__(self):
        """Initialise the tree"""
        self.addLogger()
        self.nodes = []

    def addNode(self, node):
        """Add a node"""
        self.nodes.append(node)
        return node

    def addNodes(self, nodes):
        """Add nodes"""
        for node in nodes:
            self.addNode(node)

    def numberOfNodes(self):
        """Return the number of nodes"""
        return len(self.nodes)

    def onTick(self, context):
        """Tick the tree"""
        for node in self.nodes:
            node.onTick(context)


class Node(serge.common.Loggable):
    """A node in the tree"""

    # Status
    S_NONE = 'none'
    S_SUCCESS = 'success'
    S_FAILURE = 'failure'
    S_RUNNING = 'running'
    S_EXCEPTION = 'exception'

    def __init__(self, name):
        """Initialise the node"""
        self.addLogger()
        self.name = name
        self.status = self.S_NONE

    def onTick(self, context):
        """Tick the node"""
        self.log.debug('Ticking %s' % self.getNiceName())
        if self.status == self.S_NONE:
            self.onStart()

    def onStart(self):
        """Do node initialisation"""
        self.status = self.S_SUCCESS

    def resetNode(self):
        """Reset the node to its initial state"""
        self.status = self.S_NONE

    def getNiceName(self):
        """Nice name for debugging etc"""
        return '%s (%s - %d)' % (self.name, self.__class__.__name__, id(self))


class Condition(Node):
    """A condition node that checks for something"""

    def __init__(self, name, fn):
        """Initialise the condition"""
        super(Condition, self).__init__(name)
        #
        self.fn = fn
        self.exception = None

    def onTick(self, context):
        """Tick the node"""
        super(Condition, self).onTick(context)
        #
        try:
            result = self.fn(context)
        except Exception, err:
            self.log.error('%s returned exception: %s' % (self.getNiceName(), err))
            self.status = self.S_EXCEPTION
            self.exception = err
        else:
            self.log.debug('%s returns "%s"' % (self.getNiceName(), result))
            if result:
                self.status = self.S_SUCCESS
            else:
                self.status = self.S_FAILURE


class Action(Node):
    """An action node - performs an action that could take many ticks"""

    def __init__(self, name):
        """Initialise the action"""
        super(Action, self).__init__(name)
        #
        self.iterator = None

    def onStart(self):
        """Initialise the action"""
        self.iterator = None

    def onTick(self, context):
        """Tick the node"""
        super(Action, self).onTick(context)
        #
        if self.iterator is None:
            self.iterator = self.doAction(context)
        #
        # If not an iterator then this is a one-off call
        if not inspect.isgeneratorfunction(self.doAction):
            self.status = self.S_SUCCESS
            return
        #
        try:
            self.status = self.iterator.next()
        except StopIteration:
            self.status = self.S_SUCCESS

    def doAction(self, context):
        """Perform the action - should be a generator"""
        raise NotImplementedError('The specific action (%s) has not implemented doAction' % self)


class IterationNode(Node):
    """A base class of nodes that iterate over their children"""

    # The state we end up in if we finish processing children
    pass_through_state = Node.S_NONE

    def __init__(self, name, nodes):
        """Initialise the sequence"""
        super(IterationNode, self).__init__(name)
        #
        self.nodes = nodes

    def resetNode(self):
        """Reset the node"""
        super(IterationNode, self).resetNode()
        for node in self.nodes:
            node.resetNode()


class SeriesIteration(IterationNode):
    """Process children in series"""

    def __init__(self, name, nodes):
        """Initialise the sequence"""
        super(SeriesIteration, self).__init__(name, nodes)
        #
        self.current_index = 0

    def onStart(self):
        """Initialise the node"""
        super(SeriesIteration, self).onStart()
        self.current_index = 0

    def onTick(self, context):
        """Tick the sequence"""
        super(SeriesIteration, self).onTick(context)
        #
        while True:
            #
            # Are we done?
            if self.current_index >= len(self.nodes):
                self.status = self.pass_through_state
                break
            #
            # Process the child nodes
            if not self.processChildNodes(context):
                break
        self.log.debug('%s resulted in "%s"' % (self.getNiceName(), self.status))

    def processChildNodes(self, context):
        """Process the children - return True if we should keep processing"""


class Sequence(SeriesIteration):
    """A sequence node - child nodes are processed in sequence until all succeed or one fails"""

    pass_through_state = Node.S_SUCCESS

    def processChildNodes(self, context):
        """Process the children - return True if we should keep processing"""
        self.nodes[self.current_index].onTick(context)
        #
        # If the node succeeded then we need to do the next node
        result = self.nodes[self.current_index].status
        if result == self.S_SUCCESS:
            self.current_index += 1
            return True
        else:
            self.status = result
            return False


class Selector(SeriesIteration):
    """A selector node - child nodes are processed in sequence until one succeeds"""

    pass_through_state = Node.S_FAILURE

    def processChildNodes(self, context):
        """Process the children - return True if we should keep processing"""
        self.nodes[self.current_index].onTick(context)
        #
        result = self.nodes[self.current_index].status
        if result == self.S_SUCCESS:
            #
            # If the node succeeded then we should stop
            self.status = self.S_SUCCESS
            return False
        elif result == self.S_RUNNING:
            #
            # If the node is running then we are - and we stop processing
            self.status = self.S_RUNNING
            return False
        else:
            #
            # Node failed - keep processing children
            self.current_index += 1
            return True


class Parallel(IterationNode):
    """A parallel node - child nodes are processed each iteration

    The resulting state comes from the highest priority from
    failure, running, success.

    """

    node_priorities = {
        Node.S_NONE: 0,
        Node.S_FAILURE: 1,
        Node.S_RUNNING: 2,
        Node.S_SUCCESS: 3,
    }

    pass_through_state = Node.S_FAILURE

    def onTick(self, context):
        """Tick the node"""
        super(Parallel, self).onTick(context)
        #
        result = self.pass_through_state
        #
        # Process all the children
        for node in self.nodes:
            node.onTick(context)
            this_result = node.status
            #
            # Get the highest priority result
            if self.node_priorities[this_result] > self.node_priorities[result]:
                result = this_result
        #
        self.status = result


class Decorator(Node):
    """A decorator - calls a child and does something"""

    def __init__(self, name, node):
        """Initialise the decorator"""
        super(Decorator, self).__init__(name)
        #
        self.node = node

    def onTick(self, context):
        """Tick the node"""
        super(Decorator, self).onTick(context)
        #
        self.node.onTick(context)
        self.postProcessNode(context)

    def postProcessNode(self, context):
        """Post process the node"""
        self.status = self.node.status

    def resetNode(self):
        """Reset the node"""
        super(Decorator, self).resetNode()
        self.node.resetNode()


class Loop(Decorator):
    """A looping node - loops its child as long as it returns success"""

    def postProcessNode(self, context):
        """Post process - if the node is finished then reset it and continue running"""
        if self.node.status == self.S_SUCCESS:
            self.node.resetNode()
            self.status = self.S_RUNNING
        else:
            self.status = self.node.status


class AlwaysSucceed(Decorator):
    """A decorator node that always results in success"""

    def postProcessNode(self, context):
        """Post process result"""
        super(AlwaysSucceed, self).postProcessNode(context)
        if self.node.status in (self.S_FAILURE, self.S_SUCCESS):
            self.status = self.S_SUCCESS


class AlwaysFail(Decorator):
    """A decorator node that always results in failure"""

    def postProcessNode(self, context):
        """Post process result"""
        super(AlwaysFail, self).postProcessNode(context)
        if self.node.status in (self.S_FAILURE, self.S_SUCCESS):
            self.status = self.S_FAILURE