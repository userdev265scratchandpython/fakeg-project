
#!/usr/bin/env python3

import getpass
import traceback

import atom.http_core
import gdata.blogger.client

try:
    from clientconfig import IP, PORT
    FAKEG_HOST = f"{IP}:{PORT}"
except:
    FAKEG_HOST = f"127.0.0.1:8080"
FAKEG_BASE_URL = f"http://{FAKEG_HOST}"
FAKEG_LOGIN_URL = f"{FAKEG_BASE_URL}/accounts/ClientLogin"


def element_text(element):
    if element is None:
        return "(not provided)"

    return getattr(element, "text", None) or "(not provided)"


def show_feed(feed):
    print("\n" + "=" * 60)
    print("Feed:", element_text(getattr(feed, "title", None)))
    print("ID:  ", element_text(getattr(feed, "id", None)))
    print("=" * 60)

    entries = getattr(feed, "entry", None) or []

    if not entries:
        print("No entries returned.")
        return

    for number, entry in enumerate(entries, start=1):
        print(f"\n[{number}] {element_text(getattr(entry, 'title', None))}")
        print("  ID:", element_text(getattr(entry, "id", None)))
        print("  Updated:", element_text(getattr(entry, "updated", None)))
        print("  Published:", element_text(getattr(entry, "published", None)))

        authors = getattr(entry, "author", None) or []
        for author in authors:
            print("  Author:", element_text(getattr(author, "name", None)))

        content = getattr(entry, "content", None)
        summary = getattr(entry, "summary", None)

        if content is not None:
            print("  Content:", element_text(content))
        elif summary is not None:
            print("  Summary:", element_text(summary))

        for link in getattr(entry, "link", None) or []:
            href = getattr(link, "href", None)
            if href:
                print("  Link:", href)


def main():
    token = input("FakeG token: ").strip()
    if not token:
        email = input("FakeG email [demo@example.test]: ").strip()
        if not email:
            email = "demo@example.test"

        password = getpass.getpass("FakeG password: ")
        if not password:
            password = "fakeg-demo-password"

        client = gdata.blogger.client.BloggerClient(
            source="FakeG-CLI-0.2"
        )

        client.ssl = False
        client.host = FAKEG_HOST

        try:
            client.ClientLogin(
                email,
                password,
                client.source,
                auth_url=atom.http_core.Uri.parse_uri(FAKEG_LOGIN_URL),
                account_type="GOOGLE",
            )

            print("\nClientLogin succeeded.")
            print("FakeG token acquired:", client.auth_token is not None)
            print(f"Token: {client.auth_token.token_string}")
        except Exception:
            print("\nFakeG request failed:")
            traceback.print_exc()
    else:
        client = gdata.blogger.client.BloggerClient(
            source="FakeG-CLI-0.2"
        )

        client.ssl = False
        client.host = FAKEG_HOST
        client.auth_token = gdata.gauth.ClientLoginToken(token)
    if True:
        try:
            blogs_url = f"{FAKEG_BASE_URL}/feeds/default/blogs"
            print("\nFetching blogs:", blogs_url)

            blogs_feed = client.get_feed(blogs_url)
            show_feed(blogs_feed)

            blogs = getattr(blogs_feed, "entry", None) or []
        except Exception:
            traceback.print_exc()
            blogs = []
        if not blogs:
            return
        try:
            while True:
                print("\nAvailable blogs:")
                for index, blog in enumerate(blogs, start=1):
                    print(f"  {index}. {element_text(getattr(blog, 'title', None))}")

                print("  R. Refresh blog list")
                print("  Q. Quit")

                choice = input("\nSelect a blog: ").strip().lower()

                if choice == "q":
                    break

                if choice == "r":
                    blogs_feed = client.get_feed(blogs_url)
                    blogs = getattr(blogs_feed, "entry", None) or []
                    show_feed(blogs_feed)
                    continue

                try:
                    blog = blogs[int(choice) - 1]
                except (ValueError, IndexError):
                    print("Invalid selection.")
                    continue

                blog_id_element = getattr(blog, "id", None)
                blog_id = element_text(blog_id_element)

                if blog_id == "(not provided)":
                    print("This blog has no ID; cannot request its posts.")
                    continue

                # FakeG's demo server uses the short blog ID "demo".
                # Atom IDs may instead be URNs, so prefer the blog link
                # if the server provides a posts-feed URL.
                post_url = None

                for link in getattr(blog, "link", None) or []:
                    rel = getattr(link, "rel", None)
                    href = getattr(link, "href", None)

                    if href and (
                        rel == "http://schemas.google.com/g/2005#post"
                        or rel == "http://schemas.google.com/g/2005#feed"
                    ):
                        post_url = href
                        break

                if post_url and post_url.startswith("/"):
                    post_url = f"{FAKEG_BASE_URL}{post_url}"

                if not post_url:
                    # The current FakeG server's demo blog ID is "demo".
                    # For other IDs, the server should expose a feed link.
                    if blog_id.endswith("/demo") or blog_id == "demo":
                        blog_id = "demo"

                    post_url = (
                        f"{FAKEG_BASE_URL}/feeds/"
                        f"{blog_id}/posts/default"
                    )

                print("\nFetching posts:", post_url)

                try:
                    posts_feed = client.get_feed(post_url)
                    show_feed(posts_feed)
                except Exception:
                    print("Could not fetch this blog's posts:")
                    traceback.print_exc()
        except Exception:
            print("An error occured:")
            traceback.print_exc()

if __name__ == "__main__":
    main()
