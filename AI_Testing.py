
import cohere

co = cohere.Client('HCYnZ0Csxn4dTZdQB0WV2q4K0NJ9uzgzJa4EJd4G')



def chat():


    msg = input('Enter your message: ')


    response = co.chat(
        model='command-r-plus-08-2024',
        message= (reading_memory() + '\n'+ msg, # Before getting the user's msg the AI will go through the memory file
                  #file first so that the chats are consistent and previous result/msgs sent by the AI can u updated
                  # and changed with easy, Having a memory will also allow the AI to adapt as the chat goes on

    )
    with open('memory.txt', 'a') as memory:
        memory.write(f'User: {msg}')
        memory.write(f'AI Assistant: {response}')
        memory.close()
    print(response.text)



def chat_memory():
    with open('memory.txt', 'w') as memory: # every time the program runs a new file will be created and if a file already
    #exists it will be wiped clean to make room for new memory
        memory.write("Hi, You are an Email AI assistant for a business"
                     " This text will contain all of your memory on the previous chats between you and the user "
                     "\nGo through this the recent chats before you"
                     "can generate a response.")
        memory.close()



chat_memory()

def reading_memory():
    with open('memory.txt', 'r') as memory:
        return  memory.read()




while True:
    chat()



