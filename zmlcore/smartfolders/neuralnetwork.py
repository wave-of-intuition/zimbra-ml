"""
created: 9/8/2017
(c) copyright 2017 Synacor, Inc

This is a neural network that can take both a small number of words from the subject and body, and
a few features of the e-mail, generated by relationships of the contacts and domains in the address block
to the user account as analytics, as well as any other features that may be useful.
"""
from neon.models import Model
from neon.layers import MergeMultistream, LSTM, Affine, RecurrentSum, Tree, BranchNode, SkipNode
from neon.initializers import GlorotUniform
from neon.optimizers import Adam
from neon.transforms import Softmax, Rectlinclip, Explin, Logistic, Tanh


class ClassifierNetwork(Model):
    def __init__(self, overlapping_classes=None, exclusive_classes=None, analytics_input=False,
                 optimizer=Adam()):
        self.overlapping_classes = overlapping_classes

        # we must have some exclusive classes
        if exclusive_classes is None:
            self.exclusive_classes = ['finance', 'promos', 'social', 'forums', 'updates']
        else:
            self.exclusive_classes = exclusive_classes

        init = GlorotUniform()
        activation = Rectlinclip(slope=1.0E-6)
        gate = Logistic()

        if analytics_input:
            # support analytics + content
            input_layers = MergeMultistream([
                # [LSTM(300, init, init_inner=init, activation=activation, gate_activation=gate),
                [LSTM(300, init, init_inner=init, activation=activation, gate_activation=gate),
                 RecurrentSum()],
                [Affine(300, init, activation=activation)]],
                'stack')
        else:
            # content only
            input_layers = [LSTM(300, init, init_inner=init, activation=activation, gate_activation=gate),
                            LSTM(300, init, init_inner=init, activation=activation, gate_activation=gate),
                            RecurrentSum()]

        if self.overlapping_classes is None:
            output_layers = [Affine(len(self.exclusive_classes), init, activation=Softmax())]
        else:
            output_branch = BranchNode(name='overlapping_exclusive')
            output_layers = Tree([[SkipNode(),
                                   output_branch,
                                   Affine(len(self.overlapping_classes), init, activation=Logistic())],
                                  [output_branch,
                                   Affine(len(self.exclusive_classes), init, activation=Softmax())]])
        layers = [input_layers,
                  # this is where both inputs meet, and where we may want to add depth or
                  # additional functionality
                  Affine(300, init, activation=Rectlinclip(slope=1E-06, xcut=10.0)),
                  output_layers]
        super(ClassifierNetwork, self).__init__(layers, optimizer=optimizer)

    def _epoch_fit(self, dataset, callbacks):
        """
        Just insert ourselves to shuffle the dataset each epoch
        :param dataset:
        :param callbacks:
        :return:
        """
        if hasattr(dataset, 'shuffle'):
            dataset.shuffle()

        return super(ClassifierNetwork, self)._epoch_fit(dataset, callbacks)