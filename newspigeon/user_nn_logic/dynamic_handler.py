# dynamic_handler.py

import torch
from ts.torch_handler.base_handler import BaseHandler
from user_class import User  # Import your User class
from user_nn_prefs import UserInterestModel  # Import your UserInterestModel class

class DynamicHandler(BaseHandler):
    def initialize_context(self, preferences, category_ratings, subject_vectors, user_bias):
        # Initialize your neural network and user class here

        self.user_class = User(preferences, category_ratings, subject_vectors, user_bias)  # Initialize User instance
    
    def update_attributes(self, preferences, category_ratings, subject_vectors):
        self.user_class.class_set_vectorset_vector(prefs=preferences, category_ratings=category_ratings, subject_vectors=subject_vectors)

    def get_recommendations(self, articles):

        # Assuming the 'user_vector' is obtained from your User class
        user_vector = self.user_class.get_vec()

        # You can now use the user_vector for any further processing or recommendations
        # For example, you might use it to calculate recommendations using dot products with articles
        recommendations = self.user_class.get_recs(user_vector, articles)

        return recommendations  # Return recommendations as list
    
    def handle_feedback(self, article, rating):
        # Assuming feedback_data contains information about the article and rating
        article_info = article
        rating = rating

        # Process the rating and update the neural network
        self.user_class.process_rating(article_info, rating)

handler = DynamicHandler()
