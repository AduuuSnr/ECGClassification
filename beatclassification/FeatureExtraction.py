import wfdb
import numpy as np
from scipy import stats

ann_path = "../data/sample/mitdb"


class FeatureExtraction:
    def __init__(self):
        # classes of beats
        self.classes = ["N", "S", "V", "F"]
        # physiobank symbols for beats
        self.symbols = ["N", "L", "R", "e", "J", "A", "a", "J", "S", "V", "E", "F"]
        # associates symbols to classes of beats
        self.symbol2class = {"N": "N", "L": "N", "R": "N", "e": "N", "j": "N",
                             "A": "S", "a": "S", "J": "S", "S": "S",
                             "V": "V", "E": "V",
                             "F": "F"}
        # label is the integer value associated to a class
        self.class2label = {}
        self.label2class = {}
        count = 0
        for classe in self.classes:
            self.class2label[classe] = count
            self.label2class[count] = classe
            count += 1

    def extract(self, names):
        features = []
        labels = []
        for name in names:
            print(name)
            signal, peaks, symbols = self.read_data(name)
            rr_intervals = np.diff(peaks)
            rr_mean = np.mean(rr_intervals)
            for count in range(5, len(symbols)-5):
                symbol = symbols[count]
                if symbol in self.symbols:
                    feature = []
                    self.rr_features(count, feature, rr_intervals, rr_mean)
                    peak = peaks[count]
                    qrs = signal[peak - 90:peak +90]
                    self.signal_cumulants(qrs, feature)
                    features.append(feature)
                    classe = self.symbol2class[symbol]
                    label = self.class2label[classe]
                    labels.append(label)
        return np.array(features), np.array(labels)

    def rr_features(self, count, feature, rr_intervals, rr_mean):
        window = rr_intervals[count - 5: count + 5]
        win_mean = np.mean(window)
        prev_3 = rr_intervals[count - 3: count]
        prev_3 = np.divide(prev_3, rr_mean)
        prev = rr_intervals[count - 1]
        next = rr_intervals[count]
        feature.extend([prev, next, win_mean])
        feature.extend(prev_3)

    def read_data(self, name):
        annotation = wfdb.rdann(ann_path + "/" + name, "atr")
        record = wfdb.rdrecord(ann_path + "/" + name)
        signal = []
        for elem in record.p_signal:
            signal.append(elem[0])
        symbols = annotation.symbol
        peaks = annotation.sample
        return signal, peaks, symbols

    # takes a window of [-75,75] around the Rpeak
    # TODO: does it require filtering?
    def signal_cumulants(self, signal, feature):
        lags = [15, 30, 45, 60, 75, 105, 120, 135, 150, 165]
        second = []
        third = []
        fourth =[]
        for lag in lags:
            window = signal[:lag]
            cumulant_sample = stats.kstat(window, 2)
            second.append(cumulant_sample)
            cumulant_sample = stats.kstat(window, 3)
            third.append(cumulant_sample)
            cumulant_sample = stats.kstat(window, 4)
            fourth.append(cumulant_sample)
        feature.extend(second)
        feature.extend(third)
        feature.extend(fourth)
        return feature


