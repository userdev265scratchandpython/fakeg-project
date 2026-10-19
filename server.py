from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from accounts import AccountStore
from auth import TokenStore

from datetime import datetime, timezone
from xml.etree import ElementTree as ET

from threading import Lock
from urllib.parse import urlparse

import psutil, os
from logger import print, writelog, clearlogs

CLIENT_LOGIN_PATH = "/accounts/ClientLogin"
from config import MAX_REQUEST_SIZE, ALLOW_LOGS_CLEAR

ATOM_NS = "http://www.w3.org/2005/Atom"
ET.register_namespace("", ATOM_NS)

if ALLOW_LOGS_CLEAR:
    clearlogs()

def atom_tag(name):
    return f"{{{ATOM_NS}}}{name}"


class BlogStore:
    def __init__(self):
        self.lock = Lock()
        self.blogs = {
            "demo": {
                "id": "tag:fakeg.local,2026:blog/demo",
                "title": "FakeG Demo Blog",
                "author": "FakeG Demo",
                "entries": [
                    {
                        "id": "tag:fakeg.local,2026:post/1",
                        "title": "Hello from FakeG",
                        "content": "This post is served by the local FakeG server.",
                        "updated": datetime.now(timezone.utc),
                    },
                    {
                        "id": "tag:fakeg.local,2026:post/2",
                        "title": "A second post",
                        "content": "Atom feeds, now with actual entries.",
                        "updated": datetime.now(timezone.utc),
                    },
                ],
            }
        }

    def get_blogs(self):
        with self.lock:
            return [
                {
                    "id": blog["id"],
                    "title": blog["title"],
                    "author": blog["author"],
                }
                for blog in self.blogs.values()
            ]


def build_blogs_feed(store):
    feed = ET.Element(atom_tag("feed"))

    ET.SubElement(feed, atom_tag("id")).text = (
        "tag:fakeg.local,2026:blogs"
    )
    ET.SubElement(feed, atom_tag("title"), {"type": "text"}).text = (
        "FakeG Blogs"
    )
    ET.SubElement(feed, atom_tag("updated")).text = (
        datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )

    for blog in store.get_blogs():
        entry = ET.SubElement(feed, atom_tag("entry"))

        ET.SubElement(entry, atom_tag("id")).text = blog["id"]
        ET.SubElement(
            entry, atom_tag("title"), {"type": "text"}
        ).text = blog["title"]
        ET.SubElement(entry, atom_tag("updated")).text = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        author = ET.SubElement(entry, atom_tag("author"))
        ET.SubElement(author, atom_tag("name")).text = blog["author"]

    return ET.tostring(
        feed,
        encoding="utf-8",
        xml_declaration=True,
    )

class FakeGHTTPServer(ThreadingHTTPServer):
    print("Initialized HTTP server")
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, handler_class, accounts, tokens):
        super().__init__(address, handler_class)
        self.accounts = accounts
        self.tokens = tokens
        self.blog_store = BlogStore()


class FakeGHandler(BaseHTTPRequestHandler):
    print("Initialized Winst FakeG handler")
    server_version = "FakeG/0.1"
    sys_version = ""

    def log_message(self, format_string, *args):
        pass

    def send_text(self, status, body):
        print(f"Sent {status} - {body}")
        encoded = body.encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        auth = self.headers.get("Authorization", "")
        token = None

        if auth.startswith("GoogleLogin auth="):
            token = auth.removeprefix("GoogleLogin auth=")

        print(f"Got GET {self.path} | Token: {token or 'None'}")
        if not token or not self.server.tokens.validate(token):
            self.send_text(401, "Error=NotAuthenticated\n")
        
        elif self.path == "/feeds/default/blogs":
            body = build_blogs_feed(self.server.blog_store)

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/atom+xml; charset=utf-8",
            )
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()

            print(f"Sent feed:\n--------\n{body.decode()}\n--------")
            self.wfile.write(body)
        elif self.path == "/accounts/ClientLogin":
            self.send_text(405, "Method not allowed")
        else:
            self.send_text(404, "Not Found\n")

    def do_POST(self):
        if self.path != CLIENT_LOGIN_PATH:
            self.send_text(404, "Not Found\n")
            return

        content_type = self.headers.get("Content-Type", "")
        media_type = content_type.split(";", 1)[0].strip().lower()

        if media_type != "application/x-www-form-urlencoded":
            self.send_text(
                415,
                "Error=UnsupportedMediaType\n",
            )
            return

        try:
            length_header = self.headers.get("Content-Length")

            if length_header is None:
                self.send_text(411, "Error=LengthRequired\n")
                return

            length = int(length_header)

            if length < 0:
                self.send_text(400, "Error=InvalidContentLength\n")
                return

            if length > MAX_REQUEST_SIZE:
                self.send_text(413, "Error=RequestTooLarge\n")
                return

            body = self.rfile.read(length).decode("utf-8")
            fields = parse_qs(body, keep_blank_values=True)

        except (ValueError, UnicodeDecodeError):
            self.send_text(400, "Error=InvalidRequest\n")
            return

        def field(name):
            values = fields.get(name, [])

            # Reject duplicate values instead of silently choosing one.
            if len(values) != 1:
                r = None

            value = values[0]
            r = value if value else None
            print(f"Field {name}: {r}")
            return r

        email = field("Email")
        password = field("Passwd")
        service = field("service")
        source = field("source")

        # ClientLogin's historical request fields are Email, Passwd,
        # service, and source. This particular error label is a FakeG
        # policy; exact legacy clients may expect different error details.
        if not all((email, password, service, source)):
            self.send_text(
                400,
                "Error=MissingRequiredField\n",
            )
            return

        if not self.server.accounts.authenticate(email, password):
            self.send_text(403, "Error=BadAuthentication\n")
            return

        token = self.server.tokens.issue(email)

        # Minimal success response for this first compatibility slice.
        # Historical deployments could return additional fields such as
        # SID and LSID; those are not implemented in this prototype.
        self.send_text(200, f"Auth={token}\n")


def make_server(
    host="127.0.0.1",
    port=8080,
    accounts=None,
    tokens=None,
):
    if accounts is None:
        accounts = AccountStore.for_local_development()

    if tokens is None:
        tokens = TokenStore()

    return FakeGHTTPServer(
        (host, port),
        FakeGHandler,
        accounts,
        tokens,
    )


def main():
    server = make_server()

    print(
        "FakeG ClientLogin listening on "
        f"http://{server.server_address[0]}:{server.server_address[1]}"
    )
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping FakeG.")
    finally:
        server.tokens.clear()
        server.server_close()
        writelog()


if __name__ == "__main__":
    main()
