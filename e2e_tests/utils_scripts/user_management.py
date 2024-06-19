import argparse


def parse_arguments():
    """Parsing command line arguments."""
    parser = argparse.ArgumentParser(
        description="Script used for creating or deleting users via Keycloak Admin API"
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        help="Script mode, either create or delete",
        required=True,
    )
    parser.add_argument(
        "-o", "--output", type=str, default="json", help="Output format"
    )
    parser.add_argument(
        "-rn",
        "--realm_name",
        type=str,
        help="Keycloak realm name",
        required=True,
    )
    parser.add_argument(
        "-cid",
        "--client_id",
        type=str,
        help="Keycloak client ID",
        required=True,
    )
    parser.add_argument(
        "-cs",
        "--client_secret",
        type=str,
        help="Keycloak client secret",
        required=True,
    )
    parser.add_argument(
        "-uri", "--base_uri", type=str, help="Keycloak base URI", required=True
    )
    parser.add_argument(
        "-uid",
        "--user_id",
        type=str,
        help="Keycloak user ID, used to delete an account",
    )
    return parser.parse_args()


def main():
    """Main function."""
    # Get parsed command line arguments
    args = parse_arguments()
    print(args)


if __name__ == "__main__":
    main()
