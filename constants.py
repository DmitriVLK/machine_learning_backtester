from enum_classes import EnumPair, EnumOrderBook, EnumHyperParamsOptimization

# Quote files storage path.
RAW_PATH = r"raw"
# Features and labels ready calculations storage path.
FEATURES_LABELS_PATH = r"features_labels"
# This is the path for the models to be stored.
MODELS_PATH = r"model"
# If you want to specify a path for files used only for backtest, please set this path here.
RAW_BACKTEST_PATH = r"backtest_raw"

"""
Order book and data type selection!
"""
# If you work with the Dukaskopy data sets -- please select "DUKASKOPY" otherwise use "HIGH FREQ FX". You can add
# your own implementations of order books along the way.
ORDER_BOOK_TYPE = EnumOrderBook.DUKASKOPY

"""
Utility constants
"""
# Flag if you want to process file in multithreading.
MULTITHREADED = True
# Trace is lower level debug than DEBUG
TRACE = False
# If Trace is set to True -- set it to TRUE. Otherwise, set it to whatever!
DEBUG = True if TRACE else True
# Determines how many digits to keep in the fraction.
FLOAT_ROUND_PRECISION: int = 8
# Determines how many digits to keep in the fraction.
FLOAT_ROUND_PRECISION_DEC: int = pow(10, -FLOAT_ROUND_PRECISION)
# How many digits there is after the comma in the fractions
PRICE_ROUND_PRECISION: int = 5
# Nanos in second, millisecond, minute etc.
NANOS_IN_ONE_MILLIS = 1000000
NANOS_IN_ONE_SECOND = 1000000000
NANOS_IN_ONE_MINUTE = 60 * NANOS_IN_ONE_SECOND
MILLIS_IN_ONE_SECOND = 1000
MILLIS_IN_ONE_MINUTE = 60 * MILLIS_IN_ONE_SECOND
DATE_FORMAT: str = "%Y-%m-%d-%H-%M"
# This constant modifies the frequency of FEATURE/LABEL collection updates AND the debug of the current status
# of processing
FREQUENCY_OF_DATA_TRANSFERS = 10000


"""
CALCULATE LABELS AND FEATURES PARAMETERS
"""

# Chosen currency pair for training
# If it's a DUKASKOPY order book -- then use OTHER as an ENUM PAIR. Because it will be a generic ticker.
CCY_PAIR = EnumPair.OTHER if ORDER_BOOK_TYPE == EnumOrderBook.DUKASKOPY else EnumPair.EURUSD
# the levels of searched take profit for the currency pair.
# FOR Currency Pair PROFIT_LEVELS would be (0.00008, 0.0001, 0.00013)
PROFIT_LEVELS = (0.50, 1.00, 1.50)
# How long to check for the TAKE PROFIT. During this time we monitor if the price of __currency_pair
# goes down or up for the amount set in the __profit_levels
LOOKBACK_TIME = 60 * NANOS_IN_ONE_SECOND
# How long do we wait between each step (recalculation of indicators and report to FeatureToLabelCollection)
# It manages as well the frequency at which the backtester makes the PREDICT
EACH_STEP_TIMER = 40 * NANOS_IN_ONE_MILLIS

"""
TRAIN NETWORK PARAMETERS
"""

# This is the profit level index. Remember that we calculate LABELs for several profit levels at once.
PROFIT_LEVEL_INDEX = 0
# Test is 30% fraction of all data. Train is 70%
TEST_FRACTION = 0.30
# Epochs set how many times you will sweep through the (same set of) data to train the network. With each sweep the
# model gets incremental adjustments and the loss (calculated with loss function) decreases. So, having many epochs
# might be beneficial to having a well-trained model. Too many epochs can lead to overfitting problems.
EPOCHS_COUNT = 20
# The size of a single trained slice. We use BATCH SIZE to allow for a more efficient training of model by increasing
# each iteration training size. The batch size divides the sample into BATCH_SIZE sized portions given to the training
# model. For example, if you had 1000 input points and BATCH_SIZE=4 -- the model will be trained each iteration with
# 1000/4 = 250 total iterations.
BATCH_SIZE = 4
# Type of hyperparameters optimization (GRID, RANDOM, BAYESIAN)
HYPERPARAMETERS_OPTIMIZATION = EnumHyperParamsOptimization.BAYESIAN
# Number of trials for hyperparameters optimization
TRIALS = 2

"""
BACKTEST PARAMETERS
"""
MAX_TIME_POSITION = 5 * NANOS_IN_ONE_MINUTE
TAKE_PROFIT = PROFIT_LEVELS[PROFIT_LEVEL_INDEX]
# 10 bps
# FOR Currency Pair STOP_LOSS would be 0.0010
STOP_LOSS = 5.0

