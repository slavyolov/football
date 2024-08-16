from prepare_data import *


def main():
    files = [
        "C:/Users/natal/Documents/Python Scripts/football/data/uk/2021_2022.csv",
        "C:/Users/natal/Documents/Python Scripts/football/data/uk/2022_2023.csv",
        "C:/Users/natal/Documents/Python Scripts/football/data/uk/2023_2024.csv"
    ]

    # PARAMETERS # TODO: put these in a cfg file
    min_coef = 2.3
    max_coef = None
    strategy = 'min_coef'  # min_coef; range_coef
    bet_strategy = 'min_coef'  # TODO: refactor the code for home and away games, maybe also draw
    write_csv = True
    label = "above"

    for file in files:
        year = file.split('/')[-1].split('_')[0]  # Extract the year from the filename
        data = pd.read_csv(file)

        filtered_data = get_data(data=data, strategy=strategy, min_coef=min_coef, max_coef=max_coef)
        data_ext = determine_winning_bet(data=filtered_data, bet_strategy=bet_strategy)
        statistics, data_final = apply_dalembert_system(data=data_ext)
        if write_csv:
            data_final.to_csv(
                f"C:/Users/natal/Documents/Python Scripts/football/output_data/uk/{strategy}_{bet_strategy}_results_{year}.csv",
                index=False)

        # Plotting :
        bank_balance_path = f'C:/Users/natal/Documents/Python Scripts/football/output_data/uk/bank_balance_{year}_coef_{label}_{min_coef}_{max_coef}.png'
        plot_bank_balance(year, min_coef, max_coef,
                          statistics['dalembert_bank_progress'], statistics['total_profit_dalembert'],
                          statistics['roi_dalembert'], statistics['win_ratio'],
                          save_path=bank_balance_path
                          )

        streak_path = f'C:/Users/natal/Documents/Python Scripts/football/output_data/uk/bets_and_streaks_{year}_coef_{label}_{min_coef}_{max_coef}.png'
        plot_bets_and_streaks(year, min_coef,
                              statistics['streaks_bets_df'], streak_path)


        print(data_final)


if __name__ == '__main__':
    main()
