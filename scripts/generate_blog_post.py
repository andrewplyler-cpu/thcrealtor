import os
from datetime import datetime
from zoneinfo import ZoneInfo


def main():
    now = datetime.now(ZoneInfo("America/New_York"))
    html = f"""<!doctype html>
<html>
  <head>
    <meta charset='utf-8'>
    <title>Blog | Andrew Plyler</title>
  </head>
  <body>
    <h1>Blog</h1>
    <p>Last updated {now.date()}</p>
  </body>
</html>
"""

    os.makedirs("blog", exist_ok=True)
    with open("blog/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    with open("blog.html", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
