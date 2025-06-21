import logging

from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    Agent,
    AgentSession,
)
from livekit.agents import llm
from livekit.plugins import silero, groq

load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("voice-agent")

class VoiceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
               "You are a voice assistant created by LiveKit. Your interface with users will be voice. "
               "You should use short and concise responses, and avoiding usage of unpronouncable punctuation. "
               "You were created as a demo to showcase the capabilities of LiveKit's agents framework."
            )
        )
def prewarm(proc: JobProcess):
   proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Wait for the first participant to connect
    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")

    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        stt=groq.STT(model="whisper-large-v3"),
        llm=groq.LLM(model="llama-3.3-70b-versatile"),
        tts=groq.TTS(
        model="playai-tts",
        voice="Arista-PlayAI",
        ),
    )


    await session.start(
        agent=VoiceAgent(),
        room=ctx.room
    )  
    # The agent should be polite and greet the user when it joins :)
    await session.say("Hey, how can I help you today?", allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )

