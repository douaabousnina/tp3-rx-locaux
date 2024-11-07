import subprocess
import re
import platform
import numpy as np
import matplotlib.pyplot as plt

def calculate_distance_mobile_AP(rssi, measured_power=-50, environmental_factor=2):
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
            output = output.decode(errors='ignore')  # Ignore decoding errors

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





# Positions fixes des points d'accès
predefined_positions = [
    np.array([2, 2]),
    np.array([8, 2]),
    np.array([7, 7])
]

'''
def trilaterate(positions, distances):
    # Trilateration calculation
    A = 2 * (positions['AP2'][0] - positions['AP1'][0])
    B = 2 * (positions['AP2'][1] - positions['AP1'][1])
    D = distances['AP1'] ** 2 - distances['AP2'] ** 2 - positions['AP1'][0] ** 2 + positions['AP2'][0] ** 2 - \
        positions['AP1'][1] ** 2 + positions['AP2'][1] ** 2
    E = 2 * (positions['AP3'][0] - positions['AP1'][0])
    F = 2 * (positions['AP3'][1] - positions['AP1'][1])
    G = distances['AP1'] ** 2 - distances['AP3'] ** 2 - positions['AP1'][0] ** 2 + positions['AP3'][0] ** 2 - \
        positions['AP1'][1] ** 2 + positions['AP3'][1] ** 2

    x = (D * F - B * G) / (A * F - B * E)
    y = (D - A * x) / B

    return np.array([x, y])
'''

def trilaterate(positions, distances):
    # Ensure we have exactly three access points to trilaterate
    if len(positions) != 3 or len(distances) != 3:
        raise ValueError("Exactly three access points are required for trilateration.")
    
    # Extract SSIDs (keys) dynamically
    ssid1, ssid2, ssid3 = list(positions.keys())
    
    # Coordinates of each access point
    x1, y1 = positions[ssid1]
    x2, y2 = positions[ssid2]
    x3, y3 = positions[ssid3]
    
    # Distances to each access point
    d1 = distances[ssid1]
    d2 = distances[ssid2]
    d3 = distances[ssid3]
    
    # Calculate coefficients for trilateration
    A = 2 * (x2 - x1)
    B = 2 * (y2 - y1)
    D = d1**2 - d2**2 - x1**2 + x2**2 - y1**2 + y2**2
    E = 2 * (x3 - x1)
    F = 2 * (y3 - y1)
    G = d1**2 - d3**2 - x1**2 + x3**2 - y1**2 + y3**2

    # Avoid division by zero in calculations
    denominator = A * F - B * E
    if denominator == 0:
        raise ValueError("Points are collinear or otherwise cannot be used for trilateration.")

    # Calculate x and y
    x = (D * F - B * G) / denominator
    y = (D - A * x) / B

    return np.array([x, y])

# Récupérer les points d'accès et calculer les distances
aps = get_available_aps()
print("Points d'accès disponibles:", aps)
positions = {}
distances = {}

for i, (ssid, signal) in enumerate(aps):
    rssi = convert_percent_to_dbm(int(signal))
    distance = calculate_distance_mobile_AP(rssi)
    distances[ssid] = distance
    
    # Assign a position from predefined positions if ssid is new
    if ssid not in positions:
        if i < len(predefined_positions):
            positions[ssid] = predefined_positions[i]
        else:
            # Add a fallback position if we run out of predefined positions
            positions[ssid] = np.array([0, 0])  # You could make this more dynamic if needed


# Estimer la position si nous avons au moins trois distances
if len(distances) >= 3:
    estimated_position = trilaterate(positions, distances)
else:
    estimated_position = None
    print("Pas assez de points d'accès pour estimer la position.")

# Affichage graphique des cercles de distance et de la position estimée
fig, ax = plt.subplots()

if distances:
    for ssid, distance in distances.items():
        circle = plt.Circle(positions[ssid], distance, fill=False, linestyle='dotted', label=f"{ssid} (distance: {distance:.2f}m)")
        ax.add_artist(circle)
        ax.plot(positions[ssid][0], positions[ssid][1], 'o', label=f"Point d'accès {ssid}")

if estimated_position is not None:
    ax.plot(estimated_position[0], estimated_position[1], 'x', color='red', markersize=10, label='Position Estimée')

# Configurer le graphique
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_aspect('equal', 'box')
ax.legend()

# Afficher le graphique
plt.title("Position Estimée du Mobile par Rapport aux Points d'Accès")
plt.xlabel("X")
plt.ylabel("Y")
plt.show()



"""
# Positions fixes des points d'accès
positions = {
    "AP1": np.array([2, 2]),
    "AP2": np.array([8, 2]),
    "AP3": np.array([5, 6])
}

def trilaterate(positions, distances):
    A = 2 * (positions['AP2'][0] - positions['AP1'][0])
    B = 2 * (positions['AP2'][1] - positions['AP1'][1])
    D = distances['AP1'] ** 2 - distances['AP2'] ** 2 - positions['AP1'][0] ** 2 + positions['AP2'][0] ** 2 - \
        positions['AP1'][1] ** 2 + positions['AP2'][1] ** 2
    E = 2 * (positions['AP3'][0] - positions['AP1'][0])
    F = 2 * (positions['AP3'][1] - positions['AP1'][1])
    G = distances['AP1'] ** 2 - distances['AP3'] ** 2 - positions['AP1'][0] ** 2 + positions['AP3'][0] ** 2 - \
        positions['AP1'][1] ** 2 + positions['AP3'][1] ** 2

    x = (D * F - B * G) / (A * F - B * E)
    y = (D - A * x) / B

    return np.array([x, y])

# Récupérer les points d'accès et calculer les distances
aps = get_available_aps()
print("Access Points Disponibles:", aps)
distances = {}

for ssid, rssi in aps:
    if ssid in positions:
        distance = calculate_distance_mobile_AP(rssi)
        distances[ssid] = distance

# Estimer la position si nous avons au moins trois distances
if len(distances) >= 3:
    estimated_position = trilaterate(positions, distances)
else:
    estimated_position = None
    print("Pas assez de points d'accès pour estimer la position.")

# Affichage graphique des cercles de distance et de la position estimée
fig, ax = plt.subplots()

if distances:
    for ssid, distance in distances.items():
        circle = plt.Circle(positions[ssid], distance, fill=False, linestyle='dotted',
                            label=f"{ssid} (distance: {distance:.2f}m)")
        ax.add_artist(circle)
        ax.plot(positions[ssid][0], positions[ssid][1], 'o', label=f"Point d'accès {ssid}")

if estimated_position is not None:
    ax.plot(estimated_position[0], estimated_position[1], 'x', color='red', markersize=10, label='Position Estimée')

# Configurer le graphique
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_aspect('equal', 'box')
ax.legend()

# Afficher le graphique
plt.title("Position Estimée du Mobile par Rapport aux Points d'Accès")
plt.xlabel("X")
plt.ylabel("Y")
plt.show()
"""

        
"""
    #tache 2
    # Position des points d'accès (à définir selon votre scénario)
    AP1 = np.array([2, 2])
    AP2 = np.array([8, 2])
    AP3 = np.array([5, 6])

    # RSSI mesurés (exemple, à remplacer par vos valeurs réelles)
    rssi1 = -70  # RSSI à partir du point d'accès 1
    rssi2 = -65  # RSSI à partir du point d'accès 2
    rssi3 = -70  # RSSI à partir du point d'accès 3

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
    
"""
