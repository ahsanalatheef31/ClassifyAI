try:
    from src.taxonomy_search import ShopifyTaxonomy
except ImportError:
    from taxonomy_search import ShopifyTaxonomy


class ClassificationEngine:

    def __init__(self):
        self.taxonomy = ShopifyTaxonomy()

    @staticmethod
    def _words(text):
        return set(
            text.lower().split()
        )

    def _context_score(self, candidate, product_info):

        category_name = candidate["name"].lower()
        category_path = candidate["path"].lower()

        product_name = product_info.get(
            "product_name", ""
        ).lower()

        product_type = product_info.get(
            "product_type", ""
        ).lower()

        specific_type = product_info.get(
            "specific_type", ""
        ).lower()

        intended_use = product_info.get(
            "intended_use", ""
        ).lower()

        score = candidate.get("score", 0)

        # -------------------------------------------------
        # 1. SPECIFIC TYPE
        # -------------------------------------------------

        if specific_type:

            if specific_type == category_name:
                score += 900

            elif specific_type in category_name:
                score += 500

            elif category_name in specific_type:
                score += 350

        # -------------------------------------------------
        # 2. PRODUCT TYPE
        # -------------------------------------------------

        if product_type:

            if product_type == category_name:
                score += 600

            elif product_type in category_name:
                score += 200

            elif product_type in category_path:
                score += 100

        # -------------------------------------------------
        # 3. PRODUCT NAME
        # -------------------------------------------------

        if product_name:

            product_words = self._words(
                product_name
            )

            category_words = self._words(
                category_name
            )

            matching_words = (
                product_words &
                category_words
            )

            score += (
                len(matching_words) * 100
            )

            # Strong boost when the full category
            # name appears in the product name.
            if category_name in product_name:
                score += 500

        # -------------------------------------------------
        # 4. INTENDED USE
        # -------------------------------------------------

        if intended_use:

            use_words = self._words(
                intended_use
            )

            category_words = self._words(
                category_path
            )

            matching_use_words = (
                use_words &
                category_words
            )

            score += (
                len(matching_use_words) * 50
            )

        # -------------------------------------------------
        # 5. CATEGORY-SPECIFIC RULES
        # -------------------------------------------------

        # Cosmetic / skincare products
        # -------------------------------------------------

        if "face serum" in specific_type:

            if "face serums" in category_path:
                score += 1200

            if "face moisturizers" in category_path:
                score -= 400

            if "hair serums" in category_path:
                score -= 500

        # Face moisturizer
        # -------------------------------------------------

        if (
            "face moisturizer" in specific_type
            or "facial moisturizer" in specific_type
        ):

            if "face moisturizers" in category_path:
                score += 1200

            if "face serums" in category_path:
                score -= 400

        # Hair serum
        # -------------------------------------------------

        if "hair serum" in specific_type:

            if "hair serums" in category_path:
                score += 1200

            if "face serums" in category_path:
                score -= 500

        # Bar soap
        # -------------------------------------------------

        if "bar soap" in specific_type:

            if category_name == "bar soap":
                score += 1200

            if "liquid hand soap" in category_path:
                score -= 500

            if "powdered hand soap" in category_path:
                score -= 500

            if "shaving soap" in category_path:
                score -= 400

        # -------------------------------------------------
        # 6. ACCESSORY PENALTY
        # -------------------------------------------------

        accessory_words = {
            "accessories",
            "bags",
            "pouches",
            "dispensers",
            "holders",
            "sponges",
            "cases",
            "parts",
            "replacement"
        }

        if category_words & accessory_words:
            score -= 300

        # -------------------------------------------------
        # DOMAIN MISMATCH PENALTIES
        # -------------------------------------------------

        # Pet categories should not match ordinary human products
        pet_words = {
            "pet",
            "pets",
            "animal",
            "animals",
            "dog",
            "dogs",
            "cat",
            "cats",
            "canine",
            "feline",
        }

        product_text = " ".join([
            product_name,
            product_type,
            specific_type,
            intended_use,
        ]).lower()

        if (
            any(word in category_path for word in pet_words)
            and not any(word in product_text for word in pet_words)
        ):
            score -= 1500


        # Baby categories should require baby-related evidence
        baby_words = {
            "baby",
            "infant",
            "newborn",
            "toddler",
        }

        if (
            any(word in category_path for word in baby_words)
            and not any(word in product_text for word in baby_words)
        ):
            score -= 1000    

        return max(
            score,
            0
        )

    def _collect_candidates(
        self,
        product_info,
        limit_per_query=15
    ):

        queries = []

        product_name = product_info.get(
            "product_name", ""
        ).strip()

        specific_type = product_info.get(
            "specific_type", ""
        ).strip()

        product_type = product_info.get(
            "product_type", ""
        ).strip()

        # Most specific first
        if specific_type:
            queries.append(
                specific_type
            )

        if product_name:
            queries.append(
                product_name
            )

        if product_type:
            queries.append(
                product_type
            )

        # Remove duplicate queries
        queries = list(
            dict.fromkeys(
                q.lower()
                for q in queries
                if q
            )
        )

        candidates_by_gid = {}

        for query in queries:

            results = self.taxonomy.search(
                query,
                limit=limit_per_query
            )

            for candidate in results:

                gid = candidate["gid"]

                if gid not in candidates_by_gid:

                    candidates_by_gid[gid] = candidate

                else:

                    # Keep the highest base score
                    existing = candidates_by_gid[gid]

                    if candidate.get(
                        "score", 0
                    ) > existing.get(
                        "score", 0
                    ):

                        candidates_by_gid[gid] = candidate

        return list(
            candidates_by_gid.values()
        )

    def _calculate_confidence(
        self,
        candidates
    ):

        if not candidates:
            return 0.0

        best_score = candidates[0][
            "context_score"
        ]

        second_score = (
            candidates[1]["context_score"]
            if len(candidates) > 1
            else 0
        )

        if best_score <= 0:
            return 0.0

        if second_score > 0:

            gap_ratio = (
                best_score - second_score
            ) / best_score

        else:

            gap_ratio = 1.0

        confidence = (
            0.55 +
            (gap_ratio * 0.35)
        )

        return round(
            min(
                max(
                    confidence,
                    0.0
                ),
                0.95
            ),
            2
        )

    def classify(self, product_info):

        product_name = product_info.get(
            "product_name",
            ""
        ).strip()

        product_type = product_info.get(
            "product_type",
            ""
        ).strip()

        specific_type = product_info.get(
            "specific_type",
            ""
        ).strip()

        if not (
            product_name or
            product_type or
            specific_type
        ):

            return {
                "category": None,
                "shopify_gid": None,
                "confidence": 0.0,
                "alternatives": [],
                "manual_review": True,
                "reason": (
                    "Insufficient product "
                    "information"
                )
            }

        # -------------------------------------------------
        # Build a broad candidate pool
        # -------------------------------------------------

        candidates = self._collect_candidates(
            product_info,
            limit_per_query=15
        )

        if not candidates:

            return {
                "category": None,
                "shopify_gid": None,
                "confidence": 0.0,
                "alternatives": [],
                "manual_review": True,
                "reason": (
                    "No matching Shopify "
                    "category found"
                )
            }

        # -------------------------------------------------
        # Context scoring
        # -------------------------------------------------

        for candidate in candidates:

            candidate[
                "context_score"
            ] = self._context_score(
                candidate,
                product_info
            )

        # -------------------------------------------------
        # Sort
        # -------------------------------------------------

        candidates.sort(
            key=lambda candidate: (
                -candidate[
                    "context_score"
                ],
                candidate["path"]
            )
        )

        best = candidates[0]

        confidence = (
            self._calculate_confidence(
                candidates
            )
        )

        # -------------------------------------------------
        # Alternatives
        # -------------------------------------------------

        alternatives = []

        for candidate in candidates[1:]:

            if candidate[
                "context_score"
            ] >= best[
                "context_score"
            ] * 0.60:

                alternatives.append({
                    "category": candidate[
                        "path"
                    ],

                    "shopify_gid": candidate[
                        "gid"
                    ],

                    "score": candidate[
                        "context_score"
                    ]
                })

        # -------------------------------------------------
        # Manual review
        # -------------------------------------------------

        manual_review = (
            confidence < 0.70
        )

        return {
            "category": best["path"],

            "shopify_gid": best["gid"],

            "confidence": confidence,

            "alternatives": alternatives[:3],

            "manual_review": manual_review
        }


if __name__ == "__main__":

    engine = ClassificationEngine()

    test_products = [

        {
            "product_name":
                "Cinnabari Face Serum",

            "product_type":
                "Serum",

            "specific_type":
                "Face Serum",

            "intended_use":
                "Hydrating for daily facial skincare"
        },

        {
            "product_name":
                "Cinnabari Bar Soap",

            "product_type":
                "Soap",

            "specific_type":
                "Bar Soap",

            "intended_use":
                "Body cleansing"
        },

        {
            "product_name":
                "Cinnabari Shampoo",

            "product_type":
                "Shampoo",

            "specific_type":
                "",

            "intended_use":
                "Hair care"
        }
    ]

    for product in test_products:

        print("\n" + "=" * 70)

        print(
            "PRODUCT:",
            product["product_name"]
        )

        result = engine.classify(
            product
        )

        print(
            "CATEGORY:",
            result["category"]
        )

        print(
            "GID:",
            result["shopify_gid"]
        )

        print(
            "CONFIDENCE:",
            result["confidence"]
        )

        print(
            "MANUAL REVIEW:",
            result["manual_review"]
        )

        print(
            "ALTERNATIVES:",
            result["alternatives"]
        )