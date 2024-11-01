import keras
from keras import Model
from keras_tuner.tuners import RandomSearch
from keras_tuner.tuners import BayesianOptimization
from keras_tuner.tuners import GridSearch
from tensorflow.data import Dataset

import constants
from enum_classes import EnumHyperParamsOptimization

# NB:
# Python tensorflow benefits from CUDNN acceleration: if you have an NVIDIA compatible card.
# You must install: https://docs.nvidia.com/deeplearning/cudnn/install-guide/index.html
# And add the path to the library in your PATH (in my case, I've added
# C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\cuda-7.5 10.2\bin
#

def build_model(hp, input_vector_length, output_vector_length):
    """
    Creates a model for a SEARCH algo in which it will choose/try different HYPER params.
    @param hp: some model passed by the higher level SEARCH algo.
    @param input_vector_length: the size 1xN of the input vector (Indicators array)
    @param output_vector_length: the size 1xM of the output vector. Usually equal to 1, 2 or 3 (BUY/SELL/DO NOTHING?)
    @return: next candidate for optimization.
    """
    model = keras.Sequential()
    # Input layer
    model.add(keras.layers.Input(shape=(input_vector_length,)))
    # Determine the number of layers randomly
    num_layers = hp.Int('num_layers', min_value=1, max_value=5, step=1)
    # Add dense layers dynamically
    for i in range(num_layers):
        layer_name = f'layer{i + 1}'
        model.add(keras.layers.Dense(
            #permet de fixer le nombre de neurones
            units=hp.Int(f'units_{layer_name}', min_value=1, max_value=100, step=5),
            #permet de choisir la fonction d'activation
            activation=hp.Choice(f'activation_{layer_name}', values=['relu', 'leaky_relu', 'sigmoid', 'tanh', 'elu', 'selu']),
            #permet de choisir le taux de dropout
            kernel_regularizer=keras.regularizers.l2(hp.Float(f'l2_reg_{layer_name}', min_value=1e-5, max_value=1e-1, sampling='LOG')),
            name=layer_name
        ))
    # Output layer
    model.add(keras.layers.Dense(output_vector_length, activation="softmax", name='output_layer'))
    # Compile the model
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=hp.Float('learning_rate', min_value=1e-4, max_value=1e-2, sampling='LOG')),
        loss=keras.losses.BinaryCrossentropy(),
        metrics=[keras.metrics.BinaryAccuracy()]
    )
    return model

def get_model_prototype(input_vector_length: int, output_vector_length: int,
                        train_dataset: Dataset, test_dataset: Dataset) -> Model:
    """
    This is a prototype model. With optimization of high level parameters using some kind of a SEARCH algo.
     If you are creating your own neural network model, you can base it out of this model.
    @param train_dataset: the dataset with the INPUT and OUTPUT layer and sliced by BATCH_SIZE for training the moodel
    and searching the best model params
    @param test_dataset: the dataset with the INPUT and OUTPUT layer for validation
    @param input_vector_length: the size 1xN of the input vector (Indicators array)
    @param output_vector_length: the size 1xM of the output vector. Usually equal to 1, 2 or 3 (BUY/SELL/DO NOTHING?)
    """

    # Build the model according to the hyperparameters
    if constants.HYPERPARAMETERS_OPTIMIZATION == EnumHyperParamsOptimization.BAYESIAN:
        tuner = BayesianOptimization(
            lambda hp: build_model(hp, input_vector_length, output_vector_length),
            objective='val_accuracy',  # Use 'val_accuracy' for maximizing accuracy
            max_trials=constants.TRIALS,
            directory='opt_dir_bayesian',
            project_name='accuracy_tuning')

    elif constants.HYPERPARAMETERS_OPTIMIZATION == EnumHyperParamsOptimization.GRID:
        tuner = GridSearch(
            lambda hp: build_model(hp, input_vector_length, output_vector_length),
            objective='val_accuracy',  # Use 'val_accuracy' for maximizing accuracy
            directory='opt_dir_grid',
            project_name='accuracy_tuning')

    elif constants.HYPERPARAMETERS_OPTIMIZATION == EnumHyperParamsOptimization.RANDOM:
        tuner = RandomSearch(
            lambda hp: build_model(hp, input_vector_length, output_vector_length),
            objective='val_accuracy',  # Use 'val_accuracy' for maximizing accuracy
            max_trials=constants.TRIALS,
            directory='opt_dir_random',
            project_name='accuracy_tuning')
    else:
        print("This HyperParamsOptimization is not yet implemented.")
        return None

    tuner.search_space_summary()

    # Perform the tuning
    tuner.search(train_dataset, epochs=constants.EPOCHS_COUNT, validation_data=(test_dataset,))

    # Get the best model
    best_model = tuner.get_best_models(num_models=1)[0]
    best_model.summary()

    return best_model


def get_model_prototype_simple(input_vector_length: int, output_vector_length: int) -> Model:
    """
    This is a prototype model. If you are creating your own neural network model, you can base it out of this model.
    It's the simple version of the model. The SEARCH models you see higher in this code represent the same models
    but with additional optimization routines.
    @param input_vector_length: the size 1xN of the input vector (Indicators array)
    @param output_vector_length: the size 1xM of the output vector. Usually equal to 1, 2 or 3 (BUY/SELL/DO NOTHING?)
    @return a tuple with a MODEL containing 4 layers (1 input layer, 2 fully connected layers and an output layer) plus
    a probability model to calculate the final answer for the backtester (is it a higher chance BUY/SELL/ALL/NOTHING).
    """
    model = keras.Sequential(
        [
            # Input layer: 1xN
            keras.layers.Input(shape=(input_vector_length,)),
            keras.layers.Dense(10, activation="leaky_relu", name="layer1"),
            #keras.layers.Dense(30, activation="leaky_relu", name="layer2"),
            keras.layers.Dense(output_vector_length, activation="softmax",  name="output_layer", kernel_initializer='zeros'),
        ]
    )

    # Call model on a test input
    model.compile(optimizer=keras.optimizers.RMSprop(),
                  loss=keras.losses.BinaryCrossentropy(),
                  metrics=[keras.metrics.BinaryAccuracy()])

    return model
