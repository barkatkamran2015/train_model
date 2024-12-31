import mysql.connector
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Database connection
db_connection = mysql.connector.connect(
    host="mysql.hostinger.com",
    database="u857747424_classymama",
    user="u857747424_classy",
    password="Kabuljan@123"
)

cursor = db_connection.cursor()

# Load feedback and recommendations
feedback_query = "SELECT * FROM feedback"
cursor.execute(feedback_query)
feedback_data = cursor.fetchall()

recommendations_query = "SELECT * FROM fashion_recommendations"
cursor.execute(recommendations_query)
recommendations_data = cursor.fetchall()

# Convert to pandas DataFrames for processing
feedback_df = pd.DataFrame(feedback_data, columns=['id', 'query', 'recommendation_id', 'feedback_score', 'feedback_time'])
recommendations_df = pd.DataFrame(recommendations_data, columns=['id', 'occasion', 'season', 'gender', 'age_group', 'style', 'outfit_description', 'image_url', 'tags'])

# Process feedback and update scores
recommendations_df['score'] = 0
for _, row in feedback_df.iterrows():
    if row['feedback_score'] == 1:
        recommendations_df.loc[recommendations_df['id'] == row['recommendation_id'], 'score'] += 1
    elif row['feedback_score'] == -1:
        recommendations_df.loc[recommendations_df['id'] == row['recommendation_id'], 'score'] -= 1

# Update the database with new scores
for _, row in recommendations_df.iterrows():
    update_query = f"UPDATE fashion_recommendations SET score = {row['score']} WHERE id = {row['id']}"
    cursor.execute(update_query)

db_connection.commit()
cursor.close()
db_connection.close()
