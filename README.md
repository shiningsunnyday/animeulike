# AnimeULike

This is the data collection, preprocessing and preparation code for the AnimeULike dataset, deposited with doi ([here](https://doi.org/10.7910/DVN/PT14ML)).
Sorry the repo is a bit disorganized, with some redundancies, but here's a quickstart navigation. Please reach out so I can walk you through in more depth.

## Contents

- [Contents](#contents)
- [Navigation](#navigation)
- [Cite](#cite)

## Navigation

    scripts
    ├── anime_feats_data     # Show-specific features (synopsis, reviews, popularity, etc.)
    ├── pref_data            # Processed preference matrix and latent factors from WMF
    ├── rating_data          # User supplied ratings
    ├── recs                 # Written inter-item recommendations
    ├── scrape               # Map and reduce pipeline for first scraping popular shows then discovering users from reviews
    ├── split                # Script used to split for training, val and test
    training                 # Code used for experiments

## Cite

Sun, Michael, 2021, "User-Item Feature Graph for Content Based Recommendations of Japanese Anime Shows", https://doi.org/10.7910/DVN/PT14ML, Harvard Dataverse, V1, UNF:6:jtFe6h+rcSI3u4WeMGVZ5w== [fileUNF]

@data{DVN/PT14ML_2021,
author = {sun, michael},
publisher = {Harvard Dataverse},
title = {{User-Item Feature Graph for Content Based Recommendations of Japanese Anime Shows}},
UNF = {UNF:6:jtFe6h+rcSI3u4WeMGVZ5w==},
year = {2021},
version = {V1},
doi = {10.7910/DVN/PT14ML},
url = {https://doi.org/10.7910/DVN/PT14ML}
}
