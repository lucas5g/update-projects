import puppeteer from 'puppeteer'
import axios from 'axios'
import path from 'path'
import os from 'os'
import fs from 'fs'
import 'dotenv/config'
import { login } from './login.mjs'

const sleep = ms => new Promise(res => setTimeout(res, ms))


// const project = process.argv[2]
const project = process.argv[2]
const seconds = process.argv[3] || 5
let cookies = [];

(async () => {
  const url = 'https://api.codificar.dev.br'
  const { data } = await axios.post(`${url}/login`, {
    email: process.env.CODS_USERNAME,
    password: process.env.CODS_PASSWORD
  })

  const endpoint = `${url}/clients/pendents/${project}`
  const { data: command } = await axios(endpoint, {
    headers: {
      Authorization: `Bearer ${data.accessToken}`
    }
  })

  if (!project) {
    return console.log('Preencha a variável project')
  }
  // cookies = await loginGooglePlayConsole()
  cookies = login

  const clientsUser = command.androidUser
  const clientsProvider = command.androidProvider
  // return console.log(clients)
  clientsUser.forEach(async (client, index) => {
  
    if(client.name !== 'Seu Domingos') return
    if (!fs.existsSync(os.homedir + client.pathApp)) {
      console.log(`${client.name} - não foi buildado`)
      // cont++
      return
    }

    await sleep(seconds * 1000 * index)
    await uploadApp(client, client.lastTagUser)
  })
  return 
   clientsProvider.forEach(async (client, index) => {
    if (!fs.existsSync(os.homedir + client.pathApp)) {
      console.log(`${client.name} - não foi buildado`)
      return
    }

    await sleep(seconds * 1000 * index)
    await uploadApp(client, client.lastTagProvider)
  })


  return

})();

async function loginGooglePlayConsole() {

  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto('https://play.google.com/console/signup');

  await page.type('#identifierId', process.env.MOBILE_USERNAME)

  await page.$x('//*[@id="identifierNext"]/div/button/span')
    .then(res => res[0].click())

  await sleep(3000)
  // await page.waitForTimeout(2000)
  await page.waitForSelector('input[type="password"]')
  await page.type('input[type="password"]', process.env.MOBILE_PASSWORD)

  await sleep(1000)
  // await page.waitForTimeout(50000)
  await page.$x('//*[@id="passwordNext"]/div/button/div[3]')
    .then(el => el[0].click())

  await page.waitForNavigation()
  // await page.click('button > div')

  const cookies = await page.cookies()
  await browser.close()

  console.log(cookies)
  return cookies

}

async function uploadApp(client, lastTag) {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  await page.setViewport({
    width: 1200,
    height: 756
  })
  await page.setCookie(...cookies)


  await page.goto(client.urlUpload)
  let verifyVersion = ''
  try{
    verifyVersion = await page.waitForSelector('ul.list')
  }catch(error){
    console.log(`Confira de forma correta o link de upload do aplicativo ${client.name}.`)
    throw  new Error('Erro ao tentar autalizar app')
  }
  verifyVersion = await page.waitForSelector('ul.list')

  const fullTextVersion = await page.evaluate(el => el.textContent, verifyVersion)

  // return console.log({fullTextVersion, lastTag, test: fullTextVersion.includes(lastTag)})
  if (fullTextVersion.includes(lastTag)) {

    console.log(`${client.name} já foi atualizado nessa versão ;)`)
    await page.screenshot({ path: `${path.resolve()}/screenshots/${client.name.replace(' ', '-')}.png` })
    // timeWait = 12000 * index
    await browser.close()

    return
  }
  console.log(`${client.name} - Atualizando ...`)


  const buttonRelease = await page.waitForXPath(`//button[contains(., 'versão')]`)
  await buttonRelease.click()

  const buttonEnviar = await page.waitForXPath('(//span[text()="Enviar"])[1]')
  const [fileChooser] = await Promise.all([
    page.waitForFileChooser(),
    // page.click("[name='upload']"),
    await buttonEnviar.click()
  ]);

  // const appName = `${client.name}-user-${version}.${client.extensionAndroid}`

  const pathApp = `${os.homedir()}${client.pathApp}`
  // console.log(pathApp)
  // return
  await fileChooser.accept([pathApp]);

  await page.waitForXPath(`//div[text()="${client.app}"]`, {
    timeout: 0
  })
  await sleep(200)
  const buttonProximo = await page.waitForXPath(`(//div[text()="Próximo"])[1]`)
  await buttonProximo.click()
  
  const buttonSalvar = await page.waitForXPath(`(//div[text()="Salvar"])[1]`)
  await buttonSalvar.click()

  try {
    const buttonLancar = await page.waitForXPath(`//button/div[contains(., "Iniciar lançamento")]`)
    await buttonLancar.click()


    const confirmarLancamento = await page.waitForXPath(`//button[contains(., "Lançar")]`)
    await confirmarLancamento.click()
    console.log(`${client.name} - Atualizado :)`)
    await sleep(2000)
    await page.screenshot({ path: `${path.resolve()}/screenshots/${client.name}.png` })

  } catch (erro) {
    console.log(`${client.name} - Erro ao atulizar :(`)
    await page.screenshot({ path: `${path.resolve()}/screenshots/${client.name}-ERROR.png` })

  }


  // console.log(path.resolve())


  await browser.close()
}