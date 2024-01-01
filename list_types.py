from typedb.common.transitivity import Transitivity
from typedb.driver import TypeDB, SessionType, TransactionType


def print_subtypes(t, level):
    indent = "___>" * level
    print(indent + t.get_label().name)
    subtypes = t.get_subtypes(transaction, Transitivity.EXPLICIT)
    for subtype in subtypes:
        print_subtypes(subtype, level+1)


with TypeDB.core_driver("localhost:1729") as client:  # Connect to TypeDB server
    # print(client.databases.get("test").schema())
    print("Connecting to the `test` database")
    with client.session("test", SessionType.DATA) as session:  # Access data in the `iam` database as session
        print("\nGet types")
        with session.transaction(TransactionType.READ) as transaction:  # Open transaction to read
            entities = transaction.concepts.get_root_entity_type().get_subtypes(transaction)
            attributes = transaction.concepts.get_root_attribute_type().get_subtypes(transaction)
            relations = transaction.concepts.get_root_relation_type().get_subtypes(transaction)
            print("\nEntity types:")
            for entity in entities:
                # print(entity.get_label())
                print_subtypes(entity, 0)
            print("\nAttribute types:")
            for attribute in attributes:
                # print(attribute.get_label())
                print_subtypes(attribute, 0)
            print("\nRelation types:")
            for relation in relations:
                # print(relation.get_label())
                print_subtypes(relation, 0)
