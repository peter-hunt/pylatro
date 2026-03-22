"""Allow running examples with `python -m examples` or `python -m examples.game_entities`."""

import sys

# When run as `python -m examples.game_entities`, __name__ will be __main__
# We need to handle the import properly
if __name__ == "__main__":
    # Import and run the specific example module
    if len(sys.argv) > 1:
        example_name = sys.argv[1]
    else:
        # Default to game_entities if no argument provided
        example_name = "game_entities"

    if example_name == "game_entities":
        from . import game_entities
        game_entities.main()
    elif example_name == "datatype_usage":
        from . import datatype_usage
        datatype_usage.main()
    else:
        print(f"Unknown example: {example_name}")
        print("Available examples: game_entities, datatype_usage")
        sys.exit(1)
