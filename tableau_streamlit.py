import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
st.title('Ben Reeder CIS 450 Individual Project - Restuarants and Consumer Ratings')
     
    
st.sidebar.title('Nagivation')
options = st.sidebar.radio('Pages',options = ['Introduction','Data Cleaning','Restuarant Data EDA Dashboard','Customer Data EDA Dashboard','Restuarant/Customer Features/Ratings','Logistic Regression','Recommendation System'])


def intro():
    st.subheader('This application will showcase a number of features surrounding Mexico-based restuarant and consumer data.')
    st.subheader('This data contains information on:')
    st.markdown('* General information on restuarant goers (Drinking Level, Smoker, ...)')
    st.markdown('* General metadata about the restuarants (Ambience, Cuisine, ...)')
    st.markdown('* And most importantly data pertaining to ratings given to restuarants by its patrons')
    st.markdown(f'Data is from the UCI Machine Learning Repository, link to data can be found [here](https://archive.ics.uci.edu/ml/datasets/Restaurant+%26+consumer+data)')
    
    st.subheader('This application will showcase:')
    st.markdown('* Steps taken to clean data')
    st.markdown('* General visualizations that show exploratory data analysis on the restuarants in the dataset')
    st.markdown('* General visualizations that show exploratory data analysis on the customers in the dataset')
    st.markdown('* Visualizations pertaining to particular attributes about either restuarants or customers and how they relate to the final rating given')
    st.markdown('* Logistic regression model that will predict whether a rating will be Satisfactory or Unsatisfactory based on chosen fields')
    st.markdown('* Recommender system that can recommend a restuarant based off of given consumer preferences')
def clean():
    st.title('Data Cleaning')

    st.subheader('In the dataset given, there were 9 tables that fell into three different groupings that each presented their own unique challenges in which I mitigated accordingly using SQL:')
    st.markdown('* Miscellaneous restuarant/consumser data (6 tables): payments accepted/used, parking, cuisine/cuisine preference,  and restuarant hours')
    st.markdown('>>>   * Challenges faced: Multiple entrys if multiple values. For example a restuarantID could be duplicated 5 times if it accepted 5 payement options')
    st.markdown('* Metadata for restuarants/consumers (2 tables): Data relating to particular attributes about each restuarant or consumer')
    st.markdown(""">>>   * Challenges faced: Contained strange "?" values that couldn't be fixed using Excel's find and replace so had to utilize cast statements for each column""")
    st.markdown('* Ratings table (1 table): Contained an ID for a customer, ID for a restuarant and the rating given')
    st.markdown(">>>   * Challenges faced: Knew that because of the end goal of predicting these ratings based on user and restuarant data, I would have to clean the aforementioned tables in a way that would lend to this type of analysis")
    st.title("""Mitigating Challenges for each "grouping" """)
    st.subheader('Ratings Table:')
    st.markdown('I first did initial cleaning on the ratings table to get the average rating for each category (overall, food, and service) for each restuarant and each customer')
    st.markdown('I then later joined these to their respective main tables shown not in the next section, but the section after')
    st.subheader('Restuarants Data:')
    st.code("""-- Ratings are from 0-2 and each customer/restuarant is rated on/rates on three categories: overall, food, and service
-- This query finds the average of each of those three categories for all the ratings a restuarant got
-- Then if the overall rating is above 1 it is "Satisfactory" else "Unsatisfactory"
create view avg_res_ratings as
    with first_avg as (
        select placeID, round(avg(rating),2) as avg_rating, round(avg(food_rating),2) as avg_food, round(avg(service_rating),2) as avg_service
        from rating$ 
        group by placeID)
select *, case when avg_rating >= 1 
then 'Satisfactory' 
else 'Unsatisfactory' end as on_avg_text,
case when avg_rating >=1 
then 1 
else 0 end as on_avg_bin
from first_avg""",'sql')
    st.subheader('Customer Data:')
    st.code("""--similar concept as above for customers
create view avg_user_ratings as
    with first_avg as (
        select userID, round(avg(rating),2) as avg_rating, round(avg(food_rating),2) as avg_food, round(avg(service_rating),2) as avg_service
        from rating$
        group by userID)
select *, case when avg_rating >= 1 
then 'Satisfactory' 
else 'Unsatisfactory' end as on_avg_text,
case when avg_rating >=1 
then 1 
else 0 end as on_avg_bin
from first_avg
    """,'sql')
    st.subheader('Miscellaneous restuarant/consumser data (6 tables):')
    st.markdown('For the initial visualizations, I used the original files to showcase the true distribution of these various fields for each restuarant/customer')
    st.markdown('However, to achieve my analysis by logistic regression/recommender system I knew I needed to somehow aggregate to this and have one row per tiem a certain customer rated a restuarant')
    st.markdown('For each time this came up, I used a query similair to the one below:')
    st.code("""-- This query assigns a value of "multiple" for each restuarant/customer identifier that had multiple entries in the given table

create view new_parking as 
    with res_parking as (
    select *, count(*) over (partition by placeID) as count_park from chefmozparking$)
 
 select distinct placeID, case when placeID in (select distinct placeID from res_parking where count_park !=1) 
 then 'multiple' 
 else parking_lot end as new_parking_lot 
 from chefmozparking$;""",'sql')
    st.markdown('To validate each the records each time I did this, I used a similar query to below:')
    st.code("""-- Would look at number of records in initial table (in this case 702) and compare to number of records from above query (675)
-- Then below query would validate the number of records that were duplicates, in this case 27 (702-675 = 27)

with cte_validation as (
    select * , count(*) over (partition by placeID) as count_park from chefmozparking$)
select count(*) from cte_validation where count_park != 1""",'sql')

    st.markdown('Interesting use case for payments accepted by restuarants, wanted to be able to do analysis on whether or not they just accepted cash')
    st.code("""--slightly modified case statement in below query to accomadate above thought
create view new_accepts as 
with res_accepts as (
    select *, count(*) over (partition by placeID) as count_accepts from chefmozaccepts$)

select distinct placeID, case when placeID in (select distinct placeID from res_accepts where count_accepts !=1) 
then 'multiple' 
when Rpayment = 'cash' then 'only cash'
else 'one card available' end as new_accepts 
from chefmozaccepts$;""",'sql')
    st.subheader('Metadata for restuarants/consumers (2 tables):')
    st.markdown("""Here I utilized the previously created views and joined them to the metadata for the customers/restuarants while usings case statements to remove the "?" values """)
    st.markdown('In these queries, I utilized left joins to account for all restuarants/customers in the main tables as they were the most valuable in terms of my model to be used later on as they were the most descriptive about the particular field')
    st.markdown("""(All restuarants/customers mentioned in the "miscellaneous" tables were not in these main tables)""")
    st.subheader('Restuarants Data:')
    st.code("""
create view clean_restuarants as (
    select r.placeID,latitude,longitude,
    case when name = '?' then null else name end as name,
    case when address = '?' then null else address end as address,
    case when city = '?' then null else city end as city,
    case when state = '?' then null else state end as state,
    case when country = '?' then null else country end as country,
    case when fax = '?' then null else fax end as fax,
    case when zip = '?' then null else zip end as zip,
    case when alcohol = '?' then null else alcohol end as alcohol,
    case when smoking_area = '?' then null else smoking_area end as smoking_area,
    case when dress_code = '?' then null else dress_code end as dress_code,
    case when accessibility = '?' then null else accessibility end as accessibility,
    case when price = '?' then null else price end as price,
    case when url = '?' then null else url end as url,
    case when Rambience = '?' then null else Rambience end as ambience,
    case when franchise = '?' then null else franchise end as franchise,
    case when area = '?' then null else area end as area,
    case when other_services = '?' then null else other_services end as other_services,
    new_accepts, c.new_parking_lot as new_cuisine, p.new_parking_lot as new_parking_lot, avg_rating, avg_food, avg_service,
    on_avg_text,on_avg_bin
    from restuarant$ r
left join new_accepts a
on r.placeID = a.placeID
left join new_cuisine c
on r.placeID = c.placeID
left join new_parking p 
on r.placeID = p.placeID
left join avg_res_ratings ravg
on r.placeID = ravg.placeID)""",'sql')
    st.subheader('Customers Data:')
    st.code("""
create view user_info as (
    select u.userID, latitude, longitude,
    smoker,case when drink_level = '?' then null else drink_level end as drink_level, 
    case when dress_preference= '?' then null else dress_preference end as dress_preference, 
    case when ambience = '?' then null else ambience end as ambience,
    case when transport = '?' then null else transport end as transport,
    case when marital_status = '?' then null else marital_status end as marital_status,
    case when hijos = '?' then null else hijos end as hijos,
    birth_year,
    interest,
    personality,
    religion,
    case when activity = '?' then null else activity end as activity,
    color,
    weight,
    case when budget = '?' then null else budget end as budget,
    height,
    new_user_cuisine,
    new_user_payments,
    avg_rating, avg_food, avg_service, on_avg_text,on_avg_bin
    from users u
left join user_payments p
on u.userID = p.userID
left join user_cuisine c
on u.userID = c.userID
left join avg_user_ratings av
on av.userID = u.userID)""",'sql')
    st.subheader('Final Query/Output:')
    st.markdown('I then joined the cleaned restuarant with the cleaned restuarant data along with the ratings table. This gives me all the customer data, restuarant data, as well as the rating the customer gave the restuarant, the average rating per category the customer usually gives, and the average rating per category the restuarant usually gets')
    st.code("""
create view user_restuarant_rating_data_full as 
    select rat.userID, smoker, drink_level,dress_preference, u.ambience as user_ambience,transport,marital_status, 
    hijos, birth_year, interest,personality, religion, activity, color, weight, budget, height, new_user_cuisine,
    new_user_payments, u.avg_rating as user_avg_rating,u.avg_food as user_avg_food_rating, u.avg_service as user_avg_service_rating, 
    u.on_avg_text as user_avg_rating_text, u.on_avg_bin as user_avg_rating_bin, rat.placeID, name, address, city, country, alcohol, 
    smoking_area, dress_code,accessibility, price,  state, r.ambience as res_ambience, franchise, area, other_services, 
    new_accepts as res_accept_pay, new_cuisine as res_cuisine, new_parking_lot as res_parking,r.avg_rating as res_avg_rating, 
    r.avg_food as res_avg_food, r.avg_service as res_avg_service, r.on_avg_text as res_avg_rating_text, r.on_avg_bin as res_avg_rating_bin, 
    rating as cus_res_rating, food_rating as cus_res_food_rating, service_rating as cus_res_service_rating from  rating$ rat
left join user_info u
on rat.userID = u.userID
left join clean_restuarants r
on r.placeID = rat.placeID""",'sql')
    st.subheader('Final Table:')
    st.markdown('Head of Data:')
    full_df = pd.read_csv('Customers and Restuarants CSV.csv', encoding=  'latin')
    st.write(full_df.head())
    st.markdown('General Descriptive Statistics:')
    st.write(full_df.describe())
def rest():
    st.title('Restuarant EDA Dashboard')
    st.markdown('Click in bottom right-hand corner of dashboard to view dashboard in full-screen mode')
    html_temp = """
    <div class='tableauPlaceholder' id='viz1658116504312' style='position: relative'><noscript><a href='#'><img alt=' ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Re&#47;RestuarantsandCustomers&#47;RestuarantsFeaturesOverview&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='RestuarantsandCustomers&#47;RestuarantsFeaturesOverview' /><param name='tabs' value='yes' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Re&#47;RestuarantsandCustomers&#47;RestuarantsFeaturesOverview&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /><param name='filter' value='publish=yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1658116504312');                    var vizElement = divElement.getElementsByTagName('object')[0];                    if ( divElement.offsetWidth > 800 ) { vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';} else if ( divElement.offsetWidth > 500 ) { vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';} else { vizElement.style.width='100%';vizElement.style.minHeight='1850px';vizElement.style.maxHeight=(divElement.offsetWidth*1.77)+'px';}                     var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>
    """
    components.html(html_temp, width=1490, height=1200)
    max_width_str = f"max-width: 1650px;"
    st.markdown(f"""<style>.reportview-container .main .block-container{{{max_width_str}}}</style>""",unsafe_allow_html=True)



def cust():
    st.title('Customer EDA Dashboard')
    st.markdown('Click in bottom right-hand corner of dashboard to view dashboard in full-screen mode')
    html_temp = """
   <div class='tableauPlaceholder' id='viz1658106317830' style='position: relative'><noscript><a href='#'><img alt=' ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Re&#47;RestuarantsandCustomers&#47;UserProfiles&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='RestuarantsandCustomers&#47;UserProfiles' /><param name='tabs' value='yes' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Re&#47;RestuarantsandCustomers&#47;UserProfiles&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /><param name='filter' value='publish=yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1658106317830');                    var vizElement = divElement.getElementsByTagName('object')[0];                    if ( divElement.offsetWidth > 800 ) { vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';} else if ( divElement.offsetWidth > 500 ) { vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';} else { vizElement.style.width='100%';vizElement.style.minHeight='1850px';vizElement.style.maxHeight=(divElement.offsetWidth*1.77)+'px';}                     var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>
    """
    components.html(html_temp, width=1490, height=1200)
    max_width_str = f"max-width: 1650px;"
    st.markdown(f"""<style>.reportview-container .main .block-container{{{max_width_str}}}</style>""",unsafe_allow_html=True)

def rat():
    st.title('Restuarant/Customer Features/Ratings')
    st.subheader('In progress...')
def logistic():
    st.title('Logistic Regression to predict Satisfactory/Unsatisfactory')
    st.subheader('In progress...')
def rec_sys():
    st.title('Recommendation System')
    st.subheader('In progress...')

if options == 'Introduction':
    intro()

elif options == 'Restuarant Data EDA Dashboard':
    rest()

elif options == 'Customer Data EDA Dashboard':
    cust()
elif options == 'Restuarant/Customer Features/Ratings':
    rat()

elif options == 'Data Cleaning':
    clean()
elif options == 'Logistic Regression':
    logistic()
elif options == 'Recommendation System':
    rec_sys()
