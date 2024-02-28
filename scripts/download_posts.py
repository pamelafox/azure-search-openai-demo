import json
import urllib.request


def get_blogger_urls():
    url = "http://www.blogger.com/feeds/8501278254137514883/posts/default?max-results=150&alt=json"
    with urllib.request.urlopen(url) as result:
        if result.status == 200:
            feed = json.loads(result.read())["feed"]
            entries = feed["entry"]
            for entry in entries:
                links = entry["link"]
                for link in links:
                    if link["rel"] == "alternate":
                        url = link["href"]
                        # download the post and save to data/ directory
                        with urllib.request.urlopen(url) as post_result:
                            if post_result.status == 200:
                                post = post_result.read().decode("utf-8")
                                with open("data/" + url.split("/")[-1], "w") as f:
                                    f.write(post)


if __name__ == "__main__":
    get_blogger_urls()
