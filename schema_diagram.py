from graphviz import Digraph
from typedb.common.transitivity import Transitivity
from typedb.driver import TypeDB, SessionType, TransactionType
import argparse


def add_sub_node(tx, diagram, sup_label, sub, shape):
    subtype_label = sub.get_label().name
    diagram.node(subtype_label, subtype_label, shape=shape)
    diagram.edge(sup_label, subtype_label, label='sub')
    subtypes = sub.get_subtypes(tx, Transitivity.EXPLICIT)
    for subtype in subtypes:
        add_sub_node(tx, diagram, subtype_label, subtype, shape=shape)
    return diagram


def add_owned_attr(diagram, owner, attribute):
    diagram.edge(owner.get_label().name, attribute.get_label().name,
                 label='owns', color='red', fontcolor='red')


def add_role_player(diagram, player, role, relation):
    diagram.edge(relation.get_label().name, player.get_label().name,
                 label=role.get_label().name, color='forestgreen', fontcolor='forestgreen')


def core_get_data(server, database):
    with TypeDB.core_driver(server) as client:
        print(f"Connecting to the {database} database")
        with client.session(database, SessionType.DATA) as session:
            with session.transaction(TransactionType.READ) as transaction:
                print("Transaction open")
                dot_types = Digraph('cluster_types', graph_attr={'rankdir': 'LR'})
                dot_attributes = Digraph('attributes', graph_attr={'rankdir': 'RL'})
                dot_roles = Digraph('roles', graph_attr={'rankdir': 'RL'})
                dot_all = Digraph('all', graph_attr={'rankdir': 'LR'})
                with dot_types.subgraph() as r:
                    r.attr(rank='same')
                    r.node('E', 'Entity', shape='box', rank='source')
                    r.node('A', 'Attribute', shape="ellipse", rank='min')
                    r.node('R', 'Relation', shape="diamond", rank='min')
                all_entities = transaction.concepts.get_root_entity_type().get_subtypes(transaction, Transitivity.EXPLICIT)
                all_attributes = transaction.concepts.get_root_attribute_type().get_subtypes(transaction, Transitivity.EXPLICIT)
                all_relations = transaction.concepts.get_root_relation_type().get_subtypes(transaction, Transitivity.EXPLICIT)
                for entity in all_entities:
                    if entity.get_label().name == "entity":
                        continue
                    dot_types = add_sub_node(transaction, dot_types, 'E', entity, "box")
                    if args.attributes == "true":
                        for owned_attr in entity.get_owns(transaction):
                            add_owned_attr(dot_attributes, entity, owned_attr)
                for attribute in all_attributes:
                    if attribute.get_label().name == "attribute":
                        continue
                    dot_types = add_sub_node(transaction, dot_types, 'A', attribute, "ellipse")
                    # Yes, attributes can own attributes. But this is forbidden technic!
                    if args.attributes == "true":
                        for owned_attr in attribute.get_owns(transaction):
                            add_owned_attr(dot_attributes, attribute, owned_attr)
                for relation in all_relations:
                    if relation.get_label().name == "relation":
                        continue
                    dot_types = add_sub_node(transaction, dot_types, 'R', relation, "diamond")
                    if args.attributes == "true":
                        for owned_attr in relation.get_owns(transaction):
                            add_owned_attr(dot_attributes, relation, owned_attr)
                    if args.roles == "true":
                        for role in relation.get_relates(transaction):
                            for player in role.get_player_types(transaction):
                                add_role_player(dot_roles, player, role, relation)
                print("Diagram is ready. Closing transaction.")
                if args.attributes == 'true':
                    dot_all.subgraph(dot_attributes)
                if args.roles == 'true':
                    dot_all.subgraph(dot_roles)
                dot_all.subgraph(dot_types)
    return dot_all


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Produces a visualisation of the schema of a TypeDB database.')
    arg_configs = [
        ('-o', 'output', 'png', 'set the output format. PNG is the default.'),
        ('-f', 'filename', 'schema_diagram', 'set the filename for the output. hierarchy_diagram is the default'),
        ('-d', 'database', 'test', 'set the database name. test is the default.'),
        ('-s', 'server_addr', '127.0.0.1:1729', 'set the TypeDB server address. 127.0.0.1:1729 is the default.'),
        ('-c', 'edition', 'core', 'set the TypeDB edition. Core|Cloud. Core is the default.'),
        ('-r', 'roles', 'true', 'whether to draw role players. True|False. True is the default.'),
        ('-a', 'attributes', 'true', 'whether to draw attributes ownership. True|False. True is the default.'),
    ]
    for short_opt, dest, default, help_text in arg_configs:  # Add arguments to the parser
        parser.add_argument(short_opt, dest=dest, default=default, help=help_text)
    args = parser.parse_args()
    args.output = args.output.lower()
    args.edition = args.edition.lower()
    args.roles = args.roles.lower()
    args.attributes = args.attributes.lower()

    # Get data and construct the diagram
    match args.edition:
        case "core":
            diagram_dot = core_get_data(args.server_addr, args.database)
        case "cloud":
            # diagram_dot = core_get_data(args.server_addr, args.database)
            print(f"TypeDB Cloud is not supported yet.")
            exit()
        case _:
            print(f"Unsupported TypeDB server edition input.")
            exit()

    # Save the diagram
    match args.output:
        case "png":
            diagram_dot.render('./' + args.filename, format='png', cleanup=True)
            print(f"Saved diagram to file: {args.filename}.png")
        case "svg":
            diagram_dot.render('./' + args.filename, format='svg', cleanup=True)
            print(f"Saved diagram to file: {args.filename}.svg")
        case _:
            print(f"Unrecognized output format.")
