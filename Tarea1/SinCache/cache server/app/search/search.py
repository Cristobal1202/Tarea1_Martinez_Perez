import json
import time
import numpy as np
from find_car_by_id import find_car_by_id

class CacheClient:
    def __init__(self):
        pass

    def get(self, key, simulated=False):
        start_time = time.time()  # Inicio del temporizador

        # Simulamos un retraso aleatorio de 1 a 3 segundos, con una distribución normal en 2
        delay = np.random.normal(2, 0.5)

        if not simulated:
            time.sleep(delay)

        # Buscar en el JSON
        value = find_car_by_id(int(key))
        value = str(value)
        if value:
            print("Key found in JSON.")
                
            elapsed_time = time.time() - start_time  # Calcula el tiempo transcurrido
            if simulated:
                # Agrega el retraso al tiempo
                elapsed_time += delay
            print(f"Time taken (JSON + delay): {elapsed_time:.5f} seconds")
                
            return value
        else:
            elapsed_time = time.time() - start_time  # Calcula el tiempo transcurrido
            print(f"Time taken: {elapsed_time:.5f} seconds")
            print("Key not found.")
            return None
            
    def simulate_searches(self, n_searches=100):
        keys_to_search = [f"{i}" for i in np.random.randint(1, 101, n_searches)]
        
        start_simulations_time = time.time()  # Inicio del temporizador de simulaciones

        for count, key in enumerate(keys_to_search, start=1):
            print("\033[H\033[J")
            print(f"Searching : {count}/{n_searches}")
            self.get(key)

        end_simulations_time = time.time()  # Fin del temporizador de simulaciones
        total_simulations_time = end_simulations_time - start_simulations_time
        print(f"Total time taken for simulations: {total_simulations_time:.5f} seconds")

if __name__ == '__main__':
    client = CacheClient()

    while True:
        print("\nChoose an operation:")
        print("1. Get")
        print("2. Simulate Searches")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            key = input("Enter key: ")
            value = client.get(key)
            if value is not None:
                print(f"Value: {value}")
        elif choice == "2":
            n_searches = int(input("Enter the number of searches you want to simulate: "))
            client.simulate_searches(n_searches)
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")
