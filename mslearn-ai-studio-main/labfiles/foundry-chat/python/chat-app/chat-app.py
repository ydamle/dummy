import os
from dotenv import load_dotenv

# import namespaces
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


def main(): 
    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')

    try:
        # Get configuration settings 
        load_dotenv()
        azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        model_deployment = os.getenv("MODEL_DEPLOYMENT")

        # Initialize the OpenAI client
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://ai.azure.com/.default"
        )
            
        openai_client = OpenAI(
            base_url=azure_openai_endpoint,
            api_key=token_provider
        )
        
        # Track responses
        last_response_id = None

        # Loop until the user wants to quit
        while True:
            input_text = input('\nEnter a prompt (or type "quit" to exit): ')
            if input_text.lower() == "quit":
                break
            if len(input_text) == 0:
                print("Please enter a prompt.")
                continue

            # Get a response
            # completion = openai_client.chat.completions.create(
            #     model=model_deployment,
            #     messages=[
            #         {
            #             "role": "system",
            #             "content": "You are a helpful AI assistant that answers questions and provides information."
            #         },
            #         {
            #             "role": "user",
            #             "content": input_text
            #         }
            #     ]
            # )
         
            # print(completion.choices[0].message.content)

            # Get a response
            response = openai_client.responses.create(
                        model=model_deployment,
                        instructions="You are a helpful AI assistant that answers questions and provides information.",
                        input=input_text,
                        previous_response_id = last_response_id,

                        # To add streaming, add the following parameter:
                        stream=True
                    
            )
            # print(response.output_text)
            
            # last_response_id = response.id
            # print ("\nResponse ID:", last_response_id )

            for event in response:
                if event.type == "response.output_text.delta":
                    print(event.delta, end="", flush=True)
                elif event.type == "response.completed":
                    last_response_id = event.response.id
                    # print("\nResponse ID:", last_response_id)
                elif event.type == "response.error":
                    print("\nError:", event.error)
            

    except Exception as ex:
        print(ex)

if __name__ == '__main__': 
    main()
