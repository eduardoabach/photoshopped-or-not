import configparser
import flickrapi
import os.path
import pandas as pd
import sys

def flickr_api(settings_path):
    settings = configparser.RawConfigParser()
    settings.read(settings_path)
    api_key = settings.get('Flickr', 'APIKey')
    secret = settings.get('Flickr', 'Secret')
    return flickrapi.FlickrAPI(api_key, secret, format='parsed-json')

def load_dataset(file_path, headers):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame(columns=headers)

ids_dataset_path = 'datasetFlickrID.txt'
urls_dataset_path = 'psed_images.csv'
file_headers = ['photo_id', 'url']
flickr = flickr_api('config.ini')
ids_dataset = load_dataset(ids_dataset_path, ['photo_id'])
urls_dataset = load_dataset(urls_dataset_path, file_headers)

next_row = 0
if len(urls_dataset) and len(ids_dataset):
    latest_photo_id = urls_dataset.iloc[-1]['photo_id']
    next_row = 1 + ids_dataset[ids_dataset['photo_id'] == latest_photo_id].index[0]
    if len(ids_dataset) == next_row:
        sys.exit()

for index, photo in ids_dataset[next_row:].iterrows():
    url = None
    photo_id = str(photo['photo_id'])
    try:
        available_sizes = flickr.photos.getSizes(photo_id=photo_id)
        url = available_sizes['sizes']['size'][-1]['source']
        print('+ %s' % photo_id)
    except flickrapi.exceptions.FlickrError as e:
        print('%s - %s' % (photo_id, e), file=sys.stderr)

    row = pd.Series([photo_id, url], index=file_headers)
    urls_dataset = urls_dataset.append(row, ignore_index=True)
    urls_dataset.to_csv(urls_dataset_path, encoding='utf-8', index=False)
