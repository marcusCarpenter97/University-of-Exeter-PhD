import tensorflow as tf
import tensorflow_addons as tfa
from tensorflow import keras
from tensorflow.keras import layers

def RNNMultiOutput(temporal_input_shape, word_input_shape, recurrent_units, output_size, name, layer, activation):
    """
    Individual weights.
    """
    temporal_inputs = keras.Input(shape=temporal_input_shape, name="time_series_input")
    word_inputs = keras.Input(shape=word_input_shape, name="country_name_input")

    hidden_rnn = layer(recurrent_units, activation=activation, name=f"{name}_encoder")(temporal_inputs)
    hidden_dense = layers.Dense(1, name="country_name")(word_inputs)

    context = layers.concatenate([hidden_rnn, hidden_dense], name="context")

    confirmed_out = layers.Dense(output_size, name="confirmed")(context)
    deceased_out = layers.Dense(output_size, name="deceased")(context)
    recovered_out = layers.Dense(output_size, name="recovered")(context)

    model = keras.Model(inputs=[temporal_inputs, word_inputs], outputs=[confirmed_out, deceased_out, recovered_out], name =
                        f"{name}MultiOutput")

    model.compile(optimizer=tf.keras.optimizers.Adam(), loss=tf.keras.losses.MeanSquaredError(),
                  metrics=[tf.keras.metrics.MeanSquaredError(), tf.keras.metrics.RootMeanSquaredError()])
    return model

def RNNMultiOutput_V2(temporal_input_shape, word_input_shape, recurrent_units, output_size, name, layer, activation):
    """
    Shared weights.
    """
    temporal_inputs = keras.Input(shape=temporal_input_shape, name="time_series_input")
    word_inputs = keras.Input(shape=word_input_shape, name="country_name_input")

    hidden_rnn = layer(recurrent_units, activation=activation, name=f"{name}_encoder")(temporal_inputs)
    hidden_dense = layers.Dense(1, name="country_name")(word_inputs)

    context = layers.concatenate([hidden_rnn, hidden_dense], name="context")
    context = layers.RepeatVector(output_size)(context)

    confirmed_out = layers.TimeDistributed(layers.Dense(1), name="confirmed")(context)
    deceased_out = layers.TimeDistributed(layers.Dense(1), name="deceased")(context)
    recovered_out = layers.TimeDistributed(layers.Dense(1), name="recovered")(context)

    model = keras.Model(inputs=[temporal_inputs, word_inputs], outputs=[confirmed_out, deceased_out, recovered_out], name =
                        f"{name}MultiOutput_V2")

    model.compile(optimizer=tf.keras.optimizers.Adam(), loss=tf.keras.losses.MeanSquaredError(),
                  metrics=[tf.keras.metrics.MeanSquaredError(), tf.keras.metrics.RootMeanSquaredError()])
    return model

def RNNSingleOutput(temporal_input_shape, word_input_shape, recurrent_units, output_size, name, layer, activation):
    temporal_inputs = keras.Input(shape=temporal_input_shape, name="time_series_input")
    word_inputs = keras.Input(shape=word_input_shape, name="country_name_input")

    hidden_rnn = layer(recurrent_units, activation=activation, name=f"{name}_encoder")(temporal_inputs)
    hidden_dense = layers.Dense(1, name="country_name")(word_inputs)

    context = layers.concatenate([hidden_rnn, hidden_dense], name="context")
    context = layers.RepeatVector(output_size)(context)

    output_dense = layers.TimeDistributed(layers.Dense(3))(context)

    model = keras.Model(inputs=[temporal_inputs, word_inputs], outputs=output_dense, name = f"{name}SingleOutput")

    model.compile(optimizer=tf.keras.optimizers.Adam(), loss=tf.keras.losses.MeanSquaredError(),
                  metrics=[tf.keras.metrics.MeanSquaredError(), tf.keras.metrics.RootMeanSquaredError()])
    return model

def RNNSingleOutputQuantile(temporal_input_shape, word_input_shape, recurrent_units, output_size, name, layer, activation):
    """
    One output node for each quantile. Each output node produces all features.
    e.g. 3 quantile and 3 features = 3 outputs (each has 3 features), one for each quantile.
    """
    temporal_inputs = keras.Input(shape=temporal_input_shape, name="time_series_input")
    word_inputs = keras.Input(shape=word_input_shape, name="country_name_input")

    hidden_rnn = layer(recurrent_units, activation=activation, name=f"{name}_encoder")(temporal_inputs)
    hidden_dense = layers.Dense(1, name="country_name")(word_inputs)

    context = layers.concatenate([hidden_rnn, hidden_dense], name="context")
    context = layers.RepeatVector(output_size)(context)

    output_dense_q1 = layers.TimeDistributed(layers.Dense(3))(context)
    output_dense_q2 = layers.TimeDistributed(layers.Dense(3))(context)
    output_dense_q3 = layers.TimeDistributed(layers.Dense(3))(context)

    model = keras.Model(inputs=[temporal_inputs, word_inputs], outputs=[output_dense_q1, output_dense_q2, output_dense_q3], name
                        = f"{name}SingleOutputQuantile")

    model.compile(optimizer=tf.keras.optimizers.Adam(), loss=[tfa.losses.PinballLoss(tau=0.05), tfa.losses.PinballLoss(tau=0.5),
                                                              tfa.losses.PinballLoss(tau=0.95)],
                  metrics=[tf.keras.metrics.MeanSquaredError(), tf.keras.metrics.RootMeanSquaredError(),
                           tfa.losses.PinballLoss(tau=0.05), tfa.losses.PinballLoss(tau=0.5), tfa.losses.PinballLoss(tau=0.95)])
    return model

def RNNMultiOutputQuantile(temporal_input_shape, word_input_shape, recurrent_units, output_size, name, layer, activation):
    """
    Each output node produces the values for a featue at a quantile.
    e.g. 3 quantile and 3 features = 9 outputs.
    """
    temporal_inputs = keras.Input(shape=temporal_input_shape, name="time_series_input")
    word_inputs = keras.Input(shape=word_input_shape, name="country_name_input")

    hidden_rnn = layer(recurrent_units, activation=activation, name=f"{name}_encoder")(temporal_inputs)
    hidden_dense = layers.Dense(1, name="country_name")(word_inputs)

    context = layers.concatenate([hidden_rnn, hidden_dense], name="context")

    confirmed_out_q1 = layers.Dense(output_size, name="confirmed_q1")(context)
    confirmed_out_q2 = layers.Dense(output_size, name="confirmed_q2")(context)
    confirmed_out_q3 = layers.Dense(output_size, name="confirmed_q3")(context)

    deceased_out_q1 = layers.Dense(output_size, name="deceased_q1")(context)
    deceased_out_q2 = layers.Dense(output_size, name="deceased_q2")(context)
    deceased_out_q3 = layers.Dense(output_size, name="deceased_q3")(context)

    recovered_out_q1 = layers.Dense(output_size, name="recovered_q1")(context)
    recovered_out_q2 = layers.Dense(output_size, name="recovered_q2")(context)
    recovered_out_q3 = layers.Dense(output_size, name="recovered_q3")(context)

    model = keras.Model(inputs=[temporal_inputs, word_inputs], outputs=[confirmed_out_q1, confirmed_out_q2, confirmed_out_q3,
                                                                        deceased_out_q1, deceased_out_q2, deceased_out_q3,
                                                                        recovered_out_q1, recovered_out_q2, recovered_out_q3],
                        name = f"{name}MultiOutputQuantile")

    model.compile(optimizer=tf.keras.optimizers.Adam(), loss=[tfa.losses.PinballLoss(tau=0.05), tfa.losses.PinballLoss(tau=0.5),
                                                              tfa.losses.PinballLoss(tau=0.95),
                                                              tfa.losses.PinballLoss(tau=0.05), tfa.losses.PinballLoss(tau=0.5),
                                                              tfa.losses.PinballLoss(tau=0.95),
                                                              tfa.losses.PinballLoss(tau=0.05), tfa.losses.PinballLoss(tau=0.5),
                                                              tfa.losses.PinballLoss(tau=0.95)],
                  metrics=[tf.keras.metrics.MeanSquaredError(), tf.keras.metrics.RootMeanSquaredError(),
                           tfa.losses.PinballLoss(tau=0.05), tfa.losses.PinballLoss(tau=0.5), tfa.losses.PinballLoss(tau=0.95)])
    return model

def LSTMMultiOutput(temporal_input_shape, word_input_shape, recurrent_units, output_size, activation='relu'):
    name = "LSTM"
    layer = layers.LSTM
    return RNNMultiOutput(temporal_input_shape, word_input_shape, recurrent_units, output_size, name, layer, activation)

def LSTMSingleOutput(temporal_input_shape, word_input_shape, recurrent_units, output_size, activation='relu'):
    name = "LSTM"
    layer = layers.LSTM
    return RNNSingleOutput(temporal_input_shape, word_input_shape, recurrent_units, output_size, name, layer, activation)

def LSTMMultiOutput_V2(temporal_input_shape, word_input_shape, recurrent_units, output_size, activation='relu'):
    name = "LSTM"
    layer = layers.LSTM
    return RNNMultiOutput_V2(temporal_input_shape, word_input_shape, recurrent_units, output_size, name, layer, activation)

def LSTMMultiOutputQuantile(temporal_input_shape, word_input_shape, recurrent_units, output_size, activation='relu'):
    name = "LSTM"
    layer = layers.LSTM
    return RNNMultiOutputQuantile(temporal_input_shape, word_input_shape, recurrent_units, output_size, name, layer, activation)

def LSTMSingleOutputQuantile(temporal_input_shape, word_input_shape, recurrent_units, output_size, activation='relu'):
    name = "LSTM"
    layer = layers.LSTM
    return RNNSingleOutputQuantile(temporal_input_shape, word_input_shape, recurrent_units, output_size, name, layer, activation)

def GRUMultiOutput(temporal_input_shape, word_input_shape, recurrent_units, output_size, activation='relu'):
    name = "GRU"
    layer = layers.GRU
    return RNNMultiOutput(temporal_input_shape, word_input_shape, recurrent_units, output_size, name, layer, activation)

def GRUSingleOutput(temporal_input_shape, word_input_shape, recurrent_units, output_size, activation='relu'):
    name = "GRU"
    layer = layers.GRU
    return RNNSingleOutput(temporal_input_shape, word_input_shape, recurrent_units, output_size, name, layer, activation)

def GRUMultiOutput_V2(temporal_input_shape, word_input_shape, recurrent_units, output_size, activation='relu'):
    name = "GRU"
    layer = layers.GRU
    return RNNMultiOutput_V2(temporal_input_shape, word_input_shape, recurrent_units, output_size, name, layer, activation)

def GRUMultiOutputQuantile(temporal_input_shape, word_input_shape, recurrent_units, output_size, activation='relu'):
    name = "GRU"
    layer = layers.GRU
    return RNNMultiOutputQuantile(temporal_input_shape, word_input_shape, recurrent_units, output_size, name, layer, activation)

def GRUSingleOutputQuantile(temporal_input_shape, word_input_shape, recurrent_units, output_size, activation='relu'):
    name = "GRU"
    layer = layers.GRU
    return RNNSingleOutputQuantile(temporal_input_shape, word_input_shape, recurrent_units, output_size, name, layer, activation)
