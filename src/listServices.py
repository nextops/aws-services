import boto3
import os
import argparse

# Base class for GraphDB operations
class GraphDB:
    def connect(self):
        raise NotImplementedError()

    def add_service(self, service_name):
        raise NotImplementedError()

    def check_connection(self):
        raise NotImplementedError()


class Neo4jDB(GraphDB):
    from neo4j import GraphDatabase
    from neo4j.exceptions import ServiceUnavailable

    def __init__(self):
        self.NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")
        self.NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
        self.NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "somepassword")
        self.driver = self.connect()

    def connect(self):
        try:
            # Connect to Neo4j
            return self.GraphDatabase.driver(self.NEO4J_URI, auth=(self.NEO4J_USERNAME, self.NEO4J_PASSWORD))
        except self.ServiceUnavailable:
            print("Error: Unable to connect to Neo4j. Please ensure the service is running and accessible.")
            exit(1)

    def add_service(self, service_name):
        sanitized_name = sanitize_service_name(service_name)
        with self.driver.session() as session:
            try:
                session.run("MERGE (s:Service {name: $name})", name=sanitized_name)
            except Exception as e:
                print(f"Failed to insert service {sanitized_name} into Neo4j. Error: {e}")

    def check_connection(self):
        try:
            with self.driver.session() as session:
                # Any basic query to ensure that connection is active
                session.run("MATCH (n) RETURN n LIMIT 1")
            return True
        except Exception as e:
            print(f"Error during check_connection: {e}")
            return False


def sanitize_service_name(service_name):
    return service_name.strip('"')


def get_available_services():
    session = boto3.Session()
    return session.get_available_services()


def list_services():
    services = get_available_services()
    for service in services:
        print(service)


def write_services_to_db(graph_db):
    # Check connection
    if not graph_db.check_connection():
        print("Failed to connect to the graph database. Please check your database.")
        exit(1)

    # Fetch AWS services
    services = get_available_services()

    # Write AWS services to the graph DB
    added_count = 0
    for service in services:
        try:
            graph_db.add_service(service)
            added_count += 1
        except Exception as e:
            print(f"Failed to add service {service}. Error: {e}")

    print(f"Added {added_count} services to the graph database.")


def main():
    parser = argparse.ArgumentParser(description="Interact with AWS and a graph database to list and store services.")
    parser.add_argument('--list', action='store_true', help="List available AWS services.")
    parser.add_argument('--write', action='store_true', help="Write AWS services to the graph database.")

    args = parser.parse_args()

    graph_db = Neo4jDB()  # Change this instance to another DB class when you have a new DB implementation

    if args.list:
        list_services()
    elif args.write:
        write_services_to_db(graph_db)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
