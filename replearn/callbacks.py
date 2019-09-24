"""
Custom Keras callbacks for logging and checkpointing.
"""
import numpy as np
import tensorflow as tf
from tensorflow import keras


class AzureLoggingCallback(tf.keras.callbacks.Callback):
    """Logging for Azure ML framework."""
    def __init__(self, run_logger):
        super(AzureLoggingCallback, self).__init__()
        self.run_logger = run_logger

    def on_epoch_end(self, epoch, logs=None):
        self.run_logger.log('train_loss', logs['loss'])


class AccCallback(tf.keras.callbacks.Callback):
    """Measure prediction accuracy: positive examples correctly predicted."""
    def __init__(self, acc_model, acc_data):
        super(AccCallback, self).__init__()
        self.acc_model = acc_model
        self.acc_data = acc_data

    def on_epoch_end(self, epoch, logs=None):
        accs = []
        for x in self.acc_data:
            accs.append(self.acc_model(x).numpy()[np.newaxis, :])
        accs.pop()  # remove stats from last batch, probably partial batch
        print(np.mean(np.concatenate(accs), axis=0))


def build_callbacks(config, run_logger, acc_model, data):
    """Build list of callbacks to monitor training."""
    callbacks = []
    cb = keras.callbacks.ModelCheckpoint(config['ckpt_path'] + '/cp-{epoch:04d}.ckpt',
                                         save_weights_only=True)
    callbacks.append(cb)
    cb = keras.callbacks.TensorBoard(config['tblog_path'],
                                     histogram_freq=1,
                                     update_freq=500)
    callbacks.append(cb)
    cb = AccCallback(acc_model, data)
    callbacks.append(cb)

    if config['azure_ml']:
        cb = AzureLoggingCallback(run_logger)
        callbacks.append(cb)

    return callbacks
