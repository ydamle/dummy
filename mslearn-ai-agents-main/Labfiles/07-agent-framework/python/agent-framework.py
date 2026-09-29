import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add references
from agent_framework import Agent,  tool
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from pydantic import Field
from typing import Annotated


# MODEL_DEPLOYMENT_NAME = "gpt-5.2"
# PROJECT_ENDPOINT = 'https://ai-project123-resource.services.ai.azure.com/api/projects/ai-project123'

load_dotenv()

async def main():
    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    # Load the expnses data file
    script_dir = Path(__file__).parent
    file_path = script_dir / 'data.txt'
    with file_path.open('r') as file:
        data = file.read() + "\n"

    # Ask for a prompt
    user_prompt = input(f"Here is the expenses data in your file:\n\n{data}\n\nWhat would you like me to do with it?\n\n")
    
    # Run the async agent code
    await process_expenses_data(user_prompt, data)
    
async def process_expenses_data(prompt, expenses_data):

    # Create a foundry chat client
    client = FoundryChatClient(
        project_endpoint=os.getenv("PROJECT_ENDPOINT"),
        credential=AzureCliCredential(),
        model=os.getenv("MODEL_DEPLOYMENT_NAME")
    )

    # client = FoundryChatClient(
    #     project_endpoint=os.getenv("PROJECT_ENDPOINT"),
    #     credential=AzureCliCredential(),
    #     model_deployment_name=os.getenv("MODEL_DEPLOYMENT_NAME")
    # )
    

    # Initialize an agent with the tool and instructions
    async with(
Agent(
        client=client,
        name="Expense Processing Agent",
        tools=[submit_claim],
        instructions="""You are an AI assistant for expense claim submission.
                    At the user's request, create an expense claim and use the plug-in function to send an email to expenses@contoso.com with the subject 'Expense Claim`and a body that contains itemized expenses with a total.
                    Then confirm to the user that you've done so. Don't ask for any more information from the user, just use the data provided to create the email."""
    ) as agent):

        # Use the agent to process the expenses data
        try:
            # Build the prompt text to be submitted
            prompt_text = f"{prompt}\n\n{expenses_data}"

            #Invoke the agent for the specified thread with the messages
            response = await agent.run(prompt_text)

            # Print the response from the agent
            print(f"\nAgent Response:\n{response}\n")

        except Exception as e:
            print(f"An error occurred: {e}")

# Create a tool function for the email functionality
@tool(approval_mode = "never_required")

def submit_claim(
    to: Annotated[str, Field(description="Who to send the email to")],
    subject: Annotated[str, Field(description="The subject of the email")],
    body: Annotated[str, Field(description="The body of the email")]):
        print("\nTo: ", to)
        print("Subject: ", subject)
        print(body,"\n")

if __name__ == "__main__":
    asyncio.run(main())