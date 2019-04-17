class Logic:
    def is_buy_signal(self, now_rsi, previous_rsi):
        return previous_rsi is not None and int(previous_rsi) < 25 and int(now_rsi) >= 25

    def is_sell_signal(self, now_rsi, previous_rsi):
        return previous_rsi is not None and int(previous_rsi) > 75 and int(now_rsi) <= 75
