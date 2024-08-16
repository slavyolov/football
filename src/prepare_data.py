import pandas as pd
import matplotlib.pyplot as plt


def get_data(data, strategy, min_coef=None, max_coef=None):
    """
    Generalized method to filter data and determine winning bets based on different strategies.

    Parameters:
    - data (pd.DataFrame): The input data containing odds and results.
    - strategy (str): The strategy to use for filtering and betting. Options:
      - 'min_coef': Filter matches where the minimum coefficient is above or equal to min_coef.
      - 'range_coef': Filter matches where the coefficient is between min_coef and max_coef.
    - min_coef (float): The minimum coefficient value for filtering or betting.
    - max_coef (float): The maximum coefficient value for filtering (used only in 'range_coef').

    Returns:
    - pd.DataFrame: The filtered DataFrame with the winning bet determined.

    Examples:
    >>> data = pd.DataFrame({
    ...     'B365H': [1.8, 2.5, 1.9, 3.0, 2.2],
    ...     'B365D': [3.4, 2.6, 3.1, 2.7, 2.4],
    ...     'B365A': [4.2, 3.0, 4.5, 3.5, 3.1],
    ...     'FTHG': [2, 1, 3, 0, 2],
    ...     'FTAG': [1, 1, 0, 0, 2],
    ...     'FTR': ['H', 'D', 'H', 'D', 'A']
    ... })
    >>> print(data)
    >>> get_data(data, strategy='min_coef', min_coef=2.0)
    >>> get_data(data, strategy='range_coef', min_coef=1.8, max_coef=2.2)
    """

    # Extract relevant columns for betting odds and results
    odds_columns = ['B365H', 'B365D', 'B365A']
    results_columns = ['FTHG', 'FTAG', 'FTR']

    # Create a subset of the dataframe with relevant columns
    betting_data = data[odds_columns + results_columns]

    # Apply filtering based on the selected strategy
    if strategy == 'min_coef':
        filtered_betting_data = betting_data[(betting_data['B365H'] >= min_coef) &
                                             (betting_data['B365D'] >= min_coef) &
                                             (betting_data['B365A'] >= min_coef)]
    elif strategy == 'range_coef':
        filtered_betting_data = betting_data[(betting_data['B365H'].between(min_coef, max_coef)) |
                                             (betting_data['B365D'].between(min_coef, max_coef)) |
                                             (betting_data['B365A'].between(min_coef, max_coef))]
    else:
        raise ValueError(f"Invalid strategy: {strategy}")

    return filtered_betting_data


def calculate_win_probabilities(odds):
    """
    Using the Equal MArgin method : https://winnerodds.com/valuebettingblog/true-odds-calculator/
    Calculate win probabilities from bookmaker odds, accounting for the bookmaker's margin.

    Parameters:
    odds (list of float): A list of odds for each outcome.

    Returns:
    list of float: A list of win probabilities for each outcome.

    Example:
    >>> calculate_win_probabilities([2.50, 2.80, 3.10])
    [0.3705, 0.3308, 0.2987]
    """
    # Step 1: Calculate implied probabilities
    implied_probabilities = [1 / odd for odd in odds]

    # Step 2: Calculate the total implied probability
    total_implied_probability = sum(implied_probabilities)

    # Step 3: Normalize probabilities
    normalized_probabilities = [round(prob / total_implied_probability, 4) for prob in implied_probabilities]

    return normalized_probabilities


def determine_winning_bet(data, bet_strategy):
    """
    Determine the winning bet based on the selected strategy.

    Parameters:
    - data (pd.DataFrame): The filtered data containing odds and results.
    - bet_strategy (str): The betting strategy. Options:
      - 'min_coef': Bet on the minimum coefficient, prioritize home if tied.
      - 'draw': Bet on the draw (coefficient for draw).
      - 'max_coef': Bet on the maximum coefficient, prioritize home if tied.
      - 'home': Always bet on the home team.
      - 'away': Always bet on the away team.

    Returns:
    - pd.DataFrame: The DataFrame with the winning bet determination and additional fields.

    Examples:
    >>> data = pd.DataFrame({
    ...     'B365H': [1.8, 2.5, 2.5, 3.0],
    ...     'B365D': [3.4, 3.4, 3.4, 3.0],
    ...     'B365A': [4.2, 2.5, 3.1, 2.9],
    ...     'FTHG': [2, 1, 1, 0],
    ...     'FTAG': [1, 1, 2, 1],
    ...     'FTR': ['H', 'D', 'A', 'D']
    ... })

    >>> df = determine_winning_bet(data, bet_strategy='home')
    >>> df[['FTR_num', 'B365H', 'B365D', 'B365A', 'Bet', 'Win Probability', 'Winning_Bet', 'betting_strateggy']]
      FTR_num  B365H  B365D  B365A Bet  Win Probability  Winning_Bet betting_strateggy
    0       1    1.8    3.4    4.2   1          0.5107         True               home
    1       X    2.5    3.4    2.5   1          0.3656        False               home
    2       2    2.5    3.4    3.1   1          0.3934        False               home
    3       X    3.0    3.0    2.9   1          0.3295        False               home

    >>> df = determine_winning_bet(data, bet_strategy='away')
    >>> df[['FTR_num', 'B365H', 'B365D', 'B365A', 'Bet', 'Win Probability', 'Winning_Bet', 'betting_strateggy']]
      FTR_num  B365H  B365D  B365A Bet  Win Probability  Winning_Bet betting_strateggy
    0       1    1.8    3.4    4.2   2          0.2189        False               away
    1       X    2.5    3.4    2.5   2          0.3656        False               away
    2       2    2.5    3.4    3.1   2          0.3173         True               away
    3       X    3.0    3.0    2.9   2          0.3409        False               away

    >>> df = determine_winning_bet(data, bet_strategy='min_coef')
    >>> df[['FTR_num', 'B365H', 'B365D', 'B365A', 'Bet', 'Win Probability', 'Winning_Bet', 'betting_strateggy']]
      FTR_num  B365H  B365D  B365A Bet  Win Probability  Winning_Bet betting_strateggy
    0       1    1.8    3.4    4.2   1          0.5107         True           min_coef
    1       X    2.5    3.4    2.5   1          0.3656         True           min_coef
    2       2    2.5    3.4    3.1   1          0.3934        False           min_coef
    3       X    3.0    3.0    2.9   2          0.3409        False           min_coef

    >>> df = determine_winning_bet(data, bet_strategy='draw')
    >>> df[['FTR_num', 'B365H', 'B365D', 'B365A', 'Bet', 'Win Probability', 'Winning_Bet', 'betting_strateggy']]
      FTR_num  B365H  B365D  B365A Bet  Win Probability  Winning_Bet betting_strateggy
    0       1    1.8    3.4    4.2   X          0.3308        False               draw
    1       X    2.5    3.4    2.5   X          0.3308         True               draw
    2       2    2.5    3.4    3.1   X          0.3308        False               draw
    3       X    3.0    3.0    2.9   X          0.3333         True               draw

    >>> df = determine_winning_bet(data, bet_strategy='max_coef')
    >>> df[['FTR_num', 'B365H', 'B365D', 'B365A', 'Bet', 'Win Probability', 'Winning_Bet', 'betting_strateggy']]
      FTR_num  B365H  B365D  B365A Bet  Win Probability  Winning_Bet betting_strateggy
    0       1    1.8    3.4    4.2   2          0.2189        False           max_coef
    1       X    2.5    3.4    2.5   X          0.2688         True           max_coef
    2       2    2.5    3.4    3.1   X          0.2893        False           max_coef
    3       X    3.0    3.0    2.9   X          0.3295         True           max_coef

    """

    # Recode the FTR field to numeric: 1 for Home Win, X for Draw, and 2 for Away Win
    data['FTR_num'] = data['FTR'].map({'H': '1', 'D': 'X', 'A': '2'})  # CHANGED

    # Calculate win probabilities for all outcomes
    data['Win Probabilities'] = data.apply(lambda row: calculate_win_probabilities([row['B365H'], row['B365D'], row['B365A']]), axis=1)

    if bet_strategy == 'min_coef':
        data['Coefficient'] = data[['B365H', 'B365D', 'B365A']].min(axis=1)
        data['Bet'] = data.apply(lambda row: '1' if row['Coefficient'] == row['B365H'] else
                                           ('X' if row['Coefficient'] == row['B365D'] else '2'), axis=1)
        data['Win Probability'] = data.apply(lambda row: row['Win Probabilities'][0] if row['Bet'] == '1' else
                                                             (row['Win Probabilities'][1] if row['Bet'] == 'X' else
                                                              row['Win Probabilities'][2]), axis=1)
    elif bet_strategy == 'draw':
        data['Bet'] = 'X'
        data['Coefficient'] = data['B365D']
        data['Win Probability'] = data['Win Probabilities'].apply(lambda x: x[1])
    elif bet_strategy == 'max_coef':
        data['Coefficient'] = data[['B365H', 'B365D', 'B365A']].max(axis=1)
        data['Bet'] = data.apply(lambda row: '1' if row['Coefficient'] == row['B365H'] else
                                           ('X' if row['Coefficient'] == row['B365D'] else '2'), axis=1)
        data['Win Probability'] = data.apply(lambda row: row['Win Probabilities'][0] if row['Bet'] == '1' else
                                                             (row['Win Probabilities'][1] if row['Bet'] == 'X' else
                                                              row['Win Probabilities'][2]), axis=1)
    elif bet_strategy == 'home':
        data['Bet'] = '1'
        data['Win Probability'] = data['Win Probabilities'].apply(lambda x: x[0])
    elif bet_strategy == 'away':
        data['Bet'] = '2'
        data['Win Probability'] = data['Win Probabilities'].apply(lambda x: x[2])
    else:
        raise ValueError(f"Invalid bet strategy: {bet_strategy}")

    # Determine whether the bet was successful by comparing Bet with FTR_num
    data['Winning_Bet'] = data['Bet'] == data['FTR_num']  # CHANGED

    data["betting_strateggy"] = bet_strategy

    return data


def apply_dalembert_system(data, initial_bank=500, base_bet=10):
    """
    Apply the D'Alembert betting system to the provided data and calculate various metrics.

    Parameters:
    - data (pd.DataFrame): The data containing odds, results, and whether the bet was won.
    - initial_bank (int): The initial bank balance to start with.
    - base_bet (int): The base bet amount.

    Returns:
    - dict: A dictionary containing the D'Alembert system results, including bank progress, profit, ROI, final balance, and streaks.
    - pd.DataFrame: The updated DataFrame with added columns for Winning Streak, Losing Streak, Current Bet, and dalembert_bank_progress.

    Examples:
    >>> data = pd.DataFrame({
    ...     'B365H': [1.8, 2.5, 2.5, 3.0, 1.9, 2.0, 2.1],
    ...     'B365D': [3.4, 3.4, 3.4, 3.0, 3.4, 3.6, 3.2],
    ...     'B365A': [4.2, 2.5, 3.1, 2.9, 4.2, 3.0, 2.9],
    ...     'FTHG': [2, 2, 1, 0, 2, 1, 0],
    ...     'FTAG': [1, 1, 2, 1, 2, 0, 1],
    ...     'FTR': ['H', 'H', 'A', 'D', 'D', 'H', 'A']
    ... })

    >>> data = determine_winning_bet(data, bet_strategy='min_coef')
    >>> results, updated_data = apply_dalembert_system(data)
    >>> updated_data[['Winning Streak', 'Losing Streak', 'Current Bet', 'dalembert_bank_progress']]
       Winning Streak  Losing Streak  Current Bet  dalembert_bank_progress
    0               1              0           10                 505.56
    1               2              0           10                 515.56
    2               0              1           10                 505.56
    3               0              2           20                 485.56
    4               0              3           30                 455.56
    5               1              0           40                 515.56
    6               0              1           30                 495.56
    """
    dalembert_bank = initial_bank
    dalembert_bank_progress = []
    current_bet = base_bet
    winning_streak = 0
    losing_streak = 0

    for index, row in data.iterrows():
        # Store the bet amount used before the match result is known
        data.at[index, 'Current Bet'] = current_bet  # CHANGED: Store the current bet before the match

        if row['Winning_Bet']:
            profit = current_bet * (row['Coefficient'] - 1)
            dalembert_bank += profit
            current_bet = max(base_bet, current_bet - base_bet)
            winning_streak += 1
            losing_streak = 0
        else:
            dalembert_bank -= current_bet
            current_bet += base_bet
            losing_streak += 1
            winning_streak = 0

        # Append the bank progress after the bet
        dalembert_bank_progress.append(dalembert_bank)

        # Add streak and bank progress information to the DataFrame
        data.at[index, 'Winning Streak'] = winning_streak
        data.at[index, 'Losing Streak'] = losing_streak
        data.at[index, 'dalembert_bank_progress'] = dalembert_bank

    # Calculate additional metrics
    total_profit_dalembert = dalembert_bank - initial_bank
    roi_dalembert = (total_profit_dalembert / initial_bank) * 100

    # win_ratio :
    win_ratio = 100 * (len(data[data["Winning_Bet"] == True]) / len(data))

    # Return results and updated DataFrame
    return {
        'dalembert_bank_progress': dalembert_bank_progress,
        'total_profit_dalembert': total_profit_dalembert,
        'roi_dalembert': roi_dalembert,
        'final_bank_balance': dalembert_bank,
        'win_ratio': win_ratio,
        'streaks_bets_df': data[['Winning Streak', 'Losing Streak', 'Current Bet', 'dalembert_bank_progress']]
    }, data


def plot_bank_balance(year, min_coef, max_coef, bank_progress, total_profit, roi, win_ratio, save_path):
    plt.figure(figsize=(12, 6))
    plt.plot(bank_progress, marker='o', linestyle='-', color='purple')
    plt.title(f'Bank Balance Over Time ({year}, Min Coef {min_coef}, Max Coef {max_coef})')
    plt.xlabel('Match Number')
    plt.ylabel('Bank Balance ($)')
    plt.grid(True)

    plt.text(0.5, 0.95, f'Total Profit: ${total_profit:.2f}\nROI: {roi:.2f}%\nWinning %: {win_ratio:.2f}%',
             fontsize=12, verticalalignment='top', horizontalalignment='center', transform=plt.gca().transAxes,
             bbox=dict(facecolor='white', alpha=0.8))

    # Save the figure to the new directory
    plt.tight_layout()
    plt.savefig(save_path)


def plot_bets_and_streaks(year, min_coef, streaks_bets_df, save_path):
    fig, axs = plt.subplots(3, 1, figsize=(8, 12))

    # Plot current bet size
    axs[0].plot(streaks_bets_df['Current Bet'], marker='o', linestyle='-', color='green')
    axs[0].set_title(f'Current Bet Over Time ({year}, Coef {min_coef})')
    axs[0].set_xlabel('Match Number')
    axs[0].set_ylabel('Current Bet ($)')
    axs[0].grid(True)

    # Plot winning streaks separately
    axs[1].plot(streaks_bets_df['Winning Streak'], marker='o', linestyle='-', color='blue')
    axs[1].set_title('Winning Streak Over Time')
    axs[1].set_xlabel('Match Number')
    axs[1].set_ylabel('Winning Streak')
    axs[1].grid(True)

    # Plot losing streaks separately
    axs[2].plot(streaks_bets_df['Losing Streak'], marker='x', linestyle='-', color='red')
    axs[2].set_title('Losing Streak Over Time')
    axs[2].set_xlabel('Match Number')
    axs[2].set_ylabel('Losing Streak')
    axs[2].grid(True)

    # Adjust layout with more space between subplots
    plt.tight_layout(h_pad=4)  # Add vertical padding between subplots

    plt.savefig(save_path)

