import pandas as pd

def load_csv(file):
    df = pd.read_csv(file)
    return df

def get_col(sales):
    sales = sales[:-2]
    sales = sales[["매출일자","요일","총매출","매장매출"]]
    return sales

def type_conv(sales):
    sales["매출일자"] = pd.to_datetime(sales["매출일자"])
    sales["총매출"] = sales["총매출"].str.replace(",","").astype('int')
    sales["매장매출"] = sales["매장매출"].str.replace(",","").astype('int')
    return sales

def get_delv(sales):
    sales["배달매출"] = sales["총매출"] - sales["매장매출"]
    return sales

def sales_to_csv(file):
    get_delv(type_conv(get_col(load_csv(file)))).to_csv("sales_data.csv", index=False, encoding="utf-8-sig")

def df_conc():
    weather = pd.concat(load_csv("1.csv"),load_csv("2.csv"),load_csv("3.csv"))





sales_to_csv("sales.csv")