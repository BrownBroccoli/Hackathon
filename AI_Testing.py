
import cohere

co = cohere.Client('HCYnZ0Csxn4dTZdQB0WV2q4K0NJ9uzgzJa4EJd4G')



def chat():


    msg = input('Enter your message: ')


    response = co.chat(
        model='command-r-plus-08-2024',
        message='Hi there',
    )
    with open('memory.txt', 'a') as memory:
        memory.write(f'User: {msg}')
        memory.write(f'AI Assistant: {response}')
        memory.close()
    print(response.text)



def chat_memory():
    with open('memory.txt', 'w') as memory:
        memory.write("Hi, You are an Email AI assistant for a business"
                     " This text will contain all of your memory on the previous chats between you and the user "
                     "\nGo through this the recent chats before you"
                     "can generate a response.")
        memory.close()



chat_memory()

while True:
    chat()