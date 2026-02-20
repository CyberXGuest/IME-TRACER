#!/usr/bin/env python3
"""
=====================================================
EDUCATIONAL OSINT TOOLKIT
=====================================================
Purpose: Learn about APIs, geolocation concepts, and 
         public data lookup techniques
         
Legal Notice: This tool is for EDUCATIONAL PURPOSES ONLY.
              Use only on YOUR OWN devices or with explicit
              written permission.
=====================================================
"""

import os
import sys
import json
import time
import datetime
import hashlib
import platform
import subprocess
from pathlib import Path

# Try to import required libraries with helpful error messages
try:
    import requests
except ImportError:
    print("\n[!] Installing required library: requests")
    os.system("pip install requests")
    import requests

try:
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone
except ImportError:
    print("\n[!] Installing required library: phonenumbers")
    os.system("pip install phonenumbers")
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone

try:
    from colorama import init, Fore, Style, Back
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    # Create dummy color classes if colorama not available
    class Fore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ''
        RESET = ''
    class Style:
        BRIGHT = DIM = NORMAL = ''
        RESET_ALL = ''

# =====================================================
# CONFIGURATION
# =====================================================

class Config:
    """Configuration settings"""
    DATA_DIR = "osint_data"
    LOG_FILE = "activity_log.json"
    DEVICE_FILE = "my_devices.json"
    MAX_HISTORY = 100
    
    # API endpoints (free/public for educational use)
    IP_API = "http://ip-api.com/json/"
    IPINFO_API = "https://ipinfo.io/json"
    
    # Colors
    if COLORS_AVAILABLE:
        HEADER = Fore.CYAN + Style.BRIGHT
        SUCCESS = Fore.GREEN + Style.BRIGHT
        WARNING = Fore.YELLOW + Style.BRIGHT
        ERROR = Fore.RED + Style.BRIGHT
        INFO = Fore.BLUE + Style.BRIGHT
        RESET = Style.RESET_ALL
    else:
        HEADER = SUCCESS = WARNING = ERROR = INFO = RESET = ''

# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Display tool banner"""
    banner = f"""
{Config.HEADER}╔══════════════════════════════════════════════════════════╗
║                                                              ║
║     ███████╗██████╗ ██╗   ██╗ ██████╗ █████╗ ████████╗     ║
║     ██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗╚══██╔══╝     ║
║     █████╗  ██║  ██║██║   ██║██║     ███████║   ██║        ║
║     ██╔══╝  ██║  ██║██║   ██║██║     ██╔══██║   ██║        ║
║     ███████╗██████╔╝╚██████╔╝╚██████╗██║  ██║   ██║        ║
║     ╚══════╝╚═════╝  ╚═════╝  ╚═════╝╚═╝  ╚═╝   ╚═╝        ║
║                                                              ║
║              EDUCATIONAL OSINT TOOLKIT v1.0                 ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  DISCLAIMER: This tool is for EDUCATIONAL PURPOSES only.    ║
║  Use only on YOUR OWN devices or with explicit permission.  ║
║  Unauthorized tracking is ILLEGAL and UNETHICAL.            ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def setup_directory():
    """Create data directory if it doesn't exist"""
    if not os.path.exists(Config.DATA_DIR):
        os.makedirs(Config.DATA_DIR)
        print(f"{Config.INFO}[i] Created data directory: {Config.DATA_DIR}{Config.RESET}")

def save_to_file(data, filename, subdir=None):
    """Save data to JSON file"""
    try:
        if subdir:
            path = os.path.join(Config.DATA_DIR, subdir)
            if not os.path.exists(path):
                os.makedirs(path)
            filepath = os.path.join(path, filename)
        else:
            filepath = os.path.join(Config.DATA_DIR, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"{Config.SUCCESS}[✓] Data saved to: {filepath}{Config.RESET}")
        return filepath
    except Exception as e:
        print(f"{Config.ERROR}[!] Error saving file: {e}{Config.RESET}")
        return None

def load_from_file(filename, subdir=None):
    """Load data from JSON file"""
    try:
        if subdir:
            filepath = os.path.join(Config.DATA_DIR, subdir, filename)
        else:
            filepath = os.path.join(Config.DATA_DIR, filename)
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"{Config.ERROR}[!] Error loading file: {e}{Config.RESET}")
        return None

def log_activity(activity_type, data):
    """Log user activity for educational tracking"""
    log_file = os.path.join(Config.DATA_DIR, Config.LOG_FILE)
    
    try:
        # Load existing log
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # Add new entry
        logs.append({
            'timestamp': datetime.datetime.now().isoformat(),
            'type': activity_type,
            'data': data
        })
        
        # Keep only last MAX_HISTORY entries
        if len(logs) > Config.MAX_HISTORY:
            logs = logs[-Config.MAX_HISTORY:]
        
        # Save
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2, default=str)
    except Exception as e:
        pass  # Silent fail for logging

# =====================================================
# IP GEOLOCATION MODULE
# =====================================================

class IPGeolocation:
    """IP address geolocation module"""
    
    @staticmethod
    def get_public_ip():
        """Get your public IP address"""
        try:
            response = requests.get('https://api.ipify.org?format=json', timeout=5)
            return response.json()['ip']
        except:
            try:
                response = requests.get('https://httpbin.org/ip', timeout=5)
                return response.json()['origin']
            except:
                return None
    
    @staticmethod
    def track_ip(ip_address=None):
        """
        Track geolocation of an IP address
        Uses free public APIs for educational purposes
        """
        try:
            if ip_address:
                url = f"{Config.IP_API}{ip_address}"
            else:
                url = Config.IP_API  # Your own IP
            
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get('status') == 'success':
                return {
                    'ip': data.get('query', 'Unknown'),
                    'country': data.get('country', 'Unknown'),
                    'country_code': data.get('countryCode', 'Unknown'),
                    'region': data.get('regionName', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'zip': data.get('zip', 'Unknown'),
                    'latitude': data.get('lat', 0),
                    'longitude': data.get('lon', 0),
                    'timezone': data.get('timezone', 'Unknown'),
                    'isp': data.get('isp', 'Unknown'),
                    'organization': data.get('org', 'Unknown'),
                    'as_number': data.get('as', 'Unknown'),
                    'source': 'ip-api.com',
                    'timestamp': datetime.datetime.now().isoformat()
                }
            else:
                # Fallback to ipinfo.io
                if ip_address:
                    url = f"https://ipinfo.io/{ip_address}/json"
                else:
                    url = "https://ipinfo.io/json"
                
                response = requests.get(url, timeout=10)
                data = response.json()
                
                # Parse coordinates
                loc = data.get('loc', '0,0').split(',')
                
                return {
                    'ip': data.get('ip', 'Unknown'),
                    'country': data.get('country', 'Unknown'),
                    'region': data.get('region', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'latitude': float(loc[0]) if len(loc) > 0 else 0,
                    'longitude': float(loc[1]) if len(loc) > 1 else 0,
                    'timezone': data.get('timezone', 'Unknown'),
                    'organization': data.get('org', 'Unknown'),
                    'postal': data.get('postal', 'Unknown'),
                    'source': 'ipinfo.io',
                    'timestamp': datetime.datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"{Config.ERROR}[!] Error tracking IP: {e}{Config.RESET}")
            return None
    
    @staticmethod
    def display_info(data):
        """Display IP geolocation information"""
        if not data:
            print(f"{Config.ERROR}[!] No data to display{Config.RESET}")
            return
        
        print(f"\n{Config.HEADER}╔══════════════════════════════════════════════════════════╗")
        print(f"║              IP GEOLOCATION RESULTS                     ║")
        print(f"╚══════════════════════════════════════════════════════════╝{Config.RESET}")
        
        print(f"\n{Config.INFO}📍 IP Address:{Config.RESET}     {data.get('ip', 'Unknown')}")
        print(f"{Config.INFO}🌍 Location:{Config.RESET}       {data.get('city', 'Unknown')}, {data.get('region', 'Unknown')}, {data.get('country', 'Unknown')}")
        print(f"{Config.INFO}📮 Postal Code:{Config.RESET}    {data.get('zip', data.get('postal', 'Unknown'))}")
        print(f"{Config.INFO}🗺️ Coordinates:{Config.RESET}    {data.get('latitude', 0):.4f}, {data.get('longitude', 0):.4f}")
        print(f"{Config.INFO}⏰ Timezone:{Config.RESET}       {data.get('timezone', 'Unknown')}")
        print(f"{Config.INFO}🏢 ISP:{Config.RESET}            {data.get('isp', data.get('organization', 'Unknown'))}")
        print(f"{Config.INFO}📡 Source:{Config.RESET}         {data.get('source', 'Unknown')}")
        print(f"{Config.INFO}🕒 Timestamp:{Config.RESET}      {data.get('timestamp', 'Unknown')}")
        
        print(f"\n{Config.WARNING}⚠️  Note: IP geolocation typically shows city-level accuracy{Config.RESET}")
        print(f"{Config.WARNING}   This is NOT device tracking - just ISP location data{Config.RESET}")
    
    @staticmethod
    def save_to_history(data):
        """Save IP lookup to history"""
        history_file = f"ip_history_{datetime.datetime.now().strftime('%Y%m')}.json"
        
        # Load existing history
        history = load_from_file(history_file) or []
        
        # Add new entry
        history.append(data)
        
        # Keep last 50 entries
        if len(history) > 50:
            history = history[-50:]
        
        # Save
        save_to_file(history, history_file)
        log_activity('ip_track', {'ip': data.get('ip')})

# =====================================================
# PHONE NUMBER MODULE
# =====================================================

class PhoneLookup:
    """Phone number information module"""
    
    @staticmethod
    def validate_number(number):
        """Validate and format phone number"""
        try:
            # Remove spaces and special characters
            number = ''.join(filter(lambda x: x.isdigit() or x == '+', number))
            
            # Parse
            parsed = phonenumbers.parse(number, None)
            
            # Check validity
            is_valid = phonenumbers.is_valid_number(parsed)
            is_possible = phonenumbers.is_possible_number(parsed)
            
            return {
                'parsed': parsed,
                'valid': is_valid,
                'possible': is_possible,
                'national': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
                'international': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                'e164': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            }
        except Exception as e:
            print(f"{Config.ERROR}[!] Invalid phone number format: {e}{Config.RESET}")
            return None
    
    @staticmethod
    def lookup(number):
        """
        Get publicly available information about a phone number
        Uses Google's libphonenumber database
        """
        try:
            # Validate first
            validation = PhoneLookup.validate_number(number)
            if not validation or not validation['valid']:
                print(f"{Config.WARNING}[!] Number may be invalid or not exist{Config.RESET}")
            
            parsed = validation['parsed'] if validation else phonenumbers.parse(number, None)
            
            # Get location description
            location = geocoder.description_for_number(parsed, "en")
            
            # Get carrier information
            carrier_name = carrier.name_for_number(parsed, "en")
            
            # Get timezone
            timezones = timezone.time_zones_for_number(parsed)
            
            # Get number type
            number_type = phonenumbers.number_type(parsed)
            type_names = {
                0: "FIXED_LINE",
                1: "MOBILE",
                2: "FIXED_LINE_OR_MOBILE",
                3: "TOLL_FREE",
                4: "PREMIUM_RATE",
                5: "SHARED_COST",
                6: "VOIP",
                7: "PERSONAL_NUMBER",
                8: "PAGER",
                9: "UAN",
                10: "VOICEMAIL"
            }
            
            # Get country info
            country_code = parsed.country_code
            national_number = parsed.national_number
            
            # Try to get additional info from online databases (optional)
            online_info = PhoneLookup.online_lookup(validation['e164'] if validation else number)
            
            return {
                'input': number,
                'e164': validation['e164'] if validation else number,
                'national': validation['national'] if validation else number,
                'international': validation['international'] if validation else number,
                'valid': validation['valid'] if validation else False,
                'possible': validation['possible'] if validation else False,
                'country_code': country_code,
                'national_number': national_number,
                'location': location if location else "Unknown",
                'carrier': carrier_name if carrier_name else "Unknown",
                'number_type': type_names.get(number_type, "Unknown"),
                'timezones': ', '.join(timezones) if timezones else "Unknown",
                'online_info': online_info,
                'timestamp': datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"{Config.ERROR}[!] Error looking up number: {e}{Config.RESET}")
            return None
    
    @staticmethod
    def online_lookup(e164_number):
        """Try to get additional info from public online sources"""
        # This is a placeholder - actual implementation would use
        # public APIs with proper rate limiting and attribution
        return {
            'source': 'local_database_only',
            'note': 'Online lookup disabled for privacy'
        }
    
    @staticmethod
    def display_info(data):
        """Display phone number information"""
        if not data:
            print(f"{Config.ERROR}[!] No data to display{Config.RESET}")
            return
        
        print(f"\n{Config.HEADER}╔══════════════════════════════════════════════════════════╗")
        print(f"║           PHONE NUMBER INFORMATION                       ║")
        print(f"╚══════════════════════════════════════════════════════════╝{Config.RESET}")
        
        # Format indicators
        valid_status = f"{Config.SUCCESS}✓ Valid{Config.RESET}" if data.get('valid') else f"{Config.ERROR}✗ Invalid{Config.RESET}"
        possible_status = f"{Config.SUCCESS}✓ Possible{Config.RESET}" if data.get('possible') else f"{Config.WARNING}⚠ May not exist{Config.RESET}"
        
        print(f"\n{Config.INFO}📱 Number:{Config.RESET}         {data.get('input', 'Unknown')}")
        print(f"{Config.INFO}   E.164 format:{Config.RESET}   {data.get('e164', 'Unknown')}")
        print(f"{Config.INFO}   International:{Config.RESET}  {data.get('international', 'Unknown')}")
        print(f"{Config.INFO}   National:{Config.RESET}       {data.get('national', 'Unknown')}")
        print(f"{Config.INFO}🔍 Validity:{Config.RESET}       {valid_status} | {possible_status}")
        print(f"{Config.INFO}🌍 Country Code:{Config.RESET}   +{data.get('country_code', 'Unknown')}")
        print(f"{Config.INFO}📍 Location:{Config.RESET}        {data.get('location', 'Unknown')}")
        print(f"{Config.INFO}📡 Carrier:{Config.RESET}         {data.get('carrier', 'Unknown')}")
        print(f"{Config.INFO}📊 Number Type:{Config.RESET}     {data.get('number_type', 'Unknown')}")
        print(f"{Config.INFO}⏰ Timezones:{Config.RESET}       {data.get('timezones', 'Unknown')}")
        
        print(f"\n{Config.WARNING}⚠️  Note: This shows carrier/region from public databases{Config.RESET}")
        print(f"{Config.WARNING}   This is NOT live location tracking{Config.RESET}")
    
    @staticmethod
    def save_to_history(data):
        """Save phone lookup to history"""
        history_file = f"phone_history_{datetime.datetime.now().strftime('%Y%m')}.json"
        
        # Load existing history
        history = load_from_file(history_file) or []
        
        # Add new entry
        history.append(data)
        
        # Keep last 50 entries
        if len(history) > 50:
            history = history[-50:]
        
        # Save
        save_to_file(history, history_file)
        log_activity('phone_lookup', {'number': data.get('e164')})

# =====================================================
# DEVICE TRACKER MODULE (For YOUR OWN Devices Only)
# =====================================================

class DeviceTracker:
    """
    Track YOUR OWN devices - requires prior setup
    This demonstrates how legitimate device tracking works
    """
    
    @staticmethod
    def register_device():
        """Register a device you own for tracking"""
        print(f"\n{Config.HEADER}╔══════════════════════════════════════════════════════════╗")
        print(f"║           REGISTER YOUR OWN DEVICE                        ║")
        print(f"╚══════════════════════════════════════════════════════════╝{Config.RESET}")
        
        print(f"\n{Config.WARNING}⚠️  IMPORTANT: Only register devices YOU OWN{Config.RESET}")
        print(f"{Config.WARNING}   This is for educational purposes only{Config.RESET}\n")
        
        device = {
            'device_id': hashlib.md5(str(time.time()).encode()).hexdigest()[:8],
            'name': input("Device nickname: "),
            'type': input("Device type (phone/tablet/laptop): "),
            'brand': input("Brand: "),
            'model': input("Model: "),
            'imei': input("IMEI (from *#06# or box): "),
            'serial': input("Serial number (if known): "),
            'purchase_date': input("Purchase date (YYYY-MM-DD): "),
            'registered': datetime.datetime.now().isoformat(),
            'locations': []  # Will store location history when you check in
        }
        
        # Validate IMEI format (simple check)
        imei_clean = ''.join(filter(str.isdigit, device['imei']))
        if len(imei_clean) == 15 or len(imei_clean) == 14:
            device['imei'] = imei_clean
            print(f"{Config.SUCCESS}[✓] IMEI format valid{Config.RESET}")
        else:
            print(f"{Config.WARNING}[!] IMEI format unusual - should be 14-15 digits{Config.RESET}")
        
        # Load existing devices
        devices = load_from_file(Config.DEVICE_FILE) or []
        devices.append(device)
        
        # Save
        save_to_file(devices, Config.DEVICE_FILE)
        print(f"{Config.SUCCESS}[✓] Device registered successfully!{Config.RESET}")
        print(f"{Config.INFO}[i] Device ID: {device['device_id']}{Config.RESET}")
        
        return device
    
    @staticmethod
    def check_in_device():
        """Check in your device's current location (simulated)"""
        devices = load_from_file(Config.DEVICE_FILE) or []
        
        if not devices:
            print(f"{Config.WARNING}[!] No registered devices. Register one first.{Config.RESET}")
            return
        
        print(f"\n{Config.HEADER}╔══════════════════════════════════════════════════════════╗")
        print(f"║           CHECK IN DEVICE LOCATION                        ║")
        print(f"╚══════════════════════════════════════════════════════════╝{Config.RESET}")
        
        # List devices
        print(f"\n{Config.INFO}Registered devices:{Config.RESET}")
        for i, dev in enumerate(devices):
            print(f"{i+1}. {dev.get('name')} ({dev.get('brand')} {dev.get('model')})")
        
        try:
            choice = int(input("\nSelect device number: ")) - 1
            if choice < 0 or choice >= len(devices):
                print(f"{Config.ERROR}[!] Invalid selection{Config.RESET}")
                return
            
            device = devices[choice]
            
            # Get current IP-based location
            print(f"\n{Config.INFO}[i] Getting current location...{Config.RESET}")
            ip_tracker = IPGeolocation()
            location = ip_tracker.track_ip()
            
            if location:
                # Add check-in record
                checkin = {
                    'timestamp': datetime.datetime.now().isoformat(),
                    'ip': location.get('ip'),
                    'city': location.get('city'),
                    'region': location.get('region'),
                    'country': location.get('country'),
                    'latitude': location.get('latitude'),
                    'longitude': location.get('longitude'),
                    'method': 'ip_geolocation'
                }
                
                # Add to device history
                if 'locations' not in device:
                    device['locations'] = []
                
                device['locations'].append(checkin)
                
                # Save updated devices
                save_to_file(devices, Config.DEVICE_FILE)
                
                print(f"{Config.SUCCESS}[✓] Location recorded!{Config.RESET}")
                print(f"{Config.INFO}📍 Location: {location.get('city')}, {location.get('country')}{Config.RESET}")
                print(f"{Config.INFO}🕒 Time: {checkin['timestamp']}{Config.RESET}")
                
                log_activity('device_checkin', {'device': device.get('name'), 'location': location.get('city')})
            else:
                print(f"{Config.ERROR}[!] Could not get location{Config.RESET}")
                
        except ValueError:
            print(f"{Config.ERROR}[!] Invalid input{Config.RESET}")
        except Exception as e:
            print(f"{Config.ERROR}[!] Error: {e}{Config.RESET}")
    
    @staticmethod
    def view_device_history():
        """View location history for a device"""
        devices = load_from_file(Config.DEVICE_FILE) or []
        
        if not devices:
            print(f"{Config.WARNING}[!] No registered devices.{Config.RESET}")
            return
        
        print(f"\n{Config.HEADER}╔══════════════════════════════════════════════════════════╗")
        print(f"║           DEVICE LOCATION HISTORY                         ║")
        print(f"╚══════════════════════════════════════════════════════════╝{Config.RESET}")
        
        # List devices
        print(f"\n{Config.INFO}Registered devices:{Config.RESET}")
        for i, dev in enumerate(devices):
            loc_count = len(dev.get('locations', []))
            print(f"{i+1}. {dev.get('name')} ({loc_count} locations recorded)")
        
        try:
            choice = int(input("\nSelect device number: ")) - 1
            if choice < 0 or choice >= len(devices):
                print(f"{Config.ERROR}[!] Invalid selection{Config.RESET}")
                return
            
            device = devices[choice]
            
            print(f"\n{Config.INFO}Device: {device.get('name')}{Config.RESET}")
            print(f"{Config.INFO}Model: {device.get('brand')} {device.get('model')}{Config.RESET}")
            print(f"{Config.INFO}IMEI: {device.get('imei', 'Not recorded')}{Config.RESET}")
            
            locations = device.get('locations', [])
            
            if not locations:
                print(f"\n{Config.WARNING}No location history for this device{Config.RESET}")
                print(f"{Config.INFO}Use 'Check In Device' to record locations{Config.RESET}")
                return
            
            print(f"\n{Config.HEADER}Location History:{Config.RESET}")
            print("-" * 60)
            
            for i, loc in enumerate(reversed(locations[-10:])):  # Show last 10
                print(f"{len(locations)-i}. {loc.get('timestamp')}")
                print(f"   📍 {loc.get('city')}, {loc.get('region')}, {loc.get('country')}")
                print(f"   🗺️ {loc.get('latitude')}, {loc.get('longitude')}")
                print(f"   🌐 IP: {loc.get('ip')}")
                print()
            
            # Save detailed history
            history_file = f"device_{device.get('device_id')}_history.json"
            save_to_file(locations, history_file, 'device_history')
            
        except Exception as e:
            print(f"{Config.ERROR}[!] Error: {e}{Config.RESET}")
    
    @staticmethod
    def list_devices():
        """List all registered devices"""
        devices = load_from_file(Config.DEVICE_FILE) or []
        
        if not devices:
            print(f"{Config.WARNING}[!] No registered devices.{Config.RESET}")
            return
        
        print(f"\n{Config.HEADER}╔══════════════════════════════════════════════════════════╗")
        print(f"║           YOUR REGISTERED DEVICES                         ║")
        print(f"╚══════════════════════════════════════════════════════════╝{Config.RESET}")
        
        for i, dev in enumerate(devices):
            print(f"\n{Config.INFO}{i+1}. {dev.get('name')}{Config.RESET}")
            print(f"   Type: {dev.get('type')}")
            print(f"   Model: {dev.get('brand')} {dev.get('model')}")
            print(f"   IMEI: {dev.get('imei', 'Not recorded')}")
            print(f"   Registered: {dev.get('registered')}")
            print(f"   Locations tracked: {len(dev.get('locations', []))}")
        
        # Save list to file
        save_to_file(devices, "device_list_export.json")

# =====================================================
# HISTORY VIEWER MODULE
# =====================================================

class HistoryViewer:
    """View and manage lookup history"""
    
    @staticmethod
    def view_all():
        """View all activity history"""
        log_file = os.path.join(Config.DATA_DIR, Config.LOG_FILE)
        
        if not os.path.exists(log_file):
            print(f"{Config.WARNING}[!] No history found{Config.RESET}")
            return
        
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
            
            print(f"\n{Config.HEADER}╔══════════════════════════════════════════════════════════╗")
            print(f"║           ACTIVITY HISTORY                                 ║")
            print(f"╚══════════════════════════════════════════════════════════╝{Config.RESET}")
            
            if not logs:
                print(f"\n{Config.WARNING}No activity recorded{Config.RESET}")
                return
            
            for i, entry in enumerate(reversed(logs[-20:])):  # Show last 20
                timestamp = entry.get('timestamp', 'Unknown')[:19]  # Truncate
                activity_type = entry.get('type', 'Unknown')
                data = entry.get('data', {})
                
                print(f"\n{Config.INFO}{len(logs)-i}. [{timestamp}] {activity_type}{Config.RESET}")
                
                if activity_type == 'ip_track':
                    print(f"   IP: {data.get('ip')}")
                elif activity_type == 'phone_lookup':
                    print(f"   Number: {data.get('number')}")
                elif activity_type == 'device_checkin':
                    print(f"   Device: {data.get('device')} at {data.get('location')}")
                
        except Exception as e:
            print(f"{Config.ERROR}[!] Error reading history: {e}{Config.RESET}")
    
    @staticmethod
    def clear_history():
        """Clear all history"""
        confirm = input(f"{Config.WARNING}Clear all history? (yes/no): {Config.RESET}")
        if confirm.lower() == 'yes':
            log_file = os.path.join(Config.DATA_DIR, Config.LOG_FILE)
            if os.path.exists(log_file):
                os.remove(log_file)
            print(f"{Config.SUCCESS}[✓] History cleared{Config.RESET}")

# =====================================================
# EDUCATIONAL NOTES MODULE
# =====================================================

class EducationalNotes:
    """Display educational information about tracking"""
    
    @staticmethod
    def show_imei_info():
        """Explain what IMEI actually does"""
        print(f"\n{Config.HEADER}╔══════════════════════════════════════════════════════════╗")
        print(f"║           EDUCATIONAL: WHAT IS IMEI?                      ║")
        print(f"╚══════════════════════════════════════════════════════════╝{Config.RESET}")
        
        info = """
📱 IMEI (International Mobile Equipment Identity)
------------------------------------------------
• A unique 15-digit number assigned to every mobile device
• Like a car's VIN (Vehicle Identification Number)
• Permanently stored in the device hardware
• Cannot be changed on most modern phones

🔍 What IMEI CAN do:
✓ Identify your specific device on cellular networks
✓ Allow carriers to blacklist stolen phones
✓ Help law enforcement with warrants
✓ Track YOUR OWN devices with prior setup

❌ What IMEI CANNOT do:
✗ Show real-time location without carrier access
✗ Be used by individuals to track phones
✗ Provide GPS coordinates directly
✗ Work across different carriers without cooperation

📡 How REAL tracking works:
1. Device connects to cell tower (transmits IMEI)
2. Carrier logs which tower it connected to
3. Multiple towers can triangulate approximate location
4. This data requires LAW ENFORCEMENT warrants to access

⚠️ MYTH vs REALITY:
• Myth: "IMEI tracker apps can find any phone"
• Reality: Only carriers and police with warrants can do this

🎓 Educational Takeaway:
• IMEI is an IDENTIFIER, not a GPS tracker
• Real tracking requires infrastructure access
• Protect your IMEI like you protect your SSN
"""
        print(info)
    
    @staticmethod
    def show_tracking_reality():
        """Explain the reality of device tracking"""
        print(f"\n{Config.HEADER}╔══════════════════════════════════════════════════════════╗")
        print(f"║           EDUCATIONAL: HOW TRACKING REALLY WORKS           ║")
        print(f"╚══════════════════════════════════════════════════════════╝{Config.RESET}")
        
        info = """
🌐 LOCATION TRACKING METHODS:
------------------------------------------------
1. GPS (Global Positioning System)
   • Accuracy: 1-20 meters
   • Requires: GPS chip + clear sky view
   • Used by: Google Maps, Waze, Find My Device

2. WiFi Positioning
   • Accuracy: 20-100 meters
   • Requires: WiFi scanning + database of AP locations
   • Used by: Indoor maps, urban areas

3. Cell Tower Triangulation
   • Accuracy: 50 meters - 2 kilometers
   • Requires: Carrier network access
   • Used by: Emergency services, law enforcement

4. IP Geolocation
   • Accuracy: City-level (1-50 km)
   • Requires: Internet connection
   • Used by: Websites, services (low accuracy)

🔐 WHO CAN TRACK YOUR DEVICE:
------------------------------------------------
✓ You (with Find My Device/iPhone)
✓ Your carrier (for network operations)
✓ Law enforcement (with warrant)
✗ Random apps claiming IMEI tracking
✗ Individuals without legal authority

📋 LEGITIMATE TRACKING PROCESS:
------------------------------------------------
1. Device owner reports stolen
2. Provides IMEI to carrier
3. Carrier blacklists IMEI
4. Police file warrant for tracking
5. Carrier provides last known location

🎯 EDUCATIONAL PURPOSE:
------------------------------------------------
This tool demonstrates:
• How IP geolocation works (low accuracy)
• How phone number lookup works (public data)
• The importance of tracking your OWN devices
• The limitations of publicly available data
"""
        print(info)

# =====================================================
# MAIN APPLICATION
# =====================================================

class OSINTToolkit:
    """Main application class"""
    
    def __init__(self):
        self.ip_tracker = IPGeolocation()
        self.phone_lookup = PhoneLookup()
        self.device_tracker = DeviceTracker()
        self.history_viewer = HistoryViewer()
        self.education = EducationalNotes()
        
        # Setup
        setup_directory()
    
    def main_menu(self):
        """Display main menu"""
        while True:
            clear_screen()
            print_banner()
            
            print(f"\n{Config.HEADER}MAIN MENU:{Config.RESET}")
            print(f"{Config.INFO}╔══════════════════════════════════════════════════════════╗")
            print(f"║  {Fore.YELLOW}1.{Config.RESET}  IP Geolocation Tracker      {Fore.YELLOW}6.{Config.RESET}  Educational Notes    ║")
            print(f"║  {Fore.YELLOW}2.{Config.RESET}  Phone Number Lookup         {Fore.YELLOW}7.{Config.RESET}  View History         ║")
            print(f"║  {Fore.YELLOW}3.{Config.RESET}  Register YOUR Device        {Fore.YELLOW}8.{Config.RESET}  Export All Data      ║")
            print(f"║  {Fore.YELLOW}4.{Config.RESET}  Check In Device             {Fore.YELLOW}9.{Config.RESET}  Clear Data           ║")
            print(f"║  {Fore.YELLOW}5.{Config.RESET}  View Device History         {Fore.YELLOW}0.{Config.RESET}  Exit                 ║")
            print(f"╚══════════════════════════════════════════════════════════╝{Config.RESET}")
            
            choice = input(f"\n{Config.INFO}Select option (0-9): {Config.RESET}").strip()
            
            if choice == '1':
                self.ip_menu()
            elif choice == '2':
                self.phone_menu()
            elif choice == '3':
                self.device_tracker.register_device()
                input(f"\n{Config.INFO}Press Enter to continue...{Config.RESET}")
            elif choice == '4':
                self.device_tracker.check_in_device()
                input(f"\n{Config.INFO}Press Enter to continue...{Config.RESET}")
            elif choice == '5':
                self.device_tracker.view_device_history()
                input(f"\n{Config.INFO}Press Enter to continue...{Config.RESET}")
            elif choice == '6':
                self.education_menu()
            elif choice == '7':
                self.history_viewer.view_all()
                input(f"\n{Config.INFO}Press Enter to continue...{Config.RESET}")
            elif choice == '8':
                self.export_all_data()
            elif choice == '9':
                self.clear_all_data()
            elif choice == '0':
                print(f"\n{Config.SUCCESS}Thank you for using Educational OSINT Toolkit!{Config.RESET}")
                print(f"{Config.INFO}Remember: Use this knowledge ethically and legally.{Config.RESET}")
                sys.exit(0)
            else:
                print(f"{Config.ERROR}Invalid option{Config.RESET}")
                time.sleep(1)
    
    def ip_menu(self):
        """IP geolocation submenu"""
        while True:
            clear_screen()
            print(f"\n{Config.HEADER}╔══════════════════════════════════════════════════════════╗")
            print(f"║           IP GEOLOCATION TRACKER                        ║")
            print(f"╚══════════════════════════════════════════════════════════╝{Config.RESET}")
            
            print(f"\n{Config.INFO}1. Track your own IP{Config.RESET}")
            print(f"{Config.INFO}2. Track specific IP address{Config.RESET}")
            print(f"{Config.INFO}3. View your public IP only{Config.RESET}")
            print(f"{Config.INFO}4. Back to main menu{Config.RESET}")
            
            choice = input(f"\n{Config.INFO}Select option (1-4): {Config.RESET}").strip()
            
            if choice == '1':
                print(f"\n{Config.INFO}[i] Tracking your IP...{Config.RESET}")
                location = self.ip_tracker.track_ip()
                if location:
                    self.ip_tracker.display_info(location)
                    save = input(f"\n{Config.INFO}Save this data? (y/n): {Config.RESET}").lower()
                    if save == 'y':
                        self.ip_tracker.save_to_history(location)
                input(f"\n{Config.INFO}Press Enter to continue...{Config.RESET}")
                
            elif choice == '2':
                ip = input(f"\n{Config.INFO}Enter IP address to track: {Config.RESET}").strip()
                print(f"\n{Config.INFO}[i] Tracking {ip}...{Config.RESET}")
                location = self.ip_tracker.track_ip(ip)
                if location:
                    self.ip_tracker.display_info(location)
                    save = input(f"\n{Config.INFO}Save this data? (y/n): {Config.RESET}").lower()
                    if save == 'y':
                        self.ip_tracker.save_to_history(location)
                input(f"\n{Config.INFO}Press Enter to continue...{Config.RESET}")
                
            elif choice == '3':
                public_ip = self.ip_tracker.get_public_ip()
                if public_ip:
                    print(f"\n{Config.SUCCESS}Your public IP: {public_ip}{Config.RESET}")
                else:
                    print(f"{Config.ERROR}Could not determine public IP{Config.RESET}")
                input(f"\n{Config.INFO}Press Enter to continue...{Config.RESET}")
                
            elif choice == '4':
                break
    
    def phone_menu(self):
        """Phone number lookup submenu"""
        while True:
            clear_screen()
            print(f"\n{Config.HEADER}╔══════════════════════════════════════════════════════════╗")
            print(f"║           PHONE NUMBER LOOKUP                           ║")
            print(f"╚══════════════════════════════════════════════════════════╝{Config.RESET}")
            
            print(f"\n{Config.INFO}1. Look up phone number{Config.RESET}")
            print(f"{Config.INFO}2. Validate phone number{Config.RESET}")
            print(f"{Config.INFO}3. Back to main menu{Config.RESET}")
            
            print(f"\n{Config.WARNING}📝 Format: Include country code (e.g., +639171234567){Config.RESET}")
            
            choice = input(f"\n{Config.INFO}Select option (1-3): {Config.RESET}").strip()
            
            if choice == '1':
                number = input(f"\n{Config.INFO}Enter phone number: {Config.RESET}").strip()
                print(f"\n{Config.INFO}[i] Looking up {number}...{Config.RESET}")
                info = self.phone_lookup.lookup(number)
                if info:
                    self.phone_lookup.display_info(info)
                    save = input(f"\n{Config.INFO}Save this data? (y/n): {Config.RESET}").lower()
                    if save == 'y':
                        self.phone_lookup.save_to_history(info)
                input(f"\n{Config.INFO}Press Enter to continue...{Config.RESET}")
                
            elif choice == '2':
                number = input(f"\n{Config.INFO}Enter phone number to validate: {Config.RESET}").strip()
                validation = self.phone_lookup.validate_number(number)
                if validation:
                    print(f"\n{Config.SUCCESS}Valid: {validation['valid']}{Config.RESET}")
                    print(f"{Config.SUCCESS}Possible: {validation['possible']}{Config.RESET}")
                    print(f"{Config.SUCCESS}International: {validation['international']}{Config.RESET}")
                input(f"\n{Config.INFO}Press Enter to continue...{Config.RESET}")
                
            elif choice == '3':
                break
    
    def education_menu(self):
        """Educational notes submenu"""
        while True:
            clear_screen()
            print(f"\n{Config.HEADER}╔══════════════════════════════════════════════════════════╗")
            print(f"║           EDUCATIONAL NOTES                             ║")
            print(f"╚══════════════════════════════════════════════════════════╝{Config.RESET}")
            
            print(f"\n{Config.INFO}1. What is IMEI? (Educational){Config.RESET}")
            print(f"{Config.INFO}2. How tracking really works{Config.RESET}")
            print(f"{Config.INFO}3. Legal and ethical guidelines{Config.RESET}")
            print(f"{Config.INFO}4. Back to main menu{Config.RESET}")
            
            choice = input(f"\n{Config.INFO}Select option (1-4): {Config.RESET}").strip()
            
            if choice == '1':
                self.education.show_imei_info()
                input(f"\n{Config.INFO}Press Enter to continue...{Config.RESET}")
            elif choice == '2':
                self.education.show_tracking_reality()
                input(f"\n{Config.INFO}Press Enter to continue...{Config.RESET}")
            elif choice == '3':
                self.show_legal_guidelines()
                input(f"\n{Config.INFO}Press Enter to continue...{Config.RESET}")
            elif choice == '4':
                break
    
    def show_legal_guidelines(self):
        """Display legal and ethical guidelines"""
        print(f"\n{Config.HEADER}╔══════════════════════════════════════════════════════════╗")
        print(f"║           LEGAL & ETHICAL GUIDELINES                      ║")
        print(f"╚══════════════════════════════════════════════════════════╝{Config.RESET}")
        
        guidelines = """
⚖️ LEGAL FRAMEWORK:
------------------------------------------------
• Computer Fraud and Abuse Act (US)
• Cybercrime Prevention Act (Philippines - RA 10175)
• Data Privacy Act (Philippines - RA 10173)
• General Data Protection Regulation (EU)
• Similar laws in most countries

✅ ETHICAL USE CASES:
------------------------------------------------
✓ Tracking YOUR OWN devices
✓ Penetration testing WITH written authorization
✓ Research with proper ethics board approval
✓ Assisting law enforcement WITH warrant
✓ Bug bounty programs WITH scope

❌ UNETHICAL/ILLEGAL USE CASES:
------------------------------------------------
✗ Tracking someone without consent
✗ Accessing devices you don't own
✗ Using for stalking or harassment
✗ Selling location data
✗ Attempting to bypass security measures

📋 RESPONSIBLE DISCLOSURE:
------------------------------------------------
If you find vulnerabilities:
1. Document the issue
2. Contact the owner/vendor privately
3. Allow reasonable time to fix
4. Publish only after fix is available
5. Never exploit for personal gain

🎓 EDUCATIONAL PURPOSE REMINDER:
------------------------------------------------
This tool demonstrates CONCEPTS only:
• How APIs work
• How public data lookup works
• The importance of device registration
• The limitations of publicly available data

⚠️ REMEMBER: Knowledge is power, but with power comes responsibility.
"""
        print(guidelines)
    
    def export_all_data(self):
        """Export all collected data"""
        print(f"\n{Config.HEADER}╔══════════════════════════════════════════════════════════╗")
        print(f"║           EXPORT ALL DATA                                 ║")
        print(f"╚══════════════════════════════════════════════════════════╝{Config.RESET}")
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        export_file = f"osint_export_{timestamp}.zip"
        
        try:
            import zipfile
            with zipfile.ZipFile(export_file, 'w') as zipf:
                for root, dirs, files in os.walk(Config.DATA_DIR):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.dirname(Config.DATA_DIR))
                        zipf.write(file_path, arcname)
            
            print(f"{Config.SUCCESS}[✓] Data exported to: {export_file}{Config.RESET}")
            print(f"{Config.WARNING}⚠️  Store this file securely - it contains your data{Config.RESET}")
            
        except Exception as e:
            print(f"{Config.ERROR}[!] Export failed: {e}{Config.RESET}")
        
        input(f"\n{Config.INFO}Press Enter to continue...{Config.RESET}")
    
    def clear_all_data(self):
        """Clear all collected data"""
        confirm = input(f"{Config.WARNING}This will delete ALL saved data. Continue? (yes/no): {Config.RESET}")
        
        if confirm.lower() == 'yes':
            import shutil
            try:
                if os.path.exists(Config.DATA_DIR):
                    shutil.rmtree(Config.DATA_DIR)
                setup_directory()
                print(f"{Config.SUCCESS}[✓] All data cleared{Config.RESET}")
            except Exception as e:
                print(f"{Config.ERROR}[!] Error clearing data: {e}{Config.RESET}")
        else:
            print(f"{Config.INFO}[i] Operation cancelled{Config.RESET}")
        
        input(f"\n{Config.INFO}Press Enter to continue...{Config.RESET}")


# =====================================================
# INSTALLATION CHECK AND MAIN EXECUTION
# =====================================================

def check_requirements():
    """Check if all requirements are installed"""
    requirements = ['requests', 'phonenumbers', 'colorama']
    missing = []
    
    for req in requirements:
        try:
            __import__(req)
        except ImportError:
            missing.append(req)
    
    if missing:
        print(f"\n{Config.WARNING}[!] Missing requirements: {', '.join(missing)}{Config.RESET}")
        install = input(f"{Config.INFO}Install now? (y/n): {Config.RESET}").lower()
        
        if install == 'y':
            for req in missing:
                print(f"{Config.INFO}[i] Installing {req}...{Config.RESET}")
                os.system(f"pip install {req}")
            
            print(f"{Config.SUCCESS}[✓] Requirements installed. Please restart the tool.{Config.RESET}")
            sys.exit(0)
        else:
            print(f"{Config.ERROR}[!] Cannot continue without requirements{Config.RESET}")
            sys.exit(1)

def main():
    """Main entry point"""
    # Clear screen
    clear_screen()
    
    # Check Python version
    if sys.version_info < (3, 6):
        print(f"{Config.ERROR}[!] Python 3.6 or higher required{Config.RESET}")
        sys.exit(1)
    
    # Check and install requirements
    check_requirements()
    
    # Run main application
    try:
        app = OSINTToolkit()
        app.main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Config.WARNING}[!] Interrupted by user{Config.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Config.ERROR}[!] Unexpected error: {e}{Config.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()