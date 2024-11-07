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
            process = subprocess.Popen("netsh wlan show networks mode=bssid", stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            output, error = process.communicate()

            if process.returncode != 0:
                print("Erreur lors de l'exécution de la commande:", error.decode('latin-1'))
                return []

            output = output.decode('latin-1')
            aps = []
            matches = re.findall(r'SSID \d+ : (.*?)\s+BSSID \d+ : .*?Signal.*?:.*?([0-9]*)%', output, re.DOTALL)
            for match in matches:
                ssid, percentage = match
                rssi = convert_percent_to_dbm(int(percentage))
                aps.append((ssid.strip(), rssi))  # Utiliser strip() pour enlever les espaces superflus

            if not aps:
                print("Aucun point d'accès détecté.")
            return aps
        except Exception as e:
            print(f"Erreur: {e}")
            return []
    else:
        raise Exception('Système d\'exploitation non pris en charge')

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
