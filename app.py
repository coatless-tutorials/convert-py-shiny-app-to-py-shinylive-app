from shiny import ui, render, reactive, req, App
import shinyswatch
import pandas as pd

# Define UI
app_ui = ui.page_fluid(
    # Apply theme
    shinyswatch.theme.flatly,
    
    # App title
    ui.h1("CSV File Uploader"),
  
    # Sidebar layout with input and output definitions
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_file("data_file", "Choose CSV File", accept=[".csv"], multiple=False),
            ui.input_checkbox("header", "Header", value = True),
            open = "always"
        ),

        # Show CSV data
        ui.output_table("file_contents"),
    )
)

# Define server logic
def server(input, output, session):
  
    # Read CSV file
    @reactive.calc
    def file_data():
        req(input.data_file())
        data_file_infos = input.data_file()
        df = pd.read_csv(
            data_file_infos[0]["datapath"],
            header = 'infer' if input.header() == True else None )
        return df
    
    # Show CSV data
    @render.table
    def file_contents():
        return file_data()

# Run the application
app = App(app_ui, server)
