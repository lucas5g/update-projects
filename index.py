
import os
import requests

from dotenv import load_dotenv
from sys import argv
from bs4 import BeautifulSoup as bs

load_dotenv()
# url = 'http://localhost:8000'
url = 'https://api.codificar.dev.br'

def login():
    body = {'email': os.getenv('CODS_USERNAME'), 'password': os.getenv('CODS_PASSWORD')}
    res = requests.post(url+'/login', json=body)
    auth = res.json()    
    # print(auth['accessToken'])
    return auth['accessToken']

def updateWeb(accessToken, project):
    Headers = {"Authorization": "Bearer "+accessToken}
    res = requests.get(url + "/clients/pendents/" + project, headers=Headers)
    command = res.json()
    webs = command['web']

    for web in webs:
        page = requests.get(web['link'])
        soup = bs(page.content, 'html.parser')

        if  project == 'marketplace':
            lastTagPage =  soup.find_all('strong')[1].text

        if project == 'servicos':
            lastTagPage = soup.find('strong').text

        if(lastTagPage == web['lastTag']):
            print(web['name'] + 'já foi atualizado na versão ' + lastTagPage)
        else:
            os.system('cd ' + web['pathAuto'] + ' && ' + web['auto'])
    return

def build(accessToken, project):
    Headers = {"Authorization": "Bearer "+accessToken}
    res = requests.get(url + "/clients/pendents/" + project, headers=Headers)
    command = res.json()
    clientsUser = command['androidUser']
    clientsProvider = command['androidProvider']
    for client in clientsUser:
        if os.path.exists(os.path.expanduser('~') + client['pathApp']):
            print(client['name'] + ' ' + client['lastTagUser'] + ' já foi buildado :)')
        else:
            # print(client['auto'], client['pathApp'])
            os.system('cd ' + client['pathAuto'] + ' && ' + client['auto'])

    for client in clientsProvider:
        if os.path.exists(os.path.expanduser('~') + client['pathApp']):
            print(client['name'] + ' ' + client['lastTagProvider'] + ' já foi buildado :)')
        else:
            # print(client['auto'], client['pathApp'])
            os.system('cd ' + client['pathAuto'] + ' && ' + client['auto'])

    

    os.system('node scripts/apps-upload.mjs ' + project)
    # os.system('node apps-upload.mjs ' + clients[0]['lastTagUser'])
    

accessToken = login()

# print(argv[1])
updateWeb(accessToken, argv[1])
build(accessToken, argv[1])
# build('servicos')
