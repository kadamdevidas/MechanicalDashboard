#### Chatbot that can read the excel and answer the questions properly

from dash import Dash, dcc, html, Input, Output, State, ctx, ALL, MATCH
import pandas as pd
import plotly.graph_objects as go
from flask import Flask
import google.generativeai as genai
import os

# Configure Gemini API key
genai.configure(api_key="AIzaSyAqes2b8tHnR-ulID4k64sb2E1NieOyrYE")
model = genai.GenerativeModel("gemini-2.0-flash")

# Initialize chat_session globally or in a way that it persists per user session if needed for deeper history.
# For this example, it will be re-initialized with each app run, but messages are managed in dcc.Store.
chat_session = model.start_chat()
chat_session.send_message("You are a helpful assistant that answers questions based on maintenance data including PM01 (Unplanned), PM02 (Planned), Breakdown Maintenance, Shutdown Jobs, and Vibration Monitoring from an Excel report. Keep answers concise and relevant to Indian industrial maintenance operations.")

# --- MODIFIED CODE FOR DATA INJECTION FOR CHATBOT ---
# Define the path to your single Excel file
excel_file_path = "./Merged_MPR.xlsx"

# Define the sheet names within the Excel file that you want to load for the chatbot
sheet_names_for_chatbot = [
    'PM02',
    'PM01',
    'Breakdown Maintenance',
    'Jobs Hold for Shutdown',
    'Vibration Monitoring'
]

all_data_context_for_chatbot = []

if os.path.exists(excel_file_path):
    for sheet_name in sheet_names_for_chatbot:
        try:
            # Read each sheet directly from the Excel file
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
            
            # Format each sheet's data with clear headers and CSV content
            sheet_header = f"### Data for Sheet: {sheet_name}\n"
            sheet_columns = f"Columns: {', '.join(df.columns.tolist())}\n"
            sheet_csv_content = df.to_csv(index=False)
            
            all_data_context_for_chatbot.append(f"{sheet_header}{sheet_columns}{sheet_csv_content}\n\n")
            
        except Exception as e:
            print(f"Error loading sheet '{sheet_name}' from '{excel_file_path}' for chatbot: {e}")
else:
    print(f"Excel file not found for chatbot data: {excel_file_path}")


# Join all formatted data strings into a single large context string
full_context_message = "\n".join(all_data_context_for_chatbot)

# Send the consolidated data to the Gemini chat session as context
if full_context_message:
    chat_session.send_message("Here is the maintenance data from various sheets of the Excel report in CSV format. Please use this data to answer subsequent questions:\n\n" + full_context_message)
    print("All maintenance data consolidated and sent to chatbot.")
else:
    print("No data was loaded for the chatbot.")
# --- END OF MODIFIED CODE ---

# Create the Flask server
server = Flask(__name__)

# Create the Dash app and pass the Flask server
app = Dash(__name__, server=server, suppress_callback_exceptions=True)

# Load the Excel data (original loading for dashboard components - this part remains the same)
file_path = "./Merged_MPR.xlsx" # This is used for your dashboard components
pm02_df = pd.read_excel(file_path, sheet_name='PM02')
pm01_df = pd.read_excel(file_path, sheet_name='PM01')
breakdown_df = pd.read_excel(file_path, sheet_name='Breakdown Maintenance')
shutdown_df = pd.read_excel(file_path, sheet_name='Jobs Hold for Shutdown')
vibration_df = pd.read_excel(file_path, sheet_name='Vibration Monitoring')

# CHATBOT WIDGETS
# Returns the full chatbot UI
def chatbot_main_ui(source):
    return html.Div([
        # Chatbot Header
        html.Div(
            [
                html.H4("💬 Chat with Maintenance Bot", style={'marginBottom': '0', 'flexGrow': '1', 'color': 'white', 'fontSize': '18px'}),
                html.Button(
                    "-",  # Minus sign for minimizing
                    id={'type': 'chatbot-minimize-button', 'index': source},
                    n_clicks=0,
                    style={
                        'backgroundColor': 'transparent',
                        'border': 'none',
                        'color': 'white',
                        'fontSize': '24px',
                        'fontWeight': 'bold',
                        'cursor': 'pointer',
                        'padding': '0',
                        'height': '30px',
                        'width': '30px',
                        'display': 'flex',
                        'justifyContent': 'center',
                        'alignItems': 'center'
                    }
                )
            ],
            style={
                'position': 'relative',
                'width': '100%',
                'height': '50px',
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center',
                'padding': '0 15px', # Adjusted padding for header
                'backgroundImage': 'linear-gradient(to right, #4682b4, #2c3e50)', # Approximation of gail-blue to industrial
                'borderTopLeftRadius': '10px',
                'borderTopRightRadius': '10px'
            }
        ),

        # Chat Content Area
        html.Div(
            id={'type': 'chat-response', 'index': source},
            style={
                'height': '300px',
                'overflowY': 'auto',
                'padding': '10px', # Inner padding for messages
                'backgroundColor': '#e5ddd5',
                'display': 'flex',
                'flexDirection': 'column',
                'flexGrow': '1' # Allow it to grow
            }
        ),

        # Input and Send Button Area (equivalent to CardContent bottom part)
        html.Div(
            [
                dcc.Textarea(id={'type': 'chat-input', 'index': source}, placeholder='Type your message...', style={
                    'width': '100%', 'height': 60, 'borderRadius': '6px', 'resize': 'none'
                }),
                html.Div([
                    html.Button('Send', id={'type': 'chat-submit', 'index': source}, n_clicks=0, style={
                        'backgroundColor': '#25D366', 'color': 'white', 'border': 'none',
                        'padding': '10px 20px', 'borderRadius': '6px', 'cursor': 'pointer', 'flexGrow': '1'
                    }),
                    html.Button('Clear', id={'type': 'chat-clear', 'index': source}, n_clicks=0, style={
                        'marginLeft': '10px', 'padding': '10px 20px',
                        'borderRadius': '6px', 'cursor': 'pointer', 'backgroundColor': '#f44336', 'color': 'white', 'border': 'none', 'flexGrow': '1'
                    }),
                ], style={'display': 'flex', 'gap': '10px', 'marginTop': '10px'}) # Use gap for spacing between buttons
            ],
            style={'padding': '15px', 'borderTop': '1px solid #eee'} # Padding and border-top for input section
        )
    ], id={'type': 'chatbot-container', 'index': source}, style={
        'width': '350px',
        'position': 'fixed',
        'bottom': '20px',
        'right': '20px',
        'backgroundColor': 'white',
        'boxShadow': '0px 0px 15px rgba(0,0,0,0.2)',
        'borderRadius': '10px',
        'zIndex': '1000',
        'display': 'flex', # Make container a flex column
        'flexDirection': 'column',
        'height': '450px', # Fixed height for the entire chatbot
        'overflow': 'hidden' # Crucial for border radius on child elements
    })

# Returns the minimized chatbot avatar
def chatbot_avatar_ui(source):
    return html.Button(
        html.Div("💬", style={'fontSize': '30px', 'lineHeight': '1'}), # Using emoji as icon
        id={'type': 'chatbot-avatar', 'index': source},
        n_clicks=0,
        style={
            'width': '56px',
            'height': '56px',
            'borderRadius': '50%', # Makes it a circle
            'backgroundColor': '#007bff', # gail-blue approximation
            'color': 'white', # text color for the emoji
            'border': 'none',
            'cursor': 'pointer',
            'position': 'fixed',
            'bottom': '20px',
            'right': '20px',
            'zIndex': '1001',
            'boxShadow': '0 4px 12px rgba(0,0,0,0.2)', # shadow-lg approximation
            'display': 'none', # Initially hidden, controlled by callback
            'display': 'flex', # To center the emoji
            'justifyContent': 'center', # To center the emoji
            'alignItems': 'center' # To center the emoji
        }
    )


# Theme colors
primary_bg = "linear-gradient(to right, #2193b0, #6dd5ed)"
dark_text = "#1a1a1a"
accent_color = "#ff6f00"

# Styled home page
button_style = {
    'color': 'white',
    'padding': '10px 20px',
    'margin': '10px',
    'borderRadius': '5px',
    'cursor': 'pointer',
    'fontSize': '16px',
    'textAlign': 'center'
}

selected_month_button_style = {
    'backgroundColor': '#28a745',  # green
    'color': 'white',
    'padding': '8px 16px',
    'margin': '6px',
    'borderRadius': '4px',
    'cursor': 'pointer'
}

deselected_month_button_style = {
    'backgroundColor': '#333',  # dark
    'color': 'white',
    'padding': '8px 16px',
    'margin': '6px',
    'borderRadius': '4px',
    'cursor': 'pointer'
}

### HOME LAYOUT ####
home_layout = html.Div(style={
    'backgroundImage': 'linear-gradient(to top left, #fbc2eb 0%, #a6c1ee 100%)',
    'minHeight': '100vh',
    'padding': '50px',
    'color': 'white',
    'fontFamily': 'Segoe UI, sans-serif',
    'textAlign': 'center'
}, children=[
    html.H1([
        html.Span("Mechanical Department ", style={
            'fontWeight': '800',
            'background': 'linear-gradient(90deg, #8e44ad, #6a1b9a)',
            'WebkitBackgroundClip': 'text',
            'WebkitTextFillColor': 'transparent',
            'fontSize': '48px'
        }),
        html.Span("Dashboard", style={
            'color': '#ff9800',
            'fontWeight': '800',
            'marginLeft': '10px',
            'fontSize': '48px'
        })
    ]),

  html.H3("GAIL India Limited, Vijaipur", style={
    'fontWeight': '500',
    'color': '#4b3b6e',  # Deep indigo-purple
    'fontSize': '22px',
    'marginTop': '10px',
    'textShadow': '1px 1px 2px rgba(255, 255, 255, 0.2)'
}),

   html.P(
    "Comprehensive maintenance management system for preventive maintenance tracking, audit compliance, breakdown analysis, and operational excellence.",
    style={
        'fontSize': '18px',
        'maxWidth': '800px',
        'margin': 'auto',
        'paddingTop': '20px',
        'lineHeight': '1.6',
        'color': '#3e3e55',  # Muted dark lavender
        'fontWeight': '400'
    }
),

    html.Div([
        dcc.Link(
            html.Button("Access Dashboard →", style={
                'backgroundColor': 'white',
                'color': '#6a1b9a',
                'border': 'none',
                'padding': '12px 30px',
                'fontSize': '18px',
                'borderRadius': '6px',
                'marginTop': '30px',
                'cursor': 'pointer',
                'fontWeight': '600',
                'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.1)'
            }, className='glow-button'),
            href='/main-dashboard'
        )
    ]),

    html.Div(style={
    'display': 'flex',
    'justifyContent': 'center',
    'gap': '20px',
    'marginTop': '50px',
    'flexWrap': 'wrap'
}, children=[

    # Card 1 — Maintenance Tracking
    html.Div([
        html.Div("⚙️", style={'fontSize': '32px', 'color': '#5e548e'}),
        html.H4("Maintenance Tracking", style={
            'color': '#4a4e69',
            'margin': '10px 0 5px',
            'fontWeight': '600'
        }),
        html.P("Monitor preventive maintenance schedules and completion rates", style={
            'color': '#494949',
            'fontSize': '15px',
            'lineHeight': '1.5'
        })
    ], className='card-hover', style={
        'backgroundColor': 'rgba(255,255,255,0.1)',
        'padding': '20px',
        'borderRadius': '10px',
        'width': '250px',
        'border': '1px solid rgba(255, 255, 255, 0.3)',
        'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.1)',
        'transition': 'transform 0.2s ease-in-out'
    }),

    # Card 2 — Audit Management
    html.Div([
        html.Div("🛡️", style={'fontSize': '32px', 'color': '#5e548e'}),
        html.H4("Audit Management", style={
            'color': '#4a4e69',
            'margin': '10px 0 5px',
            'fontWeight': '600'
        }),
        html.P("Track audit points and ensure compliance standards", style={
            'color': '#494949',
            'fontSize': '15px',
            'lineHeight': '1.5'
        })
    ], className='card-hover', style={
        'backgroundColor': 'rgba(255,255,255,0.1)',
        'padding': '20px',
        'borderRadius': '10px',
        'width': '250px',
        'border': '1px solid rgba(255, 255, 255, 0.3)',
        'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.1)',
        'transition': 'transform 0.2s ease-in-out'
    }),

     # Card 3 — Analytics & Reporting
    html.Div([
        html.Div("📊", style={'fontSize': '32px', 'color': '#5e548e'}),
        html.H4("Analytics & Reporting", style={
            'color': '#4a4e69',
            'margin': '10px 0 5px',
            'fontWeight': '600'
        }),
        html.P("Comprehensive breakdown analysis and performance metrics", style={
            'color': '#494949',
            'fontSize': '15px',
            'lineHeight': '1.5'
        })
    ], className='card-hover', style={
        'backgroundColor': 'rgba(255,255,255,0.1)',
        'padding': '20px',
        'borderRadius': '10px',
        'width': '250px',
        'border': '1px solid rgba(255, 255, 255, 0.3)',
        'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.1)',
        'transition': 'transform 0.2s ease-in-out'
    })
])
])


# MAIN-DASHBOARD LAYOUT-Placeholder for your current dashboard layout
main_dashboard_layout = html.Div(style={
    'position': 'relative',
    'minHeight': '100vh',
    'overflow': 'hidden',
}, children=[

    # Gradient background layer
    html.Div(style={
        'position': 'absolute',
        'top': 0,
        'left': 0,
        'right': 0,
        'bottom': 0,
        'zIndex': 0,
        'backgroundImage': 'linear-gradient(to top, #9795f0 0%, #fbc8d4 100%)'
    }),

    # Main container with transparency
    html.Div(style={
        'position': 'relative',
        'zIndex': 1,
        'backgroundColor': 'rgba(255, 255, 255, 0.85)',
        'padding': '40px',
        'color': '#1a1a1a',
        'fontFamily': 'Segoe UI, sans-serif',
        'textAlign': 'center'
    }, children=[
        html.H2("✨ Welcome to the Interactive Dashboard ✨", style={
            'fontSize': '36px',
            'fontWeight': 'bold',
            'marginBottom': '30px',
            'color': '#4b0082'
        }),

        html.Div("Select a section to view detailed insights.", style={
            'fontSize': '18px',
            'marginBottom': '40px'
        }),

        # Grid-style card tiles
        html.Div(style={
            'display': 'flex',
            'flexWrap': 'wrap',
            'justifyContent': 'center',
            'gap': '20px'
        }, children=[
            dcc.Link(html.Div([
                html.Div("🛠️", style={'fontSize': '32px', 'marginBottom': '10px'}),
                html.H4("PM01", style={'margin': 0}),
                html.P("Unplanned Maintenance")
            ], style={
                'backgroundColor': '#ffffff',
                'padding': '20px',
                'width': '200px',
                'borderRadius': '12px',
                'boxShadow': '0 4px 10px rgba(0,0,0,0.1)',
                'cursor': 'pointer',
                'transition': 'transform 0.2s ease',
                'textAlign': 'center'
            }), href='/pm01'),

            dcc.Link(html.Div([
                html.Div("🗓️", style={'fontSize': '32px', 'marginBottom': '10px'}),
                html.H4("PM02", style={'margin': 0}),
                html.P("Planned Maintenance")
            ], style={
                'backgroundColor': '#ffffff',
                'padding': '20px',
                'width': '200px',
                'borderRadius': '12px',
                'boxShadow': '0 4px 10px rgba(0,0,0,0.1)',
                'cursor': 'pointer',
                'transition': 'transform 0.2s ease',
                'textAlign': 'center'
            }), href='/pm02'),

            dcc.Link(html.Div([
                html.Div("⚠️", style={'fontSize': '32px', 'marginBottom': '10px'}),
                html.H4("Breakdown", style={'margin': 0}),
                html.P("Breakdown Maintenance")
            ], style={
                'backgroundColor': '#ffffff',
                'padding': '20px',
                'width': '200px',
                'borderRadius': '12px',
                'boxShadow': '0 4px 10px rgba(0,0,0,0.1)',
                'cursor': 'pointer',
                'transition': 'transform 0.2s ease',
                'textAlign': 'center'
            }), href='/breakdown'),

            dcc.Link(html.Div([
                html.Div("🔧", style={'fontSize': '32px', 'marginBottom': '10px'}),
                html.H4("Shutdown Jobs", style={'margin': 0}),
                html.P("Jobs Hold for Shutdown")
            ], style={
                'backgroundColor': '#ffffff',
                'padding': '20px',
                'width': '200px',
                'borderRadius': '12px',
                'boxShadow': '0 4px 10px rgba(0,0,0,0.1)',
                'cursor': 'pointer',
                'transition': 'transform 0.2s ease',
                'textAlign': 'center'
            }), href='/shutdown'),

            dcc.Link(html.Div([
                html.Div("📈", style={'fontSize': '32px', 'marginBottom': '10px'}),
                html.H4("Vibration Monitoring", style={'margin': 0}),
                html.P("Health of Equipment")
            ], style={
                'backgroundColor': '#ffffff',
                'padding': '20px',
                'width': '200px',
                'borderRadius': '12px',
                'boxShadow': '0 4px 10px rgba(0,0,0,0.1)',
                'cursor': 'pointer',
                'transition': 'transform 0.2s ease',
                'textAlign': 'center'
            }), href='/vibration'),
        ])
    ])
])


# Layout for PM01, PM02, Breakdown, Shutdown, and Vibration Monitoring
def create_sheet_layout(sheet_name, id_prefix):
    return html.Div(style={'backgroundColor': '#f9f9f9', 'font-family': 'Arial'}, children=[
        dcc.Link('Back to Home', href='/', style={'display': 'block', 'textAlign': 'center', 'padding': '20px', 'fontSize': '20px'}),
        html.H2(f'{sheet_name}', style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#50e3c2', 'color': 'white'}),

        # Month filter buttons
        html.Div(id=f'{id_prefix}-month-buttons', style={'textAlign': 'center', 'padding': '10px'}),
        html.Div(id=f'{id_prefix}-graphs', style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'center'}),
        html.Div(id=f'{id_prefix}-tables', style={'padding': '20px', 'textAlign': 'center'})
    ])

# Create layouts for each sheet
pm01_layout = create_sheet_layout('PM01 Unplanned Maintenance', 'pm01')
pm02_layout = create_sheet_layout('PM02 Planned Maintenance', 'pm02')
breakdown_layout = create_sheet_layout('Breakdown Maintenance', 'breakdown')
shutdown_layout = create_sheet_layout('Jobs Hold for Shutdown', 'shutdown')
vibration_layout = create_sheet_layout('Vibration Monitoring', 'vibration')



# Callback to dynamically generate month buttons for each sheet
def generate_month_buttons(sheet_df, prefix):
    months = sheet_df['Month'].unique()
    buttons = []
    for month in months:
        buttons.append(html.Button(month, id=f'btn-{prefix}-{month}', n_clicks=1, style=selected_month_button_style))
    return buttons

# Generate PM01 month buttons
@app.callback(
    Output('pm01-month-buttons', 'children'),
    Input('url', 'pathname')
)
def generate_pm01_month_buttons(pathname):
    if pathname == '/pm01':
        return generate_month_buttons(pm01_df, 'pm01')

# Generate PM02 month buttons
@app.callback(
    Output('pm02-month-buttons', 'children'),
    Input('url', 'pathname')
)
def generate_pm02_month_buttons(pathname):
    if pathname == '/pm02':
        return generate_month_buttons(pm02_df, 'pm02')

# Generate Breakdown month buttons
@app.callback(
    Output('breakdown-month-buttons', 'children'),
    Input('url', 'pathname')
)
def generate_breakdown_month_buttons(pathname):
    if pathname == '/breakdown':
        return generate_month_buttons(breakdown_df, 'breakdown')

# Generate Shutdown month buttons
@app.callback(
    Output('shutdown-month-buttons', 'children'),
    Input('url', 'pathname')
)
def generate_shutdown_month_buttons(pathname):
    if pathname == '/shutdown':
        return generate_month_buttons(shutdown_df, 'shutdown')

# Generate Vibration Monitoring month buttons
@app.callback(
    Output('vibration-month-buttons', 'children'),
    Input('url', 'pathname')
)
def generate_vibration_month_buttons(pathname):
    if pathname == '/vibration':
        return generate_month_buttons(vibration_df, 'vibration')


# Update graphs for PM01 and PM02
def update_pm_graphs(sheet_df, prefix):
    @app.callback(
        [Output(f'btn-{prefix}-{month}', 'style') for month in sheet_df['Month'].unique()] +
        [Output(f'{prefix}-graphs', 'children')],
        [Input(f'btn-{prefix}-{month}', 'n_clicks') for month in sheet_df['Month'].unique()]
    )
    def update_sheet_graphs(*clicked_buttons):
        months_clicked = []
        styles = []
        graphs = []

        for i, month in enumerate(sheet_df['Month'].unique()):
            if clicked_buttons[i] % 2 == 1:  # Selected
                months_clicked.append(month)
                styles.append(selected_month_button_style)  # Keep green background
            else:  # Deselected
                styles.append(deselected_month_button_style)  # Turn to black background

        # Generate graphs for the selected months
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        for i, month in enumerate(months_clicked):
            month_data = sheet_df[sheet_df['Month'] == month]
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=month_data['Plant'], y=month_data['Planned'], name='Planned',
                marker_color=colors[i % len(colors)], text=month_data['Planned'], textposition='auto'
            ))
            fig.add_trace(go.Bar(
                x=month_data['Plant'],                y=month_data['Executed'], name='Executed',
                marker_color=colors[(i + 1) % len(colors)], text=month_data['Executed'], textposition='auto'
            ))
            fig.update_layout(
                title=f'{prefix.upper()}: Planned vs Executed Jobs ({month})',
                barmode='group',
                height=350,
                width=350,
                plot_bgcolor='#f9f9f9'
            )
            graphs.append(html.Div(dcc.Graph(figure=fig), style={'display': 'inline-block', 'margin': '10px'}))

        return styles + [graphs]

# Update Breakdown graphs and tables
@app.callback(
    [Output(f'btn-breakdown-{month}', 'style') for month in breakdown_df['Month'].unique()] +
    [Output('breakdown-graphs', 'children'), Output('breakdown-tables', 'children')],
    [Input(f'btn-breakdown-{month}', 'n_clicks') for month in breakdown_df['Month'].unique()]
)
def update_breakdown_maintenance(*clicked_buttons):
    months_clicked = []
    styles = []
    graphs = []
    tables = []

    for i, month in enumerate(breakdown_df['Month'].unique()):
        if clicked_buttons[i] % 2 == 1:  # Selected
            months_clicked.append(month)
            styles.append(selected_month_button_style)  # Keep green background
        else:  # Deselected
            styles.append(deselected_month_button_style)  # Turn to black background

    # Generate graphs and tables for the selected months
    for i, month in enumerate(months_clicked):
        month_data = breakdown_df[breakdown_df['Month'] == month]

        # Generate Bar Chart for Breakdown Jobs
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=month_data['Plant'], y=month_data['No. of Breakdown Jobs'], name='Breakdown Jobs',
            marker_color='#ff7f0e', text=month_data['No. of Breakdown Jobs'], textposition='auto'
        ))
        fig.update_layout(
            title=f'Breakdown Jobs ({month})',
            barmode='group',
            height=350,
            width=350,
            plot_bgcolor='#f9f9f9'
        )
        graphs.append(html.Div(dcc.Graph(figure=fig), style={'display': 'inline-block', 'margin': '10px'}))

        # Generate Table for Short Description with better styling
        table_rows = []
        for j, row in month_data.iterrows():
            table_rows.append(html.Tr([
                html.Td(j + 1, style={'padding': '10px', 'border': '1px solid black'}),
                html.Td(row['Plant'], style={'padding': '10px', 'border': '1px solid black'}),
                html.Td(row['Short description of the job'] if not pd.isna(row['Short description of the job']) else '',
                        style={'padding': '10px', 'border': '1px solid black'})
            ], style={'backgroundColor': '#f9f9f9' if j % 2 == 0 else '#e0e0e0'}))  # Alternating row colors

        tables.append(html.Div([
            html.H3(f'{month} Breakdown Maintenance Jobs'),
            html.Table([
                html.Thead(html.Tr([
                    html.Th('Serial Number', style={'padding': '10px', 'border': '1px solid black', 'backgroundColor': '#d3a15d', 'color': 'white'}),
                    html.Th('Plant', style={'padding': '10px', 'border': '1px solid black', 'backgroundColor': '#d3a15d', 'color': 'white'}),
                    html.Th('Short description of the job', style={'padding': '10px', 'border': '1px solid black', 'backgroundColor': '#d3a15d', 'color': 'white'})
                ])),
                html.Tbody(table_rows)
            ], style={'width': '80%', 'margin': '20px auto', 'border': '1px solid black', 'borderCollapse': 'collapse',
                      'textAlign': 'center', 'borderSpacing': '0px', 'fontFamily': 'Arial'})
        ], style={'padding': '20px'}))

    return styles + [graphs, tables]

# Update Shutdown Jobs graphs and tables
@app.callback(
    [Output(f'btn-shutdown-{month}', 'style') for month in shutdown_df['Month'].unique()] +
    [Output('shutdown-graphs', 'children'), Output('shutdown-tables', 'children')],
    [Input(f'btn-shutdown-{month}', 'n_clicks') for month in shutdown_df['Month'].unique()]
)
def update_shutdown_jobs(*clicked_buttons):
    months_clicked = []
    styles = []
    graphs = []
    tables = []

    for i, month in enumerate(shutdown_df['Month'].unique()):
        if clicked_buttons[i] % 2 == 1:  # Selected
            months_clicked.append(month)
            styles.append(selected_month_button_style)  # Keep green background
        else:  # Deselected
            styles.append(deselected_month_button_style)  # Turn to black background

    # Generate graphs and tables for the selected months
    for i, month in enumerate(months_clicked):
        month_data = shutdown_df[shutdown_df['Month'] == month]

        # Generate Bar Chart for Jobs Hold for Shutdown
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=month_data['Plant'], y=month_data['No. of Jobs hold'], name='Jobs Hold',
            marker_color='#ff7f0e', text=month_data['No. of Jobs hold'], textposition='auto'
        ))
        fig.update_layout(
            title=f'Shutdown Jobs ({month})',
            barmode='group',
            height=350,
            width=350,
            plot_bgcolor='#f9f9f9'
        )
        graphs.append(html.Div(dcc.Graph(figure=fig), style={'display': 'inline-block', 'margin': '10px'}))

        # Generate Table for Short Description with better styling
        table_rows = []
        for j, row in month_data.iterrows():
            table_rows.append(html.Tr([
                html.Td(j + 1, style={'padding': '10px', 'border': '1px solid black'}),
                html.Td(row['Plant'], style={'padding': '10px', 'border': '1px solid black'}),
                html.Td(row['Short description of the job'] if not pd.isna(row['Short description of the job']) else '',
                        style={'padding': '10px', 'border': '1px solid black'})
            ], style={'backgroundColor': '#f9f9f9' if j % 2 == 0 else '#e0e0e0'}))  # Alternating row colors

        tables.append(html.Div([
            html.H3(f'{month} Jobs Hold for Shutdown'),
            html.Table([
                html.Thead(html.Tr([
                    html.Th('Serial Number', style={'padding': '10px', 'border': '1px solid black', 'backgroundColor': '#d3a15d', 'color': 'white'}),
                    html.Th('Plant', style={'padding': '10px', 'border': '1px solid black', 'backgroundColor': '#d3a15d', 'color': 'white'}),
                    html.Th('Short description of the job', style={'padding': '10px', 'border': '1px solid black', 'backgroundColor': '#d3a15d', 'color': 'white'})
                ])),
                html.Tbody(table_rows)
            ], style={'width': '80%', 'margin': '20px auto', 'border': '1px solid black', 'borderCollapse': 'collapse',
                      'textAlign': 'center', 'borderSpacing': '0px', 'fontFamily': 'Arial'})
        ], style={'padding': '20px'}))

    return styles + [graphs, tables]

# Update Vibration Monitoring graphs
@app.callback(
    [Output(f'btn-vibration-{month}', 'style') for month in vibration_df['Month'].unique()] +
    [Output('vibration-graphs', 'children')],
    [Input(f'btn-vibration-{month}', 'n_clicks') for month in vibration_df['Month'].unique()]
)
def update_vibration_monitoring(*clicked_buttons):
    months_clicked = []
    styles = []
    graphs = []

    for i, month in enumerate(vibration_df['Month'].unique()):
        if clicked_buttons[i] % 2 == 1:  # Selected
            months_clicked.append(month)
            styles.append(selected_month_button_style)  # Keep green background
        else:  # Deselected
            styles.append(deselected_month_button_style)  # Turn to black background

    # Generate graphs for the selected months
    for i, month in enumerate(months_clicked):
        month_data = vibration_df[vibration_df['Month'] == month]

        # Generate Bar Chart for Vibration Monitoring Jobs
        fig = go.Figure()

        # Left Y-axis (Equipment-related counts)
        fig.add_trace(go.Bar(
            x=month_data['Plant'], y=month_data['No. of Equipment Scheduled'], name='Scheduled Equipment',
            marker_color='#1f77b4', text=month_data['No. of Equipment Scheduled'], textposition='auto'
        ))
        fig.add_trace(go.Bar(
            x=month_data['Plant'], y=month_data['No. of Equipment Monitored (Executed)'], name='Monitored Equipment',
            marker_color='#ff7f0e', text=month_data['No. of Equipment Monitored (Executed)'], textposition='auto'
        ))
        fig.add_trace(go.Bar(
            x=month_data['Plant'], y=month_data['No. of Equipment With Normal Health'], name='Normal Health Equipment',
            marker_color='#2ca02c', text=month_data['No. of Equipment With Normal Health'], textposition='auto'
        ))
        fig.add_trace(go.Bar(
            x=month_data['Plant'], y=month_data['No. of Equipment With Critical Health'], name='Critical Health Equipment',
            marker_color='#d62728', text=month_data['No. of Equipment With Critical Health'], textposition='auto'
        ))

        # Right Y-axis (Percentage-related data)
        fig.add_trace(go.Scatter(
            x=month_data['Plant'], y=month_data['Health Index'] * 100, name='Health Index (%)',
            marker_color='#9467bd', yaxis='y2', mode='lines+markers', text=month_data['Health Index'] * 100, textposition='top center'
        ))
        fig.add_trace(go.Scatter(
            x=month_data['Plant'], y=month_data['Critical Index'] * 100, name='Critical Index (%)',
            marker_color='#e8bd13', yaxis='y2', mode='lines+markers', text=month_data['Critical Index'] * 100, textposition='top center'
        ))

        # Update layout for dual-axis graph
        fig.update_layout(
            title=f'Vibration Monitoring ({month})',
            barmode='group',
            height=400,
            width=700,
            plot_bgcolor='#f9f9f9',
            xaxis=dict(title='Plant'),
            yaxis=dict(title='Equipment Count'),
            yaxis2=dict(title='Percentage (%)', overlaying='y', side='right'),
            legend=dict(x=1.05, y=1),
            margin=dict(l=40, r=40, t=40, b=40)
        )

        graphs.append(html.Div(dcc.Graph(figure=fig), style={'display': 'inline-block', 'margin': '10px'}))

    return styles + [graphs]

# Generate the month buttons for PM01, PM02, Breakdown, Shutdown, and Vibration Monitoring
update_pm_graphs(pm01_df, 'pm01')
update_pm_graphs(pm02_df, 'pm02')


# App layout with dynamic routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='chat-store', data=[]), # Centralized chat history
    # New: dcc.Store for chatbot state (minimized/maximized) for each instance
    dcc.Store(id={'type': 'chatbot-state-store', 'index': 'home'}, data={'is_minimized': False}),
    dcc.Store(id={'type': 'chatbot-state-store', 'index': 'dashboard'}, data={'is_minimized': False}),
    html.Div(id='page-content'),
    
    # Draggable Chatbot Container with id for JavaScript
    html.Div(
        id='chatbot-draggable', # This ID is used by the JavaScript for dragging
        children=[
            chatbot_main_ui('home'),
            chatbot_avatar_ui('home'),
            chatbot_main_ui('dashboard'),
            chatbot_avatar_ui('dashboard')
        ],
        style={
            'position': 'fixed', # Important for draggable
            'bottom': '20px',
            'right': '20px',
            'zIndex': '1000'
        }
    ),
    
    # JavaScript for draggable functionality
    html.Script("""
        document.addEventListener('DOMContentLoaded', function () {
            const chatbot = document.getElementById('chatbot-draggable');
            if (chatbot) {
                chatbot.style.position = 'fixed';
                chatbot.style.zIndex = 9999;

                let offsetX = 0, offsetY = 0, initialX, initialY;
                let isDragging = false;

                // Make the header (first child of chatbot) the draggable handle
                const header = chatbot.querySelector('div'); // Assuming the first div is the header
                if (header) {
                    header.style.cursor = 'grab'; // Indicate it's draggable
                    header.addEventListener('mousedown', (e) => {
                        isDragging = true;
                        initialX = e.clientX;
                        initialY = e.clientY;
                        offsetX = chatbot.offsetLeft;
                        offsetY = chatbot.offsetTop;
                        e.preventDefault(); // Prevent text selection etc.
                    });
                }

                document.addEventListener('mousemove', (e) => {
                    if (!isDragging) return;
                    // Calculate new position based on mouse movement relative to initial click
                    const dx = e.clientX - initialX;
                    const dy = e.clientY - initialY;

                    // Update chatbot's position
                    chatbot.style.left = offsetX + dx + 'px';
                    chatbot.style.top = offsetY + dy + 'px';
                });

                document.addEventListener('mouseup', () => {
                    isDragging = false;
                });
            }
        });
    """)
])

# Routing callback (now only updates page-content)
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/':
        return home_layout
    elif pathname == '/main-dashboard':
        return main_dashboard_layout
    elif pathname in ['/pm01', '/pm02', '/breakdown', '/shutdown', '/vibration']:
        return globals()[f'{pathname[1:]}_layout']
    else:
        return home_layout

# New: Combined callback to manage the state (minimized/maximized) of each chatbot instance
@app.callback(
    Output({'type': 'chatbot-state-store', 'index': MATCH}, 'data'),
    [Input({'type': 'chatbot-minimize-button', 'index': MATCH}, 'n_clicks'),
     Input({'type': 'chatbot-avatar', 'index': MATCH}, 'n_clicks')],
    prevent_initial_call=True
)
def update_chatbot_state(minimize_n_clicks, avatar_n_clicks):
    trigger_id = ctx.triggered_id
    
    if trigger_id is None:
        return {'is_minimized': False}

    if trigger_id['type'] == 'chatbot-minimize-button':
        if minimize_n_clicks and minimize_n_clicks > 0:
            return {'is_minimized': True}
    
    elif trigger_id['type'] == 'chatbot-avatar':
        if avatar_n_clicks and avatar_n_clicks > 0:
            return {'is_minimized': False}
            
    return {'is_minimized': False}


# Single callback to control all chatbot styles based on URL and state stores
@app.callback(
    [Output({'type': 'chatbot-container', 'index': 'home'}, 'style'),
     Output({'type': 'chatbot-avatar', 'index': 'home'}, 'style'),
     Output({'type': 'chatbot-container', 'index': 'dashboard'}, 'style'),
     Output({'type': 'chatbot-avatar', 'index': 'dashboard'}, 'style')],
    [Input('url', 'pathname'),
     Input({'type': 'chatbot-state-store', 'index': 'home'}, 'data'),
     Input({'type': 'chatbot-state-store', 'index': 'dashboard'}, 'data')]
)
def update_all_chatbot_styles(pathname, home_state, dashboard_state):
    # Default styles for hidden elements
    hidden_style = {'display': 'none'}

    # Base styles for full chatbot UI (without display property)
    base_full_chat_style = {
        'width': '350px', 'position': 'fixed', 'bottom': '20px', 'right': '20px',
        'backgroundColor': 'white', 'boxShadow': '0px 0px 15px rgba(0,0,0,0.2)',
        'borderRadius': '10px', 'zIndex': '1000', 'overflow': 'hidden',
        'display': 'flex', 'flexDirection': 'column', 'height': '450px'
    }

    # Base styles for avatar UI (without display property)
    base_avatar_style = {
        'width': '56px',
        'height': '56px',
        'borderRadius': '50%', # Makes it a circle
        'backgroundColor': '#007bff', # gail-blue approximation
        'color': 'white', # text color for the emoji
        'border': 'none',
        'cursor': 'pointer',
        'position': 'fixed',
        'bottom': '20px',
        'right': '20px',
        'zIndex': '1001',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.2)', # shadow-lg approximation
        'display': 'flex', # To center the emoji
        'justifyContent': 'center', # To center the emoji
        'alignItems': 'center' # To center the emoji
    }

    # Initialize all output styles to hidden
    home_container_output_style = hidden_style
    home_avatar_output_style = hidden_style
    dashboard_container_output_style = hidden_style
    dashboard_avatar_output_style = hidden_style

    # Determine styles for home chatbot based on URL and its state
    if pathname == '/':
        is_home_minimized = home_state.get('is_minimized', False)
        if is_home_minimized:
            home_container_output_style = {**base_full_chat_style, 'display': 'none'}
            home_avatar_output_style = {**base_avatar_style, 'display': 'flex'} # Use flex for centering content
        else:
            home_container_output_style = {**base_full_chat_style, 'display': 'flex'} # Use flex for column layout
            home_avatar_output_style = {**base_avatar_style, 'display': 'none'}

    # Determine styles for dashboard chatbot based on URL and its state
    elif pathname == '/main-dashboard':
        is_dashboard_minimized = dashboard_state.get('is_minimized', False)
        if is_dashboard_minimized:
            dashboard_container_output_style = {**base_full_chat_style, 'display': 'none'}
            dashboard_avatar_output_style = {**base_avatar_style, 'display': 'flex'} # Use flex for centering content
        else:
            dashboard_container_output_style = {**base_full_chat_style, 'display': 'flex'} # Use flex for column layout
            dashboard_avatar_output_style = {**base_avatar_style, 'display': 'none'}

    return home_container_output_style, home_avatar_output_style, \
           dashboard_container_output_style, dashboard_avatar_output_style


# Callback to process user input and update chat history in dcc.Store
@app.callback(
    Output('chat-store', 'data'),
    Output({'type': 'chat-input', 'index': ALL}, 'value'), # To clear input after sending for ALL chat inputs
    Input({'type': 'chat-submit', 'index': ALL}, 'n_clicks'),
    Input({'type': 'chat-clear', 'index': ALL}, 'n_clicks'),
    State({'type': 'chat-input', 'index': ALL}, 'value'),
    State({'type': 'chat-input', 'index': ALL}, 'id'), # New: Get the IDs of the chat inputs
    State('chat-store', 'data'),
    prevent_initial_call=True
)
def process_chat_actions(submit_clicks, clear_clicks, all_user_inputs, all_user_input_ids, store_data):
    chat_history = store_data if store_data is not None else []
    
    triggered_id = ctx.triggered_id
    
    # Initialize all input values to empty string for clearing
    num_chat_inputs = len(all_user_inputs)
    input_values_to_clear = [""] * num_chat_inputs

    if not triggered_id:
        # This case handles initial load or no interaction
        return chat_history, input_values_to_clear

    # Determine which specific button (submit or clear) was clicked and its numerical index
    clicked_type = triggered_id.get('type')
    clicked_source_index = triggered_id.get('index') # This is 'home' or 'dashboard'
    
    clicked_numerical_index = -1
    # Iterate through the IDs of the chat inputs to find the numerical index corresponding to the triggered source index
    for i, input_id_dict in enumerate(all_user_input_ids):
        if input_id_dict['index'] == clicked_source_index:
            clicked_numerical_index = i
            break

    if clicked_numerical_index == -1:
        # This should ideally not happen if triggered_id is from our chat inputs
        return chat_history, input_values_to_clear

    # Handle clear action
    if clicked_type == 'chat-clear':
        # Clear the chat history
        return [], input_values_to_clear

    # Handle submit action (clicked_type == 'chat-submit')
    user_input = all_user_inputs[clicked_numerical_index]
    if user_input:
        try:
            # Append user message
            chat_history.append({'role': 'user', 'content': user_input})

            # Send message to Gemini and get response
            response = chat_session.send_message(user_input)
            gemini_response_text = response.text.strip()

            # Append Gemini's response
            chat_history.append({'role': 'gemini', 'content': gemini_response_text})
            
            # Clear the specific input field that was used
            input_values_to_clear[clicked_numerical_index] = ""

        except Exception as e:
            chat_history.append({'role': 'error', 'content': f"❌ Error: {str(e)}"})
            # If there's an error, don't clear the input
            input_values_to_clear[clicked_numerical_index] = user_input
    else:
        # If user input is empty, don't do anything but still clear the relevant input if it was submitted
        input_values_to_clear[clicked_numerical_index] = ""
    
    return chat_history, input_values_to_clear

# Callback to render chat messages from chat-store to specific chat-response divs
@app.callback(
    [Output({'type': 'chat-response', 'index': 'home'}, 'children'),
     Output({'type': 'chat-response', 'index': 'dashboard'}, 'children')],
    [Input('chat-store', 'data'),
     Input('url', 'pathname')] # Add pathname as an input
)
def render_chat_history(store_data, pathname):
    chat_history = store_data if store_data is not None else []
    
    rendered_chat_history_content = []
    for message in chat_history:
        if message['role'] == 'user':
            rendered_chat_history_content.append(html.Div(message['content'], style={
                'alignSelf': 'flex-end',
                'background': '#dcf8c6',
                'color': '#000',
                'padding': '8px 12px',
                'borderRadius': '10px',
                'margin': '5px',
                'maxWidth': '80%',
                'wordWrap': 'break-word'
            }))
        elif message['role'] == 'gemini':
            rendered_chat_history_content.append(html.Div(message['content'], style={
                'alignSelf': 'flex-start',
                'background': '#ffffff',
                'color': '#000',
                'padding': '8px 12px',
                'borderRadius': '10px',
                'margin': '5px',
                'maxWidth': '80%',
                'wordWrap': 'break-word'
            }))
        elif message['role'] == 'error':
            rendered_chat_history_content.append(html.Div(message['content'], style={
                'background': '#ffcdd2',
                'padding': '8px 12px',
                'borderRadius': '10px',
                'margin': '5px',
                'color': '#b71c1c'
            }))
    
    # Conditionally return the chat history based on the current pathname
    if pathname == '/': # Home page is active
        return rendered_chat_history_content, [] # Update home chatbot, keep dashboard chatbot empty
    elif pathname == '/main-dashboard': # Dashboard page is active
        return [], rendered_chat_history_content # Keep home chatbot empty, update dashboard chatbot
    else: # For other sub-pages (PM01, PM02, etc.), both chatbots are typically hidden by display_page callback
        return [], [] # Keep both chatbots empty


# Run app
if __name__ == '__main__':
    app.run(debug=True)
