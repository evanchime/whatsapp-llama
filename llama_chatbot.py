import langchain
from langchain_community.llms import Replicate
from flask import Flask, make_response
from flask import request
import os
from dotenv import load_dotenv
import requests
import json
from langchain_community.chat_message_histories.redis import RedisChatMessageHistory
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_experimental.chat_models import Llama2Chat
from langchain_core.runnables import ConfigurableFieldSpec

# Load the environment variables from the .env file
load_dotenv('.env')

class WhatsAppClient:
    API_URL = "https://graph.facebook.com/v18.0/"
    WHATSAPP_API_TOKEN = os.environ.get("WHATSAPP_API_TOKEN")
    WHATSAPP_CLOUD_NUMBER_ID = os.environ.get("WHATSAPP_CLOUD_NUMBER_ID")

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {self.WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json",
        }
        self.API_URL = self.API_URL + self.WHATSAPP_CLOUD_NUMBER_ID
        
    def send_text_message(self, message, phone_number):
        payload = {
            "messaging_product": 'whatsapp',
            "to": phone_number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        response = requests.post(f"{self.API_URL}/messages", json=payload, headers=self.headers)
        return response.status_code

# Load the Llama 2 model
llama2_13b_chat = "meta/llama-2-13b-chat:f4e2de70d66816a838a89eeeb621910adffb0dd0baba3976c96980970978018d"
# llama2_70b_chat = "meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3"

llm = Replicate(
    model=llama2_13b_chat, 
    # model=llama2_70b_chat,
    model_kwargs={"temperature": 0.01, "top_p": 1, "max_new_tokens":500}
)

model = Llama2Chat(llm=llm)

client = WhatsAppClient()
app = Flask(__name__)

system_prompt = f"""
You're a helpful assistant. Always start the conversation using the \
text delimited by triple backticks as is. Answer questions as comprehensively \
and informatively as possible, but be brief. If a question lacks clarity or \
factual grounding, explain the limitations instead of providing inaccurate information. \
If you don't know the answer, say that you don't know. If you're unsure about \
something, don't resort to making things up.
```Hello! I am an AI assistant, I Dey Play I Dey Show```
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        # ("system", "You're a helpful assistant"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

chain = prompt | model

chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id, ttl: RedisChatMessageHistory(
        session_id=session_id, ttl=ttl, url="redis://localhost:6379"
    ),
    input_messages_key="input",
    history_messages_key="history",
    history_factory_config=[
        ConfigurableFieldSpec(
            id="session_id",
            annotation=str,
            name="Session ID",
            description="Unique identifier for the session.",
            default="",
            is_shared=True,
        ),
        ConfigurableFieldSpec(
            id="ttl",
            annotation=str,
            name="TTL",
            description="Time to live for the session.",
            default="",
            is_shared=True,
        ),
    ],
)

@app.route("/")
def hello_llama():
    return "<p>Hello Llama 2</p>"

@app.route("/webhook", methods=["GET"])
def webhook_get():
    if request.method == "GET":
        if (
            request.args.get("hub.mode") == "subscribe"
            and request.args.get("hub.verify_token") == os.environ.get("META_VERIFY_TOKEN")
        ):
            return make_response(request.args.get("hub.challenge"), 200)
        else:
            return make_response("Forbidden", 403)

@app.route('/webhook', methods=['POST'])
def webhook_post():
  # Check the Incoming webhook message
  print(request.json)

  # info on WhatsApp text message payload: https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/payload-examples#text-messages
  if 'object' in request.json:
    if (
      'entry' in request.json and
      request.json['entry'][0]['changes'] and
      'messages' in request.json['entry'][0]['changes'][0]['value']#['messages']
    ):
      # Extract the sender's phone number from the webhook payload
      from_number = request.json['entry'][0]['changes'][0]['value']['messages'][0]['from']
      # Extract the message text from the webhook payload
      msg_body = ""
      if 'text' in request.json['entry'][0]['changes'][0]['value']['messages'][0]:
        msg_body = request.json['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
      elif 'reaction' in request.json['entry'][0]['changes'][0]['value']['messages'][0]:
        msg_body = request.json['entry'][0]['changes'][0]['value']['messages'][0]['reaction']['emoji']
      else:
        msg_body = "Sorry, we only support text messages for now.😊"

      try:
        llm_response = chain_with_history.invoke({"input":msg_body},config={"configurable": {"session_id": from_number, "ttl": 600}})
      except Exception as e:
        print('LLM error:', e)
        return make_response({'message': 'Internal server error'}, 500)
      try:
        client.send_text_message((llm_response.content), from_number)
      except Exception as e:
        print('WhatsAppClient error:', e)
        return make_response({'message': 'Internal server error'}, 500)

      # Return a '200 OK' response to all requests
      return make_response('EVENT_RECEIVED', 200)

    else:
      # Return a '204 No content for these request' if event is not a direct WhatsApp business account API text message
      return make_response('No content', 204)

  else:
    # Return a '404 Not Found' if event is not from a WhatsApp API
    return make_response('Not found', 404)

if __name__ == '__main__':
  app.run()


