import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df=pd.read_csv('cleaneddata.csv')
df=df[(df['paisa']!=0)]
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['year']=df['date'].dt.year
df['month']=df['date'].dt.month
st.set_page_config(page_title='Startup Analysis',page_icon='images.jpeg')



def load_startup_detail(name):
    st.header(name)
    s=str(df.groupby('startup')['industry'].sum().loc[name])
    st.subheader('Related Industry: '+s)

    
    p=str(df.groupby('startup')['subvertical'].sum().loc[name])

    if p=='0':
        st.subheader('Work is not known')
    else:
        st.subheader('Work on: '+p)

    L=list(set(df[df['startup']==name]['city'].values.tolist()))
    if(len(L)==0):
        pass
    else: 
        markdown_text = "#### Located in:\n"
        for i, item in enumerate(L, 1):
            markdown_text += f"{i}. {item}\n"

        st.markdown(markdown_text)
    
    st.header('Funds Recieved Till Now')
    bdf=df[df['startup']==name].set_index('date')[['investor','investmenttype','paisa']]
    bdf.rename(columns={'paisa':'Rs in Crore'},inplace=True)
    st.dataframe(bdf)

    st.header('Year Wise Received Funds')
    new_df=df[df['startup']==name]
    new_df=new_df.groupby('year')['paisa'].sum().reset_index()

    st.subheader('Funds Received')
    
    fig,ax=plt.subplots()
    ax.bar(new_df['year'],new_df['paisa'])
    st.pyplot(fig)
    
    # our investors
    new_df=df[df['startup']==name]
    l2=list(set(new_df['investor'].str.split(',').sum()))
    if len(l2)==0:
        pass
    else:
       st.subheader('Investors')
        # Create the horizontal ordered list with 2 non-breaking spaces
       html_line = "&nbsp;&nbsp;&nbsp;&nbsp;".join([f"{i+1}. {item}" for i, item in enumerate(l2)])

        # Display it using HTML
       st.markdown(f"<p>{html_line}</p>", unsafe_allow_html=True)



def perform_overall():
    col1,col2,col3,col4=st.columns(4)

    with col1:
        # total paisa in startup
        st.metric("Total Startups investment",str(int(df['paisa'].sum()))+'Cr')

    with col2:
        # total avg in startup
        st.metric("Avg Startups investment",str(round(df.groupby('startup')['paisa'].sum().mean()))+'Cr')

    with col3:
        # total startups 
        st.metric("Total Startups till invested",str(df['startup'].value_counts().shape[0]))

    with col4:
        # total max paisa  in single startup
        st.metric("Max Startup investment",str(int(df.groupby('startup')['paisa'].sum().sort_values(ascending=False).values[0]))+'Cr')

    st.header('MoM chart')
    s_item=st.selectbox('Choose Overall Investment on the basis of',['Money','Count'])
    if s_item=='Money':
        bdf=df.groupby(['month','year'])['paisa'].sum().reset_index()
    else:
        bdf=df.groupby(['month','year'])['paisa'].count().reset_index()

    bdf['my']=bdf['month'].astype(str)+" "+bdf['year'].astype(str)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(bdf['my'], bdf['paisa'], marker='o', color='green')

    ax.set_title("Investment Over Years")
    ax.set_xlabel("Year",rotation=90)
    ax.set_ylabel("Total Investment (Rs in crore)",rotation=90)
    ax.grid(True)
    plt.xticks(rotation=90)
    st.pyplot(fig)

    st.header('Sector Analysis')
    sector_item=st.selectbox('Sector Analysis on basis of',['Money','Count'])
    if sector_item=='Money':
        bdf=df.groupby('industry')['paisa'].sum().sort_values(ascending=False).head(8).reset_index()
    else:
        bdf=df.groupby('industry')['paisa'].count().sort_values(ascending=False).head(8).reset_index()
    bdf.rename(columns={'paisa':'Rs in crore'},inplace=True)
    fig, ax = plt.subplots()
    ax.pie(
        bdf['Rs in crore'], 
        labels=bdf['industry'], 
        autopct='%1.1f%%', 
        startangle=90, 
        shadow=True
    )
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig)


    st.header('Type of funding')
    bdf=df.groupby('investmenttype')['paisa'].sum().sort_values(ascending=False).head(5).reset_index()
    bdf.rename(columns={'paisa':'Rs in crore'},inplace=True)
    fig, ax = plt.subplots()
    ax.pie(
        bdf['Rs in crore'], 
        labels=bdf['investmenttype'], 
        autopct='%1.1f%%', 
        startangle=90, 
        shadow=True
    )
    ax.axis('equal')
    st.pyplot(fig)


    st.header('City Wise Funding')
    df['city']=df['city'].str.replace('Bengaluru','Bangalore')
    bdf=df.groupby('city')['paisa'].sum().sort_values(ascending=False).head().reset_index()
    bdf.rename(columns={'paisa':'Rs in crore'},inplace=True)
    fig, ax = plt.subplots()
    ax.pie(
        bdf['Rs in crore'], 
        labels=bdf['city'], 
        autopct='%1.1f%%', 
        startangle=90, 
        shadow=True
    )
    ax.axis('equal')
    st.pyplot(fig)

    st.header('Top Startups Year-Wise')
    temp_df=df.groupby(['startup','year'])['paisa'].sum().sort_values(ascending=False).reset_index()
    temp_df.sort_values(['year','paisa'],ascending=[True,False]).drop_duplicates('year',keep='first').set_index('year')
    temp_df.rename(columns={'paisa':'Rs in crore'},inplace=True)
    st.dataframe(temp_df.sort_values(['year','Rs in crore'],ascending=[True,False]).drop_duplicates('year',keep='first').set_index('year'))

    st.header('Top Startups Overall')
    st.dataframe(df.groupby('startup')['paisa'].sum().sort_values(ascending=False).head())


    st.header('Top Investers')
    l1=list(set(df['investor'].str.split(',').sum()))
    l2=[]
    for i in l1:    
        try:
            val=int(df[df['investor'].str.contains(i)]['paisa'].sum())
            l2.append(val)
        except:
            pass  
    l3=[(j,i) for i,j in zip(l1,l2)]
    l3=sorted(l3,reverse=True)
    l3.remove((310975,''))
    l4=[]
    for i in range(10):
        l4.append([l3[i][1],l3[i][0]])
    ndf=pd.DataFrame(l4,columns=['Investor Name',' Total Amount Invested '])
    st.dataframe(ndf)
    
    st.header('Funding HeatMap')
    # Assuming your DataFrame is already loaded as df and has 'year', 'month', 'paisa'

    st.subheader("Funding Heatmap (Year vs. Month)")

    # Group by year & month → sum paisa (already in crore)
    heatmap_data = df.groupby(['year', 'month'])['paisa'].sum().unstack(fill_value=0)

    # Plot heatmap
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="YlGnBu", linewidths=0.5, ax=ax)

    # Labeling
    ax.set_title("Monthly Funding (in ₹ Crore)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Year")

    st.pyplot(fig)

     


def load_investor_detail(name):
        if name!='Choose Similar Investor':
            st.title(name)
            #  5 recent investment
            st.subheader('Recent Investments')
            temp_df=df[df['investor'].str.contains(name)]
            temp_df.rename(columns={'paisa':'Rs in crore'},inplace=True)
            st.dataframe(temp_df[['date','startup','industry','investmenttype','Rs in crore']].head().set_index('date').reset_index())

            # biggest investment
            col1,col2=st.columns(2)
            with col1:
                st.subheader('Biggest Investments in Startup')
                bdf=temp_df.groupby('startup')['Rs in crore'].sum().sort_values(ascending=False).head().reset_index()  
                fig,ax=plt.subplots()
                ax.bar(bdf['startup'],bdf['Rs in crore'])
                st.pyplot(fig)
            
            with col2:
                st.subheader('Biggest Investments in each sector')
                bdf=temp_df.groupby('industry')['Rs in crore'].sum().sort_values(ascending=False).head(15).reset_index()
                fig, ax = plt.subplots()
                ax.pie(
                        bdf['Rs in crore'], 
                        labels=bdf['industry'], 
                        autopct='%1.1f%%', 
                        startangle=90, 
                        shadow=True
                    )
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

                st.pyplot(fig)


            col1,col2 =st.columns(2)
            with col1:
                st.subheader('Biggest Investment in Each stage ')
                bdf=temp_df.groupby('investmenttype')['Rs in crore'].sum().reset_index()
                fig, ax = plt.subplots()
                ax.pie(
                    bdf['Rs in crore'], 
                    labels=bdf['investmenttype'], 
                    autopct='%1.1f%%', 
                    startangle=90, 
                    shadow=True
                )
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

                st.pyplot(fig)
            
            with col2:
                st.subheader('City Wise Investment')
                bdf=temp_df.groupby('city')['Rs in crore'].sum().reset_index()
                fig, ax = plt.subplots()
                ax.pie(
                    bdf['Rs in crore'], 
                    labels=bdf['city'], 
                    autopct='%1.1f%%', 
                    startangle=90, 
                    shadow=True
                )
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

                st.pyplot(fig)
            
           

            st.subheader('YearWise Investment')
            bdf = temp_df.groupby('year')['Rs in crore'].sum().reset_index()

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(bdf['year'], bdf['Rs in crore'], marker='o', color='green')

            ax.set_title("Investment Over Years")
            ax.set_xlabel("Year",rotation=90)
            ax.set_ylabel("Total Investment (Rs in crore)",rotation=90)
            ax.grid(True)

            st.pyplot(fig)
            


            st.subheader('Similar Investors')
            L1=sorted(set(temp_df['investor'].str.split(',').sum()))
            L1.remove(name)
            L2=list(set(df['investor'].str.split(',').sum()))
            L2.remove('')
            L2.remove(' & Others')
            common = ['Choose Similar Investor']+list(set(L1) & set(L2))
            selected_investor=st.selectbox('Choose Similar Investors',common)
            load_investor_detail(selected_investor)


        








st.sidebar.title('Startup Analysis')

if 'selected_opn' not in st.session_state:
     st.session_state.selected_opn=""


selected_opn=(st.sidebar.selectbox('What you want to do?',['Overall Analysis','StartUps','Investors']))

if(st.session_state.selected_opn!=selected_opn):
     st.session_state.selected_opn=selected_opn
     if 'clicked' in st.session_state:
          st.session_state.clicked=False

if st.session_state.selected_opn =='Overall Analysis':

    st.header('Overall Analysis')
    perform_overall()

elif st.session_state.selected_opn=='StartUps':
    
    st.header('StartUps')
    name=st.sidebar.selectbox('Select Startup Name',sorted(list(set(df['startup'].values.tolist()))))
    btn1=st.sidebar.button('Find Startup Detail')
    if btn1:
     load_startup_detail(name)

elif st.session_state.selected_opn=='Investors':
    st.header('Investors')
    
    # list laane ka funda
    investors=list(set(df['investor'].str.split(',').sum()))
    investors.remove('')
    investors.remove(' & Others')

    name=st.sidebar.selectbox('Select Investor',sorted(investors))
    if 'name' not in st.session_state:
         st.session_state.name=""

    if(st.session_state.name!=name):
         st.session_state.name=name
         if 'clicked' in st.session_state:
          st.session_state.clicked=False

    if 'clicked' not in st.session_state:
         st.session_state.clicked=False

    btn=st.sidebar.button('Find Investor Detail')
    if btn | st.session_state.clicked:
         st.session_state.clicked=True
         load_investor_detail(name)
         
