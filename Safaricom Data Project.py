
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




st.set_page_config(
    page_title= "m-pesa Analysis",
    page_icon= ":bar_chart:",
    layout= "wide"
)
@st.cache_data
def data_store():
   saf_data= pd.read_csv(Path(__file__).parent / "mpesa_synthetic.csv")
   return saf_data
@st.cache_data
def calc(saf_data):
        saf_data= data_store()
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
        legit_amt= (total_volume- fraud_amt)
        legit_amt= round(legit_amt, 0)
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
        fraud_rate_region= (
            saf_data.groupby(by= ["region"])["is_fraud"].mean().reset_index()
        )
        fraud_rate_region["is_fraud"]= round(fraud_rate_region["is_fraud"]*100, 2)
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
        return (
            total_transactions,
            total_volume,
            transaction_split,
            tran_per_hour,
            transaction_split,
            fraud_amt,
            fraud_avg,
            fraud_count,
            fraud_hourly_counts,
            fraud_rate,
            fraud_rate_per_amount,
            feature_count,
            feature_pct,
            smart_count,
            smart_pct,
            legit_amt,
            legit_avg,
            peak_hour,
            peak_hour_counts,
            amount_dist,
            fraud_rate_region
        )
def show_home():
    st.markdown("""
    <style>
        [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {
            padding-top: 0rem;
        }
        .block-container {
            padding-top: 0.5rem;
        }
        div[data-testid="stHorizontalBlock"] {
            margin-top: -2rem;
        }
    </style>
""", unsafe_allow_html=True) 
    st.markdown("""
        <style>
            [data-testid="stMetric"] {
                background-color: #0E0D0B;
                border: 1px solid #333;
                border-radius: 10px;
                padding: 20px;
            }
            [data-testid="stMetricLabel"] {
                color: #F4F2F1;
                font-size: 16px;
            }
            [data-testid="stMetricValue"] {
                color: #F4F2F1;
                font-size: 28px;
            }
        </style>
    """, unsafe_allow_html=True)
    
    
    saf_data= data_store()
    (
            total_transactions,
            total_volume,
            transaction_split,
            tran_per_hour,
            transaction_split,
            fraud_amt,
            fraud_avg,
            fraud_count,
            fraud_hourly_counts,
            fraud_rate,
            fraud_rate_per_amount,
            feature_count,
            feature_pct,
            smart_count,
            smart_pct,
            legit_amt,
            legit_avg,
            peak_hour,
            peak_hour_counts,
            amount_dist,
            fraud_rate_region
        )= calc(saf_data)
    def format_number(num):
        if num >= 1_000_000_000:
            return f"{num/1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        return str(num)
    st.markdown("""
        <style>
            [data-testid="stMetric"] {
                background-color: #0E0D0B;
                border: 1px solid #333;
                border-radius: 10px;
                padding: 20px;
            }
            [data-testid="stMetricLabel"] {
                color: #F4F2F1;
                font-size: 16px;
            }
            [data-testid="stMetricValue"] {
                color: #F4F2F1;
                font-size: 28px;
            }
        </style>
    """, unsafe_allow_html=True)
    
    
    st.markdown("""
        <style>
        [data-testid="stMetricDelta"] svg {
            display: none;
        }
        </style>
        """, unsafe_allow_html=True)
    col1, col2 = st.columns([2, 8], vertical_alignment= "center")
    lef, mid_lef, mid, mid_righ, rig, col = st.columns(6)
    with col1:
        st.image(Path(__file__).parent /"SAF-MAIN-LOGO.png")
    with col2:
        st.markdown("""
                <h1 style="color: #288C1D; font-family: Courier New, monospace; 
                        font-size:30px">
                    M-Pesa Analysis
                </h1>
            """, unsafe_allow_html=True)
    with lef:
        st.metric(label= "Total Transactions", 
        value= f"{total_transactions:,}",
        delta= "full 2026 dataset",
        delta_color= "off")
    with mid_lef:
        st.metric(label= "Total Volume", 
        value= f"KES {format_number(total_volume)}",
        delta= "Across all types",
        delta_color= "off")
    with mid:
        st.metric(label="Fraud Rate", value=f"{fraud_rate}%",
        delta= f"{fraud_count} flagged txns",
        delta_color= "inverse")
    with mid_righ:
        st.metric(label= "Avg. legitimate Amount",
        value= (f"KES {round(legit_avg):,}"),
        delta= "per transaction")
    with rig:
       st.metric(label= "Avg. Fraud Amount", 
       value= (f"KES {round(fraud_avg):,}"),
       delta= f"{round(fraud_avg/legit_avg, 2)}x larger than legit",
        delta_color= "inverse"
       )
    with col:
        st.metric(label= "Peak Fraud Hour",
         value= f"{peak_hour-12} PM",
         delta= f"Hour {peak_hour}--{peak_hour_counts} cases",
         delta_color= "inverse")
    with st.container(border= True):
        st.write(
          "🔍 Biggest finding: Fraudulent transactions are on average 72% larger than legitimate ones (KES 2,535 vs KES 1,476). And for transactions above KES 5,000, the fraud rate shoots to 9.65% — nearly 1 in 10. Kenyans sending big money are the primary target."  
        )
    st.markdown("-")
    #GRAPHS
    #fraude rate per amount
    color_map={
       "cat1": "#1D9E75",
       "cat2": "#BA7517",
       "cat3": "#D85A30",
       "cat4": "#E24B4A",      
       "cat5": "#791F1F"}
    fraud_rate_bar= px.bar(
         fraud_rate_per_amount,
        x= fraud_rate_per_amount.index,
        y= fraud_rate_per_amount.values,
        title= "<b>Fraud rate by transaction amount</b>",
        color=fraud_rate_per_amount.index,
        color_discrete_sequence=["#1D9E75", "#BA7517", "#D85A30", "#E24B4A", "#791F1F"]
)

    fraud_rate_bar.update_layout(
        height= 300,
        showlegend= False,
        title_font_color= "#F4170B",
        margin= dict(t= 40, b= 10, l= 10, r= 10),
        yaxis= dict(
            ticksuffix= "%",
            title= None
        ),
        xaxis= dict(
            title= None,
            showgrid= False
        )
    )
    fraud_region= px.bar(
        fraud_rate_region,
        x= "region",
        y= "is_fraud",
        title= "<b> Fraud Rate Per Region</b>",
        color= "region",
        color_discrete_sequence=["#1D9E75", "#BA7517", "#D85A30", "#E24B4A", "#791F1F"]

    )

    fraud_region.update_layout(
        height= 300,
        showlegend= False,
        margin= dict(t= 40, b= 10, l= 10, r= 10),
        xaxis= dict(
            showgrid= False,
            title= None,
        ),
        yaxis= dict(
            ticksuffix= "%",
            title= None
        ),
    )
    col, col1= st.columns(2)

    with col:
        with st.container(border= True):
            st.plotly_chart(fraud_rate_bar)
        
    with col1:
        with st.container(border= True):
            st.plotly_chart(fraud_region)
show_home()