import streamlit as st
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Row:
    id: int
    values: Dict[str, str]

class AnnotatedDocument:
    def __init__(self):
        self.annotations = ["$temperature", "$pressure", "$flow_rate"]
        self.next_id = 1
        self.rows: List[Row] = []
        
        self.table_style = """
       
        """
        
        self.markdown_template = self.table_style + """
        <table class="custom-table">
            <tr>
                <th>ID</th>
                <th>Temperature (°C)</th>
                <th>Pressure (bar)</th>
                <th>Flow Rate (L/min)</th>
            </tr>
            {rows}
        </table>
        """
        
        self.row_template = """
            <tr>
                <td>{id}</td>
                <td>{temperature}</td>
                <td>{pressure}</td>
                <td>{flow_rate}</td>
            </tr>
        """

    def render_markdown(self) -> str:
        rows_html = ""
        for row in sorted(self.rows, key=lambda x: x.id):
            rows_html += self.row_template.format(
                id=row.id,
                temperature=row.values.get("$temperature", ""),
                pressure=row.values.get("$pressure", ""),
                flow_rate=row.values.get("$flow_rate", "")
            )
        return self.markdown_template.format(rows=rows_html)

def handle_edited_data(edited_df):
    new_rows = []
    next_id = 1
    
    for _, row in edited_df.iterrows():
        row_id = int(next_id if pd.isna(row["ID"]) else row["ID"])
        next_id = max(next_id, row_id) + 1
        
        values = {
            "$temperature": "" if pd.isna(row["Temperature"]) else str(row["Temperature"]),
            "$pressure": "" if pd.isna(row["Pressure"]) else str(row["Pressure"]),
            "$flow_rate": "" if pd.isna(row["Flow Rate"]) else str(row["Flow Rate"])
        }
        
        new_rows.append(Row(id=row_id, values=values))
    
    st.session_state.document.rows = new_rows
    st.session_state.document.next_id = next_id

def main():
    st.title("Real-time Annotated Table Editor")
    
    if 'document' not in st.session_state:
        st.session_state.document = AnnotatedDocument()
    
    col1, col2 = st.columns([0.4, 0.6])
    
    with col1:
        st.subheader("Data Editor")
        
        if len(st.session_state.document.rows) == 0:
            df = pd.DataFrame([{
                "ID": 1,
                "Temperature": "",
                "Pressure": "",
                "Flow Rate": ""
            }])
        else:
            df = pd.DataFrame([
                {
                    "ID": row.id,
                    "Temperature": row.values.get("$temperature", ""),
                    "Pressure": row.values.get("$pressure", ""),
                    "Flow Rate": row.values.get("$flow_rate", "")
                }
                for row in st.session_state.document.rows
            ])
        
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            column_config={
                "ID": st.column_config.NumberColumn(
                    "ID",
                    help="Row ID",
                    disabled=True,
                ),
                "Temperature": st.column_config.TextColumn(
                    "Temperature",
                    help="Temperature in °C"
                ),
                "Pressure": st.column_config.TextColumn(
                    "Pressure",
                    help="Pressure in bar"
                ),
                "Flow Rate": st.column_config.TextColumn(
                    "Flow Rate",
                    help="Flow rate in L/min"
                )
            },
            hide_index=True,
            key="data_editor"
        )
        
        # Update document rows only when edits are detected
        if "last_edited" not in st.session_state or st.session_state.last_edited != edited_df.to_dict():
            handle_edited_data(edited_df)
            st.session_state.last_edited = edited_df.to_dict()

    with col2:
        
        print(f"markdown:{st.session_state.document.render_markdown().strip().replace("\n", "").replace("\r", "")}")
        st.markdown(st.session_state.document.render_markdown().strip().replace("\n", "").replace("\r", ""), unsafe_allow_html=True)

if __name__ == "__main__":
    main()



