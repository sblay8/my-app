import streamlit as st
from langchain.llms import OpenAI
from langchain.document_loaders import Docx2txtLoader
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks import get_openai_callback
from langchain.chains import SimpleSequentialChain

from langchain.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

from langchain import PromptTemplate, FewShotPromptTemplate

st.set_page_config(page_title="🦜🔗 Blog Outline Generator App")
st.title('📰⛏️ Dismantl')
openai_api_key = st.sidebar.text_input('OpenAI API Key', type='password')


# Open the text file with the correct encoding and read its contents
with open('returns article argdown.txt', 'r', encoding='utf-8') as file:
    returns_article_argdown = file.read()
# Open the text file with the correct encoding and read its contents
with open('returns article.txt', 'r', encoding='utf-8') as file:
    returns_article_text = file.read()

def generate_response(article):
  llm = OpenAI(model_name='text-davinci-003', openai_api_key=openai_api_key)
    
  #split text into parts
    
  # Read the document
  text = article

  # Split the text into paragraphs
  paragraphs = text.split('\n')

  # Combine paragraphs into parts of approximately 1000 characters each
  parts = []
  current_part = ''
  for paragraph in paragraphs:
      # If adding the next paragraph doesn't exceed the limit, add it to the current part
      if len(current_part) + len(paragraph) + 1 <= 2000:  # +1 for the newline character
          current_part += '\n' + paragraph
      else:
            # If the current part is not empty, add it to the list of parts
          if current_part:
              parts.append(current_part.strip())  # strip() removes leading/trailing whitespace
            # Start a new part with the current paragrap

          current_part = paragraph
    
      # Don't forget to add the last part
      if current_part:
        parts.append(current_part)
  # Prompt
  examples = [
    {"article": returns_article_text, "argument": returns_article_argdown},
    {"article": "here is another article", "argument": "and here is the structure"}]
  example_formatter_template = """
  article: {article}
  argument: {argument}
  """
  example_prompt = PromptTemplate(
    input_variables=["article", "argument"],
    template=example_formatter_template,
  )

  prefix="""
  You are a helpful assistant that helps people think more critically by breaking articles into their different parts of arguments, that being a summary of the text, the main arguments and their supporting evidence.
  Your outputs Use correct syntax from the Argdown coding language. Here is an example of an article and it structured in the argdown language.
  """
  suffix="""
  article: create an argument map of this article using the argdown language syntax: {part}
  argument: """

  few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix=prefix,
    suffix=suffix,
    input_variables=["part"],
    example_separator="\n\n",
  )
  
  #Run model across all parts
  
  all_parts = []
  for i, part in enumerate(parts):
    chain = LLMChain(llm=llm, prompt=few_shot_prompt)
    output = chain.run(part) 
    all_parts.append(chain.run(output))
  
  #Thesis Prompt
  template = """
  You are a helpful assistant that helps people think more critically about the content they
  read. Here is an article broken into it's key arguments and supporting evidence.
  Write out the fundmanental thesis of the argument of this text: {argument}
  """

  thesis_prompt = PromptTemplate(
      input_variables=["argument"],
      template=template,)
  thesis_prompt.format(argument=all_parts)
  thesis_chain = LLMChain(llm=llm, prompt=thesis_prompt)
   
   
  all_parts.append(thesis_chain.run(all_parts))  
  
  return st.write(all_parts)

with st.form('myform'):
  article_text = st.text_area('Input Article Text:', '')
  submitted = st.form_submit_button('Submit')
  if not openai_api_key.startswith('sk-'):
    st.warning('Please enter your OpenAI API key!', icon='⚠')
  if submitted and openai_api_key.startswith('sk-'):
    generate_response(article_text)