#download bunch of library langchain...., AI libbrary and install from ENV file with API keys 

while prompt != "exit":
    prompt_1 = input()

    def save_to_txt(data: str, filename: str = "research_output.txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"--- Research Output ---\nTimestamp: {timestamp}\n\n{data}\n\n"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)
    return f"Data successfully saved to {filename}"


    def options_askedquestion(data: str, data1: int,):
        



option_prompt = ChatPromptTemplate.from_messages(
    [(
         System prompt sent to the AI Agent
"Generate a multiple-choice question based on the user's topic. 
Return the options strictly as a comma-separated list inside brackets, like this: 
[Option 1, Option 2, Option 3, Option 4] or number"
    )]
)