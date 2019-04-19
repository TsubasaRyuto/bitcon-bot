class Logic:
    def is_buy_signal(self, now_cci, previous_cci):
        return previous_cci is not None and int(previous_cci) <= -95 and int(now_cci) >= -95

    def is_sell_signal(self, now_cci, previous_cci):
        return previous_cci is not None and int(previous_cci) >= 95 and int(now_cci) <= 95
