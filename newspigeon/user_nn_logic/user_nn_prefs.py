# ----------------------------------------------------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------------------------------------------------


import numpy as np
import torch.nn as nn
import torch


# ----------------------------------------------------------------------------------------------------------------------
# Static Methods
# ----------------------------------------------------------------------------------------------------------------------


# This method is important for reading the Excel files, since pandas reads the xl files as strings
def to_float_list(string: str):
    string = string.strip("[]")
    values = string.split()
    float_list = [float(x) for x in values]
    np_list = np.array(float_list)

    return np_list


# ----------------------------------------------------------------------------------------------------------------------
# Class
# ----------------------------------------------------------------------------------------------------------------------


class UserInterestModel(nn.Module):
    def __init__(self, prefs, category_ratings, subject_vectors, bias):
        super(UserInterestModel, self).__init__()

        self.user_preferences = prefs

        # In order to do gradient descent, we need to mess with the preference types a little bit
        numerical_preferences = []
        numerical_category_ratings = []

        # Changing the user preferences to floats and getting rid of labels
        for i in range(len(self.user_preferences)):
            temp = []
            for j in range(len(self.user_preferences[i])):
                temp.append(self.user_preferences[i][j][1]*1.0)
            numerical_preferences.append(temp)

        # Change to floats and rid of labels
        for i in range(len(category_ratings)):
            numerical_category_ratings.append(category_ratings[i][1]*1.0)

        # Padding the preferences for gradient descent
        max_length = max(len(sublist) for sublist in numerical_preferences)
        padded_prefs = [sublist + [0] * (max_length - len(sublist)) for sublist in numerical_preferences]

        # Topic weights
        self.subtopic_weights = nn.Parameter(torch.tensor(padded_prefs, requires_grad=True))
        self.topic_weights = nn.Parameter(torch.tensor(numerical_category_ratings, requires_grad=True))

        # Subject vectors
        self.subject_vectors = subject_vectors

        # bias
        self.user_bias = bias

    # Simple get method
    def get_prefs(self):
        return self.subtopic_weights, self.topic_weights

    # We are just calculating the user vector here, but in a way that the gradient can flow through
    # The whole calculation is w.r.t. the preferences, which are what will change
    # The rest of the calculation is done is user.py
    def forward(self, detached_subject_vectors):
        user_vector = torch.zeros(384)

        # for each topic weight
        for i in range(len(self.topic_weights)):
            temp_vec = torch.zeros(384, dtype=torch.double, requires_grad=True)

            # Iterate through each subtopic weight
            for j in range(len(self.user_preferences[i])):
                subject = self.user_preferences[i][j][0]

                subject_vector = detached_subject_vectors.loc[detached_subject_vectors["Subject"] == subject].iloc[0][1]
                subject_vector = torch.tensor(subject_vector, dtype=torch.double, requires_grad=True)

                # Linear combination like last time
                temp_vec = temp_vec + subject_vector * self.subtopic_weights[i][j]

            # Scaling by topic interest
            user_vector = user_vector + temp_vec * self.topic_weights[i]

        # normalizing
        user_vector = user_vector / torch.norm(user_vector)

        return user_vector


# ----------------------------------------------------------------------------------------------------------------------
#  Defunct
# ----------------------------------------------------------------------------------------------------------------------

"""
# We use this method to instantiate the user vector at the start and whenever the preferences are updated
def set_vector(preferences, category_ratings, subject_vectors):
    added_ratings = 0
    number_of_ratings = 0
    user_vec = np.zeros(384)

    # Iterates through the categories
    for i in range(len(preferences)):
        temp_array = preferences[i]
        temp_vector = np.zeros(384)

        # Finding a subject in the user's personalized subject grid
        for j in range(len(temp_array)):
            temp_df_row = subject_vectors.loc[subject_vectors["Subject"] == temp_array[j][0]]

            # If the subject exists, do linear combination and update user bias vars
            if not temp_df_row.empty:
                added_ratings += temp_array[j][1]
                number_of_ratings += 1

                temp_vector += temp_df_row.iloc[0][1] * (temp_array[j][1] / 10)
            else:
                print("No subject found in temp_df_row")

        # Scaling by category preference
        temp_vector *= category_ratings[i][1]

        user_vec += temp_vector

    # Normalizing
    vector = torch.tensor(user_vec / np.linalg.norm(user_vec))

    return vector, number_of_ratings, added_ratings
    """

# ----------------------------------------------------------------------------------------------------------------------
#  End of file
# ----------------------------------------------------------------------------------------------------------------------
