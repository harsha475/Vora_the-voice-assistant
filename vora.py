from flask import Flask, render_template_string, request, jsonify
import os
import datetime
import random
import platform
import pygame
import cv2
import numpy as np
import pytz
import requests
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from nltk.tokenize import word_tokenize
import wikipedia
import webbrowser
import pyttsx3
import speech_recognition as sr
import tensorflow as tf
from bs4 import BeautifulSoup

# Initialize Flask and NLP
app = Flask(__name__)
sia = SentimentIntensityAnalyzer()

# Initialize text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 145)

# Initialize speech recognition
recognizer = sr.Recognizer()

# Initialize pygame for music playback
pygame.init()
pygame.mixer.init()
music_dir = r"D:\Music"

# Initialize object detection model
model = None
try:
    model_url = 'http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v2_coco_2017_11_17.tar.gz'
    model_dir = tf.keras.utils.get_file('ssd_mobilenet_v2_coco_2017_11_17', model_url, untar=True)
    model_path = os.path.join(model_dir, "saved_model")
    model = tf.saved_model.load(model_path)
except Exception as e:
    print(f"Error loading model: {e}")
    model = None


"""

# Functions for Assistant
def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen(mode='microphone'):
    if mode == 'microphone':
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        try:
            print("Recognizing...")
            query = recognizer.recognize_google(audio)
            print("You said:", query)
            return query.lower().strip()
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand what you said.")
            return ""
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
            return ""
    else:
        try:
            query = input("Please enter your command: ")
            return query.lower().strip()
        except Exception as e:
            print("An error occurred:", e)
            return ""

def greet():
    current_time = datetime.datetime.now()
    hour = current_time.hour
    if 0 <= hour < 12:
        speak("Good morning, sir! What should I do now?")
    elif 12 <= hour < 18:
        speak("Good afternoon, sir! What should I do now?")
    else:
        speak("Good evening, sir! What should I do now?")

def handle_specific_questions(question):
    tokens = word_tokenize(question.lower())
    if "hello" in tokens:
        greet()
        return "Hello! How can I assist you today?"
    elif "how" in tokens and "are" in tokens and "you" in tokens:
        return "I'm doing well, thank you for asking."
    elif "joke" in tokens:
        return "Why don't scientists trust atoms? Because they make up everything!"
    elif "fact" in tokens:
        return "A group of flamingos is called a flamboyance."
    elif "thank" in tokens:
        return "You are welcome!"
    elif "bye" in tokens:
        return "Goodbye!"
    elif "wake up daddy's home" in tokens:
        return "Welcome home sir"
    elif "happy" in tokens:
        return "Well sir, What's the reason for your happiness?"
    elif "know" in tokens and "me" in tokens:
        return "Yes sir, You are Mr. Sivaji."
    else:
        return None

def analyze_sentiment(text):
    sentiment = sia.polarity_scores(text)
    if sentiment['compound'] >= 0.05:
        return "Positive"
    elif sentiment['compound'] <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def handle_command(command):
    if "play music" in command:
        return "Playing music..."
    elif "weather" in command:
        city = command.split("weather in")[-1].strip()
        return f"Fetching weather for {city}..."
    elif "wikipedia" in command:
        query = command.split("wikipedia")[-1].strip()
        try:
            summary = wikipedia.summary(query)
            return summary
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Disambiguation error: {e.options}"
        except wikipedia.exceptions.PageError:
            return "Page not found on Wikipedia."
        except Exception as e:
            return f"An error occurred: {str(e)}"
    elif "search" in command:
        query = command.split("search")[-1].strip()
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Searching Google for: {query}"
    elif "open" in command:
        app_name = command.split("open")[-1].strip()
        webbrowser.open(f"https://{app_name}.com")
        return f"Opening {app_name}."
    elif "phone" in command:
        phone_number = command.split("phone")[-1].strip()
        return trace_phone_number(phone_number)
    else:
        response = handle_specific_questions(command)
        if response:
            return response
        return "I'm not sure how to handle that command."

# Phone number trace function
def trace_phone_number(phone_number):
    try:
        parsed_number = phonenumbers.parse(phone_number)
        location = geocoder.description_for_number(parsed_number, "en")
        carrier_name = carrier.name_for_number(parsed_number, "en")
        timezones = timezone.time_zones_for_number(parsed_number)
        return f"Location: {location}, Carrier: {carrier_name}, Timezones: {', '.join(timezones)}"
    except phonenumbers.NumberParseException:
        return "Invalid phone number."

@app.route("/")
def index():
    return render_template_string(html_code)

@app.route('/assistant', methods=['POST'])
def assistant():
    if request.method == 'POST':
        data = request.get_json()
        command = data['command'].lower()
        sentiment = analyze_sentiment(command)
        response = handle_command(command)
        return jsonify({'response': response, 'sentiment': sentiment})

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
