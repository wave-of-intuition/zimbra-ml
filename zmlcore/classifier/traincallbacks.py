"""
created: 9/22/2017
(c) copyright 2017 Synacor, Inc

Callbacks for reporting progress during training
"""
from neon.callbacks.callbacks import Callback
from neon.transforms.cost import Misclassification, LogLoss
from zmlcore.neonfixes.metrics import MultiMetric
import gc


class TrainingProgress(Callback):
    """
    progress callback
    """
    def __init__(self, valid):
        super(TrainingProgress, self).__init__(epoch_freq=1)
        self.valid = valid
        self.exclusive_metric = MultiMetric(Misclassification(), 0)
        self.overlapping_metric = MultiMetric(LogLoss(), 1)

    def on_epoch_end(self, callback_data, model, epoch):
        """
        Called when an epoch is about to end. This is where we shuffle the training data.

        Arguments:
            callback_data (HDF5 dataset): shared data between callbacks
            model (Model): model object
            epoch (int): index of epoch that is ending
        """
        print('Exclusive class misclassification error = {:.03}%'.format(
            model.eval(self.valid, metric=self.exclusive_metric)[0] * 100))
        print('Overlapping class log loss error = {:.05}'.format(
            model.eval(self.valid, metric=self.overlapping_metric)[0]))


class MisclassificationTest(Callback):
    """
    Callback for checking misclassification
    """
    def __init__(self, valid, metric):
        super(MisclassificationTest, self).__init__(epoch_freq=1)
        self.valid = valid
        self.metric = metric

    def on_epoch_end(self, callback_data, model, epoch):
        """
        Called when an epoch is about to end. this runs a validation set through the model and prints results.
        """
        print('Misclassification error = %.1f%%' % (model.eval(self.valid, metric=self.metric) * 100))


class LogLossTest(Callback):
    """
    Callback for checking log loss
    """
    def __init__(self, valid, metric):
        super(LogLossTest, self).__init__(epoch_freq=1)
        self.valid = valid
        self.metric = metric

    def on_epoch_end(self, callback_data, model, epoch):
        """
        Called when an epoch is about to end. this runs a validation set through the model and prints results.
        """
        print('Log loss = %.4f' % model.eval(self.valid, metric=self.metric))


class GCCallback(Callback):
    """
    Callback for triggering GC at epoch end
    """
    def __init__(self):
        super(GCCallback, self).__init__(epoch_freq=1)

    def on_epoch_end(self, callback_data, model, epoch):
        gc.collect()



