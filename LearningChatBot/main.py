import json
import requests #  allows for making api requests
from typing import Tuple

import spacy
from difflib import get_close_matches

# load english language model
nlp = spacy.load('en_core_web_sm')

# creates a function used by the ChatBot() function that loads the knowledge base we have
# the file path string parameter is provided in ChatBot() and is the string file name of our knowledge base
# the -> dict specifies that this function returns a dictionary, the knowledge base
def load_knowledge_base(file_path: str):
    with open(file_path, 'r') as file:  # the with keyword acts as a "when", open the file, and when you do, do this:
        data: dict = json.load(file)  # the variable data is of type dictionary, and will be the json file
    return data

# Puts the dictionary variable data into the knowledge_base file, data will be updated with user responses when
# used in the ChatBot() function
def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:  # Open the file to write
        json.dump(data, file, indent=2)  # Dump the data into the file

# Finds the best match to the user question in the knowledge base, returns either a string or None
# user_question variable is type string. questions variable is type string list
def find_best_match(user_question: str, questions: list[str]):
    matches = get_close_matches(user_question, questions, n=2, cutoff=0.6)  # matches variable type list, calls the imported get_close_matches
    # cutoff decimal is percentage relevance, 60% accuracy
    if matches:
        return matches[0]
    else:
        return None

# Recognizes entities using spacy and runs intent recognition function,
def process_user_input(user_input: str):
    doc = nlp(user_input)
    named_entities = ', '.join([ent.text for ent in doc.ents])
    print(f'Named Entities: {named_entities}')
    intent = detect_intent(user_input.lower())
    return named_entities, intent


def detect_intent(user_input: str):
    if 'weather' in user_input:
        return 'get_weather'
    elif 'news' in user_input:
        return 'get_news'
    else:
        return 'general'


# returns either string or none, answer for the question. string variable question and dictionary type knowledge_base
# in ChatBot() the question parameter is the best match that's found by calling find_best_match
def get_answer_for_question(question: str, knowledge_base: dict):
    for i in knowledge_base["questions"]:  # Cycles through knowledge base and returns the answer of the question
        if i["question"] == question:
            return i["answer"]


def get_current_weather():
    openWeatherResponse = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q=McLean,US&appid=367b28b0cdcf474da5cbc7afcbe51594&units=metric')
    weatherInfo = openWeatherResponse.json()

    if openWeatherResponse.status_code == 200:
        temperature = weatherInfo['main']['temp']
        description = weatherInfo['weather'][0]['description']
        return f'The current weather in Mclean is {description} with a temperature of {temperature * 9/5 + 32}°C.'
    else:
        return 'Unable to fetch weather information.'


def get_news_updates() -> str:
    newsApiResponse = requests.get(f'https://newsapi.org/v2/top-headlines?country=us&apiKey=08a24c91c0e446ef8f724b291198fa77')
    newsUpdates = newsApiResponse.json()

    if newsApiResponse.status_code == 200:
        articles = newsUpdates['articles']
        headlines = [article['title'] for article in articles]
        return 'Here are the latest news headlines:\n' + '\n'.join(headlines)
    else:
        return 'Unable to fetch news updates.'


def chat_bot():
    knowledge_base: dict = load_knowledge_base('knowledge_base.json')

    while True:
        user_input = input('You: ')

        if 'bye' in user_input.lower():
            print('Goodbye Brian')
            break

        named_entities, intent = process_user_input(user_input) #calls process_user_input to find and store entities and intent found in input

        combined_input = f'{user_input} {named_entities}'

        best_match = find_best_match(combined_input, [q["question"] for q in knowledge_base["questions"]])
        # ^^ best_match variable either a string or None. Cycles through every question in knowledge base to find best match
        if best_match:
            answer: str = get_answer_for_question(best_match, knowledge_base)
            print(f'Bot: {answer}')

            # Ask for feedback
            feedback = input('Did I respond well? (yes/no): ').lower()

            if feedback == 'no':
                # If feedback is "no," ask for the correct answer and update the knowledge base
                correct_answer = input('Please provide the correct answer: ')
                knowledge_base["questions"].append({"question": user_input, "answer": correct_answer})
                save_knowledge_base('knowledge_base.json', knowledge_base)
                print('Bot: Thank you for the feedback. I will learn from it.')
        else:
            if intent == 'get_weather':
                # Handle weather-related queries
                print('Bot: I can fetch the weather information for you.')
                print(get_current_weather())
            elif intent == 'get_news':
                # Handle news-related queries
                print('Bot: I can provide you with the latest news updates.')
                print(get_news_updates())
            else:
                print('Bot: I don\'t know how to respond. Can you teach me?')
                new_answer: str = input('Type the answer or "skip" to skip: ')

                if new_answer.lower() != 'skip':
                    knowledge_base["questions"].append({"question": user_input, "answer": new_answer})
                    save_knowledge_base('knowledge_base.json', knowledge_base)
                    print('Bot: Thank you! I learned a new response!')


# Initiating the chatbot functions
if __name__ == '__main__':
    chat_bot()
