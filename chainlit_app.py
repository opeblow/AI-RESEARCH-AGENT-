import chainlit as cl
from dotenv import load_dotenv
load_dotenv()
from app.agent import app as crag_agent
import traceback
import asyncio
@cl.on_chat_start
async def start_chat():
    cl.user_session.set("agent",crag_agent)
    await cl.Message(
        content="**Mobolaji's CRAG is ALIVE** \n\n"
                "Built By Mobolaji Opeyemi Bolatito Obinna,Corrective RAG with local PDFs = Brave Search Fallback \n\n"
                "Type your question:",
        author="CRAG SYSTEM"
    ).send()
   

@cl.on_message
async def main(message:cl.Message):
    agent=cl.user_session.get("agent")
    msg=cl.Message(content="")
    await msg.send()

    try:
        result=await asyncio.to_thread(agent.invoke,{"question":message.content})
        answer=result.get("answer","No answer generated")
        citations=result.get("citations",[])
        msg.content=answer
        await msg.update()

        if citations:
            sources_text="\n\n**Sources:**\n" + "\n".join(f" . {c}" for c in citations[:8])
            await cl.Message(content=sources_text,author="Sources").send()

        await cl.Message(
            content="\n-\nBuilt by **Mobolaji Opeyemi Bolatito Obinna** . CRAG SYSTEM\n(Corrective  Retrieval-Augmented Generation)",
            author="System"
        ).send()

    except Exception as e:
        error_msg=f"Error occurred:**\n\n{str(e)}\n\nPlease try again or rephrase your question"
        msg.content=f"Something went wrong :{str(e)}"
        await msg.update()
        print(f"Error in CRAG AGENT :{e}")
        traceback.print_exc()

        