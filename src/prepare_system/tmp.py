import pandas as pd
import ipaddress

# Esempio di DataFrame
data = {
    'targetIP': ['192.168.0.6', '192.168.0.2', '192.168.0.3', '192.168.0.4']
}
df = pd.DataFrame(data)

# Conversione degli IP in numeri
df['targetIP_numeric'] = df['targetIP'].apply(lambda x: int(ipaddress.ip_address(x)))

# Calcolo della mediana
mediana = df['targetIP_numeric'].median()
print(f"Mediana (numerica): {mediana}")

# Convertire di nuovo la mediana in formato IP (se necessario)
mediana_ip = str(ipaddress.ip_address(int(mediana)))
print(f"Mediana (IP): {mediana_ip}")
