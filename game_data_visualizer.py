import pandas as pd
import matplotlib.pyplot as plt

def visualize_results(file_path="codecrack_data.csv"):
    df = pd.read_csv(file_path)

    # Win/Loss distribution
    df['Win'].value_counts().plot(kind='bar', title='Win/Loss Distribution')
    plt.show()

    # Number of guesses histogram
    df['NumGuesses'].plot(kind='hist', bins=15, title='Distribution of Guesses Used')
    plt.xlabel("Number of Guesses")
    plt.show()

    # Boxplot of guess quality by win/loss
    df.boxplot(column='Correct', by='Win')
    plt.title("Correct Digits by Win/Loss")
    plt.suptitle("")
    plt.show()

if __name__ == "__main__":
    visualize_results()
