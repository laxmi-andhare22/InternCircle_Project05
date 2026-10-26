import requests
import json
from datetime import datetime

# --- CONFIG ---
# Get free API key from: https://openweathermap.org/api
# For demo, we use a placeholder - user can enter their own
API_KEY = "YOUR_API_KEY_HERE"  # Replace with your key
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

def get_weather_cli():
    """CLI Version - REST API integration with JSON parsing"""
    print("\n=== Weather App - CLI Mode ===")
    city = input("Enter city name (e.g. Mumbai, London): ").strip()
    if not city:
        city = "Mumbai"
    
    api_key = input("Enter OpenWeather API Key (or press Enter for demo): ").strip()
    if not api_key or api_key == "":
        # Demo mode with sample data if no key
        print("\n[Demo Mode - No API Key] Showing sample structure")
        sample_data = {
            "name": city,
            "main": {"temp": 302.15, "humidity": 78, "feels_like": 306.15, "pressure": 1012},
            "weather": [{"main": "Clouds", "description": "scattered clouds"}],
            "wind": {"speed": 3.5},
            "sys": {"country": "IN", "sunrise": 1690000000, "sunset": 1690040000}
        }
        display_weather(sample_data)
        return
    
    # Live API call
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"  # Celsius
    }
    
    try:
        print(f"\nFetching live weather for {city}...")
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()  # JSON parsing
        
        # Save raw JSON for verification
        with open("weather_response.json", "w") as f:
            json.dump(data, f, indent=2)
        print("Raw JSON saved to weather_response.json")
        
        display_weather(data)
        
        # Also fetch forecast
        forecast_params = {"q": city, "appid": api_key, "units": "metric"}
        forecast_res = requests.get(FORECAST_URL, params=forecast_params, timeout=10)
        if forecast_res.status_code == 200:
            forecast_data = forecast_res.json()
            display_forecast(forecast_data)
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            print("Error: Invalid API Key! Get free key from openweathermap.org")
        elif response.status_code == 404:
            print(f"Error: City '{city}' not found!")
        else:
            print(f"HTTP Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Network Error: {e}")
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON response")

def display_weather(data):
    """Clean display of weather data"""
    try:
        city = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp = data.get("main", {}).get("temp", "N/A")
        feels_like = data.get("main", {}).get("feels_like", "N/A")
        humidity = data.get("main", {}).get("humidity", "N/A")
        pressure = data.get("main", {}).get("pressure", "N/A")
        weather_main = data.get("weather", [{}])[0].get("main", "N/A")
        description = data.get("weather", [{}])[0].get("description", "N/A")
        wind = data.get("wind", {}).get("speed", "N/A")
        
        # Handle Kelvin to Celsius if needed (when units not metric)
        if isinstance(temp, (int, float)) and temp > 100:
            temp = temp - 273.15
            feels_like = feels_like - 273.15 if isinstance(feels_like, (int, float)) else feels_like
        
        print("\n" + "="*40)
        print(f"  WEATHER REPORT: {city}, {country}")
        print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*40)
        print(f"  Temperature    : {temp}°C")
        print(f"  Feels Like     : {feels_like}°C")
        print(f"  Condition      : {weather_main} ({description})")
        print(f"  Humidity       : {humidity}%")
        print(f"  Pressure       : {pressure} hPa")
        print(f"  Wind Speed     : {wind} m/s")
        print("="*40)
        
        # Log to file
        with open("weather_history.txt", "a") as f:
            f.write(f"{datetime.now()} | {city} | {temp}C | {description} | Humidity {humidity}%\n")
            
    except Exception as e:
        print(f"Error displaying data: {e}")
        print(f"Raw data: {data}")

def display_forecast(data):
    print("\n--- 5-Day Forecast (3-hour intervals) ---")
    try:
        for item in data.get("list", [])[:5]:  # Show next 5 intervals
            dt = item.get("dt_txt", "")
            temp = item.get("main", {}).get("temp", "")
            desc = item.get("weather", [{}])[0].get("description", "")
            print(f"  {dt} : {temp}°C, {desc}")
    except Exception as e:
        print(f"Forecast parse error: {e}")

def tkinter_app():
    """GUI Version using Tkinter"""
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
    except ImportError:
        print("Tkinter not available on this system, using CLI only.")
        return
    
    root = tk.Tk()
    root.title("Weather App - Live API")
    root.geometry("400x500")
    root.configure(bg="#1e293b")
    
    style = ttk.Style()
    style.configure("TLabel", background="#1e293b", foreground="white", font=("Arial", 11))
    style.configure("TButton", font=("Arial", 11, "bold"))
    
    tk.Label(root, text="Weather App", font=("Arial", 20, "bold"), bg="#1e293b", fg="white").pack(pady=15)
    
    frame = tk.Frame(root, bg="#1e293b")
    frame.pack(pady=10)
    
    tk.Label(frame, text="City:", bg="#1e293b", fg="white", font=("Arial", 11)).grid(row=0, column=0, padx=5)
    city_entry = tk.Entry(frame, font=("Arial", 12), width=20)
    city_entry.grid(row=0, column=1, padx=5)
    city_entry.insert(0, "Mumbai")
    
    tk.Label(frame, text="API Key:", bg="#1e293b", fg="white", font=("Arial", 11)).grid(row=1, column=0, padx=5, pady=10)
    api_entry = tk.Entry(frame, font=("Arial", 10), width=20, show="*")
    api_entry.grid(row=1, column=1, padx=5, pady=10)
    
    result_text = tk.Text(root, height=18, width=45, font=("Consolas", 10), bg="#0f172a", fg="#e2e8f0", bd=0)
    result_text.pack(pady=15, padx=15)
    
    def fetch_gui():
        city = city_entry.get().strip()
        api_key = api_entry.get().strip()
        if not city:
            messagebox.showwarning("Input", "Enter city name!")
            return
        if not api_key:
            messagebox.showinfo("Demo", "Enter API Key for live data. Get free key from openweathermap.org")
            return
        
        params = {"q": city, "appid": api_key, "units": "metric"}
        try:
            res = requests.get(BASE_URL, params=params, timeout=10)
            res.raise_for_status()
            data = res.json()
            
            result_text.delete(1.0, tk.END)
            output = f"City: {data.get('name')} {data.get('sys',{}).get('country','')}\n"
            output += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            output += "-"*35 + "\n"
            output += f"Temp: {data['main']['temp']}°C\n"
            output += f"Feels Like: {data['main']['feels_like']}°C\n"
            output += f"Condition: {data['weather'][0]['description'].title()}\n"
            output += f"Humidity: {data['main']['humidity']}%\n"
            output += f"Pressure: {data['main']['pressure']} hPa\n"
            output += f"Wind: {data['wind']['speed']} m/s\n"
            output += "-"*35 + "\n"
            output += "Data from OpenWeatherMap API\n"
            result_text.insert(tk.END, output)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    tk.Button(root, text="Get Live Weather →", command=fetch_gui, bg="#3b82f6", fg="white", font=("Arial", 12, "bold"), bd=0, padx=20, pady=8).pack()
    
    tk.Label(root, text="Powered by OpenWeatherMap API", bg="#1e293b", fg="#94a3b8", font=("Arial", 9)).pack(side=tk.BOTTOM, pady=10)
    
    root.mainloop()

def main():
    print("==============================")
    print(" WEATHER APP - CAPSTONE")
    print("==============================")
    print("1. CLI Mode (Live API)")
    print("2. GUI Mode (Tkinter)")
    print("3. Exit")
    
    while True:
        ch = input("\nChoose (1-3): ").strip()
        if ch == '1':
            get_weather_cli()
        elif ch == '2':
            tkinter_app()
        elif ch == '3':
            print("Bye! Check weather_history.txt")
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()