import os
import logging
import sys
import requests
import pandas as pd
from datetime import datetime, timedelta
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# 1. LOGGING SETUP (once at the beginning of the file)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", handlers=[
        logging.FileHandler("Loggers/log_report.txt", mode="a"),
        logging.StreamHandler(sys.stdout)]) # so that it also outputs to the console in parallel
logger = logging.getLogger(__name__)

# 1 module
def parsing() -> pd.DataFrame:
    """ Downloads the trading history for USD000UTSTOM from the Moscow Exchange and saves it in CSV format. """
    ticker = "USD000UTSTOM"
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")
    url = f"https://iss.moex.com/iss/history/engines/currency/markets/selt/securities/{ticker}.json"
    params = {"from": start_date, "till": end_date, "iss.meta": "off", "iss.only": "history",
              "history.columns": "TRADEDATE,OPEN,HIGH,LOW,CLOSE,VOLUME"}
    all_data = []
    start = 0
    limit = 100
    logger.info(f'We are starting the parsing of the Moscow Financial Exchange...')
    logger.info(f"We are starting to download the data for the ticker. {ticker}...")
    try:
        while True:
            params["start"] = start
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            history_block = data["history"]
            rows = history_block["data"]
            if not rows:
                logger.debug("We received an empty response from the exchange, so we end the cycle.")
                break
            all_data.extend(rows)
            logger.debug(f"Loaded portions: {len(all_data)} lines (current portion: {len(rows)})")
            if len(rows) < limit:
                break
            start += limit
        if not all_data:
            logger.warning("No data was received (empty response from the exchange). We return an empty DataFrame.")
            df_1 = pd.DataFrame()
        else:
            df_1 = pd.DataFrame(all_data, columns=history_block["columns"])
            df_1["TRADEDATE"] = pd.to_datetime(df_1["TRADEDATE"])
            numeric_cols = ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]
            for col in numeric_cols:
                if col in df_1.columns:
                    df_1[col] = pd.to_numeric(df_1[col], errors="coerce")
            # Filtering only daytime data
            df_1 = df_1[(df_1['OPEN'] != df_1['HIGH']) | (df_1['OPEN'] != df_1['LOW']) |
                        (df_1['OPEN'] != df_1['CLOSE'])]
            if "TRADEDATE" in df_1.columns:
                df_1 = df_1.sort_values("TRADEDATE").reset_index(drop=True)
        output_file = 'Data chest/Moscow Exchange_currency_daily.csv'
        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        df_1.to_csv(output_file, index=False)
        logger.info(f"Successfully saved: {len(df_1)} lines in the file: {output_file}")
        return df_1
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error when querying the Moscow Exchange API: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred in the parsing function: {e}")
        raise

# Module 2
def exploratory_da(df_EDA: pd.DataFrame) -> None:
    """ File analysis before processing"""
    logger.info(f'We are analyzing the file...')
    try:
        logging.info(f'---- Initial examination ----')
        logging.info(f'The first 10 lines:\n{df_EDA.head(10)}')
        logging.info(f'The last lines:\n{df_EDA.tail(10)}')
        logging.info(f'General information:\n{df_EDA.info}')
        logging.info(f'<<Statistical information:\n{df_EDA.describe()}')
        logging.info(f'Analyze the size and structure.:\n{df_EDA.shape}')
        logging.info(f'The names of all columns:\n{df_EDA.columns.tolist()}')
        logging.info(f'---- Data validation ----')
        logging.info(f'Duplicates:\n{df_EDA.duplicated().sum()}')
        logging.info(f'Gaps:\n{df_EDA.isna().sum()}')
        logging.info(f'Data types:\n{df_EDA.dtypes}')
    except FileNotFoundError:
        logging.error(f'There is no report folder....')

# Module 3: We clean the data (duplicates and all that)
def clean_df(df_cl: pd.DataFrame) -> pd.DataFrame:
    """ Here, the file will be cleaned of duplicates, and if necessary, skipped."""
    logger.info(f'Data cleaning...')
    try:
        len_row = len(df_cl)
        df_cl = df_cl[(df_cl[['OPEN', 'HIGH', 'LOW', 'CLOSE']] != 0).all(axis=1)] # Filter out null values
        df_cl = df_cl.drop_duplicates() # if there are duplicates, we delete them
        removed_rows = len_row - len(df_cl) # we remove from the total how many duplicates were removed
        # Cleaning statistics
        logger.info(f"Cleanup report: it was {len_row} lines, deleted: {removed_rows} lines, left {len(df_cl)} lines")
        save_2 = 'Data chest/Moscow Exchange_currency_daily2.csv'
        df_cl.to_csv(save_2, index=False) # save the file after cleaning
        logger.info(f'We saved the file after cleaning it up. {save_2}')
        return df_cl
    except Exception:
        logger.exception("Critical error в clean_df")
        raise

# Module 4: Machine Learning
def mashingan(df_cl: pd.DataFrame) -> pd.DataFrame:
    """ Machine learning"""
    try:
        logging.info(f'We are launching machine learning...')
        x = df_cl.drop(['TRADEDATE', 'CLOSE'], axis=1)
        y = df_cl['CLOSE']
        X_train, X_test, y_train, y_test = train_test_split(x, y, train_size=0.2, test_size=40)
        model = LinearRegression()
        model.fit(X_train, y_train)
        prediction = model.predict(X_test)
        me = mean_squared_error(y_test, prediction)
        re = r2_score(y_test, prediction)
        logging.info(f'Root mean square error {me}...')
        logging.info(f'Relative error {re}...')
        # We create a comparison of real and predicted values.
        comparison = pd.DataFrame({'Real': y_test.iloc[:10], 'Predicted': prediction[:10]})
        logging.info(f'We create a comparison of real and predicted values.\n{comparison}')
        return df_cl
    except Exception:
        logger.exception('A critical error occurred during model training.')
        raise

# everything happens here, and this is the last future module
def main():
    """ The main function is that everything is connected here."""
    logger.info(f'--- The script for the Moscow Financial Exchange is being launched. ----\n')
    df_1 = parsing()
    df_1 = clean_df(df_1)
    exploratory_da(df_1)
    mashingan(df_1)
    logging.info(f'\n=================\nThe script is completed.\n=================\n')


if __name__ == '__main__':
    main()
