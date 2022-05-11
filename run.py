
from src.the_very_simple_lightning_interface.interface import Interface

HOSTNAME = "umbrel.lan"
USERNAME = "umbrel"
PASSWORD = "vU1237aABabcZ"

print(f"HOSTNAME = {HOSTNAME}")
print(f"USERNAME = {USERNAME}")
print(f"PASSWORD = {PASSWORD}")

i = Interface(hostname=HOSTNAME, username=USERNAME, password=PASSWORD)
print(i)
print("-" * 80)
print("-" * 80)
print(i.get_invoice("097a66004642d47f6d92dedc126e3edeb0973171383332eec88ce38ac5303622"))
print(i.get_invoice_state("097a66004642d47f6d92dedc126e3edeb0973171383332eec88ce38ac5303622"))
print("-" * 80)


