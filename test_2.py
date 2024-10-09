import sqlite3
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table
import streamlit as st
import uuid

# Configuration
TABLE_NAME = "sample_table"  # This can be changed to any table name
ID_COLUMN = "id"  # This can be changed to any column name that serves as the primary key

# Step 2: Create a sample Streamlit app
st.set_page_config(page_title="SQLite + SQLAlchemy Streamlit App", layout="wide")

# SQLAlchemy connection setup
engine = create_engine("sqlite:///sample_data.db")
metadata = MetaData()

# Load table using SQLAlchemy with autoload
table = Table(TABLE_NAME, metadata, autoload_with=engine)

# Step 3: Load data using SQLAlchemy into a DataFrame
def load_data():
    with engine.connect() as connection:
        result = connection.execute(table.select())
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df

# Load initial data
df = load_data()
columns = [col for col in df.columns if col != ID_COLUMN]

# Step 4: Create filters for columns in the Streamlit app
st.write("### Filters")
filter_cols = st.columns(len([col for col in columns if df[col].dtype == 'object']))
filter_values = {}

for i, col in enumerate([col for col in columns if df[col].dtype == 'object']):
    with filter_cols[i]:
        filter_values[col] = st.multiselect(f"Filter by {col.capitalize()}", options=df[col].unique(), default=[])

# Apply filters
df_filtered = df.copy()
for col, values in filter_values.items():
    if values:
        df_filtered = df_filtered[df_filtered[col].isin(values)]

# Step 5: Show the data editor
st.write("### Edit Data")
df_filtered = df_filtered.reset_index(drop=True)

# Add a column selector
edited_df = st.data_editor(
    df_filtered,
    num_rows="dynamic",
    key="data_editor",
    hide_index=True,
    column_config={
        ID_COLUMN: None
    },
    use_container_width=True,
)

# After the data_editor
selected_rows = edited_df.loc[st.session_state.data_editor.get("selected_rows", [])]

# You can then use selected_rows for further operations
if st.button("Process Selected Rows"):
    st.write(f"Number of selected rows: {len(selected_rows)}")
    st.write("Selected rows:", selected_rows)

# Step 6: Save updated data to SQLite
def save_updates(updated_df):
    updated_rows = []
    added_rows = []

    # Use the "edited_df" keyed attribute to get changes directly
    edited_rows = st.session_state.data_editor.get("edited_rows", {})
    added_rows = st.session_state.data_editor.get("added_rows", [])

    with engine.connect() as connection:
        # Update existing rows
        for row_index, changes in edited_rows.items():
            # Get the id directly from the filtered DataFrame
            row_id = df_filtered.loc[int(row_index), ID_COLUMN]
            update_values = {column: changes[column] for column in changes}
            connection.execute(table.update().where(table.c[ID_COLUMN] == row_id).values(**update_values))
            updated_rows.append((row_id, update_values))

        for row in added_rows:
            insert_values = {column: row[column] for column in updated_df.columns if column != ID_COLUMN}
            insert_values[ID_COLUMN] = str(uuid.uuid4())
            connection.execute(table.insert().values(**insert_values))
            added_rows.append(insert_values)

    return updated_rows, added_rows

# Check if data was edited and save
if st.button("Save Changes"):
    updated_rows, added_rows = save_updates(edited_df)
    if updated_rows or added_rows:
        st.success(f"Updated {len(updated_rows)} rows and added {len(added_rows)} rows successfully!")
    else:
        st.info("No changes detected.")
