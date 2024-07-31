#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Tue Jul  9 10:07:36 2024

@author: esteban.canas
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re

# %%ET
def process_txt_to_df(file_path, output_csv_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Initialize lists to store structured data
    date_time = []
    sender = []
    message = []

    # Process each line to extract date, sender, and message
    for line in lines:
        if ' - ' in line:
            dt, rest = line.split(' - ', 1)
            if ': ' in rest:
                sndr, msg = rest.split(': ', 1)
            else:
                sndr, msg = rest, ""
            date_time.append(dt)
            sender.append(sndr)
            message.append(msg.strip())
    
    # Create a DataFrame
    data = {'DateTime': date_time, 'Sender': sender, 'Message': message}
    df = pd.DataFrame(data)
    
    # Save the DataFrame as CSV
    df.to_csv(output_csv_path, index=False)

# Specify the path to your large text file and the desired output CSV file
input_txt_path = os.path.expanduser('El chat de los Doctores.txt')
output_csv_path = os.path.expanduser('El chat de los Doctores.csv')

# Call the function to process the text file and save it as a CSV
process_txt_to_df(input_txt_path, output_csv_path)

# %%L
df = pd.read_csv('El chat de los Doctores.csv')

# Convert the DateTime column to datetime, inferring the format
df['DateTime'] = pd.to_datetime(df['DateTime'], dayfirst=True, errors='coerce')

# Drop rows where DateTime conversion failed
df = df.dropna(subset=['DateTime'])

# Filter the DataFrame to include only messages from current month
df = df[df['DateTime'].dt.month == 7]

# Replace NaN values in the Message column with empty strings
df['Message'] = df['Message'].fillna('')

# Filter out users whose names are not phone numbers or more than two words long
def is_valid_user(sender):
    # Check if the sender is a phone number
    if re.match(r'^\+\d{1,3}\s?\d+$', sender):
        return True
    # Check if the sender has exactly two words
    if len(sender.split()) == 2:
        return True
    return False

df = df[df['Sender'].apply(is_valid_user)]

# Basic Statistics
# Number of messages per user
messages_per_user = df['Sender'].value_counts()
#print(messages_per_user)

# Number of messages per day
df['Date'] = pd.to_datetime(df['DateTime']).dt.date
messages_per_day = df['Date'].value_counts().sort_index()
#print(messages_per_day)

# Plot messages per day
messages_per_day.plot(kind='bar', figsize=(12, 6))
plt.title('Number of Messages Per Day')
plt.xlabel('Date')
plt.ylabel('Number of Messages')
plt.show()

# Text Analysis
# Combine all messages into a single text
all_messages = ' '.join(df['Message']).lower()

# Generate a word cloud
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_messages)

# Display the word cloud
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Word Cloud of All Messages')
plt.show()

# Interaction Analysis
# Calculate response times
df = df.sort_values(by='DateTime')
df['ResponseTime'] = df['DateTime'].diff().fillna(pd.Timedelta(seconds=0))

# Convert response times to seconds for easier plotting
df['ResponseTimeSeconds'] = df['ResponseTime'].dt.total_seconds()

# Plot response time distribution
plt.figure(figsize=(12, 6))
plt.hist(df['ResponseTimeSeconds'], bins=50, edgecolor='k', alpha=0.7)
plt.title('Response Time Distribution (June)')
plt.xlabel('Response Time (seconds)')
plt.ylabel('Frequency')
plt.yscale('log')  # Using a logarithmic scale for better visualization of skewed data
plt.show()

# Message Length Analysis
df['MessageLength'] = df['Message'].apply(len)
message_length_per_user = df.groupby('Sender')['MessageLength'].mean()
#print(message_length_per_user)

# Plot average message length per user
message_length_per_user.plot(kind='bar', figsize=(12, 6))
plt.title('Average Message Length Per User')
plt.xlabel('User')
plt.ylabel('Average Message Length')
plt.show()

# Count of the number of messages per sender
messages_count_per_sender = df['Sender'].value_counts()
print(messages_count_per_sender)