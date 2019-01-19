from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient.http import MediaIoBaseDownload
import io
import argparse

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/drive.readonly'
FILE_ID_FILEPATH = 'google_drive_file_id.txt'

def main(file_path):
    """Downloads file from Google Drive and saves it in the argument filepath
    """
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    drive_service = build('drive', 'v3', http=creds.authorize(Http()))
    
    # File ID to download
    with open(FILE_ID_FILEPATH, 'r') as myfile:
        file_id = myfile.read().replace('\n', '')
    
    # Downloadning file
    request = drive_service.files().export_media(
            fileId=file_id, mimeType='text/csv')
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    # Saving file
    with io.open(file_path, 'wb') as f:
        fh.seek(0)
        f.write(fh.read())

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('output_filepath', type=str,
                    help='the filepath to save the downloaded file')
    args = parser.parse_args()
   
    main(args.output_filepath)



