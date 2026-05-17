import ollama


class LLMclient:
    client = ollama.Client()
    model = 'llama3.2:3b'

    def get_llm_response(self, query):
        prompt = f"""
        Extract the following information from the text below:

        - Name
        - Email
        - Role

        Output ONLY valid JSON formatted like this example:

        {{
          "name": "string",
          "email": "string",
          "role": "string"
        }}

        Text Input:
        {query}
        """

        response = self.client.generate(model=self.model, prompt=prompt)
        return response.response
