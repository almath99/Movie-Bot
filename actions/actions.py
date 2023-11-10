# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionConfirmMovieGenre(Action):

    def name(self) -> Text:
        return "action_confirm_movie_genre"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Retrieve movie genre entity
        movie_genre = tracker.get_slot("movie_genre")  
        
        # If movie_genre entity isn't filled
        if not movie_genre:
            dispatcher.utter_message(text='You did not tell me your preferred movie genre.')
        # Return preferred movie genre
        else:
            dispatcher.utter_message(text=f"Your preferred movie genre is {movie_genre}.")
        return []



import requests
import random
import string
from bs4 import BeautifulSoup
from typing import Union

class ActionMakeMovieRecommendation(Action):

    def name(self) -> Text:
        return "action_make_movie_recommendation"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Retrieve movie genre entity
        movie_genre = tracker.get_slot("movie_genre")

        # Scrape movie recommendations for given genre from IMDb
        url = f"https://www.imdb.com/search/title/?title_type=feature&genres={movie_genre.lower()}&start=1&ref_=adv_nxt"
        response = requests.get(url)                          # Send an HTTP GET request to the IMDb website for a list of movies of the specified genre 
        soup = BeautifulSoup(response.text, 'html.parser')    # Use BeautifulSoup to parse the HTML response from the website
        movie_tags = soup.select(".lister-item-header a")     # Extract the movie title tags from the soup object
        movies = [movie.text for movie in movie_tags]         # Create a list of movie titles by iterating through the title tags and extracting their text

        # Filter only movie titles in English, to avoid bot's confusion by checking if each title is composed entirely of printable ASCII characters.
        english_titles = []
        for movie in movies:   
            if all(c in string.printable for c in movie):
                english_titles.append(movie)

        # Choose 5 random English movie titles
        recommendations = random.sample(english_titles, k=5)

        # Make movie recommendation
        if recommendations:
            recommendations_str = "\n- ".join(recommendations)
            dispatcher.utter_message(f"Here are 5 recommendations for {movie_genre} movies:\n- {recommendations_str}")
        else:
            dispatcher.utter_message("Sorry, I could not find any recommendations for that genre.")

        return []


class ActionRestart(Action):
  '''Triggers default action_restart action.'''
  
  def name(self) -> Text:
      return "action_restart"

  async def run(
      self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
  ) -> List[Dict[Text, Any]]:

      # custom behavior

      return [...]


class ActionUnlikelyIntent(Action):

    def name(self) -> Text:
        return "action_unlikely_intent"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # Get the detected intent
        detected_intent = tracker.latest_message["intent"].get("name")

        # Define a list of responses for unlikely intents
        unlikely_intent_responses = {
            "greet": ["Hello! How can I assist you today?"],
            "goodbye": ["Goodbye! Feel free to return if you have more questions."],
            "fallback": ["I'm sorry, I didn't understand. Can you please rephrase your question?"],
            # Add more intent-specific responses here
        }

        # Define a default response for unknown intents
        default_response = ["I'm not sure how to respond to that. Please ask me something else."]

        # Get the response for the detected intent or use the default response
        response = unlikely_intent_responses.get(detected_intent, default_response)

        # Send the response to the user
        dispatcher.utter_message(response[0])

        return []
        

import pymongo
from rasa_sdk import Action

# Connect to your MongoDB server or cluster
client = pymongo.MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB connection string
db = client["MovieBot"]
collection = db["user_profiles"]

class ActionCreateUserProfile(Action):
    """ It connects with MongoDB database, 
    creates User profiles and stores them on the database"""
    
    def name(self):
        return "action_create_user_profile"

    def run(self, dispatcher, tracker, domain):
        user_id = tracker.sender_id
        name = tracker.get_slot("name")
        last_name = tracker.get_slot("last_name")
        age = int(tracker.get_slot("age"))  # Convert age to an integer
        email = tracker.get_slot("email")
        favourite_genre = tracker.get_slot("favourite_genre")

        # Check if the user's profile exists in the collection
        user_profile = collection.find_one({"user_id": user_id})
        if user_profile:
            # Update the user's profile
            collection.update_one(
                {"user_id": user_id},
                {"$set": {"name": name, "last_name": last_name, "age": age, "email": email, "favourite_genre": favourite_genre}}
            )
        else:
            # Create a new user profile
            new_profile = {
                "user_id": user_id,
                "name": name,
                "last_name": last_name,
                "age": age,
                "email": email,
                "favourite_genre": favourite_genre
            }
            collection.insert_one(new_profile)

        #dispatcher.utter_message("User profile created successfully!")
        return []



class ActionAccessUserProfile(Action):
    def name(self):
        return "action_access_user_profile"

    def run(self, dispatcher, tracker, domain):
        user_id = tracker.sender_id

        # Access the user's profile
        user_profile = collection.find_one({"user_id": user_id})

        if user_profile:
            name = user_profile.get("name", "N/A")
            age = user_profile.get("age", "N/A")
            email = user_profile.get("email", "N/A")
            favourite_genre = user_profile.get("favourite_genre", "N/A")

            message = f"Name: {name}, Age: {age}, Email: {email}, Favorite Genre: {favourite_genre}"
        else:
            message = "User profile not found."

        dispatcher.utter_message(message)
        return []


import openai
from rasa_sdk import Action
from rasa_sdk.events import SlotSet

class ActionGenerateText(Action):
    """ it connects with the GPT 3.5 Turbo API and uses it for language generation. """

    def name(self):
        return "action_generate_text"

    def run(self, dispatcher, tracker, domain):
        # Replace 'YOUR_API_KEY' with your GPT-3.5 Turbo API key
        api_key = "API KEY"

        # Retrieve user input
        request = tracker.latest_message['text']

        # Make a request to GPT-3.5 Turbo for text generation
        response = openai.Completion.create(
            engine="text-davinci-003",  # Use the GPT-3.5 Turbo engine
            prompt=request,
            max_tokens=50,  # Adjust this based on your desired response length
            api_key=api_key
        )

        # Extract the generated text from the response
        generated_text = response.choices[0].text

        # Send the generated text as a response
        dispatcher.utter_message(generated_text)

        return [SlotSet("generated_text", generated_text)]
    

class UserIdentificationForm(Action):
        """ It collects the name and last name of the user,
        connects with the MongoDB database and searches for the profile there.
        If the name data exist, the the suer is identified."""

    
    def name(self):
        return "user_identification"

    def run(self, dispatcher, tracker, domain):
        name = tracker.get_slot("id_name")
        last_name = tracker.get_slot("id_last_name")

        # Convert the input names to lowercase
        name = name.lower()
        last_name = last_name.lower()
        
        # Query MongoDB to find the user profile
        user_profile = collection.find_one({
            "name": {"$regex": f"^{name}$", "$options": "i"},
            "last_name": {"$regex": f"^{last_name}$", "$options": "i"}
    })

        if user_profile:
            # Extract relevant information from the user profile
            user_profile_id = str(user_profile.get("_id"))
            user_name = user_profile.get("name")
            user_last_name = user_profile.get("last_name")
            user_age = user_profile.get("age")
            user_email = user_profile.get("email")
            user_favourite_genre = user_profile.get("favourite_genre")

            # Store the user profile ID in a slot for later use
            dispatcher.utter_message(f"Found user profile for {user_name} {user_last_name} (ID: {user_profile_id})")
        
            # Store the user profile ID in a slot for later use
            return [SlotSet("user_profile_id", user_profile_id), SlotSet("age", user_age), SlotSet("favourite_genre", user_favourite_genre)]
        else:
            dispatcher.utter_message("User profile not found.")
            return []


from rasa_sdk import Action
from rasa_sdk.events import SlotSet

class PersonalizedRecommendationAction(Action):
    """ It keeps the access to the user profile form the above "user_identification" action 
    and all the information for the user's profile. For the personalized movie recommendation
    GPT 3.5 Turbo is used. 
    If the user is under 10 years old, then the action promts GPT to recommenda only kid movies.
    If the user is under 18 years old, then the action prompts GPT to reommend teen appropriate movies.
    If the user is an adult then GPT can recommend any movie.
    The genre chosen for this recommendation is the favourite_genre of the user, as it is noted in 
    the MongoDB database."""

    
    def name(self):
        return "action_personalized_recommendation"

    def run(self, dispatcher, tracker, domain):
        # Get user information from slots
        user_age = tracker.get_slot("age")
        user_favourite_genre = tracker.get_slot("favourite_genre")

        if user_age and user_favourite_genre:
            # Create a prompt for GPT-3.5 Turbo
            if user_age < 10:
                prompt = f"Recommend kids' movies for a {user_age}-year-old who loves {user_favourite_genre} movies."
            elif user_age < 18:
                prompt = f"Recommend teen (non-adult) movies for a {user_age}-year-old who loves {user_favourite_genre} movies."
            else:
                prompt = f"Recommend movies for an adult ({user_age} years old) who loves {user_favourite_genre} movies."

            # Replace 'YOUR_API_KEY' with your GPT-3.5 Turbo API key
            api_key = "API KEY"

            # Make a request to GPT-3.5 Turbo for movie recommendations
            response = openai.Completion.create(
                engine="text-davinci-003",  # Use the GPT-3.5 Turbo engine
                prompt=prompt,
                max_tokens=50,  # Adjust this based on your desired response length
                api_key=api_key
            )

            # Extract the generated movie recommendations from the response
            recommended_movies = response.choices[0].text

            # Send the generated movie recommendations as a response
            dispatcher.utter_message(recommended_movies)
        else:
            dispatcher.utter_message("I need your age and favorite genre to make personalized recommendations.")
        
        return []



import openai
from rasa_sdk import Action
from rasa_sdk.events import SlotSet

class ActionGenerateText(Action):
    """ Same as "action_personalized_recommendation", but it the recommendation isn't based 
    on the user's favourite_genre, but the movie_genre that he chooses."""

    
    def name(self):
        return "action_personalized_recommendation_genre"

    def run(self, dispatcher, tracker, domain):
        # Replace 'YOUR_API_KEY' with your GPT-3.5 Turbo API key
        api_key = "API KEY"

        # Retrieve user input and slots
        request = tracker.latest_message['text']
        user_age = tracker.get_slot("age")
        user_favourite_genre = tracker.get_slot("movie_genre")

        if user_age and user_favourite_genre:
            # Create a prompt for GPT-3.5 Turbo based on user's age and genre
            if user_age < 10:
                prompt = f"Recommend kids' movies for a {user_age}-year-old who loves {user_favourite_genre} movies."
            elif user_age < 18:
                prompt = f"Recommend teen (non-adult) movies for a {user_age}-year-old who loves {user_favourite_genre} movies."
            else:
                prompt = f"Recommend movies for an adult ({user_age} years old) who loves {user_favourite_genre} movies."

            # Make a request to GPT-3.5 Turbo for text generation
            response = openai.Completion.create(
                engine="text-davinci-003",  # Use the GPT-3.5 Turbo engine
                prompt=prompt,
                max_tokens=50,  # Adjust this based on your desired response length
                api_key=api_key
            )

            # Extract the generated text from the response
            generated_text = response.choices[0].text

            # Send the generated text as a response
            dispatcher.utter_message(generated_text)

            return [SlotSet("generated_text", generated_text)]
        else:
            dispatcher.utter_message("I need both your age and favorite genre to provide recommendations.")
            return []



# from rasa_sdk.executor import CollectingDispatcher

# class ActionUpdateUserProfile(Action):
#     """Updates a value of the user profile. 
#     For example the User wants to change his or her age."""

#     def name(self):
#         return "action_update_user_profile"

#     def run(self, dispatcher, tracker, domain):
#         user_id = tracker.sender_id

#         # Get the field and new value from the user's message
#         field_to_update = tracker.latest_message.get("entities")[0]["entity"]  # Assuming the entity name matches the field name
#         new_value = tracker.latest_message.get("text")

#         # Update the user's profile in the MongoDB collection
#         collection.update_one(
#             {"user_id": user_id},
#             {"$set": {field_to_update: new_value}}
#         )

#         dispatcher.utter_message(f"Your {field_to_update} has been updated to {new_value}.")
#         return []


#class ActionSetNewUserProfileInfo(Action):
#    def name(self) -> Text:
#        return "action_set_new_user_profile_info"

#    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#        updating_field = tracker.get_slot("updating_field")
#        new_value = tracker.latest_message['text'].strip()
        
#        if updating_field == "name":
            # Update the name in the user's profile
#            collection.update_one(
#                {"user_id": tracker.sender_id},
#                {"$set": {"name": new_value}}
#            )
#            dispatcher.utter_message(f"Great, your name is now '{new_value}'.")
#        elif updating_field == "age":
#            try:
#                new_age = int(new_value)
#                if 0 <= new_age <= 100:
                    # Update the age in the user's profile
#                    collection.update_one(
#                        {"user_id": tracker.sender_id},
#                        {"$set": {"age": new_age}}
#                    )
#                    dispatcher.utter_message(f"Your age has been updated to {new_age}.")
#                else:
#                    dispatcher.utter_message("Please provide a valid age between 0 and 100.")
#            except ValueError:
#                dispatcher.utter_message("Please provide a valid age as a number.")
#        elif updating_field == "last_name":
            # Update the last name in the user's profile
#            collection.update_one(
#                {"user_id": tracker.sender_id},
#                {"$set": {"last_name": new_value}}
#            )
#            dispatcher.utter_message(f"Great, your last_name is now '{new_value}'.")
#        elif updating_field == "email":
            # Update the email in the user's profile
#            collection.update_one(
#                {"user_id": tracker.sender_id},
#                {"$set": {"email": new_value}}
#            )
#            dispatcher.utter_message(f"Great, your email is now '{new_value}'.")
#        elif updating_field == "favourite_genre":
            # Update the favourite genre in the user's profile
#            collection.update_one(
#                {"user_id": tracker.sender_id},
#                {"$set": {"favourite_genre": new_value}}
#            )
#            dispatcher.utter_message(f"Great, your favourite movie genre is now '{new_value}'.")
#        else:
#            dispatcher.utter_message("I'm not sure what field you're trying to update.")
        
        # Reset the updating_field slot
#        return [SlotSet("updating_field", None)]



# from rasa_sdk import Action
# from rasa_sdk.events import SlotSet
# from bson import ObjectId  # Import ObjectId

# class UpdateProfileAction(Action):
#     def name(self):
#         return "action_update_profile"

#     def run(self, dispatcher, tracker, domain):
#         # Get the new name from the user's message
#         new_name = tracker.latest_message.get('text')
#         # new_last_name = tracker.latest_message.get('text')
#         # new_age = tracker.latest_message.get('text')
#         # new_email = tracker.latest_message.get('text')
#         # new_favorite_genre = tracker.latest_message.get('text')

#         # Get the user profile ID from the slot
#         user_profile_id = tracker.get_slot("user_profile_id")

#         # Update the user's name in the MongoDB database
#         collection.update_one({"_id": ObjectId(user_profile_id)}, {"$set": {"name": new_name}})

#         # Set the updated name in the slot for future reference
#         dispatcher.utter_message(f"Your name has been updated to {new_name}.")
#         return [SlotSet("name", new_name)]





