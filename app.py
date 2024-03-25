import streamlit as st
from notion_client import Client

# Initialize Notion client with your integration token
notion = Client(auth="secret_oJJCXuR2m8xXmIsDLTLLufKLy5BIWnh34qZPOtKjn3d")
# Notion database ID
database_id = "074eef9532b843938b5bad8a21d5435e"

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
    notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Title": {"title": [{"text": {"content": title}}]},
            "Description": {"rich_text": [{"text": {"content": description}}]},
            "Votes": {"number": 0}
        }
    )

# Function to increment an idea's vote count
def increment_vote(idea_id):
    idea = notion.pages.retrieve(page_id=idea_id)
    current_votes = idea['properties']['Votes']['number']
    notion.pages.update(
        page_id=idea_id,
        properties={"Votes": {"number": current_votes + 1}}
    )

# Streamlit layout
st.title("Idea Management App")

# Sidebar for submission form
with st.sidebar:
    st.header("Submit a New Idea")
    with st.form("idea_submission_form"):
        title = st.text_input("Title")
        description = st.text_area("Description")
        submitted = st.form_submit_button("Submit Idea")
        if submitted:
            save_new_idea(title, description)
            st.success("Idea submitted successfully!")

# Main page for idea display and voting
st.header("All Ideas")
ideas = get_all_ideas()

for idea in ideas:
    with st.container():
        st.subheader(idea['title'])
        st.write(idea['description'])
        if st.button(f"Vote ({idea['votes']})", key=f"vote_{idea['id']}"):
            increment_vote(idea['id'])
            st.experimental_rerun()  # Rerun the app to update the display
