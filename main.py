import subprocess
import re
import platform
import numpy as np
import matplotlib.pyplot as plt

def calculate_distance_mobile_AP(rssi, measured_power=-50, environmental_factor=3):
    distance = 10 ** ((measured_power - rssi) / (10 * environmental_factor))
    return distance

def convert_percent_to_dbm(percentage):
    dB = (percentage / 2) - 100
    return dB

def get_available_aps():
    if platform.system() == 'Windows':
        try:
            process = subprocess.Popen("netsh wlan show networks mode=bssid", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, _ = process.communicate()
            output = output.decode(errors='ignore')

            signals = re.findall(r'Signal\s*:\s*(\d+)%', output, re.DOTALL)
            ssids = []
            for line in output.splitlines():
                if 'SSID' in line:
                    cleaned_line = re.sub(r'[^\x20-\x7E]', '', line).strip()
                    if cleaned_line.startswith('SSID'):
                        ssid = cleaned_line.split(':')[1].strip()
                        ssids.append(ssid)

            networks = list(zip(ssids, signals))

            if not networks:
                print("Aucun point d'accès détecté.")
            return networks
        except Exception as e:
            print(f"Erreur: {e}")
            return []
    else:
        raise Exception('Système d\'exploitation non pris en charge')



predefined_positions = [
    np.array([2,0]),
    np.array([8,0]),
    np.array([2.5, 7.5])
]

def trilaterate(positions, distances):
    if len(distances) < 3:
        raise ValueError("Trois points d'acces sont requis.")
    
    distances_list = list(distances.values())

    position_keys = list(positions.keys())

    if len(distances_list) != 3 or len(position_keys) != 3:
        raise ValueError("Il faut exactement trois points d'accès avec leurs distances respectives.")

    r1, r2, r3 = distances_list

    x1, y1 = positions[position_keys[0]]
    x2, y2 = positions[position_keys[1]]
    x3, y3 = positions[position_keys[2]]

    A = np.array([
        [2 * (x1 - x2), 2 * (y1 - y2)],
        [2 * (x1 - x3), 2 * (y1 - y3)]
    ])
    
    B = np.array([
        [r1**2 - r2**2 + x2**2 - x1**2 + y2**2 - y1**2],
        [r1**2 - r3**2 + x3**2 - x1**2 + y3**2 - y1**2]
    ])
    
    print("A:", A)
    print("B: ",B)
    
    position = np.linalg.solve(A, B)

    return position
    


aps = get_available_aps()
print("Points d'accès disponibles:", aps)
positions = {}
distances = {}

for i, (ssid, signal) in enumerate(aps):
    rssi = convert_percent_to_dbm(int(signal))
    distance = calculate_distance_mobile_AP(rssi)
    distances[ssid] = distance
    
    if ssid not in positions:
        if i < len(predefined_positions):
            positions[ssid] = predefined_positions[i]
        else:
            positions[ssid] = np.array([0, 0])


if len(distances) >= 3:
    positions_list = list(positions.items())[:3]
    distances_list = list(distances.items())[:3]
    positions = dict(positions_list)
    distances = dict(distances_list)

    estimated_position = trilaterate(positions, distances)
    print("Estimated Position:", estimated_position)
else:
    estimated_position = None
    print("Pas assez de points d'accès pour estimer la position.")


fig, ax = plt.subplots()

if distances:
    for ssid, distance in distances.items():
        circle = plt.Circle(positions[ssid], distance, fill=False, linestyle='dotted', label=f"{ssid} (distance: {distance:.2f}m)")
        ax.add_artist(circle)
        ax.plot(positions[ssid][0], positions[ssid][1], 'o', label=f"Point d'accès {ssid}")

if estimated_position is not None:
    ax.plot(estimated_position[0], estimated_position[1], 'x', color='red', markersize=10, label='Position Estimée')

ax.set_xlim(-100, 100)
ax.set_ylim(-100, 100)
ax.set_aspect('equal', 'box')
ax.legend()

plt.title("Position Estimée du Mobile par Rapport aux Points d'Accès")
plt.xlabel("X")
plt.ylabel("Y")
plt.show()




