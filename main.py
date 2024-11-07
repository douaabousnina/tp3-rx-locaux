import subprocess
import re
import platform


def calculate_distance_mobile_AP(rssi, measured_power=-50, environmental_factor=3):
    distance = 10 ** ((measured_power - rssi) / (10 * environmental_factor))
    return distance

def convert_percent_to_dbm(percentage):
    # dB = 10 * math.log10(percentage/100)
    # check this link out ph : https://stackoverflow.com/questions/15797920/how-to-convert-wifi-signal-strength-from-quality-percent-to-rssi-dbm
    dB = (percentage / 2) - 100
    return dB

def get_wifi_rssi():
    if platform.system() == 'Windows':
        try:
            process = subprocess.Popen("netsh wlan show interfaces", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()

            if process.returncode != 0:
                print("Erreur cmd:", error.decode('latin-1'))
                return None

            output = output.decode('latin-1')
            matches = re.findall('Signal.*?:.*?([0-9]*)%', output, re.DOTALL)
            if matches:
                percentage = int(matches[0])
                rssi = convert_percent_to_dbm(percentage)
                return rssi
            else:
                print("Erreur calculant rssi.")
                return None
        except Exception as e:
            print(f"Erreur: {e}")
            return None
    else:
        raise Exception('Unsupported OS')
        


wifi_rssi = get_wifi_rssi()
if wifi_rssi is not None:
    distance = calculate_distance_mobile_AP(wifi_rssi)
    print(f"Distance estimée: {distance:.2f} m")
else:
    print("Erreur calculant rssi.")
    
    
