import json
import openai
from sklearn.metrics import classification_report

# Replace with your OpenAI API key
OPENAI_API_KEY = "API-Key"
openai.api_key = OPENAI_API_KEY

def create_chat_message(role, content):
    """
    Create a formatted message for the OpenAI chat API.

    Args:
    role (str): The role of the message sender (e.g., "system", "user", "assistant")
    content (str): The content of the message

    Returns:
    dict: A dictionary representing the chat message
    """
    return {"role": role, "content": content}

def get_etd_classification(messages):
    """
    Send a request to the OpenAI API to classify an ETD based on the given messages.

    Args:
    messages (list): A list of chat messages to send to the API

    Returns:
    str: The classification label for the ETD
    """
    completion = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=messages,
    )
    etd_classification = completion.choices[0].message.content
    # Extract only the first line (assuming label is on the first line)
    return etd_classification.splitlines()[0]

# Define the system message template for ETD classification
etd_classification_prompt = """
ETD Classification Prompt
You are an AI assistant tasked with classifying Electronic Theses and Dissertations (ETDs) based on the ProQuest subject categories. Given the text of an ETD, analyze its content and assign the most appropriate subject categories from the ProQuest list.

Instructions:
1. Carefully read the provided ETD text.
2. Identify the main themes, methodologies, and subject matter discussed in the ETD.
3. Compare these identified elements to the ProQuest subject categories.
4. Assign up to three subject categories that best represent the ETD's content. Choose one primary category and up to two secondary categories if applicable.
5. Provide a brief explanation (2-3 sentences) for each assigned category, citing specific elements from the ETD text that support your classification.

Output Format:
Primary Category: [Category Name]
Explanation: [Your explanation]
Secondary Category 1 (if applicable): [Category Name]
Explanation: [Your explanation]
Secondary Category 2 (if applicable): [Category Name]
Explanation: [Your explanation]

Note:
- Be as specific as possible when selecting categories. Choose subcategories over broader categories when appropriate.
- If the ETD spans multiple disciplines, prioritize the most prominent or central subject matter for the primary category.
- Consider both the content and methodology of the research when making your classification.

Now, please analyze the following ETD text and provide your classification based on the ProQuest subject categories:
"""

def classify_etd(etd_text):
    """
    Classify an ETD based on its text content.

    Args:
    etd_text (str): The text content of the ETD to be classified

    Returns:
    str: The classification result for the ETD
    """
    messages = [
        create_chat_message("system", etd_classification_prompt),
        create_chat_message("user", etd_text)
    ]
    return get_etd_classification(messages)

def main():
    # Sample ETD text (replace with actual ETD text in practice)
    sample_etd_text = """
    Title: "The Impact of Climate Change on Coral Reef Ecosystems: A Case Study of the Great Barrier Reef"

    Abstract:
    This dissertation examines the effects of climate change on coral reef ecosystems, with a particular focus on the Great Barrier Reef in Australia. Through a combination of field studies, satellite data analysis, and climate modeling, we investigate the long-term impacts of rising sea temperatures, ocean acidification, and extreme weather events on coral health, biodiversity, and ecosystem resilience. Our findings indicate significant coral bleaching events correlated with periods of elevated sea surface temperatures, as well as changes in species composition and distribution within the reef system. We also explore potential adaptation and mitigation strategies, including the role of marine protected areas and coral restoration techniques. This research contributes to the growing body of knowledge on climate change impacts on marine ecosystems and provides valuable insights for coral reef conservation and management in the face of global environmental change.
    """

    print("Classifying sample ETD...")
    classification_result = classify_etd(sample_etd_text)
    print("Classification result:")
    print(classification_result)

if __name__ == "__main__":
    main()
