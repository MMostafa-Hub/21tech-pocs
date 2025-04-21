import streamlit as st
import requests
import json
import pandas as pd
from typing import Dict, Any, Optional

# Configure the app
st.set_page_config(
    page_title="Maintenance Assistant",
    page_icon="🔧",
    layout="wide"
)


def main():
    st.title("Maintenance Document Processor 🔧")
    st.write("Upload a maintenance document PDF to extract and process its contents")

    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        api_url = st.text_input(
            "API Endpoint",
            value="http://localhost:8000/api/maintenance/process-document/",
            help="URL of the backend API endpoint"
        )

    # Main area for file upload
    uploaded_file = st.file_uploader("Upload PDF Document", type=["pdf"])

    # Option to create in EAM
    create_in_eam = st.checkbox(
        "Create in EAM system",
        value=False,
        help="If checked, the extracted data will be created in the EAM system"
    )

    # Process button
    if st.button("Process Document", disabled=uploaded_file is None):
        if uploaded_file:
            with st.spinner("Processing document... Please wait"):
                # Call the API
                response = call_api(api_url, uploaded_file, create_in_eam)

                # Display results
                display_results(response)


def call_api(api_url: str, file, create_in_eam: bool) -> Dict:
    """Send the document to the API and return the results."""
    try:
        files = {"document": file}
        data = {"create_in_eam": str(create_in_eam).lower()}

        response = requests.post(api_url, files=files, data=data)

        # Handle response
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return {"error": response.text}

    except requests.RequestException as e:
        st.error(f"Request error: {str(e)}")
        return {"error": str(e)}
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return {"error": str(e)}


def display_results(result: Dict[str, Any]):
    """Display the results in a structured way."""
    if "error" in result:
        st.error(f"Error: {result['error']}")
        return

    st.success("Document processed successfully!")

    # Create tabs for different result sections
    tabs = st.tabs(["Extracted Data", "EAM Created Items"])

    # Tab 1: Display extracted data
    with tabs[0]:
        if "extracted_data" in result:
            data = result["extracted_data"]

            # Display maintenance schedule info
            st.header("Maintenance Schedule")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Code", data["code"])
            with col2:
                st.metric("Description", data["description"])
            with col3:
                st.metric("Duration", f"{data['duration']} minutes")

            # Display task plans
            st.header("Task Plans")
            for i, task in enumerate(data["task_plans"]):
                with st.expander(f"Task {i+1}: {task['task_code']}"):
                    st.write(f"**Description:** {task['description']}")

                    # Display checklist as table
                    if task["checklist"]:
                        st.subheader("Checklist Items")
                        checklist_data = []
                        for item in task["checklist"]:
                            checklist_data.append({
                                "ID": item["checklist_id"],
                                "Description": item["description"]
                            })
                        st.table(pd.DataFrame(checklist_data))

    # Tab 2: Display EAM created items
    with tabs[1]:
        if "created_in_eam" in result:
            st.header("Items Created in EAM")
            for task in result["created_in_eam"]:
                with st.expander(f"Task: {task['task_code']}"):
                    st.write(f"**Description:** {task['description']}")
                    st.subheader("API Response")
                    st.json(task["api_response"])

                    # Display checklists
                    if task["checklists"]:
                        st.subheader("Created Checklists")
                        for cl in task["checklists"]:
                            st.write(
                                f"- **{cl['checklist_id']}**: {cl['description']}")
        else:
            st.info(
                "No items were created in EAM. Check the 'Create in EAM system' option to create items.")


if __name__ == "__main__":
    main()
