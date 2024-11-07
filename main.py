import subprocess
import re
import platform
import math
import numpy as np
import matplotlib.pyplot as plt


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
        
#tache 2
# Position des points d'accès (à définir selon votre scénario)
AP1 = np.array([2, 2])
AP2 = np.array([8, 2])
AP3 = np.array([5, 6])

# RSSI mesurés (exemple, à remplacer par vos valeurs réelles)
rssi1 = -60  # RSSI à partir du point d'accès 1
rssi2 = -65  # RSSI à partir du point d'accès 2
rssi3 = -60  # RSSI à partir du point d'accès 3

d1 = calculate_distance_mobile_AP(rssi1)
d2 = calculate_distance_mobile_AP(rssi2)
d3 = calculate_distance_mobile_AP(rssi3)

# Affichage graphique des cercles de distance
fig, ax = plt.subplots()

# Tracer les cercles
circle1 = plt.Circle(AP1, d1, color='r', fill=False, linestyle='dotted', label="AP1")
circle2 = plt.Circle(AP2, d2, color='g', fill=False, linestyle='dotted', label="AP2")
circle3 = plt.Circle(AP3, d3, color='b', fill=False, linestyle='dotted', label="AP3")

ax.add_artist(circle1)
ax.add_artist(circle2)
ax.add_artist(circle3)

# Tracer les points d'accès
ax.plot(AP1[0], AP1[1], 'ro', label="Point d'accès 1")
ax.plot(AP2[0], AP2[1], 'go', label="Point d'accès 2")
ax.plot(AP3[0], AP3[1], 'bo', label="Point d'accès 3")

# Paramétrage du graphique
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_aspect('equal', 'box')
ax.legend()

# Affichage du graphique
plt.title("Position estimée du mobile")
plt.xlabel("X")
plt.ylabel("Y")
plt.show()





wifi_rssi = get_wifi_rssi()
if wifi_rssi is not None:
    distance = calculate_distance_mobile_AP(wifi_rssi)
    print(f"Distance estimée: {distance:.2f} m")
else:
    print("Erreur calculant rssi.")
    
    
