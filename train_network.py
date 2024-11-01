import random
from os import linesep, makedirs, getcwd
from os.path import join, exists
import keras
from sklearn.metrics import multilabel_confusion_matrix, classification_report
from tensorflow.data import Dataset
# LOCAL LIBRARIES:
import constants
import keras_models
from common_utilities import CommonUtilities
from enum_classes import EnumHyperParamsOptimization
from indicator import Indicator
from features_labels_storage import FeaturesLabelsStorage


def shuffle_observations(labels, features) -> tuple:
    """
    This method shuffles the values inside the labels and features. It's useful when you start to consider that
    neural networks can learn patterns and if some value is reccurent after another value it could start to predict
    continuously the same thing over and over again.
    """
    count_of_observations = len(features)
    if count_of_observations == 0:
        print("No data was present in the processed files. Terminating this procedure.")
        return None, None
    # Shuffle data inplace
    shuffle_indexes = list(range(count_of_observations))
    random.Random(111).shuffle(shuffle_indexes)
    # Shuffled observations
    shuffled_labels = [None] * count_of_observations
    shuffled_features = [None] * count_of_observations

    next_index_plain = 0
    for index in shuffle_indexes:
        shuffled_labels[next_index_plain] = labels[index]
        shuffled_features[next_index_plain] = features[index]
        next_index_plain += 1
    return shuffled_labels, shuffled_features


def equalize_to_4_labels(labels, features) -> tuple:
    """
    You might want to have equal sized labels. Some training algos benefit from feeding equally sized
    labels to train. So that the training doesn't get "stuck" on one predominant value.
    """
    count_of_observations = len(features)
    true_false_labels_count = 0
    false_true_labels_count = 0
    false_false_labels_count = 0
    true_true_labels_count = 0

    for index in range(count_of_observations):
        if labels[index][0] and labels[index][1]:
            true_true_labels_count += 1
        elif labels[index][0] and not labels[index][1]:
            true_false_labels_count += 1
        elif not labels[index][0] and labels[index][1]:
            false_true_labels_count += 1
        else:
            false_false_labels_count += 1

    min_obs = min(true_false_labels_count, false_true_labels_count, false_false_labels_count, true_true_labels_count)
    print("Minimal quantity of observations: {}.".format(min_obs))
    if min_obs == 0:
        print("Skipping labels equality balance.")
        print("NB: YOU MIGHT NEED TO ADJUST THE PROFIT_LEVELS and/or THE LOOKBACK_TIME constants to match your data.")
        return None, None
    else:
        select_labels = [None] * 4 * min_obs
        select_features = [None] * 4 * min_obs

        true_false_labels_count = 0
        false_true_labels_count = 0
        false_false_labels_count = 0
        true_true_labels_count = 0

        total_retained = 0
        # We save equal portions of the values
        for index in range(count_of_observations):
            if true_true_labels_count < min_obs and labels[index][0] and labels[index][1]:
                true_true_labels_count += 1
                select_labels[total_retained] = labels[index]
                select_features[total_retained] = features[index]
                total_retained += 1
            elif true_false_labels_count < min_obs and labels[index][0] and not labels[index][1]:
                true_false_labels_count += 1
                select_labels[total_retained] = labels[index]
                select_features[total_retained] = features[index]
                total_retained += 1
            elif false_true_labels_count < min_obs and not labels[index][0] and labels[index][1]:
                false_true_labels_count += 1
                select_labels[total_retained] = labels[index]
                select_features[total_retained] = features[index]
                total_retained += 1
            elif false_false_labels_count < min_obs:
                false_false_labels_count += 1
                select_labels[total_retained] = labels[index]
                select_features[total_retained] = features[index]
                total_retained += 1
        return select_labels, select_features


def split_test_train(features, labels, test_fraction) -> tuple:
    """
    Split test train. The data is already shuffled. Data already equilibrated.
    """
    count_of_observations = len(features)
    test_fraction_count = int(count_of_observations * test_fraction)
    test_features, test_labels = features[0:test_fraction_count], \
        labels[0:test_fraction_count]

    train_features, train_labels = features[test_fraction_count:count_of_observations], \
        labels[test_fraction_count:count_of_observations]

    print("Vector test length: {}, train: {}.".format(test_fraction_count, count_of_observations - test_fraction_count))
    return test_features, test_labels, train_features, train_labels


def run():
    """
    Runs the Training application
    """
    print("Starting TRAIN NETWORK")
    # SECTION: Read the calculated data in previous step (i.e. CalculateFeaturesLabels)

    # Hold the whole calculated data in these variables.
    concatenated_features = []
    concatenated_labels = []

    # Test create the folder and file:
    # Save the trained model in the "best_model" folder with a unique name.
    # Check that we can create the file before training a heavy model.
    save_model_folder = join(getcwd(), constants.MODELS_PATH)
    makedirs(save_model_folder, exist_ok=True)
    generated_filename = CommonUtilities.generate_file_name_base(".keras")
    file_name_counter = 0
    model_path = join(save_model_folder, generated_filename.format(file_name_counter))
    while exists(model_path):
        file_name_counter += 1
        model_path = join(save_model_folder, generated_filename.format(file_name_counter))
    del file_name_counter, generated_filename, save_model_folder

    file_index = 0
    while True:
        # Restore
        print("Restoring next calculation.")
        restored = FeaturesLabelsStorage.restore_ready_features_labels(file_index,
                                                                       directory_base=constants.FEATURES_LABELS_PATH)
        if restored is not None and len(restored) > 0:
            (labels, features), \
                (original_quotes_file_name, stored_file_name), \
                (indicators, profit_levels, currency_pair) = restored
        else:
            if file_index == 0:
                # Nothing was found and nothing was read.
                print("Nothing was found. No data was read. Terminating this procedure.")
                return
            else:
                break
        print("Restored: {} calculations stored in {}. Ccy pair: {}. Profit level index {}.".format(original_quotes_file_name,
                                                                                                    stored_file_name,
                                                                                                    currency_pair,
                                                                                                    constants.PROFIT_LEVEL_INDEX))

        # Add the calculations from this file to a whole collection.
        concatenated_labels += labels[constants.PROFIT_LEVEL_INDEX]
        concatenated_features += features
        # Increase files counter.
        file_index += 1

    print("Done extracting and concatenating stored labels and features.")

    del labels, features

    # SECTION: Prepare the Features and Labels for training
    labels, features = equalize_to_4_labels(concatenated_labels, concatenated_features)
    labels, features = shuffle_observations(labels, features)

    if labels is None or features is None:
        print("There were no observations in this dataset. Ending the program execution.")
        return
    # Remember: we have ONE tuple per profit level. We can have 10 profit levels. Each one containing 2
    # instructions: SELL or BUY signal.
    output_vector_length = len(labels[0])
    # Check the amount of data in the feature's first cell.
    input_vector_length = len(features[0])
    print("Vector input length: {}, output length: {}.".format(input_vector_length, output_vector_length))
    if output_vector_length != 2:
        raise ValueError("Please check your OUTPUT: it should be equal to 2 unless you've altered the algo.")

    # subsection B: split test-train
    test_features, test_labels, train_features, train_labels = split_test_train(features, labels,
                                                                                constants.TEST_FRACTION)

    del labels, features

    # Wrap into a TF DataSet:
    #test_labels = keras.utils.to_categorical(test_labels, num_classes=2)
    #train_labels = keras.utils.to_categorical(train_labels, num_classes=2)
    train_labels = [[int(x[0]), int(x[1])] for x in train_labels]
    test_labels = [[int(x[0]), int(x[1])] for x in test_labels]
    train_dataset = Dataset.from_tensor_slices((train_features, train_labels))
    test_dataset = Dataset.from_tensor_slices((test_features, test_labels))
    # divide the dataset in batches after it being sliced.
    train_dataset = train_dataset.batch(batch_size=constants.BATCH_SIZE, drop_remainder=False)
    test_dataset = test_dataset.batch(batch_size=1)


    print("Preparing and training the NN model.")

    # subsection C: create model
    # Define Sequential model. We use sequential models.
    model: keras.Model
    # We either use the hyperparams optimization or we fetch a simple model.
    if constants.HYPERPARAMETERS_OPTIMIZATION != EnumHyperParamsOptimization.NONE:
        model = keras_models.get_model_prototype(input_vector_length,
                                                 output_vector_length,
                                                 train_dataset,
                                                 test_dataset)
    else:
        model = keras_models.get_model_prototype_simple(input_vector_length,
                                                        output_vector_length)
    # subsection D: fit
    # The y (labels) are contained in the dataset.
    model.fit(x=train_dataset, epochs=constants.EPOCHS_COUNT)

    # Test, predict and print models. Test accuracy goal 100%
    print(linesep)
    print("Evaluating your model with TEST SET")
    test_loss, test_acc = model.evaluate(x=test_dataset)
    print(linesep)
    print(model.summary())
    print(linesep)
    print("Evaluating a confusion matrix with TEST SET")
    model_predicted = model.predict(x=test_dataset)
    list_of_probas = model_predicted.tolist()
    list_of_ints = [[int(x[0] > 0.5), int(x[1] > 0.5)] for x in list_of_probas]
    cm = multilabel_confusion_matrix(test_labels, list_of_ints)
    print("Confusion matrix and metrics:")
    print(cm)
    print(classification_report(test_labels, list_of_ints))
    print("All used indicators list:")
    indicator: Indicator
    for indicator in indicators:  # There is a control statement: this one can't be empty.
        print(str(indicator.get_doc_description()))
    print(linesep)
    print('\nTest accuracy: {}%. Goal: 100%.'.format(round(test_acc * 100.00, 2)))

    # subsection E: save model
    model.save(model_path)

    # subsection F: test some prediction
    # We test the prediction mechanism:
    if constants.DEBUG:
        # Test prediction: if you decide to make a single prediction.
        single_feature = train_features[0]
        # Wrap into a NP array
        single_feature = ([single_feature,],)
        single_feature = Dataset.from_tensor_slices(single_feature).batch(constants.BATCH_SIZE)
        # Predict a single indicators array by feeding the raw numbers to the trained model
        single_prediction = model.predict(x=single_feature, verbose=2)
        # Print the output example to the user
        predicted_label_0 = single_prediction[0][0] >= 0.5
        predicted_label_1 = single_prediction[0][1] >= 0.5
        print('\nExample prediction.\nExpected: SELL: {}; BUY: {}\nPredicted : SELL: {}; BUY: {}'
              .format(train_labels[0][0], train_labels[0][1],
                      predicted_label_0, predicted_label_1))
