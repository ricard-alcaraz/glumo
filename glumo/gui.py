import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
from io import BytesIO
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
import logging
from glumo.config import get_api_instance

"""from glumo.api_clients.api import (
    store_credentials,
    get_patient_connections,
    login,
    get_patient_connections,
    get_cgm_data,
    store_patient_id,
    store_token,
    get_stored_token,
    get_stored_patient_id,
    get_stored_credentials,
)
"""
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class GlumoApp(tk.Tk):
    def __init__(self):  # Initialize the application
        super().__init__()
        self.title("CGM Data Plotter")
        self.geometry("800x600")
        self.scheduled_tasks = []
        self.fetch_data_id = None
        self.fetch_data_interval = 60000
        self.is_running = True
        self.most_recent_value_label = ttk.Label(self, text="Most Recent Value: N/A")
        self.most_recent_value_label.pack(pady=10)
        self.plot_frame = ttk.Frame(self)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)
        self.api = None
        
        self.saved_credentials = None
       

        self.api_var = tk.StringVar()
        self.api_dropdown = ttk.Combobox(self, textvariable=self.api_var)
        self.api_dropdown['values'] = ['Nightscout', 'LinkUP']  # Add more APIs as needed
        self.api_dropdown.pack(pady=10)
        self.api_dropdown.bind('<<ComboboxSelected>>', self.api_selected)

        self.create_widgets()


        



        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def select_api(self):
        """Selects the API to use based on the user's preference.
        This method is called when the application is first created.
        Returns:
            BaseAPI: The API instance to use.
        """
        # Replace with actual selection logic
        #api_type = 'LinkUP'  # Or 'B' or any other logic to select API
        
        api_type = 'Nightscout'
        return get_api_instance(api_type)
    
    def api_selected(self, event):
        self.api = get_api_instance(self.api_var.get())
        self.show_login_prompt()
        
        if self.api.name == 'Nightscout':
            token = self.api.get_stored_token()
            print(token)
            if token:
                self.saved_credentials = True
            else:
                self.saved_credentials = False
        if self.api.name == 'LinkUP':
            email, password = self.api.get_stored_credentials()
            if email and password:
                self.saved_credentials = True
            else:
                self.saved_credentials = False

        if self.saved_credentials:
            logging.debug("Stored credentials found, attempting auto login")
            self.auto_login()
        else:
            logging.debug("No stored credentials found, showing login prompt")
            self.show_login_prompt()
         
    
    def create_widgets(self):
        """Creates the widgets for the application.
        This method is called when the application is first created.
        """
        logging.debug("Creating widgets")
        self.fetch_button = ttk.Button(self, text="Fetch Data", command=self.fetch_data)
        self.login_button = ttk.Button(self, text="Login", command=self.show_login_window)
        self.welcome_label = ttk.Label(self, text="Welcome! Please log in to continue.")

    def show_login_prompt(self):
        """Shows the login prompt to the user.
        This method is called when the user has not logged in before.
        """
        logging.debug("Showing login prompt")
        self.welcome_label = ttk.Label(self, text="Welcome! Please log in to continue.")
        self.welcome_label.pack(pady=20)
        self.login_button.pack(pady=20)

    def setup_main_interface(self):
        """Sets up the main interface of the application.
        This method is called when the user has logged in.
        """
        logging.debug("Setting up main interface")
        self.welcome_label.pack_forget()
        self.login_button.pack_forget()
        self.fetch_button.pack(pady=20)


    def show_login_window(self):
        """Shows the login window to the user.
        This method is called when the user has not logged in before.
        """
        logging.debug("Showing login window")
        
        login_window = tk.Toplevel(self)
        login_window.title("Login")
        
        if self.api.name == 'Nightscout':
            ttk.Label(login_window, text="Nightscout Token:").pack(pady=5)
            token_entry = tk.Entry(login_window)
            token_entry.pack(pady=5)

        elif self.api.name == 'LinkUP':
            tk.Label(login_window, text="Email:").pack(pady=5)
            email_entry = tk.Entry(login_window)
            email_entry.pack(pady=5)

            tk.Label(login_window, text="Password:").pack(pady=5)
            password_entry = tk.Entry(login_window, show='*')
            password_entry.pack(pady=5)

        def submit():
            """Submits the login form data to the server.
            This method is called when the login form is submitted.
            """
            if self.api.name == 'Nightscout':
                token = token_entry.get()
                self.api.store_token(token)
                print(token)
                try:
                    login_window.destroy()
                    self.setup_main_interface()
                    logging.info("Login successful")
                except Exception as e:
                    logging.error(f"Incorrect token: {str(e)}")
            if self.api.name == 'LinkUP':
                email = email_entry.get()
                password = password_entry.get()
                self.api.store_credentials(email, password)
                try:
                    logging.debug(f"Attempting login")
                    self.api.login()
                    login_window.destroy()
                    self.setup_main_interface()
                    logging.info("Login successful")
                except Exception as e:
                    logging.error(f"Login failed: {str(e)}")
        
        tk.Button(login_window, text="Submit", command=submit).pack(pady=20)

    def auto_login(self):
        """Automatically logs in to the Glumo API.
        This method is called when the application is first created.
        """
        logging.debug("Auto login initiated")
        self.setup_main_interface()
        self.start_auto_refresh()


    def plot_data(self, timestamps, values):
        """Plots the CGM data.
        This method is called when new CGM data is available.
        Args:
            timestamps (list): A list of timestamps for the CGM data.
            values (list): A list of values for the CGM data.
        """
        logging.debug("Plotting data")
        # Clear any existing plots
        try:
            #print("Timestamps:", timestamps)
            #print("Values:", values)
            for widget in self.plot_frame.winfo_children():
                widget.destroy()
            fig, ax = plt.subplots(figsize=(10, 6))

            #ax.plot(timestamps, values, linestyle='-', c='g', marker=None)
            if len(timestamps) < 2:
                logging.warning("Not enough data to plot")
                return

            # Plot the data with segments colored based on the value range
            for i in range(len(timestamps) - 1):
                x_values = [timestamps[i], timestamps[i + 1]]
                y_values = [values[i], values[i + 1]]
                color = 'green' if 70 <= values[i] <= 180 and 70 <= values[i + 1] <= 180 else 'red'
                ax.plot(x_values, y_values, color=color)

            #ax.set_xlabel('Timestamp')
            #ax.set_ylabel('ValueInMgPerDl')
            #ax.set_title('CGM Data Over Time')
            ax.set_ylim(50, 250)
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            plt.xticks(rotation=45)
            
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            # Embed the plot in Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            if values:
                most_recent_value = self.api.get_last_cgm_value(values)
                self.most_recent_value_label.config(text=f"Most Recent Value: {most_recent_value} mg/dL")

        except Exception as e:
            logging.error(f"Error plotting data: {e}")
            

    def fetch_data(self):
        """Fetches CGM data from the Glumo API.
        This method is called periodically to fetch CGM data.
        """
        logging.debug("Fetching data")
        try:
            data = self.api.get_cgm_data()
            
            if data:
                timestamps, values = self.api.formatData(data)
                self.plot_data(timestamps, values)
            else:
                logging.warning("No graph data available")
        except Exception as e:
            logging.error(f"Error fetching data: {e}")

    def refresh_data(self):
        """Refreshes the CGM data.
        This method is called periodically to refresh the CGM data.
        """
        logging.debug("Refreshing data")
        if self.is_running:
            self.fetch_data()
            self.fetch_data_id = self.after(self.fetch_data_interval, self.refresh_data)
            self.scheduled_tasks.append(self.fetch_data_id)


    def start_auto_refresh(self):
        """Starts the auto refresh feature.
        This method is called when the application is first created.
        """
        logging.debug("Starting auto refresh")
        self.refresh_data()

    def stop_periodic_fetch(self):
        """Stops the periodic fetch feature.
        This method is called when the application is closing.
        """
        logging.debug("Stopping periodic fetch")
        if self.fetch_data_id is not None:
            print("Cancelling fetch data")
            self.after_cancel(self.fetch_data_id)
            self.fetch_data_id = None

    def on_closing(self):
        """Handles the application closing event.
        This method is called when the application is closing.
        """
        logging.debug("Closing application")
        self.stop_periodic_fetch()  # Stop periodic data fetch
        for task_id in self.scheduled_tasks:
            logging.debug(f"Tasks to cancel: {task_id}")
            self.after_cancel(task_id)
        
        self.is_running = False
        # Close the application
        self.destroy()
        self.quit()
          

if __name__ == "__main__":
    app = GlumoApp()
    app.mainloop()