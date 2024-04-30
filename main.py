"""
main.py - Command-line interface for processing links using the Rekonise API.

This module provides a command-line interface (CLI) for processing links using the Rekonise API.
It defines a function to parse command-line arguments and invokes the main processing function
accordingly.

Functions:
    parse_arguments() -> argparse.Namespace:
        Parse command-line arguments and return the parsed arguments as a Namespace object.
        This function defines options for specifying either a file containing links or an
        individual link. It also provides a help message detailing how to use the CLI.

Example usage:
    python main.py -f file_name.txt
        Process links from the specified file.

    python main.py -l http(s)://my-domain.com
        Process the individual link specified.
"""

import argparse
from rekonise import main


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Process links using the Rekonise API."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-f", "--file", metavar="FILE", type=str, help="Input file containing links"
    )
    group.add_argument(
        "-l", "--link", metavar="LINK", type=str, help="Individual link to process"
    )
    example_usage = (
        "\nExample usage:\n"
        "  python main.py -f file_name.txt\n"
        "    Process links from the specified file.\n\n"
        "  python main.py -l http(s)://my-domain.com\n"
        "    Process the individual link specified."
    )
    parser.epilog = example_usage
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    if args.file:
        main(file=args.file)
    else:
        main(link=args.link)
