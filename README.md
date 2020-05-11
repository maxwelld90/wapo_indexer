# Washington Post Corpus Indexer
This repository contains code for indexing the Washington Post (WaPo) corpus with the [Python Whoosh](https://whoosh.readthedocs.io/en/latest/intro.html) search engine.

It also downloads images and creates a directory of images for use with the indexed collection (including thumbnails).

## Running the Indexer
The basic command to run the indexer is

`python3 -m wapo_indexer`

Modify the `example.config` file to suit your needs. You can specify the target directory to write the index to, and the directory in which images are to be downloaded and stored to (if you require this). The images directory should be independent of the index directory -- the absolute path is not stored in the index. Rather, only filenames are used. Do not modify the contents of the images directory!