
#A safaricom mpesa dataset analysis
#modules
import pandas as pd
import streamlit as st
import plotly_express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots as msp
from streamlit_option_menu import option_menu
from pathlib import Path  
import warnings
import sys 


sys.modules['warnings'] = warnings




st.set_page_config(
    page_title= "FinPulseAnalysis",
    page_icon= ":bar_chart:",
    layout= "wide"
)
def data_store():
   saf_data= pd.read_csv(Path(__file__).parent / "mpesa_synthetic.csv")
   return saf_data
@st.cache_data(ttl= 90)
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
            .reset_index(name= "count")
            
        )
        fraud_hourly_counts= fraud_hourly_counts.sort_values("hour")
        fraud_rate_region= (
            saf_data.groupby(by= ["region"])["is_fraud"].mean().reset_index()
        )
        fraud_rate_region["is_fraud"]= round(fraud_rate_region["is_fraud"]*100, 2)
        #peak fraud hour
        peak_hour= fraud_hourly_counts.loc[fraud_hourly_counts["count"].idxmax(), "hour"]
        peak_hour_counts= fraud_hourly_counts["count"].max()
        fraud_rate_hour= (saf_data.groupby(by= ["hour"])["is_fraud"].mean().reset_index())
        fraud_rate_hour["is_fraud"]= round(fraud_rate_hour["is_fraud"]*100, 2)
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
        #phone distribution by region
        phone_dist= (saf_data.groupby(["region", "device_type"])
        .size()
        .reset_index(name= "count")
        )
        #Transaction volume by day of the weak
        Trans_daily= (
            saf_data.groupby(
               by= ["day_of_week"]
            )[["transaction_id"]].size()
            .reset_index(name="count")
            .rename(columns={"day_of_week": "day"})
        )
        Trans_daily= Trans_daily.sort_values("day")
        return (
            total_transactions,
            total_volume,
            transaction_split,
            tran_per_hour,
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
            fraud_rate_region,
            fraud_rate_hour,
            phone_dist,
            Trans_daily
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
            fraud_rate_region,
            fraud_rate_hour,
            phone_dist,
            Trans_daily
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
    
    
    
    col1, col2, col_region, col_type, col_fraud = st.columns(([1, 3, 2, 2, 2]),  vertical_alignment= "center", gap="small")
    with col1:
        st.image(Path(__file__).parent / "projectlogo.png", width=140)
    st.markdown("<div style='margin-left: 0px;'></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <h1 style="color: #9E1405; font-family: Courier New, monospace;
                font-size:30px; margin: 0; padding: 0;">
                FINPULSE REPORT
            </h1>
        """, unsafe_allow_html=True)
    with col_region:
        region_filter = st.multiselect(
            "Region",
            options=sorted(saf_data["region"].unique()),
            default=[]  
            )

    with col_type:
        type_filter = st.multiselect(
            "Transaction Type",
            options=sorted(saf_data["transaction_type"].unique()),
            default=[]
        )

    with col_fraud:
        fraud_filter = st.selectbox(
            "Fraud Status",
            options=["All", "Fraud only", "Legit only"]
        )
    filtered_data = saf_data.copy()
    
    if region_filter:
        filtered_data = filtered_data[filtered_data["region"].isin(region_filter)]

    if type_filter:
        filtered_data = filtered_data[filtered_data["transaction_type"].isin(type_filter)]

    if fraud_filter == "Fraud only":
        filtered_data = filtered_data[filtered_data["is_fraud"] == 1]
    elif fraud_filter == "Legit only":
        filtered_data = filtered_data[filtered_data["is_fraud"] == 0]

    if filtered_data.empty:
        st.warning("No transactions match the selected filters. Try widening your selection.")
        return 
    (
            total_transactions_f, total_volume_f, transaction_split_f, tran_per_hour_f,
            fraud_amt_f, fraud_avg_f, fraud_count_f, fraud_hourly_counts_f,
            fraud_rate_f, fraud_rate_per_amount_f, feature_count_f, feature_pct_f,
            smart_count_f, smart_pct_f, legit_amt_f, legit_avg_f, peak_hour_f, peak_hour_counts_f,
            amount_dist_f, fraud_rate_region_f, fraud_rate_hour_f, phone_dist_f, Trans_daily_f
    ) = calc(filtered_data)
    st.markdown("""
                    <style>
                        div[data-testid="stVerticalBlock"]:has(div.st-key-logo_header) div[data-testid="stHorizontalBlock"] {
                            gap: 0rem;
                        }
                    </style>
                """, unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    lef, mid_lef, mid, mid_righ, rig, col = st.columns(6)
    with lef:
        st.metric(label= "Total Transactions", 
        value= f"{total_transactions_f:,}",
        delta= "full 2026 dataset",
        delta_color= "off")
    with mid_lef:
        st.metric(label= "Total Volume", 
        value= f"KES {format_number(total_volume_f)}",
        delta= "Across all types",
        delta_color= "off")
    with mid:
        st.metric(label="Fraud Rate", value=f"{fraud_rate_f}%",
        delta= f"{fraud_count_f} flagged txns",
        delta_color= "inverse")
    with mid_righ:
        st.metric(label= "Avg. legitimate Amount",
        value= (f"KES {round(legit_avg_f):,}"),
        delta= "per transaction")
    with rig:
       st.metric(label= "Avg. Fraud Amount", 
       value= (f"KES {round(fraud_avg_f):,}"),
       delta= f"{round(fraud_avg_f/legit_avg_f, 2)}x larger than legit",
        delta_color= "inverse"
       )
    with col:
        st.metric(label= "Peak Fraud Hour",
         value= f"{peak_hour-12} PM",
         delta= f"Hour {peak_hour_f}--{peak_hour_counts_f} cases",
         delta_color= "inverse")
    
    st.info(
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
         fraud_rate_per_amount_f,
        x= fraud_rate_per_amount_f.index,
        y= fraud_rate_per_amount_f.values,
        title= "<b>Fraud rate by transaction amount</b>",
        color=fraud_rate_per_amount_f.index,
        color_discrete_sequence=["#1D9E75", "#BA7517", "#D85A30", "#E24B4A", "#791F1F"]
    )
    #fraud_rate_bar.update_traces(width= 0.45)

    fraud_rate_bar.update_layout(
        height= 250,
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
        ),
        #bargap= 0.2
    )
    fraud_region= px.bar(
        fraud_rate_region,
        x= "region",
        y= "is_fraud",
        title= "<b> Fraud Rate Per Region</b>",
        color= "region",
        color_discrete_sequence=["#D85A30", "#E24B4A", "#791F1F", "#1D9E75", "#BA7517"]

    )
    #fraud_region.update_traces(width= 0.45)
    fraud_region.update_layout(
        title_font_color= "#F4170B",
        height= 250,
        showlegend= False,
        margin= dict(t= 40, b= 10, l= 10, r= 10),
        xaxis= dict(
            showgrid= False,
            title= None,
        ),
        yaxis= dict(
            range= [2.7, 3],
            ticksuffix= "%",
            title= None
        ),
        #bargap= 0.1
    )
    #transaction split pie
    label_with_count= [
        f"{label.upper()} ({value:,})"
        for label, value in zip(transaction_split.index, transaction_split.values)
    ]
    transaction_split_pie= go.Figure(go.Pie(
        labels= label_with_count,
        values= transaction_split.values,
        hole= 0.7,
        textinfo = "none",
        marker_colors=["#1D9E75", "#BA7517", "#D85A30"]
    ))
    transaction_split_pie.update_traces(
        domain= dict(x=[0.1, 0.9], y=[0.1, 0.9])
        )
    transaction_split_pie.update_layout(
        title= dict(
                text= "<b>Transaction Type Split</b>",
                x= 0,
                y= 0.97,
                font= dict(color= "#618948")
                ),
        
        height= 250,
        margin= dict(t= 40, b= 10, l= 10, r= 10),
        annotations= [dict(
            text= "120,000 txns",
            x= 0.5, y= 0.5,
            font_size= 10,
            showarrow= False

        )]
        
    )
    #amount distribution graph
    hourly_tran_bar= px.area(
        tran_per_hour,
        x= tran_per_hour.index,
        y= tran_per_hour.values,
        title= "Transaction by Hour of the Day",
        markers= True,
        color_discrete_sequence= ["#AFF693"]
    )
    hourly_tran_bar.update_traces(
        line= dict(
            shape= "spline",
            color= "#1D9E75"
        )
    )
    hourly_tran_bar.update_layout(
        height= 200,
        margin= dict(t= 40, b= 10, l= 10, r= 10),
        xaxis= dict(
            showgrid= False,
            title= None,
            range= [-0.5, 23.5],
            ticksuffix= "h"
        ),
        yaxis= dict(
            range= [4700, 5200],
            showgrid= False,
            title= None,
            tickformat= "~s"
        ),
        title_font_color= "#618948",
    )
    amount_dist_bar= px.bar(
        amount_dist_f,
        x= amount_dist_f.index,
        y= amount_dist_f.values,
        title= "Amount Distribution",
        color= amount_dist_f.index,
        color_discrete_sequence=["#1D9E75", "#BA7517", "#D85A30", "#E24B4A", "#791F1F"]

    )
    #amount_dist_bar.update_traces(width= 0.45)
    amount_dist_bar.update_layout(
        height= 250,
        margin= dict(t= 40, b= 10, l= 10, r= 10),
        title_font_color= "#618948",
        showlegend= False,
        yaxis= dict(
            title= None
        ),
        xaxis= dict(
            title= None,
            showgrid= False
        ),
        bargap= 0.1
    )

    #fraude rate per hour + transaction amount per hour

    fig= msp(specs= [[{"secondary_y": True}]])
    trace = go.Scatter(
            x=tran_per_hour.index,
            y=tran_per_hour.values,
            name="Transactions",
            mode="lines",
            fill="tozeroy",
            line=dict(
                shape="spline",
                width=3,
                color="#18c29c"
            ),
            marker=dict(size=7),
            hovertemplate="<b>Hour %{x}:00</b><br>Transactions: %{y}<extra></extra>"
        )
    
    fig.add_trace(trace, secondary_y=False)
    fraud_trace = go.Scatter(
            x=fraud_rate_hour["hour"],
            y=fraud_rate_hour["is_fraud"],
            name="Fraud Rate",
            mode="lines",
            line=dict(
                shape="spline",
                width=2,
                color="#F8240C"
            ),                        
            hovertemplate="<b>Hour %{x}:00</b><br>Fraud Rate: %{y:.2f}%<extra></extra>"
        )

    fig.add_trace(fraud_trace, secondary_y=True)
    fig.update_layout(
        title= "Transactions V Fraude Rate by Hour",
        title_font= dict(color= "#618948"),
        template= "plotly_dark",
        hovermode= "x unified",

        legend= dict(
            orientation= "h",
            y= 1.08, x= 0.5, 
            xanchor= "center"
        ),
        margin=  dict(t= 40, b= 10, l= 10, r= 10),
        height= 250
    )
    fig.update_yaxes(
        title= "Transactions",
        title_font_color= "#18c29c",
        range= [4700, 5200],
        tickformat= "~s",
        secondary_y= False
    )
    fig.update_yaxes(
        title= "Fraud Rate",
        title_font= dict(color= "#F8240C"),
        ticksuffix= "%",
        secondary_y= True
    )
    fig.update_xaxes(
        ticksuffix= "h",
        tickmode= "linear",
        dtick= 2
    )
    #phone distribution bar
    phone_dist_bar= px.bar(
        phone_dist,
        x= "region",
        y= "count",
        color="device_type",
        color_discrete_sequence=["#1D9E75", "#BA7517"],
        barmode= "stack",
        title= "FEATURE PHONE VS SMARTPHONE BY REGION"
    )
    phone_dist_bar.update_layout(
        title_font= dict(color= "#BA7517"),
        showlegend= False,
        yaxis= dict(
            title= None,
            showgrid= False
        ),
        xaxis= dict(
            title= None,
            showgrid= False
        )
    )

    #daily transaction count bar
    trans_daily_bar=px.bar(
        Trans_daily,
        x= "day",
        y="count",
        category_orders={"day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]},
        title= "Transaction Volume By Day",
        color= "day",
        color_discrete_sequence= ["#1D9E75", "#378ADD", "#BA7517", "#50504B", "#D85A30", "#7F77DD", "#E24B4A"]
        )
    
    trans_daily_bar.update_layout(
        height= 300,
        margin= dict(t= 40, b= 10, l= 10, r= 10),
        title_font= dict(color= "#BA7517"),
        showlegend= False,
        yaxis= dict(
            range= [16000, 18000],
            title= None,
            showgrid= False
        ),
        xaxis= dict(
            title= None,
            showgrid= False
        )
    )
    #FRAUD hourly counts bar 
    colors = {str(hour): "#E24B4A" if hour in [4, 21] else "#888780" 
          for hour in fraud_hourly_counts["hour"]}
    fraud_count_bar= px.bar(
        fraud_hourly_counts,
        x= "hour",
        y= "count",
        title= "Fraud Counts By Hour Of Day",
        color= fraud_hourly_counts["hour"].astype(str),
        color_discrete_map= colors
)
    fraud_count_bar.update_layout(
        height= 300,
        margin= dict(t= 40, b= 10, l= 10, r= 10),
        title_font= dict(color= "#BA7517"),
        showlegend= False,
        yaxis= dict(
            title= None,
            showgrid= False
        ),
        xaxis= dict(
            title= None,
            showgrid= False,
            dtick= 2
        )
    )
    
    col, col1, col_c= st.columns(3)
    with col:
        with st.container(border= True):
            st.plotly_chart(amount_dist_bar)
            
    with col1:
        with st.container(border= True):
             st.plotly_chart(transaction_split_pie)
            
    with col_c:
        with st.container(border= True):
            st.plotly_chart(fraud_region)
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)  
    bar_col, area_col= st.columns([0.8, 2.2])
    with bar_col:
        with st.container(border= True):
            st.plotly_chart(fraud_rate_bar)

    with area_col:
        with st.container(border= True):
            st.plotly_chart(fig)
    st.info("📱 Device split insight: Feature phones and smartphones are almost exactly 50/50 (50.3% vs 49.7%) across all regions — showing M-Pesa's penetration across all economic levels. Nakuru has the highest smartphone fraud rate at 3.12%, while Kisumu feature phones are the lowest at 2.68%.")
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)  
    bar_col2,  bar_col3= st.columns([2, 3])

    #with bar_col1:
        #with st.container(border= True):
            #st.plotly_chart(phone_dist_bar)   
    with bar_col2:
        with st.container(border= True):
            st.plotly_chart(trans_daily_bar)
    with bar_col3:
        with st.container(border= True):
            st.plotly_chart(fraud_count_bar)
    st.info("🌙 Late night danger: Fraud peaks at 9 PM (hour 21) with 172 cases, followed closely by 4 AM (hour 4) with 170. The 4 AM spike is particularly suspicious — legitimate users rarely transact at 4 AM, making it a strong fraud signal for Safaricom's detection systems.")

    st.write("DEBUG total_transactions_f:", total_transactions_f)
    st.write("DEBUG total_transactions (full):", total_transactions)
show_home()
