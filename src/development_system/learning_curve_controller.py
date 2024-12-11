"""
This module contains a class for plotting a learning curve
"""

import matplotlib.pyplot as plt


class LearningCurveController:
    """
    Plotter of learning curves to a specific path
    """
    def __init__(self, filepath):
        """
        Constructor
        :param filepath: file in which the plot will be saved
        """
        self.filepath = filepath

    def update_learning_curve(self, data) -> None:
        """
        Function to plot the learning curve
        :param data: list of loss values at each epoch
        :return: None
        """
        epochs = range(1, len(data)+1)
        plt.plot(epochs, data)
        plt.plot([len(data)/2, len(data)/2], [0, max(data)], "r--")
        plt.axis([0, len(data)+1, 0, max(data)*1.05])
        plt.savefig(self.filepath)
