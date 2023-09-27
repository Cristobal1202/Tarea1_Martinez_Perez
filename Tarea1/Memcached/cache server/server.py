import grpc
from concurrent import futures
import cache_service_pb2_grpc
from cache_service_pb2 import Key, CacheItem, NodeInfo, Response
import argparse
import memcache  # Importa la biblioteca de Memcached

class CacheServiceServicer(cache_service_pb2_grpc.CacheServiceServicer):
    def __init__(self, is_master=True, max_items=100):
        self.is_master = is_master

        # Configura la conexión a Memcached
        self.memcached_client = memcache.Client(["localhost:11211"])

        self.max_items = max_items

    def RegisterNode(self, request, context):
        if not self.is_master:
            return Response(success=False, message="Not a master node")
        
        node = f"{request.ip}:{request.port}"
        return Response(success=True, message=f"Node registered successfully")

    def DeregisterNode(self, request, context):
        if not self.is_master:
            return Response(success=False, message="Not a master node")

        node = f"{request.ip}:{request.port}"
        return Response(success=True, message="Node deregistered successfully")

    def Get(self, request, context):
        key = request.key
        value = self.memcached_client.get(key)
        
        if value:
            print(f"Retrieving key '{key}:{value}' from Memcached")
            return CacheItem(key=key, value=value)
        else:
            print(f"Key '{key}' not found in Memcached.")
            return CacheItem(key=key, value="")

    def Put(self, request, context):
        key = request.key
        value = request.value
        self.memcached_client.set(key, value)

        return Response(success=True, message="Inserted successfully")

    def Remove(self, request, context):
        key = request.key
        if self.memcached_client.delete(key):
            return Response(success=True, message="Removed successfully")
        else:
            return Response(success=False, message="Key not found")

def serve(is_master=True, port=50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cache_service_pb2_grpc.add_CacheServiceServicer_to_server(CacheServiceServicer(is_master=is_master), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    if is_master:
        print(f"Master server started on port {port}")
    else:
        print(f"Slave server started on port {port}")
    server.wait_for_termination()

def register_with_master(master_node, slave_ip, slave_port):
    print(f"Registering with master node {master_node}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Distributed Cache Server")
    parser.add_argument("node_type", choices=["master", "slave"], help="Type of the node ('master' or 'slave')")
    parser.add_argument("port", default=50051, type=int, help="Port number to start the node on")
    parser.add_argument("--master_ip", default="localhost", help="IP address of the master node (required if node_type is 'slave')")
    parser.add_argument("--master_port", type=int, default=50051, help="Port number of the master node (required if node_type is 'slave')")
    
    args = parser.parse_args()

    if args.node_type == "master":
        serve(is_master=True, port=args.port)
    elif args.node_type == "slave":
        register_with_master(f"{args.master_ip}:{args.master_port}", "localhost", args.port)
        serve(is_master=False, port=args.port)
    else:
        print("Unknown node type. Use 'master' or 'slave'.")
