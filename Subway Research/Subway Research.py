import pandas as pd

def load_csv(file):
    df = pd.read_csv(file, encoding='utf-8')
    return df

def get_col(sales):
    sales = sales[:-2]
    sales = sales[["매출일자","요일","총매출","매장매출"]]
    return sales

def type_conv_sales(sales):
    sales["매출일자"] = pd.to_datetime(sales["매출일자"])
    sales["총매출"] = sales["총매출"].str.replace(",","").astype('int')
    sales["매장매출"] = sales["매장매출"].str.replace(",","").astype('int')
    return sales

def get_delv(sales):
    sales["배달매출"] = sales["총매출"] - sales["매장매출"]
    return sales

def sales_to_csv(file):
    get_delv(type_conv_sales(get_col(load_csv(file)))).to_csv("sales_data.csv", index=False, encoding="utf-8-sig")

def df_conc():
    weather = pd.concat([pd.read_csv("1.csv",encoding='cp949'),pd.read_csv("2.csv",encoding='cp949'),pd.read_csv("3.csv",encoding='cp949')],ignore_index=True)
    return weather

def type_conv_weather(weather):
    weather.iloc[:,3:] = weather.iloc[:,3:].astype('float')
    weather = weather.iloc[:,2:]
    weather = weather.fillna(0)
    return weather

def daily_conv(weather):
    whole = []
    for i in range(0,len(weather),24):
        date = weather.iloc[i,0].split(" ")
        info = list(sum(weather.iloc[i:i+24, 1:].values)/24)
        info.insert(0,date[0])
        whole.append(info)
    whole_df = pd.DataFrame(whole, columns=weather.columns)
    whole_df["일시"] = pd.to_datetime(whole_df["일시"])
    return whole_df

def weather_to_csv():
    type_conv_weather(df_conc()).to_csv("weather_data.csv", index=False, encoding="utf-8-sig")

wd = daily_conv(type_conv_weather(df_conc()))
sd = get_delv(type_conv_sales(get_col(load_csv("sales.csv"))))
td = pd.merge(wd,sd, how='inner', left_on="일시",right_on="매출일자")
td.to_csv("total_data.csv", index=False, encoding="cp949")
