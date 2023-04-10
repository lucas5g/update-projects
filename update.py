
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

    if len(webs) > 0:        
        print('Atualização web\n')

    for web in webs:
        if project == 'entregas':
            page = requests.get(web['link'] + '/version')
        else:
            page = requests.get(web['link'] + '/version')


        soup = bs(page.content, 'html.parser')

        if  project == 'marketplace':
            lastTagPage =  soup.find_all('strong')[1].text

        if project == 'servicos':
            lastTagPage = soup.find('strong').text

        if project == 'entregas':
            lastTagPage = soup.text 

        if(lastTagPage == web['lastTag']):
            print(web['name'] + ' já foi atualizado na versão ' + lastTagPage)
        else:
            os.system('cd ' + web['pathAuto'] + ' && ' + web['auto'])
    return

def builds(accessToken, project):
    print('Buildando apps')
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

    

    os.system('node upload.mjs ' + project)
    # os.system('node apps-upload.mjs ' + clients[0]['lastTagUser'])
    

def main():

    if len(argv) < 3:
        print('\nEscolha as opções: web, app ou all\n\nEx: python update ' + argv[1] + ' app. \n')
        return 
        
    project=argv[1]
    platform=argv[2]
    accessToken = login()

    if platform == 'web':
        updateWeb(accessToken, project)
        return
    if platform == 'app':
        builds(accessToken, project)
        return
    if platform == 'all':
        builds(accessToken, project)
        updateWeb(accessToken, project)
        return
    
    print('Escolha as opções web, app ou all\n')
    
main()