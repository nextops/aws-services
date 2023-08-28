import boto3
import os
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

def add_service_to_neo4j(tx, service_name):
    sanitized_name = sanitize_service_name(service_name)
    try:
        tx.run("MERGE (s:Service {name: $name})", name=sanitized_name)
    except Exception as e:
        print(f"Failed to insert service {sanitized_name} into Neo4j. Error: {e}")

def check_neo4j_connection():
    try:
        with driver.session() as session:
            # Any basic query to ensure that connection is active
            session.run("MATCH (n) RETURN n LIMIT 1")
        return True
    except Exception as e:
        print(f"Error during check_neo4j_connection: {e}")
        return False

# Check if Neo4j is available
if not check_neo4j_connection():
    print("Failed to connect to Neo4j. Please check your database.")
    exit(1)

# Fetch AWS services
session = boto3.Session()
services = session.get_available_services()

# Write AWS services to Neo4j
added_count = 0
with driver.session() as session:
    for service in services:
        try:
            session.execute_write(add_service_to_neo4j, service)
            added_count += 1
        except Exception as e:
            print(f"Failed to add service {service}. Error: {e}")

print(f"Added {added_count} services to Neo4j.")
