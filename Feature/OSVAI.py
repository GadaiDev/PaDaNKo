import os
import google.generativeai as genai
genai.configure(api_key="API-KEY")
generation_config = {
  "temperature": 0.5,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
)
def ai_que(text):
    chat_session = model.start_chat(
      history=[
      ]
    )
    response = chat_session.send_message(text)
    return response.text