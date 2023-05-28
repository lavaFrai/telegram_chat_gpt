import openai


async def start_dialog(question):
    res = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ]
    )
    return res['choices'][0]['message']['content']


async def continue_dialog(data):
    res = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=data
    )
    return res['choices'][0]['message']['content']
