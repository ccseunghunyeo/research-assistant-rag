#from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun is importing two specific tools from the langchain_community library. and it is for searching and retrieving information from Wikipedia and DuckDuckGo search engine.
#from langchain_community.utilities import WikipediaAPIWrapper is importing a utility class that provides a wrapper around the Wikipedia API, allowing for easier interaction and retrieval of information from Wikipedia in a structured manner
#from langchain_classic.tools import Tool is importing the Tool class from the langchain_classic library, which is used to define and create custom tools that can be utilized by the language model for various tasks, 
# such as saving data to a text file or performing web searches. 
#from datetime import datetime is importing the datetime class from the datetime module, which is used to work with dates and times in Python. 
# In this context, it is used to generate timestamps for when research data is saved to a text file, allowing for better organization and tracking of research outputs. 
from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_classic.tools import Tool
from datetime import datetime
import wikipedia

#Wikipedia blocks (HTTP 429) requests that use the wikipedia library's generic User-Agent.
#Wikimedia asks every client to identify itself with a name and a link, so we set one here.
wikipedia.set_user_agent("ResearchAssistantRAG/1.0 (https://github.com/ccseunghunyeo/research-assistant-rag)")


#def save_to_txt(data: str, filename: str = "research_output.txt") is a function that takes in research data as a string and an optional filename (defaulting to "research_output.txt").
# It generates a timestamp for when the data is saved, formats the data with the timestamp, and appends it to the specified text file. 
# The function returns a confirmation message indicating that the data has been successfully saved. 
#So this is basically a citation.
def save_to_txt(data: str, filename: str = "research_output.txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"--- Research Output ---\nTimestamp: {timestamp}\n\n{data}\n\n"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)
    return f"Data successfully saved to {filename}"


#save_tool = Tool( name = "save_text_to_file", func = save_to_txt, description = "Saves structured research data to a text file.") 
# is creating an instance of the Tool class named "save_text_to_file".
save_tool = Tool(
    name="save_text_to_file",
    func=save_to_txt,
    description="Saves structured research data to a text file.",
)

#search = DuckDuckGoSearchRun() is creating an instance of the DuckDuckGoSearchRun class, 
# which is responsible for performing web searches using the DuckDuckGo search engine. 
# This instance will be used to execute search queries and retrieve relevant information from the web. 
search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="search",
    func=search.run,
    description="Search the web for information",
)

#search_tool wraps the DuckDuckGo search above in a Tool so the agent knows its name ("search") and when to use it (description).
#The description matters: the LLM reads it to decide which tool to call.

#api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1000) sets up the Wikipedia connection.
# top_k_results=1 means only the single best-matching article is fetched.
# doc_content_chars_max=1000 cuts the article to 1000 characters, which keeps token usage (and cost) low.
#wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper) turns that wrapper into a tool the agent can call.
#Together, search_tool and wiki_tool are the "retrieval" part of RAG (Retrieval-Augmented Generation):
# they fetch real text from the web so the LLM answers from sources instead of only from memory.
api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1000)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

