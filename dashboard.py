# Advanced Cloud Development Technologies Project - Multi-API Dashboard

import requests # HTTP library to make API requests to external services (REST Countries, Open-Meteo, Nager, and MealDB)
import tkinter as tk # Core GUI framework for building the Tkinter dashboard application
from tkinter import ttk, messagebox # ttk provides modern themed widgets; messagebox for error/warning dialogs
from PIL import Image, ImageTk # PIL (Pillow) for loading and displaying country flag images
import io # io module for handling in-memory binary data streams (flag images from API)
import random # random module for generating simulated data (used in various places)
import datetime # datetime for parsing ISO format timestamps from weather API responses
import threading # threading to run network API calls in background threads (prevents GUI freezing)
import matplotlib # matplotlib for creating charts and plots embedded in the Tkinter GUI
matplotlib.use('TkAgg')
from matplotlib.figure import Figure # Use TkAgg backend so matplotlib integrates with Tkinter instead of creating separate windows
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # FigureCanvasTkAgg embeds matplotlib plots directly into Tkinter widgets

# API Endpoints
RESTCOUNTRIES_URL = 'https://restcountries.com/v3.1/name/{}'
OPEN_METEO_URL = 'https://api.open-meteo.com/v1/forecast'
NAGER_URL = 'https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}'
MEALDB_URL = 'https://www.themealdb.com/api/json/v1/1/search.php?s={}'

REQUEST_TIMEOUT = 8  # seconds


# API helper functions
def fetch_country(name):
    """Fetch country info from REST Countries.
    Returns dict or raises Exception.
    """
    try:
        print(f"[DEBUG] fetch_country: {name}")
        r = requests.get(RESTCOUNTRIES_URL.format(name), timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        if not data:
            raise ValueError('No country data')
        # take the first match
        c = data[0]
        country = {
            'name': c.get('name', {}).get('common', 'Unknown'),
            'official': c.get('name', {}).get('official', ''),
            'capital': c.get('capital', [''])[0] if c.get('capital') else '',
            'population': c.get('population', 0),
            'region': c.get('region', ''),
            'subregion': c.get('subregion', ''),
            'borders': c.get('borders', []),
            'flag_url': c.get('flags', {}).get('png', ''),
            'latlng': c.get('capitalInfo', {}).get('latlng') or c.get('latlng', [None, None]),
            'cca2': c.get('cca2', ''),
        }
        return country
    except Exception as e:
        print('[ERROR] fetch_country', e)
        raise


def fetch_weather(lat, lon):
    """Fetch weather from Open-Meteo. Return simplified dict."""
    try:
        print(f"[DEBUG] fetch_weather lat={lat} lon={lon}")
        params = {
            'latitude': lat,
            'longitude': lon,
            'hourly': 'temperature_2m',
            'daily': 'temperature_2m_max,temperature_2m_min',
            'current_weather': True,
            'timezone': 'auto'
        }
        r = requests.get(OPEN_METEO_URL, params=params, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        j = r.json()
        # basic parsing
        weather = {
            'current': j.get('current_weather', {}),
            'hourly': j.get('hourly', {}),
            'daily': j.get('daily', {}),
        }
        return weather
    except Exception as e:
        print('[ERROR] fetch_weather', e)
        raise


def fetch_holidays(country_code, year=2025):
    """Fetch public holidays using Nager.Date v3 API for a given year.
    Returns list of holiday objects or raises.
    """
    try:
        print(f"[DEBUG] fetch_holidays: {country_code} year={year}")
        url = NAGER_URL.format(year=year, country_code=country_code)
        r = requests.get(url, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print('[ERROR] fetch_holidays', e)
        raise


def fetch_meals(query):
    """Search meals via TheMealDB."""
    try:
        print(f"[DEBUG] fetch_meals: {query}")
        r = requests.get(MEALDB_URL.format(query), timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        j = r.json()
        return j.get('meals')
    except Exception as e:
        print('[ERROR] fetch_meals', e)
        raise


# GUI dashbaord application
class DashboardApp:
    def __init__(self, root):
        self.root = root
        root.title('Multi-API Dashboard - Student Project')
        root.geometry('1100x700')

        # Top frame for controls
        top = ttk.Frame(root, padding=8)
        top.pack(side='top', fill='x')

        ttk.Label(top, text='Country:').pack(side='left')
        self.country_var = tk.StringVar(value='United Kingdom')
        self.country_entry = ttk.Entry(top, textvariable=self.country_var, width=25)
        self.country_entry.pack(side='left', padx=4)
        self.search_btn = ttk.Button(top, text='Search', command=self.on_search)
        self.search_btn.pack(side='left', padx=4)

        ttk.Label(top, text='Meal search:').pack(side='left', padx=(20,4))
        self.meal_var = tk.StringVar()
        self.meal_entry = ttk.Entry(top, textvariable=self.meal_var, width=20)
        self.meal_entry.pack(side='left')
        self.meal_btn = ttk.Button(top, text='Find Meal', command=self.on_meal_search)
        self.meal_btn.pack(side='left', padx=4)

        # Main paned layout
        main_pane = ttk.Panedwindow(root, orient='horizontal')
        main_pane.pack(fill='both', expand=True)

        # Left pane - Country & Weather
        left_frame = ttk.Frame(main_pane, width=360)
        main_pane.add(left_frame, weight=1)

        # Country info area
        self.flag_lbl = ttk.Label(left_frame)
        self.flag_lbl.pack(pady=6)

        self.info_text = tk.Text(left_frame, width=45, height=12)
        self.info_text.pack(padx=6, pady=4)

        # Holidays list
        ttk.Label(left_frame, text='Public holidays (2025):').pack(anchor='w', padx=6)
        self.holidays_list = tk.Listbox(left_frame, height=18)
        self.holidays_list.pack(fill='both', expand=True, padx=6, pady=4)

        # Middle pane - Plot area
        mid_frame = ttk.Frame(main_pane)
        main_pane.add(mid_frame, weight=2)

        # Plot figure - single chart for hourly weather
        self.fig = Figure(figsize=(6,5), dpi=100)
        self.ax_weather = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=mid_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Right pane - Meals
        right_frame = ttk.Frame(main_pane, width=360)
        main_pane.add(right_frame, weight=1)

        ttk.Label(right_frame, text='Meals:').pack(anchor='w', padx=6)
        self.meals_list = tk.Listbox(right_frame, height=10)
        self.meals_list.pack(fill='both', padx=6, pady=4)
        self.meals_list.bind('<<ListboxSelect>>', self.on_meal_select)

        self.meal_detail = tk.Text(right_frame, width=40, height=20)
        self.meal_detail.pack(fill='both', expand=True, padx=6, pady=4)

        # Status bar
        self.status = tk.StringVar(value='Ready')
        ttk.Label(root, textvariable=self.status, relief='sunken', anchor='w').pack(side='bottom', fill='x')

    def set_status(self, msg):
        self.status.set(msg)
        print('[STATUS]', msg)

    def on_search(self):
        country = self.country_var.get().strip()
        if not country:
            messagebox.showwarning('Input', 'Please enter a country name')
            return

        threading.Thread(target=self._do_search, args=(country,), daemon=True).start()

    def _do_search(self, country):
        self.set_status('Searching country...')
        try:
            c = fetch_country(country)
        except Exception:
            self.set_status('Failed to fetch country')
            messagebox.showerror('Error', 'Could not fetch country data')
            return

        # update front end with country info
        self._display_country(c)

        # weather: try using capital lat/lng
        latlng = c.get('latlng') or [None, None]
        lat, lon = (latlng[0], latlng[1]) if latlng and len(latlng) >= 2 else (None, None)
        if lat is None or lon is None:
            # fallback: use known capitals? For simplicity, set to 0,0
            print('[WARN] No lat/lng for country, using default coords')
            lat, lon = 51.5074, -0.1278  # London fallback

        self.set_status('Fetching weather...')
        try:
            weather = fetch_weather(lat, lon)
            self._display_weather(weather)
        except Exception:
            self.set_status('Weather error')
            # continue

        # holidays
        cca2 = c.get('cca2', '')
        if cca2:
            self.set_status('Fetching holidays...')
            try:
                holidays = fetch_holidays(cca2)
                self._display_holidays(holidays)
            except Exception:
                self.set_status('Holidays error')

        self.set_status('Done')

    def _display_country(self, c):
        # show flag image (if available)
        flag_url = c.get('flag_url')
        if flag_url:
            try:
                r = requests.get(flag_url, timeout=REQUEST_TIMEOUT)
                r.raise_for_status()
                img_data = r.content
                im = Image.open(io.BytesIO(img_data)).resize((160, 100))
                self.flag_img = ImageTk.PhotoImage(im)
                self.flag_lbl.config(image=self.flag_img)
            except Exception as e:
                print('[WARN] flag load failed', e)
                self.flag_lbl.config(image='')
        else:
            self.flag_lbl.config(image='')

        # text info
        self.info_text.config(state='normal')
        self.info_text.delete('1.0', tk.END)
        lines = [
            f"Name: {c.get('name')}",
            f"Official: {c.get('official')}",
            f"Capital: {c.get('capital')}",
            f"Region: {c.get('region')} / {c.get('subregion')}",
            f"Population: {c.get('population')}",
            f"Borders: {', '.join(c.get('borders') or [])}",
            f"CCA2: {c.get('cca2')}",
        ]
        self.info_text.insert(tk.END, '\n'.join(lines))
        self.info_text.config(state='disabled')

    def _display_weather(self, weather):
        # Display current temp and plot hourly temps (hours on x-axis, Celsius on y-axis)
        current = weather.get('current', {})
        hour_times = weather.get('hourly', {}).get('time', [])
        temps = weather.get('hourly', {}).get('temperature_2m', [])

        # Clear previous plot
        self.ax_weather.clear()

        # Show current temperature in the title
        current_temp = current.get('temperature', 'N/A')
        self.ax_weather.set_title(f"Current Temperature: {current_temp} Celsius", fontsize=14, fontweight='bold')

        # Plot hourly temperatures (next 24 hours)
        if temps and hour_times:
            # Use the first 24 hours of data
            hours_ahead = list(range(24))
            temps_24h = temps[:24]
            
            self.ax_weather.plot(hours_ahead, temps_24h, marker='o', linestyle='-', color='blue', linewidth=2.5, markersize=6)
            self.ax_weather.set_xlabel('Hours from Now', fontsize=11, fontweight='bold')
            self.ax_weather.set_ylabel('Temperature (Celsius)', fontsize=11, fontweight='bold')
            self.ax_weather.set_xticks(range(0, 24, 2))  # Show every 2 hours for clarity
            self.ax_weather.set_xlim(-0.5, 23.5)
            self.ax_weather.grid(True, alpha=0.4, linestyle='--')
            self.fig.tight_layout()
        else:
            self.ax_weather.text(0.5, 0.5, 'No weather data available', ha='center', va='center')

        self.canvas.draw()

    def _display_holidays(self, holidays):
        self.holidays_list.delete(0, tk.END)
        if not holidays:
            self.holidays_list.insert(tk.END, 'No holidays found')
            return
        for h in holidays[:20]:
            name = h.get('localName') or h.get('name')
            date = h.get('date')
            self.holidays_list.insert(tk.END, f"{date} - {name}")

    def _display_traffic(self, traffic):
        # This method was removed — traffic plotting is not part of the dashboard per
        # project update. Keeping the method stub removed to avoid accidental calls.
        pass

    def on_meal_search(self):
        q = self.meal_var.get().strip()
        if not q:
            messagebox.showwarning('Input', 'Enter a meal name or ingredient')
            return
        threading.Thread(target=self._do_meal_search, args=(q,), daemon=True).start()

    def _do_meal_search(self, q):
        self.set_status('Searching meals...')
        try:
            meals = fetch_meals(q)
        except Exception:
            self.set_status('Meal search failed')
            messagebox.showerror('Error', 'Meal API error')
            return

        self.meals = meals or []
        self.meals_list.delete(0, tk.END)
        if not self.meals:
            self.meals_list.insert(tk.END, 'No meals found')
            self.set_status('No meals')
            return
        for m in self.meals:
            self.meals_list.insert(tk.END, m.get('strMeal'))
        self.set_status('Meals loaded')

    def on_meal_select(self, evt):
        sel = evt.widget.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx >= len(getattr(self, 'meals', [])):
            return
        m = self.meals[idx]
        self._display_meal_detail(m)

    def _display_meal_detail(self, m):
        self.meal_detail.config(state='normal')
        self.meal_detail.delete('1.0', tk.END)
        parts = [f"Meal: {m.get('strMeal')}", f"Category: {m.get('strCategory')}", f"Area: {m.get('strArea')}", '', 'Ingredients:']
        # gather ingredients
        for i in range(1, 21):
            ing = m.get(f'strIngredient{i}')
            measure = m.get(f'strMeasure{i}')
            if ing and ing.strip():
                parts.append(f"- {ing} : {measure}")
        parts.append('')
        parts.append('Instructions:')
        parts.append(m.get('strInstructions') or '')
        self.meal_detail.insert(tk.END, '\n'.join(parts))
        self.meal_detail.config(state='disabled')


def main():
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()