# Migrate glossary from Transifex to Weblate

This is a set of scripts I wrote to migrate the glossary from a Transifex
project to Weblate.

This is quick and dirty code created just for one time use. I have no
intention to fully maintain this or turning it into a fully generic tool.
But I put the code up here for future use. Feel free to use it, but be
aware you might need to edit the scripts directly to fit your needs.


## Downloading glossary from Transifex

You can download glossaries in your Glossaries project under "Glossaries" as
CSV files.


## Convert Transifex CSV files into Weblate format

Example:

```
./tx2weblate.py -f musicbrainz_2013-12-07_all_languages.csv -o out/
```


## Uploading to Weblate

Example:

```
./push2weblate.py -t YOUR_WEBLATE_API_TOKEN \
    -H translations.metabrainz.org \
    -c musicbrainz/glossary \
    -i out/*.csv
```


## License

All code here is published under the MIT license, see LICENSE.txt for details.
