import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load Data
df = pd.read_csv('cleaneddata.csv')
df = df[(df['paisa'] != 0)]
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month

st.set_page_config(page_title='Startup Analysis', page_icon='images.jpeg')

# ----------------- STARTUP DETAIL -----------------
def load_startup_detail(name):
    st.header(name)
    s = str(df.groupby('startup')['industry'].sum().loc[name])
    st.subheader('Related Industry: ' + s)

    p = str(df.groupby('startup')['subvertical'].sum().loc[name])
    if p == '0':
        st.subheader('Work is not known')
    else:
        st.subheader('Work on: ' + p)

    L = list(set(df[df['startup'] == name]['city'].values.tolist()))
    if len(L) > 0:
        markdown_text = "#### Located in:\n"
        for i, item in enumerate(L, 1):
            markdown_text += f"{i}. {item}\n"
        st.markdown(markdown_text)

    st.header('Funds Recieved Till Now')
    bdf = df[df['startup'] == name].set_index('date')[['investor', 'investmenttype', 'paisa']]
    bdf.rename(columns={'paisa': 'Rs in Crore'}, inplace=True)
    st.dataframe(bdf)

    st.header('Year Wise Received Funds')
    new_df = df[df['startup'] == name]
    new_df = new_df.groupby('year')['paisa'].sum().reset_index()

    st.subheader('Funds Received')
    fig, ax = plt.subplots()
    ax.bar(new_df['year'], new_df['paisa'])
    ax.set_title("Funds Received Over Years")
    ax.set_xlabel("Year")
    ax.set_ylabel("Funds (Rs in Crore)")
    st.pyplot(fig)

    # Investors list
    new_df = df[df['startup'] == name]
    l2 = list(set(new_df['investor'].str.split(',').sum()))
    if len(l2) > 0:
        st.subheader('Investors')
        html_line = "&nbsp;&nbsp;&nbsp;&nbsp;".join([f"{i+1}. {item}" for i, item in enumerate(l2)])
        st.markdown(f"<p>{html_line}</p>", unsafe_allow_html=True)


# ----------------- OVERALL ANALYSIS -----------------
def perform_overall():
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Startups investment", str(int(df['paisa'].sum())) + 'Cr')

    with col2:
        st.metric("Avg Startups investment", str(round(df.groupby('startup')['paisa'].sum().mean())) + 'Cr')

    with col3:
        st.metric("Total Startups till invested", str(df['startup'].value_counts().shape[0]))

    with col4:
        st.metric("Max Startup investment", str(int(df.groupby('startup')['paisa'].sum().sort_values(ascending=False).values[0])) + 'Cr')

    st.header('MoM chart')
    s_item = st.selectbox('Choose Overall Investment on the basis of', ['Money', 'Count'])
    if s_item == 'Money':
        bdf = df.groupby(['month', 'year'])['paisa'].sum().reset_index()
    else:
        bdf = df.groupby(['month', 'year'])['paisa'].count().reset_index()

    bdf['my'] = bdf['month'].astype(str) + " " + bdf['year'].astype(str)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(bdf['year'], bdf['paisa'], marker='o', color='green')
    ax.set_title("Investment Over Years")
    ax.set_xlabel("Year")
    ax.set_ylabel("Total Investment (Rs in crore)")
    ax.grid(True)
    ax.set_xticks(bdf['year'][::5])
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)

    # Sector Analysis
    st.header('Sector Analysis')
    sector_item = st.selectbox('Sector Analysis on basis of', ['Money', 'Count'])
    if sector_item == 'Money':
        bdf = df.groupby('industry')['paisa'].sum().sort_values(ascending=False).head(8).reset_index()
    else:
        bdf = df.groupby('industry')['paisa'].count().sort_values(ascending=False).head(8).reset_index()
    bdf.rename(columns={'paisa': 'Rs in crore'}, inplace=True)
    fig, ax = plt.subplots()
    ax.pie(bdf['Rs in crore'], labels=bdf['industry'], autopct='%1.1f%%', startangle=90, shadow=True)
    ax.axis('equal')
    st.pyplot(fig)

    # Funding Type
    st.header('Type of funding')
    bdf = df.groupby('investmenttype')['paisa'].sum().sort_values(ascending=False).head(5).reset_index()
    bdf.rename(columns={'paisa': 'Rs in crore'}, inplace=True)
    fig, ax = plt.subplots()
    ax.pie(bdf['Rs in crore'], labels=bdf['investmenttype'], autopct='%1.1f%%', startangle=90, shadow=True)
    ax.axis('equal')
    st.pyplot(fig)

    # City Wise Funding
    st.header('City Wise Funding')
    df['city'] = df['city'].str.replace('Bengaluru', 'Bangalore')
    bdf = df.groupby('city')['paisa'].sum().sort_values(ascending=False).head().reset_index()
    bdf.rename(columns={'paisa': 'Rs in crore'}, inplace=True)
    fig, ax = plt.subplots()
    ax.pie(bdf['Rs in crore'], labels=bdf['city'], autopct='%1.1f%%', startangle=90, shadow=True)
    ax.axis('equal')
    st.pyplot(fig)

    # Top Startups Year-Wise
    st.header('Top Startups Year-Wise')
    temp_df = df.groupby(['startup', 'year'])['paisa'].sum().sort_values(ascending=False).reset_index()
    temp_df = temp_df.sort_values(['year', 'paisa'], ascending=[True, False]).drop_duplicates('year', keep='first').set_index('year')
    temp_df.rename(columns={'paisa': 'Rs in crore'}, inplace=True)
    st.dataframe(temp_df)

    # Top Startups Overall
    st.header('Top Startups Overall')
    st.dataframe(df.groupby('startup')['paisa'].sum().sort_values(ascending=False).head())

    # Top Investors
    st.header('Top Investors')
    l1 = list(set(df['investor'].str.split(',').sum()))
    l2 = []
    for i in l1:
        try:
            val = int(df[df['investor'].str.contains(i)]['paisa'].sum())
            l2.append(val)
        except:
            pass
    l3 = [(j, i) for i, j in zip(l1, l2)]
    l3 = sorted(l3, reverse=True)
    if ('',) in l3:
        l3.remove(('',))
    if (' & Others',) in l3:
        l3.remove((' & Others',))
    l4 = []
    for i in range(10):
        l4.append([l3[i][1], l3[i][0]])
    ndf = pd.DataFrame(l4, columns=['Investor Name', 'Total Amount Invested'])
    st.dataframe(ndf)

    # Funding HeatMap
    st.header('Funding HeatMap')
    st.subheader("Funding Heatmap (Year vs. Month)")
    heatmap_data = df.groupby(['year', 'month'])['paisa'].sum().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="YlGnBu", linewidths=0.5, ax=ax)
    ax.set_title("Monthly Funding (in ₹ Crore)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Year")
    st.pyplot(fig)


# ----------------- INVESTOR DETAIL -----------------
def load_investor_detail(name):
    if name != 'Choose Similar Investor':
        st.title(name)
        st.subheader('Recent Investments')
        temp_df = df[df['investor'].str.contains(name)]
        temp_df.rename(columns={'paisa': 'Rs in crore'}, inplace=True)
        st.dataframe(temp_df[['date', 'startup', 'industry', 'investmenttype', 'Rs in crore']].head().set_index('date').reset_index())

        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Biggest Investments in Startup')
            bdf = temp_df.groupby('startup')['Rs in crore'].sum().sort_values(ascending=False).head().reset_index()
            fig, ax = plt.subplots()
            ax.bar(bdf['startup'], bdf['Rs in crore'])
            st.pyplot(fig)

        with col2:
            st.subheader('Biggest Investments in each sector')
            bdf = temp_df.groupby('industry')['Rs in crore'].sum().sort_values(ascending=False).head(15).reset_index()
            fig, ax = plt.subplots()
            ax.pie(bdf['Rs in crore'], labels=bdf['industry'], autopct='%1.1f%%', startangle=90, shadow=True)
            ax.axis('equal')
            st.pyplot(fig)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Biggest Investment in Each stage')
            bdf = temp_df.groupby('investmenttype')['Rs in crore'].sum().reset_index()
            fig, ax = plt.subplots()
            ax.pie(bdf['Rs in crore'], labels=bdf['investmenttype'], autopct='%1.1f%%', startangle=90, shadow=True)
            ax.axis('equal')
            st.pyplot(fig)

        with col2:
            st.subheader('City Wise Investment')
            bdf = temp_df.groupby('city')['Rs in crore'].sum().reset_index()
            fig, ax = plt.subplots()
            ax.pie(bdf['Rs in crore'], labels=bdf['city'], autopct='%1.1f%%', startangle=90, shadow=True)
            ax.axis('equal')
            st.pyplot(fig)

        st.subheader('YearWise Investment')
        bdf = temp_df.groupby('year')['Rs in crore'].sum().reset_index()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(bdf['year'], bdf['Rs in crore'], marker='o', color='green')
        ax.set_title("Investment Over Years")
        ax.set_xlabel("Year")
        ax.set_ylabel("Total Investment (Rs in crore)")
        ax.grid(True)
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)

        st.subheader('Similar Investors')
        L1 = sorted(set(temp_df['investor'].str.split(',').sum()))
        L1.remove(name)
        L2 = list(set(df['investor'].str.split(',').sum()))
        L2.remove('')
        if ' & Others' in L2:
            L2.remove(' & Others')
        common = ['Choose Similar Investor'] + list(set(L1) & set(L2))
        selected_investor = st.selectbox('Choose Similar Investors', common)
        load_investor_detail(selected_investor)


# ----------------- SIDEBAR NAVIGATION -----------------
st.sidebar.title('Startup Analysis')

if 'selected_opn' not in st.session_state:
    st.session_state.selected_opn = ""

selected_opn = st.sidebar.selectbox('What you want to do?', ['Overall Analysis', 'StartUps', 'Investors'])

if st.session_state.selected_opn != selected_opn:
    st.session_state.selected_opn = selected_opn
    if 'clicked' in st.session_state:
        st.session_state.clicked = False

if st.session_state.selected_opn == 'Overall Analysis':
    st.header('Overall Analysis')
    perform_overall()

elif st.session_state.selected_opn == 'StartUps':
    st.header('StartUps')
    name = st.sidebar.selectbox('Select Startup Name', sorted(list(set(df['startup'].values.tolist()))))
    btn1 = st.sidebar.button('Find Startup Detail')
    if btn1:
        load_startup_detail(name)

elif st.session_state.selected_opn == 'Investors':
    st.header('Investors')
    investors = list(set(df['investor'].str.split(',').sum()))
    if '' in investors:
        investors.remove('')
    if ' & Others' in investors:
        investors.remove(' & Others')
    name = st.sidebar.selectbox('Select Investor', sorted(investors))
    if 'name' not in st.session_state:
        st.session_state.name = ""
    if st.session_state.name != name:
        st.session_state.name = name
        if 'clicked' in st.session_state:
            st.session_state.clicked = False
    if 'clicked' not in st.session_state:
        st.session_state.clicked = False
    btn = st.sidebar.button('Find Investor Detail')
    if btn | st.session_state.clicked:
        st.session_state.clicked = True
        load_investor_detail(name)
