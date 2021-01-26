from google.cloud import translate
from google.cloud import storage
#from google.cloud import storage
#import os

project_id= "english-subtitle-for-video"
#GLOSSARY_ID = "ko-en"
#DIR = os.getcwd()+'/'
#BUCKET_NAME = "snu_script_bucket"
#GLOSSARY_ID = "glossary_test"


def translate_line(text="text", slan='ko', alan='en'):
    client = translate.TranslationServiceClient()
    location = "global"
    parent = "projects/" + project_id + "/locations/" + location

    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",
            "source_language_code": slan,
            "target_language_code": alan,
        }
    )
    for translation in response.translations:
        return translation.translated_text

def translate_line_glossary(text="text", slan='ko', alan='en', spec='Engineering'):
    glossary_id=spec + '_ko-en'
    #glossary_id='ko-en'
    client = translate.TranslationServiceClient()
    location = "us-central1"
    parent = "projects/" + project_id + "/locations/" + location

    glossary = client.glossary_path(project_id, location, glossary_id)
    glossary_config = translate.TranslateTextGlossaryConfig(glossary=glossary)

    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",
            "source_language_code": slan,
            "target_language_code": alan,
            "glossary_config": glossary_config,
        }
    )
    for translation in response.translations:
        return translation.translated_text
