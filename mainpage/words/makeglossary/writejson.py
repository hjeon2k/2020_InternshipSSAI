import json

data = {"name":"projects/english-subtitle-for-video/locations/us-central1/glossaries/Humanities_ko-en",
  "languagePair": {
    "sourceLanguageCode": "ko",
    "targetLanguageCode": "en"
    },
  "inputConfig": {
    "gcsSource": {
      "inputUri": "gs://snu_ensub_project/glossary/Humanities_ko_en_g.csv"
    }
  }
}

with open('request.json', 'w') as wr:
    json.dump(data, wr, indent=4)
