import grpc
import cache_service_pb2
import cache_service_pb2_grpc
import memcache  # Importa la biblioteca de memcached

class CacheClient:
    def __init__(self, host="localhost", port=50051, memcached_host="localhost", memcached_port=11211):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = cache_service_pb2_grpc.CacheServiceStub(self.channel)

        # Configura la conexión a Memcached
        self.memcached_client = memcache.Client([f"{memcached_host}:{memcached_port}"])

    def put(self, key, value):
        response = self.stub.Put(cache_service_pb2.CacheItem(key=key, value=value))
        print(response.message)

    def get(self, key):
        # Intenta obtener el valor de Memcached primero
        memcached_value = self.memcached_client.get(key)
        if memcached_value is not None:
            return memcached_value

        # Si no está en Memcached, obtén el valor del servicio gRPC
        response = self.stub.Get(cache_service_pb2.Key(key=key))
        if response.value:
            # Almacena el valor en Memcached para futuras consultas
            self.memcached_client.set(key, response.value)
            return response.value
        else:
            print("Key not found.")
            return None

    def remove(self, key):
        response = self.stub.Remove(cache_service_pb2.Key(key=key))
        print(response.message)

def main():
    client = CacheClient()
    
    while True:
        print("\nMenu:")
        print("1. Insertar un valor")
        print("2. Obtener un valor")
        print("3. Eliminar un valor")
        print("4. Salir")
        
        choice = input("Seleccione una opción: ")
        
        if choice == "1":
            key = input("Ingrese la clave: ")
            value = input("Ingrese el valor: ")
            client.put(key, value)
        elif choice == "2":
            key = input("Ingrese la clave a buscar: ")
            value = client.get(key)
            if value:
                print(f"Valor: {value}")
        elif choice == "3":
            key = input("Ingrese la clave a eliminar: ")
            client.remove(key)
        elif choice == "4":
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")

if __name__ == "__main__":
    main()
