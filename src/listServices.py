import boto3
import os
import argparse
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

# Read Neo4j configurations from environment variables
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "somepassword")

def create_neo4j_driver():
    try:
        # Connect to Neo4j
        return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    except ServiceUnavailable:
        print("Error: Unable to connect to Neo4j. Please ensure the service is running and accessible.")
        exit(1)

# Initialize Neo4j driver
driver = create_neo4j_driver()

def sanitize_service_name(service_name):
    return service_name.strip('"')

def add_service_to_neo4j(driver, service_name):
    sanitized_name = sanitize_service_name(service_name)
    with driver.session() as session:
        try:
            session.run("MERGE (s:Service {name: $name})", name=sanitized_name)
        except Exception as e:
            print(f"Failed to insert service {sanitized_name} into Neo4j. Error: {e}")

def check_neo4j_connection(driver):
    try:
        with driver.session() as session:
            # Any basic query to ensure that connection is active
            session.run("MATCH (n) RETURN n LIMIT 1")
        return True
    except Exception as e:
        print(f"Error during check_neo4j_connection: {e}")
        return False

def get_available_services():
    session = boto3.Session()
    return session.get_available_services()

def list_services():
    services = get_available_services()
    for service in services:
        print(service)

def write_services_to_neo4j():
    # Check Neo4j connection
    if not check_neo4j_connection(driver):
        print("Failed to connect to Neo4j. Please check your database.")
        exit(1)

    # Fetch AWS services
    services = get_available_services()

    # Write AWS services to Neo4j
    added_count = 0
    for service in services:
        try:
            add_service_to_neo4j(driver, service)
            added_count += 1
        except Exception as e:
            print(f"Failed to add service {service}. Error: {e}")

    print(f"Added {added_count} services to Neo4j.")

def main():
    parser = argparse.ArgumentParser(description="Interact with AWS and Neo4j to list and store services.")
    parser.add_argument('--list', action='store_true', help="List available AWS services.")
    parser.add_argument('--write', action='store_true', help="Write AWS services to Neo4j database.")

    args = parser.parse_args()

    if args.list:
        list_services()
    elif args.write:
        write_services_to_neo4j()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
