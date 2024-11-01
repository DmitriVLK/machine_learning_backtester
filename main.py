import calculate_features_labels
import train_network
import backtest_strategy

__SKIP_FEATURES_LABELS_CALCULATION = False
__SKIP_NN_TRAIN = False
__SKIP_BACKTEST = False

if __name__ == '__main__':

    if not __SKIP_FEATURES_LABELS_CALCULATION:
        # Prepare Features and Labels
        calculate_features_labels.run()

    if not __SKIP_NN_TRAIN:
        # Train network on prepared data
        train_network.run()

    if not __SKIP_BACKTEST:
        # Backtest the trading strategy
        backtest_strategy.run()
