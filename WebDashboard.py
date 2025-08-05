#### WebDashboard.py — Enhanced Version with Modern UI Inspired by Lovable.dev

from dash import Dash, dcc, html, Input, Output, State, ctx, ALL, MATCH
import pandas as pd
import plotly.graph_objects as go
from flask import Flask
import google.generativeai as genai
import os

# Configure Gemini API key from environment variable
# Replace "YOUR_GEMINI_API_KEY_ENV_VAR" with the actual name you'll use (e.g., "GEMINI_API_KEY")
api_key = os.getenv("GEMINI_API_KEY") 
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# Initialize chat_session globally or in a way that it persists per user session if needed for deeper history.
# For this example, it will be re-initialized with each app run, but messages are managed in dcc.Store.
chat_session = model.start_chat()
chat_session.send_message("You are a helpful assistant that answers questions based on maintenance data including PM01 (Unplanned), PM02 (Planned), Breakdown Maintenance, Shutdown Jobs, Vibration Monitoring, Monthly Lube Oil Analysis, Spares Management, Running Contracts, and Gate Pass Details from an Excel report. Keep answers concise and relevant to Indian industrial maintenance operations.")

# --- MODIFIED CODE FOR DATA INJECTION FOR CHATBOT ---
# Define the path to your single Excel file
excel_file_path = "./Merged_MPR.xlsx"

# Define the sheet names within the Excel file that you want to load for the chatbot
sheet_names_for_chatbot = [
    'PM02',
    'PM01',
    'Breakdown Maintenance',
    'Jobs Hold for Shutdown',
    'Vibration Monitoring',
    'Monthly Lube Oil Analysis)', # Corrected sheet name
    'SPARES MANAGMENT',
    'Running Contracts',
    'Gate Pass Details'
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
# Load new sheets
lube_oil_df = pd.read_excel(file_path, sheet_name='Monthly Lube Oil Analysis)') # Corrected sheet name for DataFrame loading
spares_df = pd.read_excel(file_path, sheet_name='SPARES MANAGMENT')
contracts_df = pd.read_excel(file_path, sheet_name='Running Contracts') # This will be loaded as is, then column accessed by proper name
gate_pass_df = pd.read_excel(file_path, sheet_name='Gate Pass Details')


# CHATBOT WIDGETS
# Returns the full chatbot UI
def chatbot_main_ui(source):
    return html.Div([
        # Chatbot Header
        html.Div(
            [
                html.H4("💬 Chat with MeVi Bot", style={'marginBottom': '0', 'flexGrow': '1', 'color': 'white', 'fontSize': '18px'}),
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
    'cursor': 'pointer',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.2)'
}

deselected_month_button_style = {
    'backgroundColor': '#333',  # dark
    'color': 'white',
    'padding': '8px 16px',
    'margin': '6px',
    'borderRadius': '4px',
    'cursor': 'pointer',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.2)'
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
        html.Span("Mechanical", className="animated-heading-word", style={
            'fontWeight': '800',
            'background': 'linear-gradient(90deg, #8e44ad, #6a1b9a)',
            'WebkitBackgroundClip': 'text',
            'WebkitTextFillColor': 'transparent',
            'fontSize': '48px',
            'marginRight': '10px'
        }),
        html.Span("Department", className="animated-heading-word", style={
            'fontWeight': '800',
            'background': 'linear-gradient(90deg, #8e44ad, #6a1b9a)',
            'WebkitBackgroundClip': 'text',
            'WebkitTextFillColor': 'transparent',
            'fontSize': '48px',
            'marginRight': '10px'
        }),
        html.Span("Dashboard", className="animated-heading-word", style={
            # Apply same gradient and clipping for consistency with animation effect
            'fontWeight': '800',
            'background': 'linear-gradient(90deg, #ff9800, #ff6f00)', # Orange gradient for Dashboard word
            'WebkitBackgroundClip': 'text',
            'WebkitTextFillColor': 'transparent',
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
        html.Div("⚙️", style={'fontSize': '32px', 'marginBottom': '10px', 'color': '#5e548e'}),
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
        html.Div("🛡️", style={'fontSize': '32px', 'marginBottom': '10px', 'color': '#5e548e'}),
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
        html.Div("📊", style={'fontSize': '32px', 'marginBottom': '10px', 'color': '#5e548e'}),
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
    }),
    
    # NEW Card 4 — Chatbot Clusters
    dcc.Link(
        html.Div([
            html.Div("🤖", style={'fontSize': '32px', 'marginBottom': '10px', 'color': '#5e548e'}),
            html.H4("Chatbot Clusters", style={
                'color': '#4a4e69',
                'margin': '10px 0 5px',
                'fontWeight': '600'
            }),
            html.P("RAG chatbots for quick information", style={
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
        }), href='/chatbot-clusters'
    )
])
])

# CHATBOT CLUSTERS LAYOUT
chatbot_clusters_layout = html.Div(style={
    'backgroundImage': 'linear-gradient(to top, #c1e4f0 0%, #e0f2f7 100%)',
    'minHeight': '100vh',
    'padding': '50px',
    'color': '#333',
    'fontFamily': 'Segoe UI, sans-serif',
    'textAlign': 'center'
}, children=[
    dcc.Link(
        html.Div("🏠", style={ 
            'fontSize': '30px',
            'position': 'absolute',
            'top': '20px',
            'right': '30px',
            'cursor': 'pointer',
            'zIndex': '10',
            'color': '#4b0082',
            'textShadow': '1px 1px 2px rgba(0,0,0,0.2)'
        }),
        href='/',
        style={'textDecoration': 'none'}
    ),
    html.H2("Chatbot Clusters", style={
        'fontSize': '36px',
        'fontWeight': 'bold',
        'marginBottom': '30px',
        'color': '#4b0082'
    }),
    html.P("Select a chatbot for quick information retrieval.", style={
        'fontSize': '18px',
        'marginBottom': '40px'
    }),
    html.Div(style={
        'display': 'flex',
        'justifyContent': 'center',
        'gap': '20px',
        'flexWrap': 'wrap'
    }, children=[
        # OISD RAG Chatbot tile
        html.A(
            html.Div([
                html.Div("📚", style={'fontSize': '32px', 'marginBottom': '10px'}),
                html.H4("OISD RAG Chatbot", style={'margin': 0}),
                html.P("Information on Oil Industry Safety Directorate guidelines")
            ], className='card-hover', style={
                'backgroundColor': '#ffffff',
                'padding': '20px',
                'width': '250px',
                'borderRadius': '12px',
                'boxShadow': '0 4px 10px rgba(0,0,0,0.1)',
                'cursor': 'pointer',
                'transition': 'transform 0.2s ease',
                'textAlign': 'center'
            }),
            href='https://huggingface.co/spaces/okadam1112/oisd-rag-chatbot',
            target='_blank',
            style={'textDecoration': 'none', 'color': 'inherit'}
        ),
        # HR RAG Chatbot tile
        html.Div([
            html.Div("👤", style={'fontSize': '32px', 'marginBottom': '10px'}),
            html.H4("HR RAG Chatbot", style={'margin': 0}),
            html.P("RAG chatbot for HR-related queries")
        ], className='card-hover', style={
            'backgroundColor': '#ffffff',
            'padding': '20px',
            'width': '250px',
            'borderRadius': '12px',
            'boxShadow': '0 4px 10px rgba(0,0,0,0.1)',
            'transition': 'transform 0.2s ease',
            'textAlign': 'center'
        }),
        # C&P RAG Chatbot tile
        html.Div([
            html.Div("💰", style={'fontSize': '32px', 'marginBottom': '10px'}),
            html.H4("C&P RAG Chatbot", style={'margin': 0}),
            html.P("RAG chatbot for contracts and procurement information")
        ], className='card-hover', style={
            'backgroundColor': '#ffffff',
            'padding': '20px',
            'width': '250px',
            'borderRadius': '12px',
            'boxShadow': '0 4px 10px rgba(0,0,0,0.1)',
            'transition': 'transform 0.2s ease',
            'textAlign': 'center'
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

            # NEW CARDS ADDED HERE
            dcc.Link(html.Div([
                html.Div("🧪", style={'fontSize': '32px', 'marginBottom': '10px'}),
                html.H4("Lube Oil Analysis", style={'margin': 0}),
                html.P("Moisture & Viscosity")
            ], style={
                'backgroundColor': '#ffffff',
                'padding': '20px',
                'width': '200px',
                'borderRadius': '12px',
                'boxShadow': '0 4px 10px rgba(0,0,0,0.1)',
                'cursor': 'pointer',
                'transition': 'transform 0.2s ease',
                'textAlign': 'center'
            }), href='/lubeoil'),

            dcc.Link(html.Div([
                html.Div("📦", style={'fontSize': '32px', 'marginBottom': '10px'}),
                html.H4("Spares Management", style={'margin': 0}),
                html.P("Indent & PR Tracking")
            ], style={
                'backgroundColor': '#ffffff',
                'padding': '20px',
                'width': '200px',
                'borderRadius': '12px',
                'boxShadow': '0 4px 10px rgba(0,0,0,0.1)',
                'cursor': 'pointer',
                'transition': 'transform 0.2s ease',
                'textAlign': 'center'
            }), href='/spares'),

            dcc.Link(html.Div([
                html.Div("📄", style={'fontSize': '32px', 'marginBottom': '10px'}),
                html.H4("Running Contracts", style={'margin': 0}),
                html.P("Contract Status & Renewal")
            ], style={
                'backgroundColor': '#ffffff',
                'padding': '20px',
                'width': '200px',
                'borderRadius': '12px',
                'boxShadow': '0 4px 10px rgba(0,0,0,0.1)',
                'cursor': 'pointer',
                'transition': 'transform 0.2s ease',
                'textAlign': 'center'
            }), href='/contracts'),

            dcc.Link(html.Div([
                html.Div("🚪", style={'fontSize': '32px', 'marginBottom': '10px'}),
                html.H4("Gate Pass Details", style={'margin': 0}),
                html.P("In/Out Pass Monitoring")
            ], style={
                'backgroundColor': '#ffffff',
                'padding': '20px',
                'width': '200px',
                'borderRadius': '12px',
                'boxShadow': '0 4px 10px rgba(0,0,0,0.1)',
                'cursor': 'pointer',
                'transition': 'transform 0.2s ease',
                'textAlign': 'center'
            }), href='/gatepass'),

        ])
    ])
])


# Layout for PM01, PM02, Breakdown, Shutdown, Vibration, Lube Oil, Spares, Contracts, and Gate Pass
def create_sheet_layout(sheet_name, id_prefix):
    return html.Div(style={
        'position': 'relative', # For absolute positioning of home icon
        'minHeight': '100vh',
        'padding': '20px',
        'fontFamily': 'Arial, sans-serif',
        'backgroundImage': 'linear-gradient(to bottom right, #e0f2f7, #c1e4f0)', # Light blue gradient
        'color': '#333'
    }, children=[
        # Home Icon at top right, linking to the actual home page (/)
        dcc.Link(
            html.Div("🏠", style={ # Using a unicode home symbol
                'fontSize': '30px',
                'position': 'absolute',
                'top': '20px',
                'right': '30px',
                'cursor': 'pointer',
                'zIndex': '10',
                'color': '#4b0082', # Dark purple for contrast
                'textShadow': '1px 1px 2px rgba(0,0,0,0.2)'
            }),
            href='/', # Directing to the true home page (Mechanical Department Dashboard)
            style={'textDecoration': 'none'}
        ),
        html.H2(f'{sheet_name}', style={
            'textAlign': 'center',
            'padding': '20-x',
            'backgroundImage': 'linear-gradient(to right, #4CAF50, #8BC34A)', # Green gradient
            'color': 'white',
            'borderRadius': '10px',
            'margin': '20px auto',
            'width': '90%',
            'boxShadow': '0 8px 16px rgba(0,0,0,0.2)',
            'fontSize': '32px',
            'fontWeight': 'bold',
            'letterSpacing': '1.5px',
            'textShadow': '2px 2px 4px rgba(0,0,0,0.3)'
        }),

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
lubeoil_layout = create_sheet_layout('Monthly Lube Oil Analysis', 'lubeoil') # Display name is without parenthesis
spares_layout = create_sheet_layout('SPARES MANAGMENT', 'spares')
contracts_layout = create_sheet_layout('Running Contracts', 'contracts')
gatepass_layout = create_sheet_layout('Gate Pass Details', 'gatepass')


# Callback to dynamically generate month buttons for each sheet
def generate_month_buttons(sheet_df, prefix):
    months = sheet_df['Month'].unique()
    buttons = []
    for month in months:
        buttons.append(html.Button(month, id=f'btn-{prefix}-{month}', n_clicks=1, style=selected_month_button_style))
    return buttons

# Generate month buttons for all sheets
@app.callback(
    Output('pm01-month-buttons', 'children'),
    Input('url', 'pathname')
)
def generate_pm01_month_buttons(pathname):
    if pathname == '/pm01':
        return generate_month_buttons(pm01_df, 'pm01')

@app.callback(
    Output('pm02-month-buttons', 'children'),
    Input('url', 'pathname')
)
def generate_pm02_month_buttons(pathname):
    if pathname == '/pm02':
        return generate_month_buttons(pm02_df, 'pm02')

@app.callback(
    Output('breakdown-month-buttons', 'children'),
    Input('url', 'pathname')
)
def generate_breakdown_month_buttons(pathname):
    if pathname == '/breakdown':
        return generate_month_buttons(breakdown_df, 'breakdown')

@app.callback(
    Output('shutdown-month-buttons', 'children'),
    Input('url', 'pathname')
)
def generate_shutdown_month_buttons(pathname):
    if pathname == '/shutdown':
        return generate_month_buttons(shutdown_df, 'shutdown')

@app.callback(
    Output('vibration-month-buttons', 'children'),
    Input('url', 'pathname')
)
def generate_vibration_month_buttons(pathname):
    if pathname == '/vibration':
        return generate_month_buttons(vibration_df, 'vibration')

# New callbacks for new sheets' month buttons
@app.callback(
    Output('lubeoil-month-buttons', 'children'),
    Input('url', 'pathname')
)
def generate_lubeoil_month_buttons(pathname):
    if pathname == '/lubeoil':
        return generate_month_buttons(lube_oil_df, 'lubeoil')

@app.callback(
    Output('spares-month-buttons', 'children'),
    Input('url', 'pathname')
)
def generate_spares_month_buttons(pathname):
    if pathname == '/spares':
        return generate_month_buttons(spares_df, 'spares')

@app.callback(
    Output('contracts-month-buttons', 'children'),
    Input('url', 'pathname')
)
def generate_contracts_month_buttons(pathname):
    if pathname == '/contracts':
        return generate_month_buttons(contracts_df, 'contracts')

@app.callback(
    Output('gatepass-month-buttons', 'children'),
    Input('url', 'pathname')
)
def generate_gatepass_month_buttons(pathname):
    if pathname == '/gatepass':
        return generate_month_buttons(gate_pass_df, 'gatepass')

# Update graphs for PM01 and PM02 (re-used for consistent bar charts)
def update_pm_graphs(sheet_df, prefix):
    @app.callback(
        [Output(f'btn-{prefix}-{month}', 'style') for month in sheet_df['Month'].unique()] + [Output(f'{prefix}-graphs', 'children')],
        [Input(f'btn-{prefix}-{month}', 'n_clicks') for month in sheet_df['Month'].unique()]
    )
    def update_sheet_graphs(*clicked_buttons):
        months_clicked = []
        styles = []
        graphs = []
        for i, month in enumerate(sheet_df['Month'].unique()):
            if clicked_buttons[i] % 2 == 1: # Selected
                months_clicked.append(month)
                styles.append(selected_month_button_style) # Keep green background
            else: # Deselected
                styles.append(deselected_month_button_style) # Turn to black background

        # Generate graphs for the selected months
        # Defined gradient-like colors for PM graphs
        planned_colors = ['#4CAF50', '#66BB6A', '#81C784', '#9CCC65', '#D4E157']
        executed_colors = ['#FFC107', '#FFD54F', '#FFEB3B', '#FFF176', '#FFEE58']

        for i, month in enumerate(months_clicked):
            month_data = sheet_df[sheet_df['Month'] == month]
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=month_data['Plant'],
                y=month_data['Planned'],
                name='Planned',
                marker_color=planned_colors[i % len(planned_colors)],
                text=month_data['Planned'],
                textposition='auto'
            ))
            fig.add_trace(go.Bar(
                x=month_data['Plant'],
                y=month_data['Executed'],
                name='Executed',
                marker_color=executed_colors[i % len(executed_colors)],
                text=month_data['Executed'],
                textposition='auto'
            ))

            fig.update_layout(
                title={
                    'text': f'{prefix.upper()}: Planned vs Executed Jobs ({month})',
                    'font': {'size': 24, 'color': '#333', 'family': 'Arial'},
                    'x': 0.5,  # Center the title
                    'xanchor': 'center'
                },
                barmode='group',
                height=400, # Increased height
                width=600,  # Increased width
                plot_bgcolor='#f9f9f9',
                font=dict(family="Arial", size=12, color="#7f7f7f"),
                margin=dict(l=40, r=40, t=60, b=40), # Increased top margin for title
                legend=dict(
                    x=0.5,
                    y=1.1,
                    xanchor='center',
                    yanchor='top',
                    orientation='h'
                )
            )

            graphs.append(dcc.Graph(figure=fig, style={'width': '48%', 'margin': '10px'})) # Added margin
        
        return styles + [graphs]

update_pm_graphs(pm01_df, 'pm01')
update_pm_graphs(pm02_df, 'pm02')
update_pm_graphs(breakdown_df, 'breakdown')
update_pm_graphs(shutdown_df, 'shutdown')

# Vibration Monitoring Graphs
@app.callback(
    [Output(f'btn-vibration-{month}', 'style') for month in vibration_df['Month'].unique()] +
    [Output('vibration-graphs', 'children')],
    [Input(f'btn-vibration-{month}', 'n_clicks') for month in vibration_df['Month'].unique()]
)
def update_vibration_graphs(*clicked_buttons):
    months_clicked = []
    styles = []
    graphs = []
    for i, month in enumerate(vibration_df['Month'].unique()):
        if clicked_buttons[i] % 2 == 1:
            months_clicked.append(month)
            styles.append(selected_month_button_style)
        else:
            styles.append(deselected_month_button_style)
    
    health_colors = {
        'Critical': '#FF5733', # Red
        'Alert': '#FFC300',    # Orange
        'Normal': '#33FF57',   # Green
        'No Data': '#D3D3D3'   # Grey
    }

    for month in months_clicked:
        month_data = vibration_df[vibration_df['Month'] == month]
        plant_data = month_data.groupby('Plant')['Health'].value_counts().unstack(fill_value=0)
        
        # Ensure all health categories are present to avoid key errors
        for health_status in health_colors.keys():
            if health_status not in plant_data.columns:
                plant_data[health_status] = 0
        
        # Calculate percentages
        plant_data_percent = plant_data.div(plant_data.sum(axis=1), axis=0) * 100
        plant_data_percent = plant_data_percent.round(2)

        fig_percent = go.Figure()
        for health_status, color in health_colors.items():
            if health_status in plant_data_percent.columns:
                fig_percent.add_trace(go.Bar(
                    x=plant_data_percent.index,
                    y=plant_data_percent[health_status],
                    name=health_status,
                    marker_color=color
                ))

        fig_percent.update_layout(
            barmode='stack',
            title={
                'text': f'Equipment Health Status by Plant (Percentage) - {month}',
                'font': {'size': 24, 'color': '#333', 'family': 'Arial'},
                'x': 0.5,
                'xanchor': 'center'
            },
            height=600,
            width=900,
            xaxis_title="Plant",
            yaxis_title="Percentage of Equipment",
            yaxis_tickformat=".0f",
            plot_bgcolor='#f9f9f9',
            font=dict(family="Arial", size=12, color="#7f7f7f"),
            legend=dict(
                x=0.5, y=1.1, xanchor='center', yanchor='top', orientation='h'
            ),
            margin=dict(l=40, r=40, t=80, b=40),
            hovermode='x unified'
        )
        graphs.append(dcc.Graph(figure=fig_percent, style={'width': '90%', 'margin': '20px auto'}))
    
    return styles + [graphs]

# Lube Oil Analysis Graphs
@app.callback(
    [Output(f'btn-lubeoil-{month}', 'style') for month in lube_oil_df['Month'].unique()] +
    [Output('lubeoil-graphs', 'children')],
    [Input(f'btn-lubeoil-{month}', 'n_clicks') for month in lube_oil_df['Month'].unique()]
)
def update_lubeoil_graphs(*clicked_buttons):
    months_clicked = []
    styles = []
    graphs = []
    for i, month in enumerate(lube_oil_df['Month'].unique()):
        if clicked_buttons[i] % 2 == 1:
            months_clicked.append(month)
            styles.append(selected_month_button_style)
        else:
            styles.append(deselected_month_button_style)
    
    for month in months_clicked:
        month_data = lube_oil_df[lube_oil_df['Month'] == month]
        
        # Moisture Trend
        fig_moisture = go.Figure()
        fig_moisture.add_trace(go.Scatter(x=month_data['Equipment'], y=month_data['Moisture (%)'], mode='markers+lines', name='Moisture (%)', marker=dict(color='blue')))
        fig_moisture.update_layout(
            title=f'Monthly Lube Oil Analysis - Moisture Content ({month})',
            xaxis_title='Equipment',
            yaxis_title='Moisture (%)',
            height=400,
            width=800,
            plot_bgcolor='#f9f9f9',
            margin=dict(t=40)
        )
        graphs.append(dcc.Graph(figure=fig_moisture, style={'width': '48%', 'margin': '10px'}))

        # Viscosity Trend
        fig_viscosity = go.Figure()
        fig_viscosity.add_trace(go.Scatter(x=month_data['Equipment'], y=month_data['Viscosity (cSt)'], mode='markers+lines', name='Viscosity (cSt)', marker=dict(color='orange')))
        fig_viscosity.update_layout(
            title=f'Monthly Lube Oil Analysis - Viscosity ({month})',
            xaxis_title='Equipment',
            yaxis_title='Viscosity (cSt)',
            height=400,
            width=800,
            plot_bgcolor='#f9f9f9',
            margin=dict(t=40)
        )
        graphs.append(dcc.Graph(figure=fig_viscosity, style={'width': '48%', 'margin': '10px'}))
    
    return styles + [graphs]


# Spares Management Table
@app.callback(
    [Output(f'btn-spares-{month}', 'style') for month in spares_df['Month'].unique()] +
    [Output('spares-tables', 'children')],
    [Input(f'btn-spares-{month}', 'n_clicks') for month in spares_df['Month'].unique()]
)
def update_spares_table(*clicked_buttons):
    months_clicked = []
    styles = []
    tables = []
    for i, month in enumerate(spares_df['Month'].unique()):
        if clicked_buttons[i] % 2 == 1:
            months_clicked.append(month)
            styles.append(selected_month_button_style)
        else:
            styles.append(deselected_month_button_style)
    
    for month in months_clicked:
        month_data = spares_df[spares_df['Month'] == month]
        
        table = html.Div(
            [
                html.H4(f'Spares Management Details ({month})', style={'margin-top': '20px'}),
                html.Table([
                    html.Thead(html.Tr([html.Th(col) for col in month_data.columns])),
                    html.Tbody([
                        html.Tr([
                            html.Td(month_data.iloc[i][col]) for col in month_data.columns
                        ]) for i in range(len(month_data))
                    ])
                ], style={'width': '100%', 'border-collapse': 'collapse', 'margin-top': '10px'})
            ]
        )
        tables.append(table)
    
    return styles + [tables]

# Running Contracts Table
@app.callback(
    [Output(f'btn-contracts-{month}', 'style') for month in contracts_df['Month'].unique()] +
    [Output('contracts-tables', 'children')],
    [Input(f'btn-contracts-{month}', 'n_clicks') for month in contracts_df['Month'].unique()]
)
def update_contracts_table(*clicked_buttons):
    months_clicked = []
    styles = []
    tables = []
    for i, month in enumerate(contracts_df['Month'].unique()):
        if clicked_buttons[i] % 2 == 1:
            months_clicked.append(month)
            styles.append(selected_month_button_style)
        else:
            styles.append(deselected_month_button_style)
    
    for month in months_clicked:
        month_data = contracts_df[contracts_df['Month'] == month]
        
        table = html.Div(
            [
                html.H4(f'Running Contracts ({month})', style={'margin-top': '20px'}),
                html.Table([
                    html.Thead(html.Tr([html.Th(col) for col in month_data.columns])),
                    html.Tbody([
                        html.Tr([
                            html.Td(month_data.iloc[i][col]) for col in month_data.columns
                        ]) for i in range(len(month_data))
                    ])
                ], style={'width': '100%', 'border-collapse': 'collapse', 'margin-top': '10px'})
            ]
        )
        tables.append(table)
    
    return styles + [tables]

# Gate Pass Details Table
@app.callback(
    [Output(f'btn-gatepass-{month}', 'style') for month in gate_pass_df['Month'].unique()] +
    [Output('gatepass-tables', 'children')],
    [Input(f'btn-gatepass-{month}', 'n_clicks') for month in gate_pass_df['Month'].unique()]
)
def update_gatepass_table(*clicked_buttons):
    months_clicked = []
    styles = []
    tables = []
    for i, month in enumerate(gate_pass_df['Month'].unique()):
        if clicked_buttons[i] % 2 == 1:
            months_clicked.append(month)
            styles.append(selected_month_button_style)
        else:
            styles.append(deselected_month_button_style)
    
    for month in months_clicked:
        month_data = gate_pass_df[gate_pass_df['Month'] == month]
        
        table = html.Div(
            [
                html.H4(f'Gate Pass Details ({month})', style={'margin-top': '20px'}),
                html.Table([
                    html.Thead(html.Tr([html.Th(col) for col in month_data.columns])),
                    html.Tbody([
                        html.Tr([
                            html.Td(month_data.iloc[i][col]) for col in month_data.columns
                        ]) for i in range(len(month_data))
                    ])
                ], style={'width': '100%', 'border-collapse': 'collapse', 'margin-top': '10px'})
            ]
        )
        tables.append(table)
    
    return styles + [tables]


# Main Layout and URL routing callback
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Store(id='chat-messages-store', data=[]), # Store for chat history
    dcc.Store(id='chat-state-store', data={'is_minimized': True}), # Store for chatbot state
    html.Div(id='chatbot-ui-container', children=[
        chatbot_main_ui('main'),
        chatbot_avatar_ui('main')
    ])
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/main-dashboard':
        return main_dashboard_layout
    elif pathname == '/pm01':
        return pm01_layout
    elif pathname == '/pm02':
        return pm02_layout
    elif pathname == '/breakdown':
        return breakdown_layout
    elif pathname == '/shutdown':
        return shutdown_layout
    elif pathname == '/vibration':
        return vibration_layout
    elif pathname == '/lubeoil':
        return lubeoil_layout
    elif pathname == '/spares':
        return spares_layout
    elif pathname == '/contracts':
        return contracts_layout
    elif pathname == '/gatepass':
        return gatepass_layout
    elif pathname == '/chatbot-clusters':
        return chatbot_clusters_layout
    else:
        return home_layout

# Chatbot callbacks
# This callback manages the minimization/maximization of the chatbot widget
@app.callback(
    Output({'type': 'chatbot-container', 'index': ALL}, 'style'),
    Output({'type': 'chatbot-avatar', 'index': ALL}, 'style'),
    Output('chat-state-store', 'data'),
    Input({'type': 'chatbot-minimize-button', 'index': ALL}, 'n_clicks'),
    Input({'type': 'chatbot-avatar', 'index': ALL}, 'n_clicks'),
    State('chat-state-store', 'data'),
    prevent_initial_call=True
)
def toggle_chatbot_visibility(minimize_clicks, avatar_clicks, state_data):
    is_minimized = state_data['is_minimized']
    
    # Determine if a button was clicked
    button_id = ctx.triggered_id
    if button_id and (isinstance(button_id, dict) and button_id['type'] == 'chatbot-minimize-button' or isinstance(button_id, dict) and button_id['type'] == 'chatbot-avatar'):
        is_minimized = not is_minimized
    
    state_data['is_minimized'] = is_minimized

    container_style = {'display': 'none'} if is_minimized else {
        'width': '350px',
        'position': 'fixed',
        'bottom': '20px',
        'right': '20px',
        'backgroundColor': 'white',
        'boxShadow': '0px 0px 15px rgba(0,0,0,0.2)',
        'borderRadius': '10px',
        'zIndex': '1000',
        'display': 'flex',
        'flexDirection': 'column',
        'height': '450px',
        'overflow': 'hidden'
    }

    avatar_style = {'display': 'none'} if not is_minimized else {
        'width': '56px',
        'height': '56px',
        'borderRadius': '50%',
        'backgroundColor': '#007bff',
        'color': 'white',
        'border': 'none',
        'cursor': 'pointer',
        'position': 'fixed',
        'bottom': '20px',
        'right': '20px',
        'zIndex': '1001',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.2)',
        'display': 'flex',
        'justifyContent': 'center',
        'alignItems': 'center'
    }

    return [container_style] * len(minimize_clicks), [avatar_style] * len(avatar_clicks), state_data

# This callback handles the chat messages
@app.callback(
    Output({'type': 'chat-response', 'index': ALL}, 'children'),
    Output({'type': 'chat-input', 'index': ALL}, 'value'),
    Output('chat-messages-store', 'data'),
    [
        Input({'type': 'chat-submit', 'index': ALL}, 'n_clicks'),
        Input({'type': 'chat-clear', 'index': ALL}, 'n_clicks'),
    ],
    State({'type': 'chat-input', 'index': ALL}, 'value'),
    State('chat-messages-store', 'data'),
    prevent_initial_call=True
)
def update_chat_history(submit_clicks, clear_clicks, user_input_list, stored_messages):
    triggered_id = ctx.triggered_id
    
    # Check if a clear button was clicked
    if triggered_id and triggered_id['type'] == 'chat-clear' and sum(clear_clicks) > 0:
        return [[]] * len(user_input_list), [''] * len(user_input_list), []

    # Check if a submit button was clicked and there is user input
    if triggered_id and triggered_id['type'] == 'chat-submit' and sum(submit_clicks) > 0:
        user_message = user_input_list[0]
        if user_message.strip():
            # Append user message
            user_msg_element = html.Div(user_message, style={
                'backgroundColor': '#dcf8c6', # Light green for user
                'borderRadius': '10px',
                'padding': '8px 12px',
                'marginBottom': '5px',
                'maxWidth': '80%',
                'alignSelf': 'flex-end' # Align to the right
            })
            stored_messages.append({'speaker': 'user', 'text': user_message})
            
            # Get bot response using the chat session
            response = chat_session.send_message(user_message).text
            bot_msg_element = html.Div(response, style={
                'backgroundColor': '#ffffff', # White for bot
                'borderRadius': '10px',
                'padding': '8px 12px',
                'marginBottom': '5px',
                'maxWidth': '80%',
                'alignSelf': 'flex-start' # Align to the left
            })
            stored_messages.append({'speaker': 'bot', 'text': response})

            # Create the list of message components from the stored data
            chat_history_elements = [
                html.Div(
                    message['text'],
                    style={
                        'backgroundColor': '#dcf8c6' if message['speaker'] == 'user' else '#ffffff',
                        'borderRadius': '10px',
                        'padding': '8px 12px',
                        'marginBottom': '5px',
                        'maxWidth': '80%',
                        'alignSelf': 'flex-end' if message['speaker'] == 'user' else 'flex-start'
                    }
                ) for message in stored_messages
            ]

            return [chat_history_elements] * len(user_input_list), [''] * len(user_input_list), stored_messages

    return [[]] * len(user_input_list), [''] * len(user_input_list), stored_messages

if __name__ == '__main__':
    app.run(debug=True)
