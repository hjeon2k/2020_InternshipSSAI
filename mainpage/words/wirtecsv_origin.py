import csv
from google.cloud import storage
import shutil
import os
from google.cloud import translate_v3 as translate

ID = "english-subtitle-for-video"
bucket_name = 'snu_ensub_project'

def addword(spec, srt, arr):
    fname = 'glossary/' + spec + '_ko_en_g.csv'
    destination = fname
    with open('./'+fname, 'a', encoding='utf-8', newline='') as f:
        wr = csv.writer(f)
        wr.writerow([srt, arr])
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination)

    blob.upload_from_filename(fname)

def delword(spec, srt, arr):
    fname = 'glossary/'+ spec + '_ko_en_g.csv'
    tmp = '_' + spec + '_ko_en_g.csv'
    destination = fname

    shutil.copy(fname,tmp)
    tmpfr = open('./'+tmp, 'r', encoding='utf-8', newline='')
    tmpfw = open('./'+fname, 'w', encoding='utf-8', newline='')
    fr=csv.reader(tmpfr)
    fw=csv.writer(tmpfw)
    for row in fr:
        if (srt not in row[0]) or (arr not in row[1]):
            fw.writerow(row)
    tmpfr.close()
    tmpfw.close()
    os.remove('./'+ tmp)

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination)

    blob.upload_from_filename(fname)
    

def delete_glossary(
    project_id=ID, glossary_id='Engineering_ko-en', timeout=180,):

    client = translate.TranslationServiceClient()

    name = client.glossary_path(project_id, "us-central1", glossary_id)

    operation = client.delete_glossary(name=name)
    result = operation.result(timeout)
    print("Deleted: {}".format(result.name))


def create_glossary(
    project_id=ID,
    input_uri="gs://snu_ensub_project/glossary/Engineering_ko_en_g.csv",
    glossary_id="Engineering_ko-en",
    timeout=180,
):
    client = translate.TranslationServiceClient()

    # Supported language codes: https://cloud.google.com/translate/docs/languages
    source_lang_code = "ko"
    target_lang_code = "en"
    location = "us-central1"  # The location of the glossary

    name = client.glossary_path(project_id, location, glossary_id)
    language_codes_set = translate.types.Glossary.LanguageCodesSet(
        language_codes=[source_lang_code, target_lang_code]
    )

    gcs_source = translate.types.GcsSource(input_uri=input_uri)

    input_config = translate.types.GlossaryInputConfig(gcs_source=gcs_source)

    glossary = translate.types.Glossary(
        name=name, language_codes_set=language_codes_set, input_config=input_config
    )

    parent = f"projects/{project_id}/locations/{location}"
    # glossary is a custom dictionary Translation API uses
    # to translate the domain-specific terminology.
    operation = client.create_glossary(parent=parent, glossary=glossary)

    result = operation.result(timeout)
    print("Created: {}".format(result.name))
    print("Input Uri: {}".format(result.input_config.gcs_source.input_uri))

