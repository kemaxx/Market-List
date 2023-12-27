import time
import pandas as pd
import gspread
import numpy as np
import re
from datetime import timedelta
import json
import math
from dotenv import load_dotenv

load_dotenv()
import os
import warnings

warnings.filterwarnings("ignore")


class MarketList():
    def __init__(self):
        STEAM_TALENT_SERVICE_ACCOUNT = os.environ.get("STEAM_TALENT_ACCOUNT")
        self.gc = gspread.service_account(STEAM_TALENT_SERVICE_ACCOUNT)

    def get_top_x_number_of_items_to_buy(self, x_items=100):
        issue_df = self.get_issue_voucher()
        categories = ['WINE', 'BEVERAGE', 'FOOD ITEM', 'ELECTRONICS AND LIGHTING', 'CLEANING SUPPLY',
                      'GUEST SUPPLY', 'DRINKS', 'CONSUMABLE', 'PRINTING AND STATIONERIES', 'VEGETABLE', '']
        sel_cat = ['BEVERAGE', 'FOOD ITEM', 'CLEANING SUPPLY', 'GUEST SUPPLY', 'CONSUMABLE',
                   'PRINTING AND STATIONERIES']

        sel_item_df = issue_df.loc[issue_df["Category"].isin(sel_cat)]
        top_x_items = sel_item_df["Item name"].value_counts()[:x_items]
        items_db = top_x_items.index.tolist()
        return items_db

    def remove_outliers_col_freq(self, df):

        """"
        The remove_outliers_col_freq function calculates the number of days between consecutive dates in a DataFrame,
        identifies and removes outliers using the IQR method, calculates the average time difference,
        and adds an additional day if needed.
        """

        df["diff"] = df["Date"] - df["Date"].shift(1)

        statistics = df["diff"].describe()

        Q1 = statistics["25%"]
        Q3 = statistics["75%"]

        IQR = statistics["75%"] - statistics["25%"]

        lower_bound, upper_bound = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR

        crt1 = df["diff"] <= lower_bound
        crt2 = df["diff"] >= upper_bound

        avg_date_time = df.where(~(crt1 | crt2))['diff'].mean()

        # print("Average Collection Rate Df: ")
        # print(avg_date_time)
        f = f"Timedelta('{avg_date_time}')"
        # print("Time delta: "+str(f))

        # Your timedelta string
        timedelta_str = str(f)

        # Use regular expression to extract days, hours, minutes, and seconds
        match = re.match(r"Timedelta\('(\d+) days (\d+):(\d+):(\d+)(.(\d+))*'\)", timedelta_str)
        # print("Time delta group match: "+str(match))

        if match:
            days, hours, minutes, seconds = int(match.groups()[0]), int(match.groups()[1]), int(match.groups()[2]), int(
                match.groups()[3])
            time_part_timedelta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

            if hours >= 13:
                days += 1
                return days
            elif days == 0:
                days = days + 1
                return days
            else:
                return days
        else:
            return np.nan

    def compute_moving_average(self, item, period):
        global top_item_df
        issues_df = self.get_issue_voucher()  # top_item_df.loc[top_item_df["Item name"] == item, :]
        item_df = issues_df.loc[issues_df["Item name"] == item, :]
        # print("Item Df: "+str(item_df))

        if not item_df.empty:

            self.avg_col_freq = self.remove_outliers_col_freq(item_df)

            item_df['Mv_Ag'] = item_df["Usage"].rolling(window=period).mean()

            # print("Mv Column: "+str(item_df['Mv_Ag']))

            # print(item_df)
            period_roll_value = item_df["Mv_Ag"].tail(period).mean() * period
            # print("MV "+str(period_roll_value))

            # print("Av_Col "+str(self.avg_col_freq))

            # print(period_roll_value)
            if np.isnan(period_roll_value):
                i_df = item_df.set_index("Date")
                i_df_sample = i_df.resample("M").sum()
                i_df["M_avg"] = i_df_sample["Usage"] / i_df_sample.index.days_in_month
                # i_df = i_df.reset_index()
                return i_df["M_avg"].mean() * period
            else:

                if np.isnan(period_roll_value / self.avg_col_freq):
                    i_df = item_df.set_index("Date")
                    i_df_sample = i_df.resample("M").sum()
                    i_df["M_avg"] = i_df_sample["Usage"] / i_df_sample.index.days_in_month
                    # i_df = i_df.reset_index()
                    return i_df["M_avg"].mean() * period
                else:
                    return period_roll_value / self.avg_col_freq

        else:
            return np.nan

    def get_stock_data(self):
        """
        This method returns a preprocessed data from the stock database in a pandas dataframe form
        :return:
        """
        stock_sheet = self.gc.open_by_key("1qqI-9I99Kix2PS1ksUralHeFXoyaArN7ZXYmCnMDLA0")
        stock_wksheet = stock_sheet.worksheet("My Stock")

        columns = stock_wksheet.row_values(1)
        columns = [data.replace('"', '') for data in columns]

        rows = stock_wksheet.get_all_values()

        rows = [[re.sub('"', '', data) for data in row] for row in rows[1:]]

        stock_df = pd.DataFrame(rows)
        stock_df.columns = columns

        stock_df["Rate"] = stock_df["Rate"].replace(['', "null", 'nan'], np.nan).astype(float)
        stock_df["Case Qty"] = stock_df["Case Qty"].replace(['', "null", 'nan'], np.nan).astype(float)
        stock_df["Safety Stock_80_Sl"] = stock_df["Safety Stock_80_Sl"].replace(['', "null", 'nan'], np.nan).astype(
            float)
        stock_df["Reorder Point"] = stock_df["Reorder Point"].replace(['', "null", 'nan'], np.nan).astype(float)
        stock_df["Daily Average"] = stock_df["Daily Average"].replace(['', "null", 'nan'], np.nan).astype(float)
        stock_df["Daily Std"] = stock_df["Daily Std"].replace(['', "null", 'nan'], np.nan).astype(float)
        stock_df["Sample Size"] = stock_df["Sample Size"].replace(['', "null", 'nan'], np.nan).astype(float)
        stock_df["Last Issued (In Days)"] = stock_df["Last Issued (In Days)"].replace(['', "null", 'nan'],
                                                                                      np.nan).astype(float)
        stock_df["Current Balance"] = stock_df["Current Balance"].replace(['', "null", 'nan'], np.nan).astype(float)
        stock_df["Ptn Qty"] = stock_df["Ptn Qty"].replace(['', "null", 'nan'], np.nan).astype(float)
        stock_df["Bundle Qty"] = stock_df["Bundle Qty"].replace(['', "null", 'nan'], np.nan).astype(float)

        return stock_df

    def get_issue_voucher(self):
        """
        This method returns a issues voucher in a pandas dataframe
        :return:
        """
        issue_voucher_sheet = self.gc.open_by_key("1y-I8V05Anud-j7VWaob3OaE9ubUEd7qqUkVFB0N942w")
        issue_voucher_wksheet = issue_voucher_sheet.worksheet("Issues")

        columns = issue_voucher_wksheet.row_values(1)
        data = issue_voucher_wksheet.get_all_values()

        df = pd.DataFrame(data)
        df.columns = columns

        df.drop(0, axis="rows", inplace=True)
        df["Date"] = pd.to_datetime(df["Date"])
        df["Usage"] = df["Usage"].str.replace(",", "").astype(float)
        df["Af_Qty"] = df["Af_Qty"].str.replace(",", "").astype(float)

        df = df.groupby(["Date", "Item name"], as_index=False).sum()

        df = df.loc[~(df["Dept"] == "FUNCTION"), :]
        return df

    def process_procurement(self):
        """
        This method pulls purchases, processes it and returns it as a pandas dataframe.
        :return:
        """
        df = pd.read_excel("zecool_purchases.xlsx", usecols=[1, 2, 3, 12, 13, 14])
        df = df[:-1]
        df.columns = ['Date', 'Item name', 'Category', 'Portion', 'Unit Cost', 'Total Amount']
        df["Date"] = pd.to_datetime(df["Date"])
        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
        df = df.dropna(thresh=4, axis=0)
        return df

    def process_batch_stock(self, batch_description, item_qty, item_cost):

        import re
        batch_description = batch_description.replace("Batch", "").strip()
        item_cost = str(item_cost)[:-2]

        print("Length of Item Cost " + str(len(item_cost)))
        if len(item_cost) > 4:
            item_cost = str(item_cost)[:2]
        else:
            item_cost = str(item_cost)[:1]
        item_qty = str(item_qty)
        match = re.match("\((.*)\)", batch_description)
        grp = match.group()
        cleaned_txt = re.sub("\(*\)*", "", grp)
        n_item_n_amt = cleaned_txt.split("X")[1].split("/")
        n_item_n_amt[0] = re.sub("\d+", str(item_qty), n_item_n_amt[0])
        n_item_n_amt[1] = re.sub("\d+", str(item_cost), n_item_n_amt[1])
        average_value = cleaned_txt.split("X")[0]
        return str("Batch(") + average_value + "X" + n_item_n_amt[0] + str("/") + n_item_n_amt[1] + str(")")

    def skip_item_for_purchase_sig_test(self,reorder_level,forcasted_qty):
        ratio = (reorder_level/forcasted_qty)
        deviation = abs(ratio-1)

        significance_threshold = 0.05 # Deviation cut off of 5%
        if deviation<significance_threshold:
            return False
        else:
            return True

    def create_market_list(self, x_days_period=30):
        gc = self.gc
        sheet = gc.open_by_key("1powB6YQD3WzpgZowXR-vsB9h9g-4FKzJ5fzXlZqEB0k")
        worksheet = sheet.worksheet("Zeccol Mkl")
        worksheet.batch_clear(["A4:E200"])

        stock_df = self.get_stock_data()
        issues_df = self.get_issue_voucher()
        items_to_buy = sorted(self.get_top_x_number_of_items_to_buy())

        for item in items_to_buy:
            time.sleep(2)
            item_mv = self.compute_moving_average(item, x_days_period)

            if np.isnan(item_mv):
                item_mv = (issues_df.loc[issues_df["Item name"] == item, :][
                               "Usage"].mean() * x_days_period) / self.avg_col_freq

            item_stock_df = None
            item_issue_df = None

            item_df = stock_df.loc[stock_df["Stock Name"] == item, :]
            ptn_name = item_df["Ptn Name"].values[0]
            case_qty = item_df["Case Qty"].values[0]
            b_qty = item_df["Bundle Qty"].values[0]
            b_name = item_df["Bundle_qty Unit"].values[0]
            rate = item_df["Rate"].values[0]
            current_bal = float(item_df["Current Bal"].values[0])
            if current_bal<0:
                current_bal=0

            if current_bal >= item_mv:
                if self.skip_item_for_purchase_sig_test(current_bal,item_mv):
                    continue

            if "Batch" in b_name:
                purchase_df = self.process_procurement()
                item_purchase_df = purchase_df.loc[purchase_df["Item name"] == item, :]
                real_purchase_item_df = item_purchase_df.loc[item_purchase_df["Total Amount"] > 1, :]
                last_three_purchase = real_purchase_item_df.tail(3)
                mean_amt = round(last_three_purchase["Total Amount"].mean(), -3)
                mean_received = math.ceil(last_three_purchase["Portion"].mean())

                b_name = self.process_batch_stock(b_name, mean_received, mean_amt)

            # Modifications - Start
            reorder_qty = None
            reorder_level_str = None
            if current_bal < b_qty:
                reorder_level = current_bal
                reorder_level_str = str(current_bal) + " " + str(ptn_name)

            elif current_bal > b_qty and b_qty == 1:
                reorder_level = current_bal // b_qty
                reorder_level_str = str(current_bal // b_qty) + " " + str(b_name)
            else:
                reorder_level = current_bal // b_qty
                reorder_level_str = str(current_bal // b_qty) + " " + str(b_name)

            buy = None
            buy_flag = None
            #More modifications:
            print()
            print(item)
            print("Current Bal: " + str(current_bal))
            print(f"Moving Average: {math.ceil(item_mv)}")

            item_mv = math.ceil(item_mv-current_bal)
            if item_mv<0:
                item_mv = math.ceil(current_bal-item_mv)

            if case_qty == 1:
                buy = item_mv // b_qty
                buy_flag = item_mv/b_qty
            else:
                buy = item_mv // case_qty
                buy_flag = item_mv / b_qty

            #buy = buy-current_bal

            if buy_flag < 0.5:
                buy = 0.5
            elif 0.5 <= buy_flag < 1:
                buy = 1

            buy = round(buy, 1)
            buy_str = str(buy) + f" {b_name}"
            mkl_rate = None
            mkl_amt = None
            if case_qty == 1:
                mkl_rate = round((rate * b_qty), -2)
            else:
                if buy < b_qty:
                    buy_str = str((b_qty // buy)) + f" {b_name}"
                    buy =  buy // b_qty
                mkl_rate = round((rate * case_qty * b_qty), -2)

            mkl_amt = round(mkl_rate * buy, 0)



            time.sleep(1)
            worksheet.append_rows([[item, str(reorder_level_str), buy_str, str(mkl_rate), str(mkl_amt)]])


if __name__ == "__main__":
    mkl = MarketList()
    mkl.create_market_list()
