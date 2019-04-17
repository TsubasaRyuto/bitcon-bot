import numpy as np
class RSI:
    def rsi_calculater(self, cpl, period):
        markup_list = []
        markdown_list = []
        for i in range(len(cpl) - 1):
            if cpl[i] > cpl[i + 1]:
                markup_list.append(cpl[i] - cpl[i + 1])
            else:
                markdown_list.append(cpl[i + 1] - cpl[i])
        sum_markup = np.sum(np.array(markup_list))
        sum_markdown = np.sum(np.array(markdown_list))
        return int((sum_markup / (sum_markup + sum_markdown)) * 100)
