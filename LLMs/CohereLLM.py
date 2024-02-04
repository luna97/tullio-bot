#!/usr/bin/env python3

import cohere
# import LLMs.LLMInterface as LLMInterface

class CohereLLM:#(LLMInterface):

    def __init__(self):
        # super().__init__()
        self.co = cohere.Client('FbLvBqufuKyXooaQWUHyNdQIAzrdsYyAa5uunK8E')
        self.history = []

    def respond_to_query(self, query):
        response = self.co.chat(
            query,
            chat_history=self.history,
        )
        self.history.append({'user_name': 'User', 'text': query})
        self.history.append({'user_name': 'Chatbot', 'text': response.text})
        return response.text
