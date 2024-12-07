import os
import matplotlib.pyplot as plt
from utility import data_folder


class LearningCurveController:
    def __init__(self):
        self.filepath = os.path.join(data_folder, "development_system_data/learning_curve.png")

    def update_learning_curve(self, data):
        epochs = range(1, len(data)+1)
        plt.plot(epochs, data)
        plt.plot([len(data)/2, len(data)/2], [0, max(data)], "r--")
        plt.axis([0, len(data)+1, 0, max(data)*1.05])
        plt.savefig(self.filepath)
