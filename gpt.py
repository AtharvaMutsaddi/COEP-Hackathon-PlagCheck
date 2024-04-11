from openai import OpenAI

def getGPTResp(prb_stat:str,option:str):
  """
    option is always meant to be passes as either "code" or "writeup"
  """
  client = OpenAI(api_key="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")
  prompt=f"Give me a {option} for the following problem statement:{prb_stat}"
  content=f"Generate a complete {option} for the given question and return ONLY the {option} without any comments or any description."
  completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": content},
      {"role": "user", "content": prompt}
    ],
    # temperature=1, # to be checked...
    max_tokens=4096,
    top_p=1

  )

  return completion.choices[0].message.content

