"""Local dev server for the portfolio.

Threaded, and answers HTTP Range requests so browsers can stream and seek the
videos in media/ (the stock SimpleHTTPRequestHandler always sends whole files).
"""
import http.server
import os
import re
import sys
import webbrowser

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)")


class RangeHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def send_head(self):
        match = RANGE_RE.fullmatch(self.headers.get("Range", "").strip())
        path = self.translate_path(self.path)
        if not match or not os.path.isfile(path):
            return super().send_head()

        size = os.path.getsize(path)
        first, last = match.groups()
        if first:
            start, end = int(first), int(last) if last else size - 1
        else:  # suffix range: last N bytes
            start, end = max(0, size - int(last or 0)), size - 1
        end = min(end, size - 1)
        if start > end:
            self.send_error(416, "Requested Range Not Satisfiable")
            return None

        f = open(path, "rb")
        f.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        self._remaining = end - start + 1
        return f

    def copyfile(self, source, outputfile):
        remaining = getattr(self, "_remaining", None)
        if remaining is None:
            return super().copyfile(source, outputfile)
        try:
            while remaining > 0:
                chunk = source.read(min(64 * 1024, remaining))
                if not chunk:
                    break
                outputfile.write(chunk)
                remaining -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass  # the browser cancelled the request mid-stream; that's normal for video
        finally:
            self._remaining = None


def run_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    try:
        with http.server.ThreadingHTTPServer(("", PORT), RangeHandler) as httpd:
            url = f"http://localhost:{PORT}"
            print(f"Anmolpreet Singh portfolio running at {url}  (Ctrl+C to stop)")
            try:
                webbrowser.open(url)
            except Exception:
                pass
            httpd.serve_forever()
    except OSError as e:
        print(f"Error binding to port {PORT}: {e}")


if __name__ == "__main__":
    run_server()
