import streamlit as st
from notion_client import Client

# Initialize Notion client with your integration token
notion = Client(auth="")
# Notion database ID
database_id = ""
st.write("database_id:", st.secrets["database_id"])
st.write("auth:", st.secrets["auth"])

# Function to get all ideas from your Notion database
def get_all_ideas():
    ideas = []
    query = notion.databases.query(database_id=database_id)
    for item in query['results']:
        # Initialize default values in case any field is missing
        title = "Untitled"
        description = "No Description"
        votes = 0

        # # Check and fetch the 'title' property
        # if 'title' in item['properties'] and item['properties']['title']['type'] == 'title':
        #     title_elements = item['properties']['title']['title']
        #     if title_elements:  # Check if title elements are present
        #         title = title_elements[0]['plain_text']
        
        # Check and fetch the 'title' property assuming it's a rich text field
        if 'title' in item['properties'] and item['properties']['title']['type'] == 'rich_text':
            title_elements = item['properties']['title']['rich_text']
            if title_elements:  # Check if title elements are present
                title = title_elements[0]['plain_text']

        
        # Check and fetch the 'description' property
        if 'description' in item['properties'] and item['properties']['description']['type'] == 'rich_text':
            description_elements = item['properties']['description']['rich_text']
            if description_elements:  # Check if description elements are present
                description = description_elements[0]['plain_text']
        
        # Check and fetch the 'vote' property
        if 'vote' in item['properties'] and item['properties']['vote']['type'] == 'number':
            votes = item['properties']['vote']['number'] or 0

        # Since you mentioned an 'id' field, assuming you might want to use Notion's internal ID
        # If you have a custom 'id' field, replace 'item['id']' with the custom field's access method
        idea_id = item['id']
        
        ideas.append({'id': idea_id, 'title': title, 'description': description, 'votes': votes})
    
    return ideas


# Function to save a new idea to your Notion database
def save_new_idea(title, description):
    # Create a new page in Notion with the provided title and description
    new_page = notion.pages.create(
        parent={"database_id": database_id},
        properties={
            'title': {
                'rich_text': [
                    {
                        'text': {
                            'content': title
                        }
                    }
                ]
            },
            'description': {
                'rich_text': [
                    {
                        'text': {
                            'content': description
                        }
                    }
                ]
            },
            'vote': {
                'number': 0
            }
        }
    )
    return new_page  # You can return the new_page object if needed


# Function to increment an idea's vote count
def increment_vote(idea_id):
    # Retrieve the current vote count for the idea
    page = notion.pages.retrieve(page_id=idea_id)
    
    # Check if the 'vote' property exists and is a number property
    if 'vote' in page['properties'] and 'number' in page['properties']['vote']:
        current_votes = page['properties']['vote']['number']
        
        # If current_votes is None (which can happen if no votes have been recorded yet), set it to 0
        if current_votes is None:
            current_votes = 0
        
        # Increment the vote count
        new_votes = current_votes + 1
        
        # Update the page with the new vote count
        notion.pages.update(
            page_id=idea_id,
            properties={
                "vote": {
                    "number": new_votes
                }
            }
        )
        return new_votes  # Optionally return the new vote count if needed

# Streamlit layout
st.title("Idea Management App")

# Sidebar for submission form
with st.sidebar:
    st.header("Submit a New Idea")
    with st.form("idea_submission_form"):
        title = st.text_input("Title", max_chars=50)
        description = st.text_area("Description", height=100)
        submitted = st.form_submit_button("Submit Idea")
        if submitted:
            save_new_idea(title, description)
            st.success("Idea submitted successfully!")



# Main page for idea display and voting
st.header("All Ideas")
ideas = get_all_ideas()

# Use columns to create a card-like layout
for idea in ideas:
    with st.container():
        col1, col2 = st.columns([1, 4])  # Adjust the ratio as needed
        with col1:
            st.markdown(f"### {idea['votes']}")
            if st.button("Vote", key=f"vote_{idea['id']}"):
                increment_vote(idea['id'])
                st.experimental_rerun()
        with col2:
            st.markdown(f"##### {idea['title']}")
            st.write(idea['description'])
        st.markdown("---")  # Horizontal line to separate ideas
