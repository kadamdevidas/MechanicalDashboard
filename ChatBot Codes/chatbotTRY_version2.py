from dash import Dash, dcc, html, Input, Output, State
import pandas as pd
import plotly.graph_objects as go
from flask import Flask
import google.generativeai as genai
import os
from dash import ctx

# Configure Gemini API key
genai.configure(api_key="AIzaSyAqes2b8tHnR-ulID4k64sb2E1NieOyrYE")
model = genai.GenerativeModel("gemini-2.0-flash")
chat_session = model.start_chat()
chat_session.send_message("You are a helpful assistant that answers questions based on maintenance data including PM01 (Unplanned), PM02 (Planned), Breakdown Maintenance, Shutdown Jobs, and Vibration Monitoring from an Excel report. Keep answers concise and relevant to Indian industrial maintenance operations.")
chat_history = []


# Create the Flask server
server = Flask(__name__)
app = Dash(__name__, server=server, suppress_callback_exceptions=True)

# Load Excel Data
file_path = "./Merged_MPR.xlsx"
pm02_df = pd.read_excel(file_path, sheet_name='PM02')
pm01_df = pd.read_excel(file_path, sheet_name='PM01')
breakdown_df = pd.read_excel(file_path, sheet_name='Breakdown Maintenance')
shutdown_df = pd.read_excel(file_path, sheet_name='Jobs Hold for Shutdown')
vibration_df = pd.read_excel(file_path, sheet_name='Vibration Monitoring')

# Homepage with Chatbot
home_layout = html.Div([
    html.Div([
        html.H1("Mechanical Department Dashboard", style={'textAlign': 'center'}),
        dcc.Link(html.Button("Access Dashboard"), href="/main-dashboard"),
        html.Br(), html.Br(),

        html.Div("Ask about PM01, PM02, breakdown maintenance, etc.", style={'fontSize': '18px'}),
        dcc.Textarea(id='chat-input', placeholder='Ask me anything...', style={'width': '100%', 'height': 100}),
        html.Div([
            html.Button('Submit', id='chat-submit', n_clicks=0, style={'marginTop': '10px'}),
            html.Button('Clear Chat', id='clear-chat', n_clicks=0, style={'marginTop': '10px', 'marginLeft': '10px'}),
        ]),
        dcc.Loading(id="loading", type="circle", children=[
            html.Div(id='chat-response', style={
                'marginTop': '20px',
                'whiteSpace': 'pre-wrap',
                'backgroundColor': '#f2f2f2',
                'padding': '10px',
                'minHeight': '200px'
            })
        ])
    ], style={'padding': '40px', 'maxWidth': '800px', 'margin': 'auto'})
])



#CallBack Function
@app.callback(
    Output('chat-response', 'children'),
    Input('chat-submit', 'n_clicks'),
    Input('clear-chat', 'n_clicks'),
    State('chat-input', 'value')
)
def generate_chatbot_reply(submit_clicks, clear_clicks, user_input):
    global chat_history

    # If Clear Chat button clicked
    if ctx.triggered_id == 'clear-chat':
        chat_history = []
        return ""

    # If Submit clicked
    if ctx.triggered_id == 'chat-submit' and user_input:
        try:
            response = chat_session.send_message(user_input)
            chat_history.append(f"👤 You: {user_input}")
            chat_history.append(f"🤖 Gemini: {response.text.strip()}")
        except Exception as e:
            chat_history.append(f"❌ Error: {str(e)}")

    return "\n\n".join(chat_history)


# Dummy dashboard layout
main_dashboard_layout = html.Div([
    html.H2("Welcome to the Main Dashboard"),
    dcc.Link("Go back to Home", href="/")
])

# Routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/main-dashboard':
        return main_dashboard_layout
    else:
        return home_layout

if __name__ == '__main__':
    app.run(debug=True)
