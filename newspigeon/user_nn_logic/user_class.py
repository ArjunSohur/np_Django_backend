# ----------------------------------------------------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------------------------------------------------


import numpy
import numpy as np
import pandas as pd
import openpyxl
from .user_nn_prefs import UserInterestModel
import torch.nn as nn
import torch
import json
from django.db.models.query import QuerySet


# ----------------------------------------------------------------------------------------------------------------------
# Static methods
# ----------------------------------------------------------------------------------------------------------------------

# This method is important for reading the Excel files, since pandas reads the xl files as strings
def to_float_list(string: str):
    string = string.strip("[]")
    values = string.split()
    float_list = [float(x) for x in values]
    np_list = np.array(float_list)

    return np_list

def convert_subject_vector(subject_vectors):
    new_subject_vectors = []

    for sub_vec_obj in subject_vectors:
        name = sub_vec_obj.name
        vector = to_float_list(sub_vec_obj.value)
        new_subject_vectors.append([name, vector])
        
    new_subject_vectors = pd.DataFrame(new_subject_vectors, columns=["Subject", "Vector"])

    return new_subject_vectors



# We use this method to instantiate the user vector at the start and whenever the preferences are updated
def set_vector(preferences, category_ratings, subject_vectors):
    added_ratings = 0
    number_of_ratings = 0
    temp_user_vector = numpy.zeros(384)

    if isinstance(subject_vectors, QuerySet):
        subject_vectors = convert_subject_vector(subject_vectors=subject_vectors)

    # Iterates through the categories
    for i in range(len(preferences)):
        # Gets all the ratings for a certain category
        temp_array = preferences[i]

        # During active training, the temp_array is a tensor, so we need to strip it to an array to be compatible
        if torch.is_tensor(temp_array):
            temp_array = temp_array.detach().numpy().tolist()

        temp_vector = np.zeros(384)


        # Finding a subject in the user's personalized subject grid
        for j in range(len(temp_array)):
            temp_df_row = subject_vectors.loc[subject_vectors["Subject"] == temp_array[j][0]]

            # If the subject exists, do linear combination and update user bias vars
            if not temp_df_row.empty:
                added_ratings += temp_array[j][1]
                number_of_ratings += 1

                temp_vector = temp_vector + temp_df_row.iloc[0][1] * temp_array[j][1]
            else:
                print(f"No subject found in temp_df_row for: {temp_array[j][0]}")

        # Scaling by category preference
        temp_user_vector = temp_user_vector + temp_vector * category_ratings[i][1]

    # normalizing the end vector
    vector = temp_user_vector / (np.linalg.norm(temp_user_vector))

    return vector, number_of_ratings, added_ratings


# ----------------------------------------------------------------------------------------------------------------------
# Class
# ----------------------------------------------------------------------------------------------------------------------


class User:
    # Initialization class is decently self-explanatory
    def __init__(self, preferences, category_ratings, subject_vectors, bias):
        self.preferences = preferences
        self.category_ratings = category_ratings

        self.subject_vectors = []

        for sub_vec_obj in subject_vectors:
            name = sub_vec_obj.name
            vector = to_float_list(sub_vec_obj.value)
            self.subject_vectors.append([name, vector])
        
        self.subject_vectors = pd.DataFrame(self.subject_vectors, columns=["Subject", "Vector"])

        self.vector, self.num_ratings, added_ratings = set_vector(preferences=preferences,
                                                                  category_ratings=category_ratings,
                                                                  subject_vectors=self.subject_vectors)
        self.bias = bias

        self.user_nn = UserInterestModel(self.preferences, self.category_ratings, self.subject_vectors, self.bias)

    # sorting recs by dot product with articles - may change it to predicting with UserInterestModel
    def get_recs(self, articles):
        data = []
        for query in articles:
            data.append([query, to_float_list(query.vector)])
        
        data = pd.DataFrame(data)

        if np.any(np.isnan(self.vector)):
            self.reset_vector()


        recs = []

        for i in range(len(data)):
            score = abs(np.dot(data.iloc[i][1], self.vector))
            recs.append([data.iloc[i][0], score])

        recs = sorted(recs, key=lambda x: x[1], reverse=True)

        return recs

    # Gets a rating and a dataframe row
    def process_rating(self, article_info, rating):
        # self.print_prefs()

        print("-------------------------------------------------")
        print("ARTICLE INFO:")
        print(article_info)
        print("-------------------------------------------------")

        article_vector = torch.tensor(to_float_list(article_info.vector))

        # setting learning rate and optimizer
        learning_rate = 5
        criterion = nn.MSELoss()
        optimizer = torch.optim.SGD(self.user_nn.parameters(), lr=learning_rate)

        # Using the class to predict the user vector
        predicted_user_vector = self.user_nn(self.subject_vectors)

        # NEED TO SEE IF THIS RATING IS TRULY THE BEST SYSTEM - TESTING NEEDED
        dot_product = torch.dot(predicted_user_vector, article_vector)
        predicted_rating = torch.abs((2 * self.bias) * dot_product - self.user_nn.user_bias)
        true_rating = torch.tensor(rating, dtype=torch.double)

        # Also seeing if the loss is best served here
        loss = criterion(predicted_rating, true_rating)

        # descent
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # getting new prefs + setting new vector and bias
        temp_preferences, temp_category_ratings = self.user_nn.get_prefs()
        self.update_prefs(temp_preferences, temp_category_ratings)

        bias_numerator = self.bias * self.num_ratings

        self.num_ratings += 1
        self.bias = (bias_numerator + true_rating)/self.num_ratings

        self.vector, _, _, = set_vector(preferences=self.preferences, category_ratings=self.category_ratings,
                                        subject_vectors=self.subject_vectors)

        print(f"PREDICTED RATING: {predicted_rating.detach().numpy().item()}")
        print(f"ACTUAL RATING: {rating}")
        print(self.get_prefs())
        print("-------------------------------------------------")

        # self.print_prefs()
    
    def get_prefs(self):
        return self.preferences, self.category_ratings
    
     # Changing the preference numbers
    def update_prefs(self, new_pref, new_cat_rating):
        if isinstance(new_pref, torch.Tensor):
            for i in range(len(self.preferences)):
                for j in range(len(self.preferences[i])):
                    self.preferences[i][j][1] = new_pref[i][j].detach().numpy().item()

            for k in range(len(self.category_ratings)):
                self.category_ratings[k][1] = new_cat_rating[k].detach().numpy().item()
        else:
            for i in range(len(self.preferences)):
                for j in range(len(self.preferences[i])):
                    self.preferences[i][j][1] = new_pref[i][j][1]

            for k in range(len(self.category_ratings)):
                self.category_ratings[k][1] = new_cat_rating[k][1]
    
    def reset_vector(self):
        self.vector, _, _, = set_vector(preferences=self.preferences, category_ratings=self.category_ratings,
                                        subject_vectors=self.subject_vectors)


# ----------------------------------------------------------------------------------------------------------------------
# Defunct
# ----------------------------------------------------------------------------------------------------------------------
"""
def vector_subject_breakdown(article_vector, subject_vectors):
    sub_vec = np.array(subject_vectors.iloc[:, 1])

    similarities_list = []

    for i in range(len(subject_vectors)):
        cos_sim = abs(np.dot(article_vector, sub_vec[i]))

        similarities_list.append([subject_vectors.iloc[i][0], cos_sim])

    similarities_list = sorted(similarities_list, key=lambda x: x[1], reverse=True)

    for j in range(len(similarities_list)):
        print(f"{similarities_list[j][0]}: {similarities_list[j][1]}")

    return similarities_list


    def class_set_vector(self, prefs, category_ratings, subject_vectors):
        self.update_prefs(prefs, category_ratings)

        self.subject_vectors = subject_vectors
        self.vector, _, _, = set_vector(preferences=self.preferences, category_ratings=self.category_ratings,
                                        subject_vectors=self.subject_vectors)



    # get methods ------------------------------------------------------------------------------------------------------

    def print_prefs(self):

        print("-------------------------------------------------")

        for i in range(len(self.preferences)):
            print()
            print(f"TOPIC: {self.category_ratings[i]}")
            print("SUBTOPIC PREFERENCES:")
            for j in range(len(self.preferences[i])):
                print(self.preferences[i][j])

        print("-------------------------------------------------")

    def get_bias(self):
        return self.bias

    def get_vec(self):
        return self.vector
"""
# ----------------------------------------------------------------------------------------------------------------------
#  End of file
# ----------------------------------------------------------------------------------------------------------------------