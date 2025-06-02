# pip install openai

# from openai import OpenAI

# client = OpenAI(
#     base_url="https://ulpglj58bbjakoej.us-east-1.aws.endpoints.huggingface.cloud/v1/",
#     api_key="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"
# )

# chat_completion = client.chat.completions.create(
#     model="tgi",
#     messages=[
#         {
#             "role": "user",
#             "content": "What is deep learning?"
#         }
#     ],
#     top_p=None,
#     temperature=None,
#     max_tokens=150,
#     stream=True,
#     seed=None,
#     stop=None,
#     frequency_penalty=None,
#     presence_penalty=None
# )

# for message in chat_completion:
#     print(message.choices[0].delta.content, end="")

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="tgi",
    base_url="https://ulpglj58bbjakoej.us-east-1.aws.endpoints.huggingface.cloud/v1/",
    api_key="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",
    temperature=0.7,
    top_p=0.9,
    max_tokens=150,
)

response = llm.invoke("hi")
print(response)
