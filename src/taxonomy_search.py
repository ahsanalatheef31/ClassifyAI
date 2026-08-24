from pathlib import Path
import re

TAXONOMY_FILE = Path("taxonomy/categories.txt")


class ShopifyTaxonomy:
    def __init__(self, taxonomy_file=TAXONOMY_FILE):
        self.categories = self._load_categories(taxonomy_file)

    def _load_categories(self, taxonomy_file):
        categories = []

        for line in taxonomy_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            gid, path = line.split(" : ", 1)

            categories.append({
                "gid": gid.strip(),
                "path": path.strip(),
                "name": path.strip().split(" > ")[-1]
            })

        return categories

    @staticmethod
    def _words(text):
        return set(re.findall(r"[a-z0-9]+", text.lower()))

    def search(self, query, limit=10):
        query = query.strip().lower()
        query_words = self._words(query)

        if not query_words:
            return []

        results = []

        for category in self.categories:
            path = category["path"].lower()
            name = category["name"].lower()
            name_words = self._words(name)

            score = 0

            if name == query:
                score += 1000
            elif query in name:
                score += 500
            elif query in path:
                score += 200

            matching_name_words = query_words & name_words
            score += len(matching_name_words) * 50

            if matching_name_words and matching_name_words != query_words:
                score -= len(query_words - matching_name_words) * 20

            if score > 0:
                results.append((score, category))

        results.sort(key=lambda item: (-item[0], item[1]["path"]))

        return [
            {
                **category,
                "score": score
            }
            for score, category in results[:limit]
        ]


if __name__ == "__main__":
    taxonomy = ShopifyTaxonomy()

    print("Loaded categories:", len(taxonomy.categories))
    print()
    print("Search: Bar Soap")
    print()

    results = taxonomy.search("Bar Soap", limit=10)

    for i, category in enumerate(results, 1):
        print(f"{i}. {category['path']}")
        print(f"   GID: {category['gid']}")
        print(f"   Score: {category['score']}")
        print()
