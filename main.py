import requests
import json


def get_valid_node_ip(target_node_id, connected_nodes, visited_nodes):
    headers = {"Content-type": "application/json"}

    for node_id, info in connected_nodes.items():
        if node_id in visited_nodes:
            continue  # Daha önce denenen düğümleri atla

        node_ip = info[0]

        # Sadece IPv4 adreslerini seç
        if node_ip.startswith("::ffff:"):
            node_ip = node_ip.replace("::ffff:", "")
        elif ":" in node_ip:
            continue  # IPv6 adreslerini atla

        node_url = f"http://{node_ip}:33035/"
        print(f"Attempted node: {node_ip}")

        try:
            response = requests.post(
                node_url,
                headers=headers,
                data='{"jsonrpc": "2.0", "method": "get_status", "id": 123 }',
                timeout=3,
            )
            if response.status_code == 200:
                data = response.json()
                print(f"Connection successful: {node_ip}")
                visited_nodes.add(node_id)  # Bu düğüm başarıyla denendi

                if target_node_id in data["result"]["connected_nodes"]:
                    return (
                        data["result"]["connected_nodes"][target_node_id][0],
                        visited_nodes,
                    )  # Hedef node'un IP'si

                return None, visited_nodes, data["result"]["connected_nodes"]
        except requests.RequestException:
            print(f"Connection failed: {node_ip}")
            visited_nodes.add(node_id)  # Başarısız olan düğüm de işaretlenmeli
            return None, visited_nodes, connected_nodes  # connected_nodes ekledim

    return None, visited_nodes, connected_nodes


# Aranacak hedef node ID
target_node_id = "N12hthwajwGWrvLL51q9Cedgohhj6dmX1PxbUVawvhXyLHRSB8GT"

# İlk bağlantıyı dene
initial_node_ip = "5.75.230.201"
initial_url = f"http://{initial_node_ip}:33035/"
headers = {"Content-type": "application/json"}
visited_nodes = set()

try:
    print(f"Connecting to the start node: {initial_node_ip}")
    response = requests.post(
        initial_url,
        headers=headers,
        data='{"jsonrpc": "2.0", "method": "get_status", "id": 123 }',
        timeout=3,
    )
    data = response.json()
    print(f"Connection from start node successful: {initial_node_ip}")
    connected_nodes = data["result"]["connected_nodes"]
except requests.RequestException:
    print("Failed to connect to the start node.")
    connected_nodes = {}

# Hedef node IP'yi bulana kadar devam et
node_ip = None
while node_ip is None and connected_nodes:
    print("Trying a new node...")
    result = get_valid_node_ip(
        target_node_id, connected_nodes, visited_nodes
    )  # Sonucu bir değişkene ata

    if len(result) == 3:  # 3 değer döndürülmüşse atama yap
        node_ip, visited_nodes, connected_nodes = result
    elif len(result) == 2:  # 2 değer döndürülmüşse visited_nodes'ı güncelle
        node_ip, visited_nodes = result
    else:
        print("An unexpected return value")
        break  # veya uygun bir hata yönetimi yap

    if connected_nodes is None:
        print("Could not get connected node information. Exiting.")
        break
print("IP address of the destination node:", node_ip)
