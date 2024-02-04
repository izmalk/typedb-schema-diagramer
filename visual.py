from graphviz import Digraph
from typedb.common.transitivity import Transitivity
from typedb.driver import TypeDB, SessionType, TransactionType

DB_NAME = "test"
count = 0


def label():
    global count
    count += 1
    return str(count)


def add_sub_node(d, sup_label, sub, shape):
    subtype_label = label()
    d.node(subtype_label, sub.get_label().name, shape=shape)
    d.edge(sup_label, subtype_label, label='sub')
    subtypes = sub.get_subtypes(transaction, Transitivity.EXPLICIT)
    for subtype in subtypes:
        add_sub_node(d, subtype_label, subtype, shape=shape)
    return d


with TypeDB.core_driver("localhost:1729") as client:  # Connect to TypeDB server
    # print(client.databases.get("test").schema())
    print(f"Connecting to the {DB_NAME} database")
    with client.session(DB_NAME, SessionType.DATA) as session:  # Access data in the `iam` database as session
        print("\nVisualize hierarchy of types")
        with session.transaction(TransactionType.READ) as transaction:  # Open transaction to read
            all_entities = transaction.concepts.get_root_entity_type().get_subtypes(transaction, Transitivity.EXPLICIT)
            all_attributes = transaction.concepts.get_root_attribute_type().get_subtypes(transaction, Transitivity.EXPLICIT)
            all_relations = transaction.concepts.get_root_relation_type().get_subtypes(transaction, Transitivity.EXPLICIT)
            dot = Digraph(graph_attr={'rankdir': 'LR'})
            """
            dot = Digraph(graph_attr={'rankdir': 'LR'})
            with dot.subgraph() as s:
                s.attr(rank='same')
                s.node('E', 'Entity')
                s.node('A', 'Attribute')
                s.node('R', 'Relation')
            """
            dot.node('E', 'Entity', shape="box")
            dot.node('A', 'Attribute', shape="ellipse")
            dot.node('R', 'Relation', shape="diamond")
            # Adding invisible edges to arrange the root labels vertically
            # dot.edge('E', 'A', style="invis")
            # dot.edge('A', 'R', style="invis")
            # print("\nEntity types:")
            for entity in all_entities:
                print(entity.get_label())
                if entity.get_label().name == "entity":
                    continue
                # dot.edge("E", entity.get_label().name, label='sub')
                dot = add_sub_node(dot, 'E', entity, "box")
            # print("\nAttribute types:")
            for attribute in all_attributes:
                if attribute.get_label().name == "attribute":
                    continue
                # print(attribute.get_label())
                # dot.edge("A", attribute.get_label().name, label='sub')
                dot = add_sub_node(dot, 'A', attribute, "ellipse")
            # print("\nRelation types:")
            for relation in all_relations:
                if relation.get_label().name == "relation":
                    continue
                # print(relation.get_label())
                # dot.edge("R", relation.get_label().name, label='sub')
                dot = add_sub_node(dot, 'R', relation, "diamond")

# Save the diagram as a PNG file
output_path = './hierarchy_diagram'
dot.render(output_path, format='png', cleanup=True)

print(f"Diagram created at: {output_path}")
