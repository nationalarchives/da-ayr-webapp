import argparse
import json

from e2e_tests.utils.user_management import (
    create_aau_keycloak_user,
    create_standard_keycloak_user,
    delete_keycloak_user,
    keycloak_admin,
)


def generate_pa11y_config(email, password):
    uri = "https://127.0.0.1:5000"
    return json.dumps(
        {
            "defaults": {
                "timeout": 2000,
                "useIncognitoBrowserContext": False,
                "chromeLaunchConfig": {
                    "ignoreHTTPSErrors": True,
                },
                "viewport": {
                    "width": 1280,
                    "height": 1080,
                },
                "userAgent": "A11Y TESTS",
            },
            "urls": [
                # static pages
                f"{uri}/how-to-use-this-service",
                f"{uri}/terms-of-use",
                f"{uri}/privacy",
                f"{uri}/cookies",
                f"{uri}/accessibility",
                f"{uri}/signed-out",
                f"{uri}/",
                # authentication steps
                f"{uri}/sign-out",
                {
                    "url": f"{uri}/sign-in",
                    "actions": [
                        "wait for element #username to be visible",
                        f"set field #username to {email}",
                        f"set field #password to {password}",
                        'click element button[type="submit"]',
                        "wait for path to be /browse",
                    ],
                },
                # pages that require authentication
                f"{uri}/browse",
                f"{uri}/browse/series/1d4cedb8-95f5-4e5e-bc56-c0c0f6cccbd7",
                f"{uri}/browse/consignment/bf203811-357a-45a8-8b38-770d1580691c",
                f"{uri}/record/097e1fde-70f5-4eef-9a46-c85ea4350bf7",
                f"{uri}/search_results_summary?query=test",
                f"{uri}/search/transferring_body/c3e3fd83-4d52-4638-a085-1f4e4e4dfa50?query=test",
            ],
        }
    )


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
        "-o",
        "--output",
        type=str,
        default="json",
        help="Output format, e.g. json, text, pa11y",
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
    parser.add_argument(
        "-ut",
        "--user_type",
        type=str,
        help="Keycloak user type, can be aau or standard",
    )
    return parser.parse_args()


def generate_output(output_type, user_id, user_email, user_pass, base_uri):
    if output_type == "pa11y":
        config_file = open("configs/pa11y_config.json", "w")
        config_file.write(generate_pa11y_config(user_email, user_pass))
        config_file.close()

        user_id_file = open("configs/user_id.txt", "w")
        user_id_file.write(user_id)
        user_id_file.close()
        return print("Generated pa11y config inside configs/pa11y_config.json")
    else:
        return print(user_id, user_email, user_pass)


def main():
    """Main function."""
    # Get parsed command line arguments
    args = parse_arguments()
    kc_admin = keycloak_admin(
        args.realm_name, args.client_id, args.client_secret, args.base_uri
    )

    if args.mode == "create" and kc_admin:
        if args.user_type == "aau":
            user_id, user_email, user_pass = create_aau_keycloak_user(kc_admin)
            print("Created user ", user_id)
            return generate_output(
                args.output, user_id, user_email, user_pass, args.base_uri
            )
        if args.user_type == "standard":
            user_id, user_email, user_pass = create_standard_keycloak_user(
                kc_admin
            )
            print("Created user ", user_id)
            return generate_output(
                args.output, user_id, user_email, user_pass, args.base_uri
            )
    elif args.mode == "delete" and kc_admin and args.user_id:
        delete_keycloak_user(kc_admin, args.user_id)
        print("Deleted user ", args.user_id)


if __name__ == "__main__":
    main()
