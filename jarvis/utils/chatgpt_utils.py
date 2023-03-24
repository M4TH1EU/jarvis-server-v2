import json
import time

import openai

chat_messages = []


def chatgpt_recognise(text):
    if len(chat_messages) == 0:
        chatgpt_init()

    print("START-TIME GPT: " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    chat_messages.append({"role": "user", "content": text})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_messages
    )

    print("END-TIME GPT: " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    response = json.loads(str(response.choices[0].message.content))
    print(response)

    return response


def chatgpt_init():
    prompt = open("utils/chatgpt_prompt_2_smaller.txt", "r").read()

    prompt.replace("{{timestamp}}", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    prompt.replace("{{location}}", "Lausanne in the canton Vaud of Switzerland")

    chat_messages.append({"role": "system", "content": prompt})
