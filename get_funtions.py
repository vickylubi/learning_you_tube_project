import pandas as pd

#reading the csv and json files. Each file is a different country  
def load_trending(country):
    df = pd.read_csv(f"{country}videos.csv")
#transform object data to datetime where needed. 
    df["trending_date"] = pd.to_datetime(df["trending_date"], format='%y.%d.%m')
    df["publish_time"] = pd.to_datetime(df["publish_time"])

    df1 = pd.read_json(f"{country}_category_id.json")
    categories = pd.json_normalize(df1['items'])
    categories = categories[['id', 'snippet.title']]
    categories = categories.rename(columns={'id': 'category_id', 'snippet.title': 'category_name'})
    categories['category_id'] = categories['category_id'].astype('int64')
#merge two dataframes together 
    df_merged = df.merge(categories, on='category_id', how='left')
    df_merged = df_merged.drop_duplicates(subset=['video_id', 'trending_date'], keep='last')
    return df_merged

def calc_shares(df_merged):   
#Categories shares by country 
    country_shares = df_merged['category_name'].value_counts(normalize=True)*100
#Get rid of duplicates videos to work with unique videos only
    unique_df = df_merged.drop_duplicates(subset='video_id',  keep='last')
    unique_country_shares =unique_df['category_name'].value_counts(normalize = True)*100
#Check maximum views 
    max_views = df_merged.groupby('video_id')['views'].max().reset_index()
    views_by_video = max_views.merge(
        unique_df[['video_id', 'category_name']],
        on='video_id',
        how='left'
    )
#Checking trending videos by number of views 
    print(len(views_by_video))
    print(views_by_video['category_name'].isna().sum())
#Checking views by category
    views_sum = views_by_video.groupby("category_name")["views"].sum()
    views_share = views_sum / views_sum.sum() * 100
#Concat three results in one table 
    shares = pd.concat ([country_shares, unique_country_shares, views_share],axis=1) 
    shares.columns=["appearances", "unique_videos", "views"]
    return shares

