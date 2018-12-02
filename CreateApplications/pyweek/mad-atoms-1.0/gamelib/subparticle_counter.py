import cocos


FONT_SIZE = 36
X_DELTA = 220


class SubparticleCounter(cocos.cocosnode.CocosNode):
    def __init__(self, position, n_electrons, n_protons):
        super(SubparticleCounter, self).__init__()
        self.position = position
        self.n_electrons = n_electrons
        self.n_protons = n_protons

        self.protons_label = cocos.text.Label('0+', font_size=FONT_SIZE,
                                              anchor_x='right',
                                              anchor_y='center')
        self.protons_label.position = (X_DELTA, 0)
        self.electron_label = cocos.text.Label('-0', font_size=FONT_SIZE,
                                               anchor_x='left',
                                               anchor_y='center')
        self.electron_label.position = (-X_DELTA, 0)
        self.add(self.protons_label)
        self.add(self.electron_label)
        self.update_labels()

    def update_labels(self):
        self.update_electron_label()
        self.update_proton_label()

    def update_electron_label(self):
        self.electron_label.element.text = '-{0}'.format(self.n_electrons)

    def update_proton_label(self):
        self.protons_label.element.text = '{0}+'.format(self.n_protons)

    def is_enough_for_atom(self):
        return self.n_electrons > 0 and self.n_protons > 0

    def has_electrons(self):
        return self.n_electrons > 0

    def has_protons(self):
        return self.n_protons > 0

    def dec_protons(self):
        self.n_protons -= 1
        self.update_proton_label()

    def inc_protons(self):
        self.n_protons += 1
        self.update_proton_label()

    def dec_electrons(self):
        self.n_electrons -= 1
        self.update_electron_label()

    def inc_electrons(self):
        self.n_electrons += 1
        self.update_electron_label()

    def on_new_atom(self):
        self.n_electrons -= 1
        self.n_protons -= 1
        self.update_labels()
