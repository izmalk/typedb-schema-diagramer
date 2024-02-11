# TypeDB database schema visualizer

Draws a diagram of the schema of a TypeDB database.
Requires TypeDB server running the database to visualize its schema.

## User manual

To run:

```bash
schema_diagram.py
```

Or use CLI arguments, for example:

```bash
schema_diagram.py -o png -f 111 -d iam -s localhost:1729 -c core
```

For more information on arguments:

```bash
schema_diagram.py -h
```
