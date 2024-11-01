import constants


class FeatureToLabelCollection:
    """
    Corresponds Features (from the past) to labels (from the future)
    Checks each step if the price delta was hit (upwards or downwards). If so -> saves this as a
    signal (BUY or SELL) in the collection.
    We store past observations in the collection. At every step we check the price point from which we've started
    i.e. the price level at which we stored the features (BID and ASK for SELL and BUY signals respectively).
    And if some price level was hit -> we assume that these features are the signal (to BUY or to SELL).
    If during some time the price level wasn't hit -> we assume that these features are the signal to do nothing.

    If ASK_t0 + PRICE_DELTA > BID_tN -> BUY signal LABEL
    If BID_t0 - PRICE_DELTA < ASK_tN -> SELL signal LABEL
    where tN - t0 < causality_timespan
    If neither was triggered during the causality timespan -> we mark this feature as NO_ACTION signal LABEL
    """

    def __init__(self, causality_timespan: int, price_deltas: tuple):
        """
        Initialize the collection
        @param causality_timespan: the time interval (usually nanos) during which we monitor the price for each feature
        set.
        @param price_deltas: the price delta(s) that activate the BUY/SELL signal Label(s). Provide one or multiple
        price levels in a tuple.
        """
        self._causality_timespan = causality_timespan
        for price_delta in price_deltas:
            if price_delta < 0:
                raise ValueError("Please input a positive price target." +
                                 " It will be correctly added/subtracted by the algo.")
        self._price_deltas = price_deltas
        self._price_deltas_count = len(price_deltas)
        self._price_targets_count = self._price_deltas_count * 2
        self._price_targets = []
        self._end_time_reference = []
        self._features = []
        self._labels = [[] for i in range(self._price_deltas_count)]
        self.__monitored_indexes = set()

    def put(self, inserted_time_reference: int, current_bid: float, current_offer: float, feature: tuple) -> None:
        """
        Insert next monitored line. Call the check_profit_levels_on_active_cells separately to update the collection.

        @param inserted_time_reference: time reference of this inserted line
        @param current_bid: the best price observed on the market right now for SALE
        @param current_offer: the best price observed on the market right now for BUY
        @param feature: the DATA (1-D or 2-D or N-D) that is representing the Features saved to correspond to the
        Labels calculated during the _causality_timespan
        """
        current_count = len(self._features)
        # One for sell, one for buy.
        for delta_index in range(self._price_deltas_count):
            # Workaround to add the LIST to the collection.
            self._labels[delta_index].append(None)
            self._labels[delta_index][current_count] = [False, False]
        # One for each level of price.
        self._features.append(feature)

        self.__monitored_indexes.add(current_count)

        self._end_time_reference.append(inserted_time_reference + self._causality_timespan)

        # Calculate price targets
        price_targets = []
        for price_delta in self._price_deltas:
            sell_target = current_bid - price_delta
            sell_target = round(sell_target, constants.PRICE_ROUND_PRECISION)
            buy_target = current_offer + price_delta
            buy_target = round(buy_target, constants.PRICE_ROUND_PRECISION)
            targets = sell_target, buy_target
            price_targets.append(targets)
        self._price_targets.append(tuple(price_targets))

    def check_profit_levels_on_active_cells(self, quote_time: int, current_bid: float, current_offer: float) -> None:
        """
        Checks profit levels on all the ACTIVE price targets. Please regulate how far back we are checking the profit
        level by creating appropriate collections (nanos to look back in class constructor!)

        @param quote_time: reference time to check if the TIMER has elapsed for some of the price checks.
        If the timer elapses => we won't check those profit levels. If timer didn't elpse -> we check the
        price targets and mark the LABELS accordingly.
        @param current_bid: the [best] bid corresponding to this quote time
        @param current_offer: the [best] offer corresponding to this quote time
        """
        removed_indexes = set()
        for index in self.__monitored_indexes:
            if self._end_time_reference[index] >= quote_time:
                # We check the prices because the TIME SPAN didn't end.
                for price_delta_index in range(self._price_deltas_count):
                    # Check downwards movement (we've Sold at BID. We now Buy out at OFFER)
                    if self._price_targets[index][price_delta_index][0] >= current_offer \
                            and not self._labels[price_delta_index][index][0]:
                        # Mark SELL LABEL as TRUE
                        self._labels[price_delta_index][index][0] = True

                    # Check upwards movement (we've Bought at OFFER. We now Sell out at BID)
                    if self._price_targets[index][price_delta_index][1] <= current_bid \
                            and not self._labels[price_delta_index][index][1]:
                        # Mark BUY LABEL as TRUE
                        self._labels[price_delta_index][index][1] = True

                    # If all price targets were hit or it's exactly on the timer:
                    if self._end_time_reference[index] == quote_time:
                        removed_indexes.add(index)
            else:
                # self._end_time_reference[index] < quote_time
                # We've passed the monitoring time span: we remove it from the checked indexes and don't check the
                # prices anymore.
                removed_indexes.add(index)

        # Remove the expired/unused keys
        self.__monitored_indexes.difference_update(removed_indexes)

    def get_ready_calculations(self) -> tuple:
        """
        Returns all the ready calculations from this collection. Doesn't mark those as "returned" and keeps the
        returned observations in the memory.
        @return: tuple in form of [labels], [features]
        """
        # In case there is no values in __monitored_indexes:
        first_monitored_index = 0
        if len(self.__monitored_indexes) > 0:
            first_monitored_index = min(self.__monitored_indexes)
        else:
            if len(self._labels[0]) > 0:
                first_monitored_index = len(self._labels[0])

        if first_monitored_index == 0:
            # Nothing calculated so far -> we return an empty collection
            return [], []

        # There are some calculations: return the ready ones. Please note that their indexes follow each other.
        # We don't want any gaps to the future in the observations.

        # Create PRICE DELTAS COUNT lists of NONE x  first_monitored_index equal vectors
        returned_labels = [[[None] for j in range(first_monitored_index)] for i in range(self._price_deltas_count)]
        returned_features = [None] * first_monitored_index

        index = 0
        while index < first_monitored_index:
            price_delta_index = 0
            while price_delta_index < self._price_deltas_count:
                this_delta = self._labels[price_delta_index]
                returned_labels[price_delta_index][index] = this_delta[index]
                price_delta_index += 1
            returned_features[index] = self._features[index]
            index += 1

        price_delta_index = 0
        while price_delta_index < self._price_deltas_count:
            self._labels[price_delta_index] = self._labels[price_delta_index][first_monitored_index:]
            price_delta_index += 1
        self._features = self._features[first_monitored_index:]
        self._price_targets = self._price_targets[first_monitored_index:]
        self._end_time_reference = self._end_time_reference[first_monitored_index:]

        self.__monitored_indexes = set([x - first_monitored_index for x in self.__monitored_indexes])

        return returned_labels, returned_features
