#!/usr/bin/env python3

import getpass

import atom.http_core
import gdata.blogger.client

FAKEG_HOST = "127.0.0.1:8080"
FAKEG_LOGIN_URL = f"http://{FAKEG_HOST}/accounts/ClientLogin"


def main():
    email = "demo@example.test"
    password = "fakeg-demo-password"

    client = gdata.blogger.client.BloggerClient(
        source="FakeG-LegacyClientTest-0.1"
    )

    # Route Blogger API requests to FakeG.
    client.ssl = False
    client.host = FAKEG_HOST

    # Route ClientLogin to FakeG rather than Google's real endpoint.
    client.ClientLogin(
        email,
        password,
        client.source,
        auth_url=atom.http_core.Uri.parse_uri(FAKEG_LOGIN_URL),
        account_type="GOOGLE",
    )

    print("ClientLogin succeeded.")
    print("FakeG token acquired:", client.auth_token is not None)

    # This is a separate API request. The current FakeG server does not
    # implement the Blogger feed endpoint yet.
    try:
        feed = client.get_feed(
            f"http://{FAKEG_HOST}/feeds/default/blogs"
        )

        print("Feed request succeeded:", type(feed).__name__)
        print("Feed class module:", type(feed).__module__)
        print("Feed attributes:", list(vars(feed).keys()))
        title = feed.title

        print("Title type:", type(title).__name__)

        if title is not None:
            print("Title text:", repr(getattr(title, "text", None)))
    except Exception:
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
