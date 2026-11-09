# pseudocode.py - Multiple-choice quiz generator (a small RAG test)
#
# How it works:
#   1. The user types a topic (or "exit" to quit).
#   2. RETRIEVAL: we fetch real text about the topic from Wikipedia and DuckDuckGo (tools.py).
#   3. GENERATION: we send that text to the LLM (from main.py) and ask it for a multiple-choice question
#      based ONLY on that text. This is what "Retrieval-Augmented Generation" (RAG) means.
#   4. The user answers by typing the option number, we say if it was right, and save the result to a text file.
#
# Run it with:  python pseudocode.py

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# save_to_txt already exists in tools.py, so we import it instead of writing it a second time.
from tools import save_to_txt, wiki_tool, search_tool
# llm is the model set up in main.py. Importing it does NOT start the research prompt,
# because main.py only runs that inside `if __name__ == "__main__":`.
from main import llm


# QuizQuestion describes the exact shape we want back from the LLM.
# Asking for structured JSON is more reliable than parsing "[Option 1, Option 2, ...]" text by hand.
class QuizQuestion(BaseModel):
    question: str
    options: list[str]
    # We ask for the TEXT of the right answer, not its number: LLMs mix up counting from 0 vs 1,
    # but copying the text is reliable. Field(description=...) is included in the instructions the LLM sees.
    correct_answer: str = Field(description="The correct option, copied exactly from the options list")
    explanation: str

    # correct_number() works out which option number (starting at 1) matches correct_answer.
    def correct_number(self) -> int:
        cleaned = [o.strip().lower() for o in self.options]
        return cleaned.index(self.correct_answer.strip().lower()) + 1


quiz_parser = PydanticOutputParser(pydantic_object=QuizQuestion)

# option_prompt is the system prompt sent to the AI.
# {context} is filled with the Wikipedia/DuckDuckGo text, {topic} with the user's topic,
# and {num_options} with how many answer choices we want.
option_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You generate one multiple-choice question about the user's topic.
Use ONLY the facts in the context below. Give exactly {num_options} options, with exactly one correct answer.
Return only the JSON described here and no other text:
{format_instructions}

Context:
{context}""",
        ),
        ("human", "Topic: {topic}"),
    ]
).partial(format_instructions=quiz_parser.get_format_instructions())


# retrieve_context() is the "R" in RAG: it gathers source text for the topic.
# Each source is wrapped in try/except so one failing source (e.g. DuckDuckGo rate-limiting) doesn't stop the quiz.
def retrieve_context(topic: str) -> str:
    parts = []
    for name, tool in (("Wikipedia", wiki_tool), ("DuckDuckGo", search_tool)):
        try:
            parts.append(f"[{name}]\n{tool.run(topic)}")
        except Exception as e:
            print(f"(Could not search {name}: {e})")
    return "\n\n".join(parts)


# options_askedquestion(data, data1) builds one quiz question.
#   data  = the topic the user typed
#   data1 = how many answer options to generate
# option_prompt | llm | quiz_parser is a LangChain "chain": fill the prompt -> send to the LLM -> parse JSON.
def options_askedquestion(data: str, data1: int = 4) -> QuizQuestion:
    context = retrieve_context(data)
    if not context:
        raise RuntimeError("No source text found, so there is nothing to base a question on.")
    chain = option_prompt | llm | quiz_parser
    return chain.invoke({"topic": data, "num_options": data1, "context": context})


# ask_number() keeps asking until the user types a valid option number.
def ask_number(max_number: int) -> int:
    while True:
        answer = input(f"Your answer (1-{max_number}): ").strip()
        if answer.isdigit() and 1 <= int(answer) <= max_number:
            return int(answer)
        print("Please type one of the option numbers.")


def main():
    # The loop variable starts empty so `while prompt != "exit"` has something to compare on the first pass.
    prompt = ""
    while prompt != "exit":
        prompt = input("\nEnter a topic for a quiz question (or 'exit' to quit): ").strip()
        if prompt.lower() == "exit":
            break
        if not prompt:  # empty input: just ask again
            continue

        try:
            quiz = options_askedquestion(prompt, 4)
            answer_number = quiz.correct_number()  # fails if the LLM's answer isn't one of the options
        except Exception as e:
            print("Could not generate a question:", e)
            continue

        print(f"\n{quiz.question}")
        for number, option in enumerate(quiz.options, start=1):
            print(f"  {number}. {option}")

        choice = ask_number(len(quiz.options))
        correct = choice == answer_number
        print("Correct!" if correct else f"Not quite. The answer was {answer_number}. {quiz.correct_answer}")
        print("Why:", quiz.explanation)

        save_to_txt(
            f"Quiz topic: {prompt}\nQuestion: {quiz.question}\nOptions: {quiz.options}\n"
            f"Your answer: {choice} | Correct answer: {answer_number} | "
            f"{'Correct' if correct else 'Incorrect'}"
        )


if __name__ == "__main__":
    main()
