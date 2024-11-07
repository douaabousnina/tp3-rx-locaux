import subprocess
import re
import platform
import math


def calculate_distance_mobile_AP(rssi, measured_power=-50, environmental_factor=3):
    distance = 10 ** ((measured_power - rssi) / (10 * environmental_factor))
    return distance

def convert_percent_to_dbm(percentage):
    # dB = 10 * math.log10(percentage/100)
    dB = (percentage / 2) - 100
    return dB

def get_wifi_rssi():
    if platform.system() == 'Windows':
        try:
            process = subprocess.Popen("netsh wlan show interfaces", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()

            if process.returncode != 0:
                print("Error retrieving WiFi signal strength:", error.decode('latin-1'))
                return None

            output = output.decode('latin-1')
            matches = re.findall('Signal.*?:.*?([0-9]*)%', output, re.DOTALL)
            if matches:
                percentage = int(matches[0])
                rssi = convert_percent_to_dbm(percentage)
                print(rssi)
                print(percentage)
                return rssi
            else:
                print("Signal strength not found in output.")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    else:
        raise Exception('Unsupported OS')
        


wifi_rssi = get_wifi_rssi()
if wifi_rssi is not None:
    distance = calculate_distance_mobile_AP(wifi_rssi)
    print(f"Estimated distance to the WiFi access point: {distance:.2f} meters")
else:
    print("Could not determine WiFi signal strength.")
