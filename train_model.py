from flask import Flask, jsonify, request
import mysql.connector
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize Flask app
app = Flask(__name__)

# Database connection function
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="mysql.hostinger.com",
            database="u857747424_classymama",
            user="u857747424_classy",
            password="Kabuljan@123"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Endpoint to update recommendation scores
@app.route('/update_scores', methods=['POST'])
def update_scores():
    db_connection = get_db_connection()
    if db_connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = db_connection.cursor()

    try:
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
        message = "Scores updated successfully!"
        print(message)
        return jsonify({"message": message}), 200

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"error": "Failed to update scores", "details": str(err)}), 500

    finally:
        cursor.close()
        db_connection.close()

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "API is running!"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
