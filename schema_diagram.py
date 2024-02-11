from graphviz import Digraph
from typedb.common.transitivity import Transitivity
from typedb.driver import TypeDB, SessionType, TransactionType
import argparse

label_count = 0


def label():
    global label_count
    label_count += 1
    return str(label_count)


def add_sub_node(tx, diagram, sup_label, sub, shape):
    subtype_label = label()
    diagram.node(subtype_label, sub.get_label().name, shape=shape)
    diagram.edge(sup_label, subtype_label, label='sub')
    subtypes = sub.get_subtypes(tx, Transitivity.EXPLICIT)
    for subtype in subtypes:
        add_sub_node(tx, diagram, subtype_label, subtype, shape=shape)
    return diagram


def query_data(server, database):
    with TypeDB.core_driver(server) as client:
        print(f"Connecting to the {database} database")
        with client.session(database, SessionType.DATA) as session:
            with session.transaction(TransactionType.READ) as transaction:
                print("Transaction open")
                all_entities = transaction.concepts.get_root_entity_type().get_subtypes(transaction, Transitivity.EXPLICIT)
                all_attributes = transaction.concepts.get_root_attribute_type().get_subtypes(transaction, Transitivity.EXPLICIT)
                all_relations = transaction.concepts.get_root_relation_type().get_subtypes(transaction, Transitivity.EXPLICIT)
                dot = Digraph(graph_attr={'rankdir': 'LR'})
                dot.node('E', 'Entity', shape="box")
                dot.node('A', 'Attribute', shape="ellipse")
                dot.node('R', 'Relation', shape="diamond")
                for entity in all_entities:
                    # print(entity.get_label()) # This is for debugging
                    if entity.get_label().name == "entity":
                        continue
                    dot = add_sub_node(transaction, dot, 'E', entity, "box")
                for attribute in all_attributes:
                    if attribute.get_label().name == "attribute":
                        continue
                    dot = add_sub_node(transaction, dot, 'A', attribute, "ellipse")
                for relation in all_relations:
                    if relation.get_label().name == "relation":
                        continue
                    dot = add_sub_node(transaction, dot, 'R', relation, "diamond")
                print("Diagram is ready. Closing transaction.")
    return dot


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Produces a visualisation of the schema of a TypeDB database.')
    # Define a list of argument configurations
    arg_configs = [
        ('-o', 'output', 'png', 'set the output format. PNG is the default.'),
        ('-f', 'filename', 'hierarchy_diagram', 'set the filename for the output. hierarchy_diagram is the default'),
        ('-d', 'database', 'test', 'set the database name. test is the default.'),
        ('-s', 'server_addr', '127.0.0.1:1729', 'set the TypeDB server address. 127.0.0.1:1729 is the default.'),
        ('-c', 'edition', 'core', 'set the TypeDB edition. Core is the default.'),
    ]
    # Loop through the argument configurations and add them to the parser
    for short_opt, dest, default, help_text in arg_configs:
        parser.add_argument(short_opt, dest=dest, default=default, help=help_text)
    args = parser.parse_args()

    # Print arguments
    # for attr in ['output', 'filename', 'database', 'server_addr', 'edition']:
    #    print(f"{attr.replace('_', ' ').capitalize()}: {getattr(args, attr)}")

    # count = 0
    # Get data and construct the diagram
    diagram = query_data(args.server_addr, args.database)
    # Save the diagram
    match args.output:
        case "png":
            diagram.render('./' + args.filename, format='png', cleanup=True)
            print(f"Saved diagram to file: {args.filename}.png")
        case _:
            print(f"Unrecognized output format.")
