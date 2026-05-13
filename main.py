import os
import json
import time
from dotenv import load_dotenv
from google import genai

# ==========================================
# LOAD ENV
# ==========================================

load_dotenv()

# ==========================================
# GEMINI CLIENT
# ==========================================

client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)

# Recommended model
# model_name = "gemini-2.0-flash"
model_name = "gemini-2.5-flash"

# ==========================================
# SYSTEM PROMPTS
# ==========================================

HR_SYSTEM_PROMPT = """
You are a Senior HR at BlackRock.

Your job:
- Interview the candidate for Applied AI Engineer role
- Ask deep technical questions
- Focus on:
    - Production AI systems
    - RAG pipelines
    - Multi-agent AI
    - LLM orchestration
    - AI deployment
    - Vector databases
    - AI scalability
    - AI observability
- Be professional
- Ask one question at a time
- Maintain conversation context
- Internally evaluate the candidate

When interview is complete,
end with exactly:
HIRED

or

NOT ACCEPTED
"""

CANDIDATE_SYSTEM_PROMPT = """
You are an Applied AI Engineer with 2 years experience.

Your job:
- Answer professionally
- Give detailed technical answers
- Explain real-world projects
- Discuss production deployments
- Discuss architecture decisions
- Discuss RAG pipelines
- Discuss multi-agent systems
- Maintain conversational context
"""

# ==========================================
# SAVE LOGS
# ==========================================

def save_logs(history):

    with open("interview_log.json", "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

    with open("interview_log.txt", "w", encoding="utf-8") as f:

        for entry in history:

            f.write(
                f"{entry['role']}:\n{entry['content']}\n\n"
            )

    print("Logs saved successfully.\n")

# ==========================================
# GENERATE RESPONSE
# ==========================================

def generate_response(system_prompt, conversation):

    response = client.models.generate_content(
        model=model_name,
        contents=f"""
{system_prompt}

Conversation History:
{conversation}
"""
    )

    return response

# ==========================================
# MAIN INTERVIEW LOOP
# ==========================================

def run_interview():

    chat_history = []

    conversation_text = """
HR:
Good morning. Thank you for joining us today.
Let's start with your experience in production AI.
"""

    print(conversation_text)

    chat_history.append({
        "role": "HR",
        "content": conversation_text
    })

    turn_count = 0

    while True:

        turn_count += 1

        # ==================================
        # AI ENGINEER RESPONSE
        # ==================================

        try:

            candidate_response = generate_response(
                CANDIDATE_SYSTEM_PROMPT,
                conversation_text
            )

            candidate_text = candidate_response.text.strip()

            # Live token usage
            usage = getattr(candidate_response, "usage_metadata", None)

            if usage:
                print("\n[Candidate Token Usage]")
                print(usage)

            print(f"\nAI ENGINEER:\n{candidate_text}\n")

            chat_history.append({
                "role": "AI_ENGINEER",
                "content": candidate_text
            })

            conversation_text += f"\nAI ENGINEER:\n{candidate_text}\n"

        except Exception as e:

            error_message = f"Candidate Error: {str(e)}"

            print(error_message)

            chat_history.append({
                "role": "SYSTEM",
                "content": error_message
            })

            save_logs(chat_history)

            if "429" in str(e):

                print("\nQuota exceeded. Waiting 60 seconds...\n")

                time.sleep(60)

                continue

            break

        # ==================================
        # HR RESPONSE
        # ==================================

        try:

            hr_response = generate_response(
                HR_SYSTEM_PROMPT,
                conversation_text
            )

            hr_text = hr_response.text.strip()

            # Live token usage
            usage = getattr(hr_response, "usage_metadata", None)

            if usage:
                print("\n[HR Token Usage]")
                print(usage)

            print(f"\nHR:\n{hr_text}\n")

            chat_history.append({
                "role": "HR",
                "content": hr_text
            })

            conversation_text += f"\nHR:\n{hr_text}\n"

        except Exception as e:

            error_message = f"HR Error: {str(e)}"

            print(error_message)

            chat_history.append({
                "role": "SYSTEM",
                "content": error_message
            })

            save_logs(chat_history)

            if "429" in str(e):

                print("\nQuota exceeded. Waiting 60 seconds...\n")

                time.sleep(60)

                continue

            break

        # ==================================
        # FINAL DECISION
        # ==================================

        final_text = hr_text.upper()

        if (
            final_text.endswith("HIRED")
            or final_text.endswith("NOT ACCEPTED")
        ):

            print(
                f"\nInterview completed in {turn_count} rounds.\n"
            )

            break

        # Safety stop
        if turn_count >= 20:

            print("\nSafety limit reached.\n")

            break

    # ==================================
    # SAVE FINAL LOGS
    # ==================================

    save_logs(chat_history)

# ==========================================
# START
# ==========================================

if __name__ == "__main__":

    run_interview()
