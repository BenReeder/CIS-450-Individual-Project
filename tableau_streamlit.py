import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from PIL import Image
import plotly.express as px
im = Image.open('ASU.jpg')
st.set_page_config(page_title='Ben Reeder CIS 450 Ind. Project', page_icon=im, layout="wide", initial_sidebar_state='expanded')
st.title('Ben Reeder CIS 450 Individual Project - Restaurants and Consumer Ratings')
max_width_str = f"max-width: 1650px;"
st.markdown(f"""<style>.reportview-container .main .block-container{{{max_width_str}}}</style>""",unsafe_allow_html=True)
     
    
st.sidebar.title('Nagivation')
options = st.sidebar.radio('Pages',options = ['Introduction','Data Cleaning','Restaurant Data EDA Dashboard','Customer Data EDA Dashboard','Logistic Regression','Decision Tree', 'Customer Ratings Analysis','Restaurant Ratings Analysis'])
st.sidebar.info('My name is Ben Reeder and I am currently studying Data Analytics at Arizona State University. This project is a part of the Data Analytics Capstone course at ASU.')


def intro():
    st.subheader('This application will showcase a number of features surrounding Mexico-based restaurant and consumer data.')
    st.subheader('This data contains information on:')
    st.markdown('* General information on restaurant goers (Drinking Level, Smoker, ...)')
    st.markdown('* General metadata about the restaurants (Ambience, Cuisine, ...)')
    st.markdown('* And most importantly data pertaining to ratings given to restaurants by its patrons')
    st.markdown(f'Data is from the UCI Machine Learning Repository, link to data can be found [here](https://archive.ics.uci.edu/ml/datasets/Restaurant+%26+consumer+data)')
    
    st.subheader('This application will showcase:')
    st.markdown('* Steps taken to clean data')
    st.markdown('* General visualizations that show exploratory data analysis on the restaurants in the dataset')
    st.markdown('* General visualizations that show exploratory data analysis on the customers in the dataset')
    st.markdown('* Visualizations pertaining to particular attributes about either restaurants or customers and how they relate to the final rating given')
    st.markdown('* Logistic regression model that will predict whether a rating will be Satisfactory or Unsatisfactory based on chosen fields')
    st.markdown('* Decision Tree that will be basis for user interactive experience that  a restaurant based off of given consumer preferences')
def clean():
    st.title('Data Cleaning')

    st.subheader('In the dataset given, there were nine tables that fell into three different groupings that each presented their own unique challenges in which I mitigated accordingly using SQL:')
    st.markdown('* Miscellaneous restaurant/consumser data (6 tables): payments accepted/used, parking, cuisine/cuisine preference,  and restaurant hours')
    st.markdown('>>>   * Challenges faced: Multiple entrys if multiple values. For example a restaurantID could be duplicated 5 times if it accepted 5 payement options')
    st.markdown('* Metadata for restaurants/consumers (2 tables): Data relating to particular attributes about each restaurant or consumer')
    st.markdown(""">>>   * Challenges faced: Contained strange "?" values that couldn't be fixed using Excel's find and replace so had to utilize cast statements for each column""")
    st.markdown('* Ratings table (1 table): Contained an ID for a customer, ID for a restaurant and the rating given for each category of overall, food, and service.')
    st.markdown(">>>   * Challenges faced: Knew that because of the end goal of predicting these ratings based on user and restaurant data, I would have to clean the aforementioned tables in a way that would lend to this type of analysis")
    st.title("""Mitigating Challenges for each "grouping" """)
    st.subheader('Ratings Table:')
    st.markdown('I first did initial cleaning on the ratings table to get the average rating for each category (overall, food, and service) for each restaurant and each customer')
    st.markdown('I then later joined these to their respective main tables shown not in the next section, but the section after')
    st.subheader('Restaurants Data:')
    st.code("""-- Ratings are from 0-2 and each customer/restaurant is rated on/rates on three categories: overall, food, and service
-- This query finds the average of each of those three categories for all the ratings a restaurant got
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
    st.subheader('Miscellaneous restaurant/consumser data (6 tables):')
    st.markdown('For the initial visualizations, I used the original files to showcase the true distribution of these various fields for each restaurant/customer')
    st.markdown('However, to achieve my analysis by logistic regression/recommender system I knew I needed to somehow aggregate this data and have one row per time a certain customer rated a restaurant')
    st.markdown('For each time this came up, I used a query similair to the one below:')
    st.code("""-- This query assigns a value of "multiple" for each restaurant/customer identifier that had multiple entries in the given table

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

    st.markdown('Interesting use case for payments accepted by restaurants, wanted to be able to do analysis on whether or not they just accepted cash')
    st.code("""--slightly modified case statement in below query to accomadate above thought
create view new_accepts as 
with res_accepts as (
    select *, count(*) over (partition by placeID) as count_accepts from chefmozaccepts$)

select distinct placeID, case when placeID in (select distinct placeID from res_accepts where count_accepts !=1) 
then 'multiple' 
when Rpayment = 'cash' then 'only cash'
else 'one card available' end as new_accepts 
from chefmozaccepts$;""",'sql')
    st.subheader('Metadata for restaurants/consumers (2 tables):')
    st.markdown("""Here I utilized the previously created views and joined them to the metadata for the customers/restaurants while usings case statements to remove the "?" values """)
    st.markdown('In these queries, I utilized left joins to account for all restaurants/customers in the main tables as they were the most valuable in terms of my model to be used later on as they were the most descriptive about the particular field')
    st.markdown("""(All restaurants/customers mentioned in the "miscellaneous" tables were not in these main tables)""")
    st.subheader('Restaurants Data:')
    st.code("""
create view clean_restaurants as (
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
    from restaurant$ r
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
    st.markdown('I then joined the cleaned restaurant with the cleaned restaurant data along with the ratings table. This gives me all the customer data, restaurant data, as well as the rating the customer gave the restaurant, the average rating per category the customer usually gives, and the average rating per category the restaurant usually gets')
    st.code("""
create view user_restaurant_rating_data_full as 
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
left join clean_restaurants r
on r.placeID = rat.placeID""",'sql')
    st.subheader('Final Table:')
    st.markdown('Head of Data:')
    full_df = pd.read_csv('Customers and Restuarants CSV.csv', encoding=  'latin')
    st.write(full_df.head())
    st.markdown('General Descriptive Statistics:')
    st.write(full_df.describe())
def rest():
    st.title('Restaurant EDA Dashboard')
    st.success('Click in bottom right-hand corner of dashboard to view dashboard in full-screen mode')
    st.info("Click X on Navigation pane in order for dashboard to correctly render")
    html_temp = """
   <div class='tableauPlaceholder' id='viz1659047050039' style='position: relative'><noscript><a href='#'><img alt=' ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Re&#47;RestuarantsandCustomers&#47;CountsbyRestaurantProfile&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='RestuarantsandCustomers&#47;CountsbyRestaurantProfile' /><param name='tabs' value='yes' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Re&#47;RestuarantsandCustomers&#47;CountsbyRestaurantProfile&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /><param name='filter' value='publish=yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1659047050039');                    var vizElement = divElement.getElementsByTagName('object')[0];                    if ( divElement.offsetWidth > 800 ) { vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';} else if ( divElement.offsetWidth > 500 ) { vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';} else { vizElement.style.width='100%';vizElement.style.minHeight='1600px';vizElement.style.maxHeight=(divElement.offsetWidth*1.77)+'px';}                     var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>
    """
    components.html(html_temp, width=1400, height=1100)
    max_width_str = f"max-width: 1650px;"
    st.markdown(f"""<style>.reportview-container .main .block-container{{{max_width_str}}}</style>""",unsafe_allow_html=True)
    st.subheader('Information Gathered From Initial Overview of Restaurant Data:')
    st.markdown('* The highest accepted payment is cash at 500 restaurants with the second highest being Visa with almost half (255)')
    st.markdown('* Almost half of the restaurants in the dataset have a designation of "no parking"')
    st.markdown('* High majority of restaurants have informal dress code, very few are casual or formal')
    st.markdown('* As this data is from Mexico, no surprise to see that Mexican cuisine is by far most prominent')
    st.markdown('* Overwhelming majority of restaurants are designated as closed (normal restaurant) as opposed to open (open-air restaurant)')

def cust():
    st.title('Customer EDA Dashboard')
    st.success('Click in bottom right-hand corner of dashboard to view dashboard in full-screen mode')
    st.info("Click X on Navigation pane in order for dashboard to correctly render")
    html_temp = """
   <div class='tableauPlaceholder' id='viz1659046972716' style='position: relative'><noscript><a href='#'><img alt=' ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Re&#47;RestuarantsandCustomers&#47;CountsbyUserProfile&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='RestuarantsandCustomers&#47;CountsbyUserProfile' /><param name='tabs' value='yes' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Re&#47;RestuarantsandCustomers&#47;CountsbyUserProfile&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /><param name='filter' value='publish=yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1659046972716');                    var vizElement = divElement.getElementsByTagName('object')[0];                    if ( divElement.offsetWidth > 800 ) { vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';} else if ( divElement.offsetWidth > 500 ) { vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';} else { vizElement.style.width='100%';vizElement.style.minHeight='1600px';vizElement.style.maxHeight=(divElement.offsetWidth*1.77)+'px';}                     var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>
    """
    components.html(html_temp, width=1400, height=1100)
    max_width_str = f"max-width: 1650px;"
    st.markdown(f"""<style>.reportview-container .main .block-container{{{max_width_str}}}</style>""",unsafe_allow_html=True)
    st.subheader('Information Gathered From Initial Overview of Customer Data:')
    st.markdown('* High majority of the consumers in this dataset are single')
    st.markdown("* Most of the consumer's personalities can be described as either thrifty-protector or hard working")
    st.markdown('* Majority of consumers are classified as being a student (also intersting to see the only high budget consumers were students)')
    st.markdown('* Highest payment method is again cash')
    st.markdown('* Few consumers who classify as those who like to dress elegantly, most are categorized as informal, formal, or no preference ')

def cus_ratings():
    st.title('Customer Ratings Analysis')
    st.success('Click in bottom right-hand corner of dashboard to view dashboard in full-screen mode')
    st.info("Click X on Navigation pane in order for dashboard to correctly render")
    html_temp = """
    <div class='tableauPlaceholder' id='viz1659046889564' style='position: relative'><noscript><a href='#'><img alt=' ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Re&#47;RestuarantsandCustomers&#47;AverageUserRatings&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='RestuarantsandCustomers&#47;AverageUserRatings' /><param name='tabs' value='yes' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Re&#47;RestuarantsandCustomers&#47;AverageUserRatings&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /><param name='filter' value='publish=yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1659046889564');                    var vizElement = divElement.getElementsByTagName('object')[0];                    if ( divElement.offsetWidth > 800 ) { vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';} else if ( divElement.offsetWidth > 500 ) { vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';} else { vizElement.style.width='100%';vizElement.style.minHeight='1600px';vizElement.style.maxHeight=(divElement.offsetWidth*1.77)+'px';}                     var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>
    """
    components.html(html_temp, width=1400, height=1100)
    max_width_str = f"max-width: 1650px;"
    st.markdown(f"""<style>.reportview-container .main .block-container{{{max_width_str}}}</style>""",unsafe_allow_html=True)
    st.subheader('Customer Ratings Insights:')
    st.markdown('* Most users give ratings around the 1 - 1.6 range')
    st.markdown("* Sushi is the highest rated cuisine, but probably doesn't have many instances in the dataset")
    st.markdown('* Mexcian cuisine, the most prominent cuisine in the dataset, has an average rating of 1.2')
    st.markdown("* The higher the user's budget is, the higher the average rating")
    st.markdown('* Users with Eco-Friendly or No interest give the highest average ratings, those with a Variety of interests by far the lowest')
    st.markdown('* Those who are widowed or have kids give low ratings in comparison to the average rating by user')
    st.markdown('* Users classified as Social Drinkers give an average rating above the mean rating throghout the dataset')
    st.markdown('* Informal users showed low average ratings unless they were social drinkers in which case they were above average')
    
def res_ratings():
    st.title('Restaurant Ratings Analysis')
    st.success('Click in bottom right-hand corner of dashboard to view dashboard in full-screen mode')
    st.info("Click X on Navigation pane in order for dashboard to correctly render")
    html_temp = """
    <div class='tableauPlaceholder' id='viz1659046913348' style='position: relative'><noscript><a href='#'><img alt=' ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Re&#47;RestuarantsandCustomers&#47;AverageRestaurantRatings&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='RestuarantsandCustomers&#47;AverageRestaurantRatings' /><param name='tabs' value='yes' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Re&#47;RestuarantsandCustomers&#47;AverageRestaurantRatings&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /><param name='filter' value='publish=yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1659046913348');                    var vizElement = divElement.getElementsByTagName('object')[0];                    if ( divElement.offsetWidth > 800 ) { vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';} else if ( divElement.offsetWidth > 500 ) { vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';} else { vizElement.style.width='100%';vizElement.style.minHeight='1600px';vizElement.style.maxHeight=(divElement.offsetWidth*1.77)+'px';}                     var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>
    """
    components.html(html_temp, width=1400, height=1100)
    max_width_str = f"max-width: 1650px;"
    st.markdown(f"""<style>.reportview-container .main .block-container{{{max_width_str}}}</style>""",unsafe_allow_html=True)
    st.subheader('Restaurant Ratings Insights:')
    st.markdown('* A variety of offered by activites led to a higher average rating')
    st.markdown('* Low price point restaurants had the lowest average rating')
    st.markdown('* Public parking and permitted smoking had a low average rating, sectional smoking seemed to have a consitently high rating')
    st.markdown("* Wasn't much of a difference between the different categories of alcohol served")
    st.markdown('* Mexican, the most prominent cuisine in the dataset, had an average rating of 1.17')

    
    
def logistic():
    st.title('Logistic Regression to predict Satisfactory/Unsatisfactory Customer Experience')
    st.subheader('Preprocessing/Testing Models')
    cus_res = pd.read_csv('Customers and Restuarants CSV.csv',encoding = 'latin')
    st.text('Initial Dataframe')
    st.dataframe(cus_res)
    cus_res = pd.read_csv('Customers and Restuarants CSV.csv',encoding = 'latin')
    cus_res['cus_res_rating_bin'] = 0
    cus_res.loc[cus_res['cus_res_rating'] >= 1, 'cus_res_rating_bin'] = 1

    X = cus_res[['user_avg_rating','user_avg_food_rating','user_avg_service_rating','user_avg_rating_bin', 'res_avg_rating', 'res_avg_food', 'res_avg_service', 'res_avg_rating_bin']]
    y = cus_res['cus_res_rating_bin']
    from sklearn.preprocessing import StandardScaler

    
    
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state= 123)
    
    from sklearn.linear_model import LogisticRegression
    logreg = LogisticRegression(max_iter=400)
    logreg.fit(X_train, y_train)
    
    

    st.code("""
    #Creating new column for Satisfactory or Unsatisfactory 
    #If rating is 0, Unsatisfactory, else Satisfactory
    cus_res = pd.read_csv('Customers and Restuarants CSV.csv',encoding = 'latin')
    cus_res['cus_res_rating_bin'] = 0
    cus_res.loc[cus_res['cus_res_rating'] >= 1, 'cus_res_rating_bin'] = 1""",'python')

    st.code("""
    # First attempt at using just the average ratings to see what the results yielded

    X = cus_res[['user_avg_rating','user_avg_food_rating','user_avg_service_rating','user_avg_rating_bin', 'res_avg_rating', 'res_avg_food', 'res_avg_service', 'res_avg_rating_bin']]
    y = cus_res['cus_res_rating_bin']
    
    #Data is already "scaled" from 0-2 range, no need to scale further
    
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X_standardized, y, test_size = 0.2, random_state= 123)
    
    from sklearn.linear_model import LogisticRegression
    logreg = LogisticRegression(max_iter=400)
    logreg.fit(X_train, y_train)
    print('Accuracy Score:', round((logreg.score(X_test, y_test) * 100),2),'%')""",'python')
    st.write('Accuracy Score:', round((logreg.score(X_test, y_test) * 100),2),'%')

    st.text('Checked the coeffecients of model')
    coef = logreg.coef_[0]
    sorted_coef_df = pd.DataFrame(coef,index = X.columns,columns = ['Coeffecients']).sort_values(by = "Coeffecients",ascending = False)
    st.write(sorted_coef_df)
    st.write('From this, we can see that the customers and the average ratings they gave had by far the highest impact')
    st.subheader('However, there were some issues that needed to be mitigated')
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    vif = pd.DataFrame()
    vif['VIF'] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
    vif['variable'] = X.columns
    st.text('All of the VIF values were extremely high, should be closer to 5')
    st.dataframe(vif)
    st.text('Also noticed that many of the variables have high correlation, especially the ones related to User ratings')
    st.plotly_chart(px.imshow(cus_res.corr(),title='Heatmap of Customer/Restaurant Features',color_continuous_scale='reds',width = 1000,height = 750,labels = {'color': True}))

    st.code("""
    #Experimented with multiple different X parameters before settling on just the User's Average Rating and the Restaurant's Average Rating
    X = cus_res[['user_avg_rating', 'res_avg_rating']]
    y = cus_res['cus_res_rating_bin']
    X_train, X_test, y_train, y_test = train_test_split(X_standardized, y, test_size = 0.2, random_state= 123)
    logreg = LogisticRegression(max_iter=400)

    logreg.fit(X_train, y_train)

    print('Accuracy Score:', round((logreg.score(X_test, y_test) * 100),2),'%')""",'python')
    X = cus_res[['user_avg_rating', 'res_avg_rating']]
    y = cus_res['cus_res_rating_bin']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state= 123)
    logreg = LogisticRegression(max_iter=400)

    logreg.fit(X_train, y_train)

    st.write('Accuracy Score:', round((logreg.score(X_test, y_test) * 100),2),'%')
    st.write('Check Coeffecients')
    coef = logreg.coef_[0]
    sorted_coef_df = pd.DataFrame(coef,index = X.columns,columns = ['Coeffecients']).sort_values(by = "Coeffecients",ascending = False)
    st.write(sorted_coef_df)
    vif = pd.DataFrame()
    vif['VIF'] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
    vif['variable'] = X.columns
    st.text('Check VIF values')
    st.write(vif)
    st.text('Check independent variable correlation')
    st.write(X.corr())
    st.text('VIF values are a little high, but correlation between variables is acceptable meaning the use of these variables are acceptable')
    st.text('ROC Curve')
    st.image('roc_log.png')
    st.subheader('Result is a logistic regression model that is able to predict whether or not a customer will find a restaurant satisfactory/unsatisfactory based on just the average rating the customer gives and the restaurant gets at ~ 87%')
    st.text('Will do further analysis and focus on what types of customers give the best ratings')
def rec_sys():
    st.title('Decision Tree')
    st.subheader('Initial Unpruned Decision Tree')
    st.code("""
    from sklearn.tree import DecisionTreeClassifier
    tree = DecisionTreeClassifier(random_state = 123)
    tree.fit(X_train, y_train)
    print('Accuracy on the training set: ',round((tree.score(X_train, y_train) * 100),2),'%')
    y_pred = tree.predict(X_test)
    cus_res = pd.read_csv('Customers and Restuarants CSV.csv',encoding = 'latin')
    print('Accuracy on the test set: ', round((accuracy_score(y_pred, y_test) *100),2),'%')""",'python')
    
    from sklearn.tree import DecisionTreeClassifier
    tree = DecisionTreeClassifier(random_state = 123)
    from sklearn.model_selection import train_test_split
    cus_res = pd.read_csv('Customers and Restuarants CSV.csv',encoding = 'latin')
    cus_res['cus_res_rating_bin'] = 0
    cus_res.loc[cus_res['cus_res_rating'] >= 1, 'cus_res_rating_bin'] = 1
    X = cus_res[['user_avg_rating', 'res_avg_rating']]
    y = cus_res['cus_res_rating_bin']
    from sklearn.metrics import accuracy_score
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2,random_state = 0 )
    tree.fit(X_train, y_train)
    cus_res = pd.read_csv('Customers and Restuarants CSV.csv',encoding = 'latin')
    st.write('Accuracy on the training set: ',round((tree.score(X_train, y_train) * 100),2),'%')
    y_pred = tree.predict(X_test)
    st.write('Accuracy on the test set: ', round((accuracy_score(y_pred, y_test) *100),2),'%')
    st.text('Need to prune decision tree to better account for possible overfitting and getting closer accuracy on test/training sets')
    st.subheader('Pruned Decision Tree')
    st.code("""
    tree_pruned = DecisionTreeClassifier(max_depth = 2, random_state = 0)
    tree_pruned.fit(X_train,y_train)
   
    y_pruned_pred = tree_pruned.predict(X_test)
    print('Accuracy on the training set: {:.3f}'.format(tree_pruned.score(X_train, y_train)*100))
    print('Accuracy on the test set: {:.3f}'.format(accuracy_score(y_pruned_pred, y_test)*100))""",'python')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2,random_state = 0 )

    tree_pruned = DecisionTreeClassifier(max_depth = 2, random_state = 0)
    tree_pruned.fit(X_train,y_train)
    y_pruned_pred = tree_pruned.predict(X_test)
    st.write('Accuracy on the pruned training set:', round((tree_pruned.score(X_train, y_train) *100),2),'%')
    st.write('Accuracy on the pruned test set:', round((accuracy_score(y_pruned_pred, y_test)* 100),2),'%')
    from sklearn.metrics import plot_roc_curve

    roc = plot_roc_curve(tree_pruned, X_test, y_test)
    st.subheader('ROC Curve')
    st.image('roc.png')
    from sklearn.tree import export_graphviz
    dot_data = export_graphviz(tree_pruned, class_names=['Unsatisfactory','Satisfactory'],
                           feature_names= ['User Average Rating','Restaurant Average Rating'],
                           filled = True,
                           out_file = None)

    
    d_tree = st.checkbox('Show Decision Tree')
    if d_tree:

        st.graphviz_chart(dot_data)
    else:
        pass
    st.header('User Interaction with Decision Tree Parameters')
    cus_rating = st.number_input('Average Customer Rating (0-2, can be a decimal)',min_value=0.0,max_value=2.0,step = .1)
    res_rating = st.number_input('Average Restaurant Rating (0-2, can be a decimal)',min_value=0.0,max_value=2.0,step = .1)
    if st.button('Run'):

        if cus_rating <= .525:
            if cus_rating <= .335:
                st.write(round(100/104 * 100 ,2),'% of customers rated a restuarant as unsatisfactory')
            else:
                st.write(round(13/22 * 100 ,2),  '% of customers rated a restuarant as unsatisfactory')
        else:
            if res_rating <= .905:
                st.write(round(80/113 * 100 ,2),  '% of customers rated a restuarant as satisfactory')
            else:
                st.write(round(632/689 * 100 ,2),  '% of customers rated a restuarant as satisfactory')
    
if options == 'Introduction':
    intro()

elif options == 'Restaurant Data EDA Dashboard':
    rest()

elif options == 'Customer Data EDA Dashboard':
    cust()
elif options == 'Customer Ratings Analysis':
    cus_ratings()
elif options == 'Restaurant Ratings Analysis':
    res_ratings()
elif options == 'Data Cleaning':
    clean()
elif options == 'Logistic Regression':
    logistic()
elif options == 'Decision Tree':
    rec_sys()

