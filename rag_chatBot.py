import os
from groq import Groq
from dotenv import load_dotenv
from retrieve_only import retrieve_context_for_llm
load_dotenv()

# Read key from environment (set this on your machine / server)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def ask_garden_bot(user_query: str) -> str:
    print(f"🔍 Searching manual for: '{user_query}'...")

    # Clean, LLM‑friendly context
    context_text = retrieve_context_for_llm(user_query, k=4)

    if not context_text.strip():
        return (
            "Right now I only know about the plants in my manual. "
            "Please mention one of them by name, like 'aloe vera water needs'."
        )

    system_prompt = (
        "You are an expert botanist assistant for home gardeners.\n"
        "You must answer using only the context provided.\n"
        "If the context is partially relevant, still give the best possible answer from it.\n"
        "Say \"I don't know\" only when nothing in the context is helpful.\n"
        "Be concise (2–4 sentences) and friendly."
    )

    user_message = (
        "Context:\n"
        f"{context_text}\n\n"
        "User question:\n"
        f"{user_query}\n\n"
        "Task: Using only the context, answer the question in 2–4 sentences. "
        "If the plant or problem is not covered, say you don't have enough information."
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.2,
    )

    return chat_completion.choices[0].message.content


# Optional: keep CLI mode for local testing
if __name__ == "__main__":
    print("🌿 Garden Bot (RAG + Llama) is ready! (Type 'exit' to stop)")
    print("-" * 40)
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("🌿 Bot: Happy gardening! Goodbye.")
            break
        if not user_input.strip():
            continue
        response = ask_garden_bot(user_input)
        print(f"🤖 Bot: {response}")
