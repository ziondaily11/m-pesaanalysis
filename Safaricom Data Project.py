
#A safaricom mpesa dataset analysis
#modules
import pandas as pd
import streamlit as st
import plotly_express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from pathlib import Path  
import warnings
import sys 
sys.modules['warnings'] = warnings

saf_data= pd.read_csv(Path(__file__).parent / "mpesa_synthetic.csv")
saf_data= saf_data.dropna(subset= "transaction_id")
#calculations
#total transactions
total_transactions= saf_data["transaction_id"].nunique()
#total volume of transaction amount
total_volume= saf_data["amount"].sum()
#fraud rate
fraud_count= saf_data["is_fraud"].sum()
fraud_rate= fraud_count*100/total_transactions
#return rate per amount categories
saf_data["amount_cat"]= pd.cut(
    saf_data["amount"],
    bins= [0, 500, 1000, 2000, 5000, float("inf")],
    labels= ["0-500", "500-1k", "1k-2k", "2k-5k", "5k+"]
)
fraud_rate_per_amount= (
    saf_data.groupby("amount_cat")["is_fraud"]
    .mean()
    *100
)
#fraud & Legit amountrs
fraud_amt= saf_data[saf_data["is_fraud"]==1]["amount"].sum()
legit_amt= total_volume- fraud_amt
#Averages
fraud_avg= saf_data[saf_data["is_fraud"]==1]["amount"].mean()
legit_avg= saf_data[saf_data["is_fraud"]==0]["amount"].mean()
#fraud counts per hour
fraud_hourly_counts= (
    saf_data[saf_data["is_fraud"]==1]
    .groupby("hour")
    .size()
    .sort_values(ascending= False)
)
#peak fraud hour
peak_hour= fraud_hourly_counts.idxmax()
peak_hour_counts= fraud_hourly_counts.max()
#Transaction type splitt
transaction_split= (saf_data.groupby(by= "transaction_type")[["transaction_id"]]
                    .size()
                   )
#amount distribution bucket
amount_dist= (
    saf_data.groupby("amount_cat")["amount"].sum()
)
#transactions per hour
tran_per_hour= (
    saf_data.groupby("hour")["transaction_id"].size().sort_index()
                )
#Device split
smart_count= (saf_data["device_type"]=="smartphone").sum()
feature_count= (saf_data["device_type"]=="feature").sum()
total= smart_count+feature_count
smart_pct= round(smart_count*100/total, 2)
feature_pct= round(feature_count*100/total, 2)

device_per_region= (
    saf_data.groupby(["region", "device_type"]).size()
)          
st.image(Path(__file__).parent / "SAF-MAIN-LOGO.png")
