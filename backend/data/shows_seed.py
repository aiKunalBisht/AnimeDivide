"""
shows_seed.py
=============
Seed data for the `shows` table.

Sources: MyAnimeList (myanimelist.net)
All MAL IDs verified at time of authoring (April 2026).
"""

SHOWS: list[dict] = [
    {
        "slug": "chainsaw-man",
        "title_en": "Chainsaw Man",
        "title_jp": "チェンソーマン",
        "mal_id": 44511,
        "genres": ["Action", "Dark Fantasy", "Horror", "Comedy"],
        "year": 2022,
    },
    {
        "slug": "jujutsu-kaisen",
        "title_en": "Jujutsu Kaisen",
        "title_jp": "呪術廻戦",
        "mal_id": 40748,
        "genres": ["Action", "Adventure", "Dark Fantasy", "Supernatural"],
        "year": 2020,
    },
    {
        "slug": "vinland-saga",
        "title_en": "Vinland Saga",
        "title_jp": "ヴィンランド・サガ",
        "mal_id": 37521,
        "genres": ["Action", "Adventure", "Historical", "Drama"],
        "year": 2019,
    },
    {
        "slug": "berserk-2016",
        "title_en": "Berserk (2016)",
        "title_jp": "ベルセルク",
        "mal_id": 32379,
        "genres": ["Action", "Dark Fantasy", "Horror", "Adventure"],
        "year": 2016,
    },
    {
        "slug": "attack-on-titan-final-season",
        "title_en": "Attack on Titan Final Season",
        "title_jp": "進撃の巨人 The Final Season",
        "mal_id": 40028,
        "genres": ["Action", "Dark Fantasy", "Post-Apocalyptic", "Military"],
        "year": 2020,
    },
    {
        "slug": "demon-slayer-mugen-train-arc",
        "title_en": "Demon Slayer: Kimetsu no Yaiba — Mugen Train Arc",
        "title_jp": "鬼滅の刃 無限列車編",
        "mal_id": 49926,
        "genres": ["Action", "Supernatural", "Horror", "Drama"],
        "year": 2021,
    },
    {
        "slug": "bleach-tybw",
        "title_en": "Bleach: Thousand-Year Blood War",
        "title_jp": "BLEACH 千年血戦篇",
        "mal_id": 41467,
        "genres": ["Action", "Adventure", "Supernatural"],
        "year": 2022,
    },
    {
        "slug": "one-piece-post-timeskip",
        "title_en": "One Piece (post-timeskip)",
        "title_jp": "ONE PIECE",
        # MAL has no separate entry for post-timeskip; this is the canonical series ID.
        "mal_id": 21,
        "genres": ["Action", "Adventure", "Comedy", "Fantasy"],
        "year": 2011,  # Post-timeskip story arc begins ~episode 517, aired January 2011
    },
    {
        "slug": "frieren",
        "title_en": "Frieren: Beyond Journey's End",
        "title_jp": "葬送のフリーレン",
        "mal_id": 52991,
        "genres": ["Adventure", "Drama", "Fantasy", "Slice of Life"],
        "year": 2023,
    },
    {
        "slug": "solo-leveling",
        "title_en": "Solo Leveling",
        "title_jp": "俺だけレベルアップな件",
        "mal_id": 52299,
        "genres": ["Action", "Adventure", "Fantasy"],
        "year": 2024,
    },
]
