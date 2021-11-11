#api de google sheets
from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import regex as re
import pandas as pd
import random
import requests
import urllib.request
from IPython.display import Image


class Recomanador:
    
    def __init__(self):
        self.players = None
        self.dificultat = None
        self.dif_min = None
        self.dif_max = None
        self.temps = None
        
    
    def simple_questions(self):
        
        while True:
            valid = False
            while valid == False:
                self.players = input('quants jugadors sou? ')
                if self.players.isnumeric():
                    self.players = int(self.players)
                    valid = True
            break

        while True:
            valid = False
            while valid == False:
                print('quina profunditat de joc esperes? Facil/Mitja/Dificil \n')
                self.dificultat = input('introdueix F,M o D ')
                if self.dificultat.upper() == 'F':
                    self.dificultat = self.dificultat.upper()
                    valid = True
                elif self.dificultat.upper() == 'M':
                    self.dificultat = self.dificultat.upper()
                    valid = True
                elif self.dificultat.upper() == 'D':
                    self.dificultat = self.dificultat.upper()
                    valid = True
            break

        if self.dificultat == 'F':
            self.dif_min = 0
            self.dif_max = 2.5
        elif self.dificultat == 'M':
            self.dif_min = 2
            self.dif_max = 3.5
        else:
            self.dif_min = 3.5
            self.dif_max = 5    

        while True:
            valid = False
            while valid == False:
                print('quanta estona voleu jugar aproximadament? ')
                self.temps = input('introdueix temps en minuts ')
                if self.temps.isnumeric():
                    self.temps = int(self.temps)
                    valid = True
            break
    
    
    def simple_choice(self,data):
        queried_jocs = data.query('min <= @self.players & max >= @self.players & Duració <= (@self.temps + 15) & Duració >= (@self.temps - 15) & Profunditat >= @self.dif_min & Profunditat <= @self.dif_max ')
        while True:
            try:
                pick = random.choice(list(queried_jocs['Nom del joc']))
            except:
                print('no hi ha cap joc que cumpleixi els teus requisits\n')
                print("et recomanaré un joc a l'atzar\n")
                pick = random.choice(data['Nom del joc'])
            print(f' Perquè no jugueu a {pick} ?')
            try:
                image = requests.get(f'https://www.boardgamegeek.com/search/boardgame?q={pick}&nosession=1&showcount=20', headers = {'user-agent': '{Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36}'})
                object_pattern = re.compile('/boardgame/([0-9]*)/')
                object_id = object_pattern.findall(image.text)[0]
                resp = requests.get(f'https://api.geekdo.com/api/images?ajax=1&gallery=all&nosession=1&objectid={object_id}&objecttype=thing&pageid=1&showcount=36&size=thumb&sort=hot')
                image_url = resp.json()['images'][random.randint(0,10)]['imageurl_lg']
            except:
                print("No s'ha pogut trobar cap imatge del joc\n")
                image_url = None
            try:
                display(Image(image_url))
            except:
                print(f'una imatge de mostra aqui: {image_url}')

            agree = input("T'agrada aquesta opció? Y/N ")
            if agree.upper() == 'Y':
                break


class JocDB:
    
    def __init__(self):
        self.jocs_list = []
        self.jocs_df = None
        
    
    def apiCall(self):
        # obtenim la jocs de taula sheet desded l'Api de google

        # If modifying these scopes, delete the file token.json.
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

        # The ID and range of a sample spreadsheet.
        SAMPLE_SPREADSHEET_ID = '1Ixtc7aIaMxe8XeKQC9fAfBerZxYFsifS0sy0X2yJfB4'
        SAMPLE_RANGE_NAME = 'Jocs - Gerard and Cris!A1:O222'

        creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        print('retrieving boardgame collection from google sheets...')
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME
                                   ).execute()
        values = result.get('values', [])
        self.jocs_list = values
        
    def toDf(self):
        
        # creem a mà un Dataframe accedint a les llistes com si fosin columnes
        self.jocs_df = pd.DataFrame({'Nom del joc':[self.jocs_list[i][1] for i in range(3,len(self.jocs_list))],
                                     'Num. Jugadors':[self.jocs_list[i][2] for i in range(3,len(self.jocs_list))],
                                      'Gènere':[self.jocs_list[i][3] for i in range(3,len(self.jocs_list))],
                                      'Millor a 2?':[self.jocs_list[i][4] for i in range(3,len(self.jocs_list))],
                                      "Dificultat d'aprenentatge (sobre 5)":[self.jocs_list[i][5] for i in range(3,len(self.jocs_list))],
                                      'Profunditat':[float(self.jocs_list[i][6]) for i in range(3,len(self.jocs_list))],
                                      'Duració':[int(self.jocs_list[i][8]) for i in range(3,len(self.jocs_list))]
                                     })
        
        # continuem tractant el df
        minjoc = re.compile('([1-9]) a [1-9]')
        maxjoc = re.compile('[1-9] a ([1-9])')
        
        # creem noves columnes amb el min i el max
        for i in self.jocs_df['Num. Jugadors'].index:
            min_p = minjoc.findall(self.jocs_df.loc[i,'Num. Jugadors'])
            if len(min_p) > 0:
                min_p = int(min_p[0])
                self.jocs_df.loc[i,'min'] = min_p
            else:
                self.jocs_df.loc[i,'min'] = 0
            max_p = maxjoc.findall(self.jocs_df.loc[i,'Num. Jugadors'])
            if len(max_p) > 0:
                max_p = int(max_p[0])
                self.jocs_df.loc[i,'max'] = max_p
            else:
                self.jocs_df.loc[i,'max'] = 0
            
        #jocs només per un numero fix de persones
        for i in self.jocs_df['Num. Jugadors'].index:
            if self.jocs_df.loc[i,'min'] == 0:
                self.jocs_df.loc[i,'min'] = int(self.jocs_df.loc[i,'Num. Jugadors'])
                self.jocs_df.loc[i,'max'] = int(self.jocs_df.loc[i,'Num. Jugadors'])

def main():
    
    # creem la conexió?
    coleccio = JocDB()
    try:
        coleccio.apiCall()
    except:
        raise 'Conexió amb API ha fallat'
    
    # transformem a DataFrame
    coleccio.toDf()
    game_df = coleccio.jocs_df
    
    # creem el recomanador
    recom = Recomanador()
    recom.simple_questions()
    recom.simple_choice(game_df)

if __name__ == '__main__':
    main()