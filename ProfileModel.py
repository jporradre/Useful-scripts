from LogModel import LogModel
import traceback

class ProfileModel:


	def __init__(self,driver=None,timeout=30):
	
		from ConfigModel import ConfigModel
		cmod = ConfigModel()

		self.driver = driver
		self.timeout = timeout
		self.mLogger = LogModel()
		self.session_user = ""
		self.enckey = "ef4e4be2a7d847edd51910e7547a14bb"
		self.notifInterval = 100
		self.curGroup = ""
		self.curProfile = ""
		self.notifMail = "extractor@localhost" 

		try:
			notifint = cmod.getConfig("notif_interval")
			self.notifInterval = int(notifint[0].valor)
		except:
			pass

		try:
			notifmail = cmod.getConfig("notif_mail")
			self.notifMail = notifmail[0].valor
		except:
			pass 	
 		


	def getDriver(self):
		return self.driver



	def login(self,pUser,pPassword,pContinue=None):
		
		from selenium import webdriver
		from selenium.webdriver.common.keys import Keys		
		from selenium.common.exceptions import TimeoutException
		from selenium.common.exceptions import NoSuchElementException
		from selenium.webdriver.support.ui import WebDriverWait
		from selenium.webdriver.common.by import By
		from selenium.webdriver.support import expected_conditions as EC
		from selenium.webdriver.common.action_chains import ActionChains
		from random import uniform
		from ConfigModel import ConfigModel
		from sqlalchemy.exc import IntegrityError
		from RandomAction import RandomAction
		import os
		import time
		webpage = r"https://www.facebook.com"
		chromedriver = "./chromedriver"
	
		os.environ["webdriver.chrome.driver"] = chromedriver
		options = webdriver.ChromeOptions()
		options.add_argument("--disable-notifications")
		options.add_argument('--start-maximized')

		self.driver = webdriver.Chrome(chromedriver,chrome_options=options)

		self.driver.get(webpage)

		try:
			password = pPassword
			emailinput = self.driver.find_element_by_xpath("//input[@name='email']")
			hov = ActionChains(self.driver).move_to_element(emailinput)
			hov.perform()
			for l in pUser:
				emailinput.send_keys(l)
				time.sleep(uniform(0.05,0.1))
				

			self.mLogger.log("Se ingreso la direccion de mail para el login")

			passinput = self.driver.find_element_by_xpath("//input[@name='pass']")
			hov = ActionChains(self.driver).move_to_element(passinput)
			hov.perform()

			for l in password:
				passinput.send_keys(l)
				time.sleep(uniform(0.05,0.1))

			self.mLogger.log("Se ingreso el password para el login")
			time.sleep(1)

			xpathLoginBtnSpn = "//*[contains(@value,'Iniciar sesi')]"
			xpathLoginBtnEng = "//*[contains(@value,'Log In')]"
			loginBtn = None
			click = False
			i = 0
			
			while not click and i<5:
				try:
					loginBtn = self.driver.find_element_by_xpath(xpathLoginBtnSpn)
				except NoSuchElementException,TimeoutException:
						loginBtn = self.driver.find_element_by_xpath(xpathLoginBtnEng)
				
				if loginBtn is not None:
					loginBtn.click()
					click = True
				else:
					self.mLogger.log("No se encontro el boton de login.")

				i+=1


			if click:		
				self.mLogger.log("Se hizo clic en el boton de login")
			else:
				raise Exception("No se pudo hacer click finalmente en el boton de login")

			time.sleep(3)
			
			try:
				popupbadlogin = self.driver.find_element_by_xpath("//div[@class='_4rbf _53ij']")
				self.mLogger.log("Aparecio el popup de login erroneo")				
				if popupbadlogin is not None:
					return [{"retcode":4,"errmsg":"No se pudo loggear, pruebe ingresando nuevamente los datos de usuario"}]

			except NoSuchElementException as nse:
				self.mLogger.log("No aparecio el popup de login erroneo, por lo que se logueo bien")

			xpathUsername = '//*[@id="userNav"]//div[@dir="ltr"]'

			self.session_user = pUser

			self.mLogger.log("Se chequea que exista el nombre del usuario en el menu")
			wait = WebDriverWait(self.driver, 30)
			wait.until(EC.element_to_be_clickable((By.XPATH, xpathUsername)))
			self.mLogger.log("Se termina de chequear que exista el nombre del usuario en el menu")

			usernameElem = self.driver.find_element_by_xpath(xpathUsername)
			self.mLogger.log("Se encontro el nombre del usuario en el menu")
			username = usernameElem.text

			conf = ConfigModel()

			from AESCipher import AESCipher
			encpass = AESCipher(self.enckey).encrypt(password)
			
			conf.setConfigs([{"config":{"username":pUser}},{"config":{"password":encpass}}])


			rand = RandomAction(self.driver)
			rand.makeAction()

			return [{"retcode":0,"data":{"username":username}}]

		except TimeoutException as tex:
			raise Exception("La peticion demoro demasiado")
		except Exception as ex:
			trace=traceback.format_exc()
			raise Exception("Error no identificado en el login: "+trace)

		finally:
			if not pContinue:
				self.driver.quit()




	def getProfilesToExtract(self):
		from DTOS.ProfileIniDTO import ProfileIniDTO
		from Persistence import Persistence

		prof = ProfileIniDTO()
		per = Persistence()

		self.mLogger.log("Se van a cargar los perfiles iniciales a extraer")
		pret = per.select(ProfileIniDTO,[ProfileIniDTO.excluido,ProfileIniDTO.nombre,ProfileIniDTO.dato_extra,ProfileIniDTO.categoria,ProfileIniDTO.origen_dato,ProfileIniDTO.excluido_por,ProfileIniDTO.prioritario_por,ProfileIniDTO.perfil_url],ProfileIniDTO.excluido==0,ProfileIniDTO.prioridad.asc())
		self.mLogger.log("Se cargaron los perfiles iniciales a extraer: "+str(pret.count()))

		json={"data": []}
	
		for p in pret:
			json["data"].append([p.excluido,p.nombre,p.dato_extra,p.categoria,p.origen_dato,p.excluido_por,p.prioritario_por,p.perfil_url])
		per.close()
		return json



	def getProfilesExcluded(self):
		from DTOS.ProfileIniDTO import ProfileIniDTO
		from Persistence import Persistence

		prof = ProfileIniDTO()
		per = Persistence()

		self.mLogger.log("Se van a cargar los perfiles iniciales excluidos")
		pret = per.select(ProfileIniDTO,[ProfileIniDTO.excluido,ProfileIniDTO.nombre,ProfileIniDTO.dato_extra,ProfileIniDTO.categoria,ProfileIniDTO.origen_dato,ProfileIniDTO.excluido_por,ProfileIniDTO.prioritario_por,ProfileIniDTO.perfil_url],ProfileIniDTO.excluido==1,ProfileIniDTO.prioridad.asc())
		self.mLogger.log("Se cargaron los perfiles iniciales excluidos: "+str(pret.count()))

		json={"data": []}
	
		for p in pret:
			json["data"].append([p.excluido,p.nombre,p.dato_extra,p.categoria,p.origen_dato,p.excluido_por,p.prioritario_por,p.perfil_url])
		per.close()
		return json



	def getProfileResults(self):
		
		try:

			from DTOS.ProfileDTO import ProfileDTO
			from Persistence import Persistence

			self.mLogger.log("Se van a cargar los perfiles sin excluir desde la base de datos")
			per = Persistence()
			profs = per.select(ProfileDTO,None)
			self.mLogger.log("Se obtuvieron "+str(profs.count())+" perfiles desde la base de datos")
			
			json={"data": []}
	
			for p in profs:
				json["data"].append([p.nombre,p.categoria,p.ciudad,p.pais,p.cargo,p.empresa,p.categoria])
			per.close()
			return json


		except Exception as ex:
			trace=traceback.format_exc()
			raise Exception("Error no identificado en la obtencion de perfiles desde la base de datos: "+trace)





	def getEnterpriseProfiles(self):

		try:

			from ConfigModel import ConfigModel
			from selenium.common.exceptions import TimeoutException
			from selenium.common.exceptions import NoSuchElementException
			from selenium.webdriver.common.action_chains import ActionChains
			import time
			from random import uniform
			from DTOS.ProfileIniDTO import ProfileIniDTO
			from Persistence import Persistence
			from unidecode import unidecode
			from selenium.webdriver.common.by import By
			from selenium.webdriver.support import expected_conditions as EC
			from selenium.webdriver.support.ui import WebDriverWait

			xpathLinkPagesLiked = '//a[@href="/pages/?category=liked&ref=bookmarks"]/..'
			xpathLinkPagesLiked2 = '//a[@href="/pages/?category=your_pages&ref=bookmarks"]/..'


			cmod = ConfigModel()
			per = Persistence()


			
			try:
				username = cmod.getConfig("username")[0].valor
				encpass = cmod.getConfig("password")[0].valor
				from AESCipher import AESCipher
				password = AESCipher(self.enckey).decrypt(encpass)
				
			except IndexError:
				raise Exception("No se encontraron las credenciales, por favor cerrar sesion y volverse a loguear")			
	
			self.login(username,password,True)

			self.seeIfDelPag()

			time.sleep(uniform(3,4))

			try:
				linkPagesLiked = self.driver.find_element_by_xpath(xpathLinkPagesLiked)
			except NoSuchElementException, TimeoutException:
				linkPagesLiked = self.driver.find_element_by_xpath(xpathLinkPagesLiked2)

			hov = ActionChains(self.driver).move_to_element(linkPagesLiked)
			hov.perform()

			linkPagesLiked.click()
			time.sleep(10)

			xpathLinkInnerPagesLiked = "//a[@href='/pages/?category=liked']"


			linkInnerPagesLiked = self.driver.find_element_by_xpath(xpathLinkInnerPagesLiked)
			hov = ActionChains(self.driver).move_to_element(linkInnerPagesLiked)
			hov.perform()

			linkInnerPagesLiked.click()

			time.sleep(10)			

			xpathPagesLiked = '//div[@class="_4-u2 _5l2a stat_elem _5l2a stat_elem _4-u8"]'
			xpathEndFinding = '//span[@class="phl _50f8 _50f4"]'

			count = 0
			saw = False
			descend = False
			retry_count = 20
			height = 0
			newHeight = 0

			self.mLogger.log("Se van a recabar todos los perfiles de empresa")

			while not saw and count < retry_count:

				try:
					descend = False

					height = self.driver.execute_script('return document.body.scrollHeight')	
					self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')	
					time.sleep(uniform(5,7))
				
					newHeight = self.driver.execute_script('return document.body.scrollHeight')	
		
					if newHeight > height:
						count = 0
						descend = True

					end = self.driver.find_element_by_xpath(xpathEndFinding)
					saw = True
					self.mLogger.log("Se llego hasta el final de la pagina de perfiles de empresa")

				except NoSuchElementException:
					self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')	
					time.sleep(uniform(5,7))
				finally:
					if not descend:
						self.mLogger.log("Se suma un punto al contador. Valor "+str(count))
						count+=1
				
		
			self.mLogger.log("Termino la busqueda de perfiles de empresa con un contador de reintentos de scroll de  "+str(count)+ ". Los mismos van a ser guardados.") 
			pagesLiked = []
			try:	
				pagesLiked = self.driver.find_elements_by_xpath(xpathPagesLiked)
				strOK = "Se extrajeron "+str(len(pagesLiked))+" perfiles de empresa"
				self.mLogger.log(strOK)
				
			except NoSuchElementException:
				strEmptyOK = "No se encontraron perfiles de empresa para extraer"
				self.mLogger.log(strEmptyOK)
				return [{"retcode":0,"data":strEmptyOK}]

			pdtos = []
			

			for pl in pagesLiked:
				v_foto_url = pl.find_element_by_xpath(".//img[contains(@class,'_s0 _4ooo')]").get_attribute("src")
				v_nombre = pl.find_element_by_xpath(".//a[@class='_5l2d']").text
				v_perfil_url = pl.find_element_by_xpath(".//a[@class='_5l2d']").get_attribute("href").split("?")[0]
				v_dato_extra = pl.find_element_by_xpath(".//div[@class='fsm fwn fcg']").text
				v_categoria = "Empresa"
				v_origen_dato = "Paginas"
				v_prioridad = 3

				pdto = ProfileIniDTO(nombre=unidecode(self.nvl(v_nombre)),dato_extra=unidecode(self.nvl(v_dato_extra)),foto_url=unidecode(self.nvl(v_foto_url)),perfil_url=unidecode(self.nvl(v_perfil_url)),categoria=unidecode(self.nvl(v_categoria)),origen_dato=unidecode(self.nvl(v_origen_dato)),prioridad=v_prioridad,excluido=False)				
				pdtos.append(pdto)


			per.bulkSave(pdtos)

			self.mLogger.log("Se grabaron todos los perfiles de empresa")

			self.updateExcluded()
			self.updatePriority()
	
			strEndOK = "Termino la extraccion de todos los perfiles de empresa"
			self.mLogger.log(strEndOK)

			return [{"retcode":0,"data":strEndOK}]


		except TimeoutException as tex:
			raise Exception("La peticion demoro demasiado")
		except Exception as ex:
			trace=traceback.format_exc()
			raise Exception("Error no identificado en la extraccion de perfiles de empresa: "+trace)

		finally:
			if self.driver is not None:
				self.driver.quit()



	
	def getFriendsProfiles(self):
			
		try:

			from ConfigModel import ConfigModel
			from selenium.common.exceptions import TimeoutException
			from selenium.common.exceptions import NoSuchElementException
			from selenium.webdriver.common.action_chains import ActionChains
			import time
			from random import uniform
			from DTOS.ProfileIniDTO import ProfileIniDTO
			from Persistence import Persistence
			from unidecode import unidecode

			xpathLinkGroups = '//a[@href="/bookmarks/lists/"]/..'

			cmod = ConfigModel()
			per = Persistence()

			
			try:
				username = cmod.getConfig("username")[0].valor
				encpass = cmod.getConfig("password")[0].valor
				from AESCipher import AESCipher
				password = AESCipher(self.enckey).decrypt(encpass)
			except IndexError:
				raise Exception("No se encontraron las credenciales, por favor cerrar sesion y volverse a loguear")			
	
			self.login(username,password,True)
	
			self.seeIfDelPerf()

			linkGroups = self.driver.find_element_by_xpath(xpathLinkGroups)
			hov = ActionChains(self.driver).move_to_element(linkGroups)
			hov.perform()

			linkGroups.click()
			time.sleep(10)

			xpathLinkAllFriends = '//a[@class="_42ft _4jy0 _4jy3 _517h _51sy"]'
			linkAllFriends = self.driver.find_elements_by_xpath(xpathLinkAllFriends)[1]
			hov = ActionChains(self.driver).move_to_element(linkAllFriends)
			hov.perform()

			linkAllFriends.click()
			time.sleep(10)

			xpathFriends = "//li[@class='_698']"
			xpathEndFinding = "//div[@class='mbm _5vf sectionHeader _4khu']"

			count = 0
			saw = False
			descend = False
			retry_count = 20

			self.mLogger.log("Se van a recabar todos los perfiles iniciales de amigos")
			while not saw and count < retry_count:

				try:
					descend = False

					height = self.driver.execute_script('return document.body.scrollHeight')	
					self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')	
					time.sleep(uniform(1,5))
			
					newHeight = self.driver.execute_script('return document.body.scrollHeight')	
		
					if newHeight > height:
						count = 0
						descend = True

					end = self.driver.find_element_by_xpath(xpathEndFinding)
					hov = ActionChains(self.driver).move_to_element(end)
					hov.perform()

					saw = True
					self.mLogger.log("Se llego hasta el final de la pagina de perfiles iniciales de amigos")

				except NoSuchElementException:
					self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')	
					time.sleep(uniform(1,5))
				finally:
					if not descend:
						count+=1
			
		
			self.mLogger.log("Termino la busqueda de perfiles iniciales de amigos con un contador de reintentos de scroll de "+str(count)+ ". Los mismos van a ser guardados.") 
			friends = []
			try:	
				friends = self.driver.find_elements_by_xpath(xpathFriends)
				strOK = "Se encontraron "+str(len(friends))+" perfiles iniciales de amigos"
				self.mLogger.log(strOK)
			
			except NoSuchElementException:
				strEmptyOK = "No se encontraron perfiles iniciales de amigos para extraer"
				self.mLogger.log(strEmptyOK)
				return [{"retcode":0,"data":strEmptyOK}]

			pdtos = []
			
			try:
				self.driver.execute_script('document.getElementById("pagelet_dock").remove();')	
			except:
				pass

			for f in friends:

				v_nombre = f.find_element_by_xpath(".//div[@class='fsl fwb fcb']/a").text

				v_perfil_url = f.find_element_by_xpath(".//div[@class='fsl fwb fcb']/a").get_attribute("href").split("?")[0]
				
				if "/friends" in v_perfil_url :
					self.mLogger.log("Se saltea la extraccion del perfil "+unidecode(v_nombre)+" porque esta dado de baja")					
					continue

				v_foto_url = None
				try:
					v_foto_url = f.find_element_by_xpath(".//img[@class='_s0 _rv img']").get_attribute("src")
				except NoSuchElementException:
					pass
					
			
				v_dato_extra = None
				try:
					v_dato_extra = f.find_element_by_xpath(".//a[@class='_39g5']").text
				except NoSuchElementException:
					try:
						v_dato_extra = f.find_element_by_xpath(".//div[@class='fsm fwn fcg']").text
					except NoSuchElementException:
						v_dato_extra = None

				v_categoria = "Persona"
				v_origen_dato = "Amigos"
				v_prioridad = 3
				v_excluido = False

				pdto = ProfileIniDTO(nombre=unidecode(self.nvl(v_nombre)),dato_extra=unidecode(self.nvl(v_dato_extra)),foto_url=unidecode(self.nvl(v_foto_url)),perfil_url=unidecode(self.nvl(v_perfil_url)),categoria=unidecode(self.nvl(v_categoria)),origen_dato=unidecode(self.nvl(v_origen_dato)),prioridad=v_prioridad,excluido=v_excluido)
				self.mLogger.log(pdto.to_string())			
				pdtos.append(pdto)

			self.mLogger.log("Se van a grabar "+str(len(pdtos))+" perfiles iniciales de amigos")

			i = per.bulkSave(pdtos)

			self.mLogger.log("Quedaron grabados todos los perfiles iniciales de amigos. Cantidad final: "+str(i))

			self.updateExcluded()
			self.updatePriority()
	
			strEndOK = "Termino la extraccion de los perfiles iniciales de amigos"
			self.mLogger.log(strEndOK)

			return [{"retcode":0,"data":strEndOK}]


		except TimeoutException as tex:
			raise Exception("La peticion demoro demasiado")
		except Exception as ex:
			trace=traceback.format_exc()
			raise Exception("Error no identificado en la extraccion de perfiles iniciales de amigos: "+trace)

		finally:
			if self.driver is not None:
				self.driver.quit()





	def getProfilesIniDB(self):
		try:

			from DTOS.ProfileIniDTO import ProfileIniDTO
			from Persistence import Persistence

			self.mLogger.log("Se van a cargar los perfiles iniciales sin excluir desde la base de datos")
			per = Persistence()
			profs = per.select(ProfileIniDTO,None,ProfileIniDTO.excluido == 0)
			self.mLogger.log("Se obtuvieron "+str(profs.count())+" perfiles iniciales desde la base de datos")
			per.close()
			return profs

		except Exception as ex:
			trace=traceback.format_exc()
			raise Exception("Error no identificado en la obtencion de perfiles iniciales desde la base de datos: "+trace)





	def seeIfUpdatePrioProfile(self,pProfile):
		try:		
			from DTOS.ProfileDTO import ProfileDTO
			from Persistence import Persistence
			from PriorityModel import PriorityModel
			from unidecode import unidecode

			prof = pProfile
			per = Persistence()		
			self.mLogger.log("Se revisa si se debe actualizar la prioridad")
		
			prim = PriorityModel()
			prios = prim.getPriorities()

			for pri in prios["data"]:
				if pri[0].upper() in self.snvl(prof.nombre).upper() or pri[0].upper() in self.snvl(prof.datos_extras_1).upper() or pri[0].upper() in self.snvl(prof.datos_extras_2).upper() or pri[0].upper() in self.snvl(prof.datos_extras_3).upper() or pri[0].upper() in self.snvl(prof.perfil_url).upper() or pri[0].upper() in self.snvl(prof.categoria).upper() or pri[0].upper() in self.snvl(prof.intro).upper() or pri[0].upper() in self.snvl(prof.acerca_de).upper() or pri[0].upper() in self.snvl(prof.info_general).upper() or pri[0].upper() in self.snvl(prof.tipo_empresa).upper() or pri[0].upper() in self.snvl(prof.empresa).upper() or pri[0].upper() in self.snvl(prof.cargo).upper() or pri[0].upper() in self.snvl(prof.estudios).upper():

					per.update(ProfileDTO,{"prioridad":"0","prioritario_por":pri[0]},ProfileDTO.perfil_url == prof.perfil_url)
	

			strEndOK = "Termino de actualizar la prioridad"
			self.mLogger.log(strEndOK)
			return [{"retcode":0,"data":strEndOK}]

		except Exception as ex:
			trace=traceback.format_exc()
			raise Exception("Error no identificado en la actualizacion de prioridad de perfil: "+trace)






	def updatePriority(self):
		try:		
			from DTOS.ProfileIniDTO import ProfileIniDTO
			from Persistence import Persistence
			from PriorityModel import PriorityModel
			from unidecode import unidecode

			per = Persistence()		
			self.mLogger.log("Se actualiza la prioridad de todos los perfiles a valor 3")
			per.update(ProfileIniDTO,{"prioridad":3,"prioritario_por":None},ProfileIniDTO.excluido == 0)
			self.mLogger.log("Se actualizo la prioridad de todos a 3. Se va a actualizar la prioridad segun los terminos indicados.")
		
			prim = PriorityModel()
			prios = prim.getPriorities()
			profs = self.getProfilesIniDB()

			for prof in profs:
				for pri in prios["data"]:
					if pri[0].upper() in self.snvl(prof.nombre).upper() or pri[0].upper() in self.snvl(prof.dato_extra).upper() or pri[0].upper() in self.snvl(prof.perfil_url).upper() or pri[0].upper() in self.snvl(prof.categoria).upper() or pri[0].upper() in self.snvl(prof.origen_dato).upper():
						per.update(ProfileIniDTO,{"prioridad":0,"prioritario_por":pri[0]},ProfileIniDTO.perfil_url == prof.perfil_url)
	
			strEndOK = "Termino de actualizar las prioridades"
			self.mLogger.log(strEndOK)
			return [{"retcode":0,"data":strEndOK}]

		except Exception as ex:
			trace=traceback.format_exc()
			raise Exception("Error no identificado en la actualizacion de prioridad de perfiles iniciales de amigos: "+trace)

			
	

	def updateExcluded(self):
		try:		
			from DTOS.ProfileIniDTO import ProfileIniDTO
			from Persistence import Persistence
			from ExclusionModel import ExclusionModel
			from unidecode import unidecode
			

			per = Persistence()		
			self.mLogger.log("Se realiza el filtrado por exclusiones")

			excm = ExclusionModel()
			excs = excm.getExclusions()
			profs = self.getProfilesIniDB()
			
			for prof in profs:
				for exc in excs["data"]:
					if exc[0].upper() in self.snvl(prof.nombre).upper() or exc[0].upper() in self.snvl(prof.dato_extra).upper() or exc[0].upper() in self.snvl(prof.perfil_url).upper() or exc[0].upper() in self.snvl(prof.categoria).upper() or exc[0].upper() in self.snvl(prof.origen_dato).upper():
						per.update(ProfileIniDTO,{"excluido":1,"excluido_por":"Exclusion por termino :"+exc[0]},ProfileIniDTO.perfil_url == prof.perfil_url)

			strEndOK = "Termino de realizar el filtrado por exclusiones"
			self.mLogger.log(strEndOK)
			return [{"retcode":0,"data":strEndOK}]

		except Exception as ex:
			trace=traceback.format_exc()
			raise Exception("Error no identificado en el filtrado por exclusiones: "+trace)






	def seeIfExcludeProfile(self,pProfile):
		try:		
			from DTOS.ProfileDTO import ProfileDTO
			from Persistence import Persistence
			from ExclusionModel import ExclusionModel
			from unidecode import unidecode
			
			prof = pProfile
			per = Persistence()		
			self.mLogger.log("Se revisa si se debe filtrar por exclusiones un perfil")

			excm = ExclusionModel()
			excs = excm.getExclusions()

			
			for exc in excs["data"]:
				if exc[0].upper() in self.snvl(prof.nombre).upper() or exc[0].upper() in self.snvl(prof.datos_extras_1).upper() or exc[0].upper() in self.snvl(prof.datos_extras_2).upper() or exc[0].upper() in self.snvl(prof.datos_extras_3).upper() or exc[0].upper() in self.snvl(prof.perfil_url).upper() or exc[0].upper() in self.snvl(prof.categoria).upper() or exc[0].upper() in self.snvl(prof.intro).upper() or exc[0].upper() in self.snvl(prof.acerca_de).upper() or exc[0].upper() in self.snvl(prof.info_general).upper() or exc[0].upper() in self.snvl(prof.tipo_empresa).upper() or exc[0].upper() in self.snvl(prof.empresa).upper() or exc[0].upper() in self.snvl(prof.cargo).upper() or exc[0].upper() in self.snvl(prof.estudios).upper():

					per.update(ProfileDTO,{"excluir_registro":True,"motivo_exclusion":"Exclusion por termino :"+exc[0]},ProfileDTO.perfil_url == prof.perfil_url)
					self.mLogger.log("Se excluyo el perfil "+prof.perfil_url)


			strEndOK = "Termino de revisar si se debe filtrar por exclusiones un perfil"
			self.mLogger.log(strEndOK)
			return [{"retcode":0,"data":strEndOK}]

		except Exception as ex:
			trace=traceback.format_exc()
			raise Exception("Error no identificado en el filtrado por exclusiones de un perfil: "+trace)






	def updateManualExcluded(self,pExcl):
		try:		
			from DTOS.ProfileIniDTO import ProfileIniDTO
			from Persistence import Persistence
			
			per = Persistence()		
			self.mLogger.log("Se realiza el filtrado manual por exclusiones")
		
			exclArr = []
			for excl in pExcl:
				exclArr.append(excl["perfil_url"])


			self.mLogger.log("Se van a setear los perfiles excluidos")
			per.update(ProfileIniDTO,{"excluido":1,"excluido_por":"Manual"},ProfileIniDTO.perfil_url.in_(exclArr))
			self.mLogger.log("Se van a setear los perfiles no excluidos")
			per.update(ProfileIniDTO,{"excluido":0,"excluido_por":None},~ProfileIniDTO.perfil_url.in_(exclArr))


			strEndOK = "Termino de realizar el filtrado manual por exclusiones"
			self.mLogger.log(strEndOK)
			return [{"retcode":0,"data":strEndOK}]

		except Exception as ex:
			trace=traceback.format_exc()
			raise Exception("Error no identificado en el filtrado manual por exclusiones: "+trace)




	def startExtractGroupPersonProfiles(self):
		from Mail import Mail
		from ConfigModel import ConfigModel

		cmod = ConfigModel()

		try:

			self.seeIfDelExcl()

			self.extractGroupPersonProfiles()

			try:
				pause = cmod.getConfig("pause_extr")[0].valor

				if pause == "1":
					strEnd = "Se pauso manualmente la extraccion de los perfiles individuales de miembros de grupos. Se retomara la extraccion en el grupo '"+self.curGroup+"' y el perfil '"+self.curProfile+"'"

					try:
						from ConfigModel import ConfigModel
						cmod = ConfigModel()
						cmod.setConfigs([{"config":{"retom_gru":self.curGroup}},{"config":{"retom_perf":self.curProfile}}])
					except:
						trace=traceback.format_exc()
						self.mLogger.log("Hubo un error al intentar grabar la configuracion para retomar la extraccion: "+trace)

				else:
					strEnd = "Termino correctamente la extraccion de los perfiles individuales de miembros de grupos"

			except IndexError:
				strEnd = "Termino correctamente la extraccion de los perfiles individuales de miembros de grupos"	

			cmod.setConfigs([{"config":{"pause_extr":"0"}}])

			retcode=0

		except Exception as ex:
			trace=traceback.format_exc()
			strEnd = trace + "\n Retomar extraccion en el grupo '"+self.curGroup+"' y el perfil '"+self.curProfile+"'"
			retcode=1
			try:
				from ConfigModel import ConfigModel
				cmod = ConfigModel()
				cmod.setConfigs([{"config":{"retom_gru":self.curGroup}},{"config":{"retom_perf":self.curProfile}}])
			except:
				trace=traceback.format_exc()
				self.mLogger.log("Hubo un error al intentar grabar la configuracion para retomar la extraccion. Se va a recomenzar la extraccion desde el error: "+trace)

		finally:
			try:
				self.mLogger.log(strEnd)

				from Mail import Mail
				m = Mail()

				fr="alertasrimbos@softdor.com"
				to=[self.notifMail]
				sub="Notificacion de extraccion de Facebook"
				body=strEnd

				m.sendMail(fr,to,sub,body)

				try:
					if self.driver is not None:
						self.driver.quit()
				except:
					pass

			except:
				pass

			if retcode == 0:
				return [{"retcode":retcode,"data":strEnd}]
			else:
				return self.retryExtractPersonProfiles("Group")





	def startExtractIndivPersonProfiles(self):
		from Mail import Mail
		from ConfigModel import ConfigModel

		cmod = ConfigModel()

		try:

			self.seeIfDelExcl()

			self.extractIndivPersonProfiles()

			try:
				pause = cmod.getConfig("pause_extr")[0].valor

				if pause == "1":
					strEnd = "Se pauso manualmente la extraccion de los perfiles individuales de amigos. Se retomara la extraccion en el perfil '"+self.curProfile+"'"

					try:
						from ConfigModel import ConfigModel
						cmod = ConfigModel()
						cmod.setConfigs([{"config":{"retom_gru":self.curGroup}},{"config":{"retom_perf":self.curProfile}}])
					except:
						trace=traceback.format_exc()
						self.mLogger.log("Hubo un error al intentar grabar la configuracion para retomar la extraccion: "+trace)

				else:
					strEnd = "Termino correctamente la extraccion de los perfiles individuales de amigos"

			except IndexError:
				strEnd = "Termino correctamente la extraccion de los perfiles individuales de amigos"	

			cmod.setConfigs([{"config":{"pause_extr":"0"}}])

			retcode=0

		except Exception as ex:
			trace=traceback.format_exc()
			strEnd = trace + "\n Retomar extraccion en el perfil '"+self.curProfile+"'"
			retcode=1
			try:
				from ConfigModel import ConfigModel
				cmod = ConfigModel()
				cmod.setConfigs([{"config":{"retom_gru":""}},{"config":{"retom_perf":self.curProfile}}])
			except:
				trace=traceback.format_exc()
				self.mLogger.log("Hubo un error al intentar grabar la configuracion para retomar la extraccion. Se va a recomenzar la extraccion desde el error: "+trace)

		finally:
			try:
				self.mLogger.log(strEnd)

				from Mail import Mail
				m = Mail()

				fr="alertasrimbos@softdor.com"
				to=[self.notifMail]
				sub="Notificacion de extraccion de Facebook"
				body=strEnd

				m.sendMail(fr,to,sub,body)

				try:
					if self.driver is not None:
						self.driver.quit()
				except:
					pass

			except:
				pass

			if retcode == 0:
				return [{"retcode":retcode,"data":strEnd}]
			else:
				return self.retryExtractPersonProfiles("Indiv")



	

	def retryExtractPersonProfiles(self,pProcess):

		from ConfigModel import ConfigModel		
		from subprocess import check_output, CalledProcessError

		self.mLogger.log("Se va a reintentar la extraccion luego de un evento irrecuperable bajando Chrome previamente.")

		tret = [1,"Error desconocido"]

		try:
			out = check_output(["pkill chromedriver"],shell=True)
			tret = 0, out
		except CalledProcessError as e:
			tret = e.returncode, e.output


		if tret[0] in [0,1]:

			self.mLogger.log("Se bajo correctamente Chrome, por lo que se loggea y retoma la extraccion.")

			if pProcess == "Group":
				return self.startExtractGroupPersonProfiles()
			else:
				return self.startExtractIndivPersonProfiles()

		else:
			msgErr= "Error al intentar bajar Chrome y reintentar el proceso. Por favor reinicie manualmente la extraccion. Error: "+str(tret[0])+" : "+tret[1]
			self.mLogger.log(msgErr)

			try:

				from Mail import Mail
				m = Mail()

				fr="alertasrimbos@softdor.com"
				to=[self.notifMail]
				sub="Notificacion de extraccion de Facebook"
				body=msgErr

				m.sendMail(fr,to,sub,body)

			except:
				pass

			return [{"retcode":2,"data":msgErr}]

	



	def extractIndivPersonProfiles(self):
		
		from Persistence import Persistence
		from DTOS.ProfileIniDTO import ProfileIniDTO
		from DTOS.ProfileErrorDTO import ProfileErrorDTO
		from DTOS.ProfileDTO import ProfileDTO
		from ConfigModel import ConfigModel
		from datetime import datetime
		import time
		from random import uniform
		from selenium.common.exceptions import TimeoutException
		from selenium.common.exceptions import NoSuchElementException
		from selenium.common.exceptions import WebDriverException
		from selenium.common.exceptions import ElementNotVisibleException
		from unidecode import unidecode

		per = Persistence()
		cmod = ConfigModel()

		try:

			try:
				pause = cmod.getConfig("pause_extr")[0].valor

				if pause == "1":
					self.mLogger.log("Se pausa la extraccion a pedido del usuario.")
					return

			except IndexError:
				self.mLogger.log("No se encontro la configuracion de pausa, por lo que se continua extrayendo")		

			self.seeIfDelExcl()

			self.updateExcluded()
			self.updatePriority()
		
			self.mLogger.log("Va a comenzar la extraccion de perfiles individuales")
			self.mLogger.log("Se van a cargar los perfiles iniciales individuales")
			pret = per.select(ProfileIniDTO,None,ProfileIniDTO.categoria == "Persona",ProfileIniDTO.prioridad.asc())

			try:
				cantMiemInd = cmod.getConfig("val_extr_perf_ind")[0].valor
			except IndexError:
				cantMiemInd = None

			if cantMiemInd is None or cantMiemInd == '' or cantMiemInd == "0":
				cantMiemInd = pret.count()-1
			else:
				cantMiemInd = int(cantMiemInd)

			try:
				timeout = cmod.getConfig("val_timeout_ext")[0].valor
			except IndexError:
				timeout = None

			if timeout is None or timeout == '':
				timeout = 0
			else:
				timeout = int(timeout)

			try:
				extr_entre_tout = cmod.getConfig("val_cant_extr_antes_timeout")[0].valor
			except IndexError:
				extr_entre_tout = None

			if extr_entre_tout is None or extr_entre_tout == '':
				extr_entre_tout = 1
			else:
				extr_entre_tout = int(extr_entre_tout)

			self.mLogger.log("Se cargaron "+str(pret.count())+" perfiles iniciales individuales. Se iteran para extraer "+str(cantMiemInd)+" perfiles")

			i = 0

			try:
				retom_perf = cmod.getConfig("retom_perf")[0].valor
			except IndexError:
				retom_perf = None	

			retom_flag = False

			if not (retom_perf is None or retom_perf == ''):
	 			retom_flag = True
			
		
			try:
				username = cmod.getConfig("username")[0].valor
				encpass = cmod.getConfig("password")[0].valor
				from AESCipher import AESCipher
				password = AESCipher(self.enckey).decrypt(encpass)
				
			except IndexError:
				raise Exception("No se encontraron las credenciales, por favor cerrar sesion y volverse a loguear")			
	
			self.login(username,password,True)


			origen = "Persona"
			totOK = 0
			totERR = 0

			for p in pret[0:int(cantMiemInd)-1]:

				try:
					pause = cmod.getConfig("pause_extr")[0].valor

					if pause == "1":
						self.mLogger.log("Se pausa la extraccion a pedido del usuario.")
						break

				except IndexError:
					self.mLogger.log("No se encontro la configuracion de pausa, por lo que se continua extrayendo")			


				if retom_flag:
					if p.nombre.upper() == retom_perf.upper():
						retom_flag = False
						self.mLogger.log("Se va a retomar la extraccion en el perfil "+p.nombre)
					else:
						continue


				if p.excluido:
					self.mLogger.log("No se extrae el perfil de "+p.nombre+" ya que fue excluido")
					continue


				per2 = Persistence()

				try:
					psel = per2.select(ProfileDTO,None,ProfileDTO.perfil_url == p.perfil_url)
						
					if psel.count() > 0:						
						self.mLogger.log("Se omite la extraccion de "+p.nombre+" ya que ya fue extraido")
						continue
					else:
						self.mLogger.log("No se encontro el perfil de "+p.nombre+", por lo que pasa a extraerse")
				except:
					trace=traceback.format_exc()
					self.mLogger.log("Ocurrio un error al verificar la existencia del perfil: "+trace)
					continue
				finally:
					per2.close()


				try:
					self.driver.get(p.perfil_url)
					time.sleep(uniform(5,7))
					self.extractPersonProfile(p.nombre,p.perfil_url,origen)
					totOK +=1
				except (TimeoutException, NoSuchElementException, WebDriverException,ElementNotVisibleException):
					try:
						trace=traceback.format_exc()
						self.mLogger.log("Hubo un problema (1) con la extraccion del perfil "+p.perfil_url+" : "+trace)

						if "WebDriverException" in trace and not "clickable" in trace:
							raise Exception("Error fatal en la extraccion del perfil: "+trace)

						self.extractPersonProfile(p.nombre,p.perfil_url,origen,True)
						totOK +=1
					except (TimeoutException, NoSuchElementException, WebDriverException,ElementNotVisibleException):
						try:
							trace=traceback.format_exc()
							self.mLogger.log("Hubo un problema (2) con la extraccion del perfil "+p.perfil_url+" : "+trace)

							if "WebDriverException" in trace and not "clickable" in trace:
								raise Exception("Error fatal en la extraccion del perfil: "+trace)

							self.extractPersonProfile(p.nombre,p.perfil_url,origen,True)
							totOK +=1
						except (TimeoutException, NoSuchElementException, WebDriverException,ElementNotVisibleException):
							totERR +=1
							trace=traceback.format_exc()
							self.mLogger.log("Hubo un problema (3) con la extraccion del perfil "+p.perfil_url+" y no se pudo extraer finalmente :"+trace)

							if "WebDriverException" in trace and not "clickable" in trace:
								raise Exception("Error fatal en la extraccion del perfil: "+trace)

							try:
							
								dt = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S');
								p = ProfileErrorDTO(nombre=p.nombre,perfil_url=p.perfil_url,fecha=dt,error=trace,sesionfb_origen=self.session_user,categoria="Persona")
								per.merge(p)

								self.mLogger.log("Se grabo como perfil con error el perfil de "+p.nombre)

							except (TimeoutException, NoSuchElementException, WebDriverException,ElementNotVisibleException):
								trace=traceback.format_exc()
								self.mLogger.log("Error en el loggeo de errores de extraccion de perfiles individuales: "+trace)

								if "WebDriverException" in trace and not "clickable" in trace:
									raise Exception("Error fatal en la extraccion del perfil: "+trace)
	


				if totOK != 0 and (totOK % self.notifInterval) == 0:
			
					try:
						strInter = "Se van extrayendo "+str(totOK)+" perfiles individuales"
						self.mLogger.log(strInter)

						from Mail import Mail
						m = Mail()

						fr="alertasrimbos@softdor.com"
						to=[self.notifMail]
						sub="Notificacion de extraccion de Facebook"
						body=strInter

						m.sendMail(fr,to,sub,body)
					except:
						pass


				if extr_entre_tout != 0 and i % extr_entre_tout == 0:
					self.mLogger.log("Se va a hacer un timeout de "+str(timeout)+" segundos")
					time.sleep(timeout)


				i+=1


			strEndOK = "Se terminaron de extraer los perfiles individuales con un total de "+str(totOK)+" perfiles extraidos y "+str(totERR)+" perfiles con error"

			try:
				self.mLogger.log(strEndOK)

				from Mail import Mail
				m = Mail()

				fr="alertasrimbos@softdor.com"
				to=[self.notifMail]
				sub="Notificacion de extraccion de Facebook"
				body=strEndOK

				m.sendMail(fr,to,sub,body)
			except:
				pass

			return [{"retcode":0,"data":strEndOK}]

		except:
			raise
		finally:
			per.close()




	def extractPersonProfile(self,pNombre,pPerfilURL,pOrigenDato,pReload=False):
		import time
		from selenium.common.exceptions import NoSuchElementException
		from selenium.webdriver.common.action_chains import ActionChains
		from selenium.webdriver.common.keys import Keys	
		from unidecode import unidecode
		from random import uniform
		from DTOS.ProfileDTO import ProfileDTO
		from DTOS.ProfileIniDTO import ProfileIniDTO
		from Persistence import Persistence
 		from datetime import datetime
		from RandomAction import RandomAction
		from selenium.webdriver.common.by import By
		from selenium.webdriver.support import expected_conditions as EC
		from selenium.webdriver.support.ui import WebDriverWait
		from ConfigModel import ConfigModel

		self.mLogger.log("Se comienza a extraer el perfil de "+pNombre)

		self.curProfile = pNombre

		xpathInfoLink = "(//a[@class='_6-6'])[1]"
		xpathFormEmp = "//a[@data-testid='nav_edu_work']"
		xpathAbout = "//a[@data-testid='nav_about']"
		xpathSpanPres = "(//span[@class='_50f5 _5kx5'])[1]"

		xpathFotoCoverURLImg = "//img[@class='coverPhotoImg photo img']"
		xpathFotoCoverURLVideo = "//video[@class='_ox1 _blh']"
		xpathFotoURL = "//div[@class='photoContainer']//a//img"
		xpathNick = "//span[@id='fb-timeline-cover-name']//span"
		xpathNombre = "//a[@class='_2nlw']/span"
		xpathDireccion = "//i[@class='img sp_qAzfdP9HhqM sx_25a073']/../../..//ul[@class='uiList _4kg']/li"
		xpathOtrasRedes = "//img[contains(@src,'p80lW4Ut7OF.png')]/../../../div[@class='_4bl9 _2pis _2dbl']/span/div/span[not(contains(@class,'accessible_elem'))]" 
		xpathSitiosWeb = "//img[contains(@src,'dmaB0KwVoXI.png')]/../../../div[@class='_4bl9 _2pis _2dbl']/span/div/a"  
		xpathFechaNacimiento = "//i[@class='img sp_zR425wRe-ty sx_c71a91']/../../..//div[@class='_4bl9 _2pis _2dbl']/span/div[2]"
		xpathMails = "//i[@class='img sp_qAzfdP9HhqM sx_6a564c']/../../..//div[@class='_4bl9 _2pis _2dbl']/span/div[position()>1]/a"
		xpathCargos = "(//div[@class='_c24 _50f4'])[1]/a[(position() mod 2) > 0]" 
		xpathEmpresas = "(//div[@class='_c24 _50f4'])[1]/a[(position() mod 2) = 0]"
		xpathEmpresasPrevias = "//div[@id='u_3z_0']//li[position() > 1]"
		xpathEstudios = "//div[@id='u_3z_1']//li"
		xpathCiudad = "//div[@data-overviewsection='places']//div[@class='_6a _5u5j _6b']//a" 
		xpathPais = "//div[@class='_3boo']/a[position()=2]"
		xpathAcercaDe = "//div[@id='pagelet_bio']//li[@class='_3pw9 _2pi4']/span[@class='_50f8 _50f4']"
		xpathInfoGral = "//div[@class='_3c-4 _2a57 _3-8w _46ye']"
		xpathTelefonos = "//i[@class='img sp_zR425wRe-ty sx_1225af']/../../../div[@class='_4bl9 _2pis _2dbl']"
		xpathIntro = "//div[@class='_3c-4 _2x70 __2p _2pi0 _52jv']"
		xpathQuotes = "//div[@id='pagelet_quotes']//li[@class='_3pw9 _2pi4']/span[@class='_50f8 _50f4']" 


		Categoria = "Persona"
		FotoURL = ""
		Nick = ""
		Nombre = ""
		Direccion = ""
		OtrasRedes = ""
		SitiosWeb = ""
		FechaNacimiento = ""
		Mails = ""
		EmpresasPrevias = ""
		Estudios = ""
		Ciudad = ""
		Pais = ""
		AcercaDe = ""
		InfoGral = ""
		Cargos = ""
		Empresas = ""
		Telefonos = ""
		Intro = ""
		Quotes = ""
		EmpresasFanPage = ""


		cmod = ConfigModel()

		try:
			pause = cmod.getConfig("pause_extr")[0].valor

			if pause == "1":
				self.mLogger.log("Se pausa la extraccion a pedido del usuario.")
				return

		except IndexError:
			self.mLogger.log("No se encontro la configuracion de pausa, por lo que se continua extrayendo")			

		
		try:
			self.driver.execute_script('document.getElementById("pagelet_dock").remove();')	
		except:
			pass

		rand = RandomAction(self.driver)
		rand.makeAction()	

		if pReload:
			time.sleep(uniform(13,15))
			self.driver.refresh()


		self.mLogger.log("Se chequea que exista el link de informacion")
		wait = WebDriverWait(self.driver, 30)
		wait.until(EC.element_to_be_clickable((By.XPATH, xpathInfoLink)))
		self.mLogger.log("Se termina de chequear que exista el link de informacion")

		try:
			IntroElem = self.driver.find_element_by_xpath(xpathIntro)
			Intro = IntroElem.text
		except NoSuchElementException as nse:
			pass


		try:
			InfoGralElem = self.driver.find_element_by_xpath(xpathInfoGral)
			InfoGral = InfoGralElem.text
		except NoSuchElementException as nse:
			pass

		infoLink = self.driver.find_element_by_xpath(xpathInfoLink)
		ActionChains(self.driver).move_to_element(infoLink).perform()

		infoLink.click()
		
		time.sleep(uniform(3,4))

		CoverPhotoURL = ""

		try:
			FotoCoverURLImgElem = self.driver.find_element_by_xpath(xpathFotoCoverURLImg)
			CoverPhotoURL = FotoCoverURLImgElem.get_attribute("src")
		except NoSuchElementException as nse:
			try:
				FotoCoverURLVideoElem = self.driver.find_element_by_xpath(xpathFotoCoverURLVideo)
				CoverPhotoURL = FotoCoverURLVideoElem.get_attribute("src")
			except NoSuchElementException as nse:
				pass

		try:
			FotoURLElem = self.driver.find_element_by_xpath(xpathFotoURL)
			FotoURL = FotoURLElem.get_attribute("src")
		except NoSuchElementException as nse:
			pass

		try:
			NickElem = self.driver.find_element_by_xpath(xpathNick)
			Nick = NickElem.text
		except NoSuchElementException as nse:
			pass
		
		try:	
			NombreElem = self.driver.find_element_by_xpath(xpathNombre)
			Nombre = NombreElem.text
		except NoSuchElementException as nse:
			pass

		try:	
			TelefonosElem = self.driver.find_element_by_xpath(xpathTelefonos)
			Telefonos = TelefonosElem.text
		except NoSuchElementException as nse:
			pass


		try:
			DireccionesIter = self.driver.find_elements_by_xpath(xpathDireccion)

			for Dir in DireccionesIter:
				Direccion += Dir.text + " , "
			
		except NoSuchElementException as nse:
			pass

		try:
			OtrasRedesIter = self.driver.find_elements_by_xpath(xpathOtrasRedes)

			for OR in OtrasRedesIter:
				OtrasRedes += OR.text + " , "

		except NoSuchElementException as nse:
			pass

		try:
			SitiosWebIter = self.driver.find_elements_by_xpath(xpathSitiosWeb)

			for SW in SitiosWebIter:
				SitiosWeb += SW.text + " , "

		except NoSuchElementException as nse:
			pass

		try:
			FechaNacimientoElem = self.driver.find_element_by_xpath(xpathFechaNacimiento)
			FechaNacimiento = FechaNacimientoElem.text
		except NoSuchElementException as nse:
			pass


		try:
			MailsIter = self.driver.find_elements_by_xpath(xpathMails)

			for M in MailsIter:
				Mails += M.text + " , "

		except NoSuchElementException as nse:
			pass


		try:
			CargosIter = self.driver.find_elements_by_xpath(xpathCargos)
			
			for C in CargosIter:
				Cargos += C.text + " , "

		except NoSuchElementException as nse:
			pass

		try:
			EmpresasIter = self.driver.find_elements_by_xpath(xpathEmpresas)

			for E in EmpresasIter:
				Empresas += E.text + " , "
				EmpresasFanPage += E.get_attribute("href")+ " , "

		except NoSuchElementException as nse:
			pass


		default_handle = self.driver.current_window_handle
		handles = list(self.driver.window_handles)
		iniwindows = len(handles)

		try:
			CiudadElem = self.driver.find_element_by_xpath(xpathCiudad)
			Ciudad = CiudadElem.text			
		
			ActionChains(self.driver).move_to_element(CiudadElem).key_down(Keys.SHIFT).click(CiudadElem).key_up(Keys.SHIFT).perform();

			time.sleep(uniform(3,4))

			handles = list(self.driver.window_handles)
			self.driver.switch_to_window(handles[len(handles)-1])

			wait = WebDriverWait(self.driver, 30)
			wait.until(EC.element_to_be_clickable((By.XPATH, xpathPais)))

			PaisElem = self.driver.find_element_by_xpath(xpathPais)
			Pais = PaisElem.text			

			self.mLogger.log("Se obtuvo la informacion de pais y ciudad")
				
		except NoSuchElementException, TimeoutException:
			pass
			

		handles2 = list(self.driver.window_handles)
		endwindows = len(handles2)

		self.mLogger.log("Ventanas antes: "+str(iniwindows)+" Ventanas despues: "+str(endwindows))

		if iniwindows < endwindows:
			self.closeAndSwitchWindow(default_handle)

						


		self.mLogger.log("Se chequea que exista el link de formacion y empleo")
		wait = WebDriverWait(self.driver, 30)
		wait.until(EC.element_to_be_clickable((By.XPATH, xpathFormEmp)))
		self.mLogger.log("Se termina de chequear que exista el link de formacion y empleo")

		formEmpLink = self.driver.find_element_by_xpath(xpathFormEmp)
		ActionChains(self.driver).move_to_element(formEmpLink).perform()

		formEmpLink.click()

		time.sleep(uniform(2,4))

		try:
			EmpresasPreviasIter = self.driver.find_elements_by_xpath(xpathEmpresasPrevias)

			for EP in EmpresasPreviasIter:
				EmpresasPrevias += EP.text + " , "

		except NoSuchElementException as nse:
			pass

		try:
			EstudiosIter = self.driver.find_element_by_xpath(xpathEstudios)

			for E in EstudiosIter:
				Estudios += E.text + " , "

		except NoSuchElementException as nse:
			pass


		self.mLogger.log("Se chequea que exista el link de 'acerca de'")
		wait = WebDriverWait(self.driver, 30)
		wait.until(EC.element_to_be_clickable((By.XPATH, xpathAbout)))
		self.mLogger.log("Se termina de chequear que exista el link de 'acerca de'")

		formAboutLink = self.driver.find_element_by_xpath(xpathAbout)
		ActionChains(self.driver).move_to_element(formAboutLink).perform()

		formAboutLink.click()

		time.sleep(uniform(2,4))

		try:
			AcercaDeElem = self.driver.find_element_by_xpath(xpathAcercaDe)
			AcercaDe = AcercaDeElem.text
		except NoSuchElementException as nse:
			pass


		try:
			QuotesElem = self.driver.find_element_by_xpath(xpathQuotes)
			Quotes = QuotesElem.text
		except NoSuchElementException as nse:
			pass


		per = Persistence()

		try:
			profq = None

			profq = per.select(ProfileIniDTO,None,ProfileIniDTO.perfil_url == pPerfilURL)

			v_prioridad = 3
			v_excluido = False
			v_excluido_por = None

			for pini in profq:
				v_prioridad = pini.prioridad
		except:
			raise
		finally:
			per.close()
   
		dt = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S');

		p = ProfileDTO(coverphoto_url=unidecode(CoverPhotoURL),foto_url=unidecode(FotoURL),categoria=Categoria,perfil_url=pPerfilURL.split("?")[0],nombre=unidecode(Nombre),sitio_web=unidecode(SitiosWeb),emails=unidecode(Mails),telefonos=Telefonos,direccion_completa=unidecode(Direccion),ciudad=unidecode(Ciudad),pais=unidecode(Pais),acerca_de=unidecode(AcercaDe),info_general=unidecode(InfoGral),cargo=unidecode(Cargos),empresa=unidecode(Empresas),empresas_previas=unidecode(EmpresasPrevias),estudios=unidecode(Estudios),fecha_nacimiento=unidecode(FechaNacimiento),nick=unidecode(Nick),intro=Intro,datos_extras_1=unidecode(Quotes),datos_extras_2=unidecode(OtrasRedes),sesionfb_origen=self.session_user,extraido_fecha_hora=dt,prioridad=v_prioridad,excluir_registro=v_excluido,motivo_exclusion=v_excluido_por,origen_dato=pOrigenDato,empresa_fan_page_url=EmpresasFanPage)

		per2 = Persistence()
		per2.merge(p)

		self.mLogger.log("Se termino de extraer el perfil individual de "+pNombre)

		self.seeIfExcludeProfile(p)




	def extractGroupPersonProfiles(self):

		from Persistence import Persistence
		from DTOS.GroupDTO import GroupDTO
		from DTOS.ProfileErrorDTO import ProfileErrorDTO
		from DTOS.ProfileDTO import ProfileDTO
		from ConfigModel import ConfigModel
		from selenium.common.exceptions import TimeoutException
		from selenium.common.exceptions import WebDriverException
		from selenium.common.exceptions import NoSuchElementException
		from selenium.common.exceptions import ElementNotVisibleException
		from selenium.webdriver.common.action_chains import ActionChains
		from selenium.webdriver.common.keys import Keys	
		import time
		from unidecode import unidecode
		from random import uniform
		from datetime import datetime
		from selenium.webdriver.common.by import By
		from selenium.webdriver.support import expected_conditions as EC
		from selenium.webdriver.support.ui import WebDriverWait

		per = Persistence()
		cmod = ConfigModel()
		
		try:

			try:
				pause = cmod.getConfig("pause_extr")[0].valor

				if pause == "1":
					self.mLogger.log("Se pausa la extraccion a pedido del usuario.")
					return

			except IndexError:
				self.mLogger.log("No se encontro la configuracion de pausa, por lo que se continua extrayendo")


			self.mLogger.log("Va a comenzar la extraccion de perfiles individuales dentro de grupos")

			gps = per.select(GroupDTO,None,GroupDTO.excluido==False)

			self.mLogger.log("Se cargaron los grupos recabados. Ahora se iteran y se les extrae los miembros")

			pathGrps = "https://www.facebook.com/groups/"

			
			try:
				username = cmod.getConfig("username")[0].valor
				encpass = cmod.getConfig("password")[0].valor
				from AESCipher import AESCipher
				password = AESCipher(self.enckey).decrypt(encpass)
			except IndexError:
				raise Exception("No se encontraron las credenciales, por favor cerrar sesion y volverse a loguear")			


			self.login(username,password,True)
			
			try:
				retom_perf = cmod.getConfig("retom_perf")[0].valor
			except IndexError:
				retom_perf = None

			try:
				retom_gru = cmod.getConfig("retom_gru")[0].valor
			except IndexError:
				retom_gru = None	
		
			retom_flag_gru = False

			if not (retom_gru is None or retom_gru == ''):
				self.mLogger.log("Se va a retomar la extraccion en el grupo "+retom_gru)
 				retom_flag_gru = True

			retom_flag_perf = False

			if not (retom_perf is None or retom_perf == ''):
				self.mLogger.log("Se va a retomar la extraccion en el perfil "+retom_perf)
 				retom_flag_perf = True



			for g in gps:
			
				totOK = 0
				totERR = 0

				try:
					pause = cmod.getConfig("pause_extr")[0].valor

					if pause == "1":
						self.mLogger.log("Se pausa la extraccion a pedido del usuario.")
						break

				except IndexError:
					self.mLogger.log("No se encontro la configuracion de pausa, por lo que se continua extrayendo")			


				if retom_flag_gru:
					if g.nombre.upper() == retom_gru.upper():
						retom_flag_gru = False
						self.mLogger.log("Se va a retomar la extraccion en el grupo "+g.nombre)
					else:
						continue


				self.mLogger.log("Se va a extraer los miembros del grupo "+g.nombre)

				self.curGroup = g.nombre

				PathGrpsComplete = pathGrps+g.id

				self.driver.get(PathGrpsComplete)

				time.sleep(uniform(5,6))

				try:
					self.driver.execute_script('document.getElementById("pagelet_dock").remove();')	
				except:
					pass

				xpathLinkMembers = "//div[@class='uiHeaderActions rfloat _ohf']/span/span/a"
				xpathLinkMembers2 = "(//a[@class='_2yau'])[2]"
			
				members = False
				i=0

				while not members and i<5:
					i+=1
					try:
						self.mLogger.log("Se chequea que exista el link de miembros")
						wait = WebDriverWait(self.driver, 30)
						wait.until(EC.element_to_be_clickable((By.XPATH, xpathLinkMembers)))
						self.mLogger.log("Se termina de chequear que exista el link de miembros")
				
						linkMembers = self.driver.find_element_by_xpath(xpathLinkMembers)
						members = True
					except (TimeoutException,NoSuchElementException,WebDriverException,ElementNotVisibleException):
						try:
							self.mLogger.log("Se chequea que exista el segundo link de miembros")
							wait = WebDriverWait(self.driver, 30)
							wait.until(EC.element_to_be_clickable((By.XPATH, xpathLinkMembers2)))
							self.mLogger.log("Se termina de chequear que exista el segundo link de miembros")
				
							linkMembers = self.driver.find_element_by_xpath(xpathLinkMembers2)
							members = True
						except (TimeoutException,NoSuchElementException,WebDriverException,ElementNotVisibleException):
							self.mLogger.log("No se pudo obtener el link de miembros del grupo, se reintenta.")

				if not members:
					raise Exception("No se pudo obtener el link de miembros del grupo finalmente")


				hov = ActionChains(self.driver).move_to_element(linkMembers)
				hov.perform()

				linkMembers.click()
				time.sleep(uniform(8,10))

				self.loadGroupPage()
				
				xpathMembers = "//div[@data-name='GroupProfileGridItem']"
				xpathLinkMember = ".//div[@class='fsl fwb fcb']/a"

				memberElems = self.driver.find_elements_by_xpath(xpathMembers)
			
				try:
					cantMiemGru = cmod.getConfig("val_cant_extr_miem_gru")[0].valor
				except IndexError:
					cantMiemGru = None

				if cantMiemGru is None or int(cantMiemGru) < 1:
					cantMiemGru = len(memberElems)-1
				else:
					cantMiemGru = int(cantMiemGru)-1

				self.mLogger.log("Se van a extraer "+str(cantMiemGru+1)+" miembros del grupo")

				try:
					timeout = cmod.getConfig("val_timeout_ext")[0].valor
				except IndexError:
					timeout = None

				if timeout is None or timeout == '':
					timeout = 0
				else:
					timeout = int(timeout)

				try:
					extr_entre_tout = cmod.getConfig("val_cant_extr_antes_timeout")[0].valor
				except IndexError:
					extr_entre_tout = None

				if extr_entre_tout is None or extr_entre_tout == '':
					extr_entre_tout = 1
				else:
					extr_entre_tout = int(extr_entre_tout)

				self.mLogger.log("Se van a iterar "+str(cantMiemGru)+" miembros del grupo")

				self.driver.execute_script('window.scrollTo(0,0);')	
						
				time.sleep(uniform(13,15))			

				default_handle = self.driver.current_window_handle

				i = 1
				h = 0

				origen = "Grupo "+g.nombre
				

				for memberElem in memberElems[0:int(cantMiemGru)]:

					try:
						pause = cmod.getConfig("pause_extr")[0].valor

						if pause == "1":
							
							self.mLogger.log("Se pausa la extraccion a pedido del usuario.")
							break

					except IndexError:
						self.mLogger.log("No se encontro la configuracion de pausa, por lo que se continua extrayendo")			

					h+=1
					
					linkMember = ""
					nameMember = ""
					urlMember = ""

					self.mLogger.log("Comienza a iterar el elemento nro. "+str(h)+" del grupo "+g.nombre)

					try:
						linkMember = memberElem.find_element_by_xpath(xpathLinkMember)
						nameMember = unidecode(linkMember.text)
						urlMember = unidecode(linkMember.get_attribute("href")).split("?")[0]
						self.mLogger.log("Se cargaron los campos basicos del perfil de "+nameMember)
					except (TimeoutException, NoSuchElementException,ElementNotVisibleException):
						trace=traceback.format_exc()
						self.mLogger.log("Ocurrio un error al cargar algun atributo del perfil: "+trace)
						continue



					if retom_flag_perf and (retom_gru is None or retom_gru == '' or g.nombre.upper() == retom_gru.upper()):
						if nameMember.upper() == retom_perf.upper():
							self.mLogger.log("Se encontro el perfil para retomar la extraccion: "+nameMember+" Grupo: "+g.nombre)
							retom_flag_perf = False
							hov = ActionChains(self.driver).move_to_element(memberElem)
							hov.perform()
						else:
							continue

					per2 = Persistence()

					try:
						pret = per2.select(ProfileDTO,None,ProfileDTO.perfil_url == urlMember)
						
						if pret.count() > 0:						
							self.mLogger.log("Se omite la extraccion de "+nameMember+" ya que ya fue extraido")
							continue
						else:
							self.mLogger.log("No se encontro el perfil de "+nameMember+", por lo que pasa a extraerse")
					except (TimeoutException, NoSuchElementException,ElementNotVisibleException):
						trace=traceback.format_exc()
						self.mLogger.log("Ocurrio un error al verificar la existencia del perfil: "+trace)
						continue
					except:
						raise
					finally:
						per2.close()



					f = 0
					handles = []

					while len(handles) < 2 and f < 5:
						ActionChains(self.driver).move_to_element(linkMember).key_down(Keys.SHIFT).click(linkMember).key_up(Keys.SHIFT).perform();

						time.sleep(uniform(3,4))
	
						handles = list(self.driver.window_handles)

						if len(handles) == 2:
							self.driver.switch_to_window(handles[1])
							self.mLogger.log("Se cargo la pestana con el perfil de "+nameMember)
					
						f += 1


					per3 = Persistence()

					if len(handles) < 2:
						try:
							dt = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S');
							errstr = "No se abrio la pestana del perfil para extraer"
							self.mLogger.log(errstr)
							p = ProfileErrorDTO(nombre=unidecode(nameMember),perfil_url=urlMember,fecha=dt,error=errstr,sesionfb_origen=self.session_user,categoria="Persona")
							per3.merge(p)
						except:
							trace=traceback.format_exc()
							errstr = "Error al verificar apertura del perfil para extraer: "+trace
							self.mLogger.log(errstr)
						finally:
							per3.close()


					
					try:
						self.extractPersonProfile(nameMember,urlMember,origen)
						totOK +=1
					except (TimeoutException, NoSuchElementException, WebDriverException,ElementNotVisibleException):
						try:
							trace=traceback.format_exc()
							self.mLogger.log("Hubo un problema (1) con la extraccion del perfil "+urlMember+" :"+trace)

							if "WebDriverException" in trace and not "clickable" in trace:
								raise Exception("Error fatal en la extraccion del perfil: "+trace)

							self.extractPersonProfile(nameMember,urlMember,origen,True)
							totOK +=1
						except (TimeoutException, NoSuchElementException, WebDriverException,ElementNotVisibleException):
							try:
								trace=traceback.format_exc()
								self.mLogger.log("Hubo un problema (2) con la extraccion del perfil "+urlMember+" :"+trace)

								if "WebDriverException" in trace and not "clickable" in trace:
									raise Exception("Error fatal en la extraccion del perfil: "+trace)

								self.extractPersonProfile(nameMember,urlMember,origen,True)
								totOK +=1
							except (TimeoutException, NoSuchElementException, WebDriverException,ElementNotVisibleException):
								totERR +=1
								trace=traceback.format_exc()
								self.mLogger.log("Hubo un problema (3) con la extraccion del perfil "+urlMember+" y no se pudo extraer finalmente :"+trace)

								if "WebDriverException" in trace and not "clickable" in trace:
									raise Exception("Error fatal en la extraccion del perfil: "+trace)

								try:

									if urlMember != "":
										dt = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S');
										p = ProfileErrorDTO(nombre=unidecode(nameMember),perfil_url=urlMember,fecha=dt,error=trace,sesionfb_origen=self.session_user,categoria="Persona")

										per4 = Persistence()
										try:
											per4.merge(p)
										except:
											raise
										finally:
											per4.close()

										self.mLogger.log("Se grabo como perfil con error el perfil de "+nameMember)

								except (TimeoutException, NoSuchElementException, WebDriverException):
									trace=traceback.format_exc()
									self.mLogger.log("Error en el loggeo de errores de extraccion de perfil de grupo: "+trace)

									if "WebDriverException" in trace and not "clickable" in trace:
										raise Exception("Error fatal en la extraccion del perfil: "+trace)


					finally:
						self.closeAndSwitchWindow(default_handle)




					if totOK != 0 and (totOK % self.notifInterval) == 0:
			
						try:
							strInter = "Se van extrayendo "+str(totOK)+" perfiles miembros del grupo "+g.nombre
							self.mLogger.log(strInter)

							from Mail import Mail
							m = Mail()

							fr="alertasrimbos@softdor.com"
							to=[self.notifMail]
							sub="Notificacion de extraccion de Facebook"
							body=strInter

							m.sendMail(fr,to,sub,body)
						except:
							pass



					if extr_entre_tout != 0 and i % extr_entre_tout == 0:
						self.mLogger.log("Se va a hacer un timeout de "+str(timeout)+" segundos")
						time.sleep(timeout)

					i+=1
				

				try:
					strEndGroup = "Se terminaron de extraer los perfiles miembros del grupo "+g.nombre+" con un total de "+str(totOK)+" perfiles extraidos y "+str(totERR)+" perfiles con error"
					self.mLogger.log(strEndGroup)

					from Mail import Mail
					m = Mail()

					fr="alertasrimbos@softdor.com"
					to=[self.notifMail]
					sub="Notificacion de extraccion de Facebook"
					body=strEndGroup

					m.sendMail(fr,to,sub,body)
				except:
					pass



		except Exception as ex:
			trace=traceback.format_exc()
			raise Exception("Error no identificado en la extraccion de perfiles individuales de grupos: "+trace)

		finally:
			per.close()

			if self.driver is not None:
				self.driver.quit()




	def extractEnterpriseProfiles(self):
		
		from Persistence import Persistence
		from DTOS.ProfileIniDTO import ProfileIniDTO
		from DTOS.ProfileErrorDTO import ProfileErrorDTO
		from DTOS.ProfileDTO import ProfileDTO
		from ConfigModel import ConfigModel
		import time
		from unidecode import unidecode
		from datetime import datetime
		from selenium.common.exceptions import TimeoutException
		from selenium.common.exceptions import NoSuchElementException
		from selenium.common.exceptions import WebDriverException
		from selenium.common.exceptions import ElementNotVisibleException

		cmod = ConfigModel()
		per = Persistence()

		try:
		
			try:
				username = cmod.getConfig("username")[0].valor
				encpass = cmod.getConfig("password")[0].valor
				from AESCipher import AESCipher
				password = AESCipher(self.enckey).decrypt(encpass)
			except IndexError:
				raise Exception("No se encontraron las credenciales, por favor cerrar sesion y volverse a loguear")			

			self.login(username,password,True)

			self.mLogger.log("Va a comenzar la extraccion de perfiles de empresa")
			self.mLogger.log("Se van a cargar los perfiles iniciales de empresa")

			pret = per.select(ProfileIniDTO,None,ProfileIniDTO.categoria == "Empresa",ProfileIniDTO.prioridad.asc())

			try:
				cantMiemEnt= cmod.getConfig("val_cant_extr_pag")[0].valor
			except IndexError:
				cantMiemEnt = None

			if cantMiemEnt is None or cantMiemEnt == '' or cantMiemEnt == "0":
				cantMiemEnt = pret.count()-1
			else:
				cantMiemEnt = int(cantMiemEnt)

			try:
				timeout = cmod.getConfig("val_timeout_ext")[0].valor
			except IndexError:
				timeout = None

			if timeout is None or timeout == '':
				timeout = 0
			else:
				timeout = int(timeout)

			try:
				extr_entre_tout = cmod.getConfig("val_cant_extr_antes_timeout")[0].valor
			except IndexError:
				extr_entre_tout = None

			if extr_entre_tout is None or extr_entre_tout == '' or extr_entre_tout == "0":
				extr_entre_tout = 1
			else:
				extr_entre_tout = int(extr_entre_tout)

			self.mLogger.log("Se cargaron "+str(pret.count())+" perfiles iniciales de empresa. Se iteran para extraer "+str(cantMiemEnt)+" perfiles")

			i = 0

			for p in pret[0:int(cantMiemEnt)]:

				if p.excluido:
					self.mLogger.log("No se extrae el perfil de "+p.nombre+" ya que fue excluido")
					continue
 
				per2 = Persistence()

				try:
					psel = per2.select(ProfileDTO,None,ProfileDTO.perfil_url == p.perfil_url)
						
					if psel.count() > 0:						
						self.mLogger.log("Se omite la extraccion de "+p.nombre+" ya que ya fue extraido")
						continue
					else:
						self.mLogger.log("No se encontro el perfil de "+p.nombre+", por lo que pasa a extraerse")
				except:
					per2.close()
					trace=traceback.format_exc()
					self.mLogger.log("Ocurrio un error al verificar la existencia del perfil: "+trace)
					continue


				try:
					self.extractEnterpriseProfile(unidecode(p.nombre),p.perfil_url)
				except (NoSuchElementException, TimeoutException, WebDriverException,ElementNotVisibleException):
					try:
						trace=traceback.format_exc()			
						self.mLogger.log("Hubo un error al intentar extraer el perfil "+p.perfil_url+" :"+trace)
		
						if "WebDriverException" in trace and not "clickable" in trace:
							raise Exception("Error fatal en la extraccion del perfil: "+trace)

						self.extractEnterpriseProfile(unidecode(p.nombre),p.perfil_url)			
					except (NoSuchElementException, TimeoutException, WebDriverException,ElementNotVisibleException):
						try:
							trace=traceback.format_exc()			
							self.mLogger.log("Hubo un error al intentar extraer el perfil "+p.perfil_url+" :"+trace)

							if "WebDriverException" in trace and not "clickable" in trace:
								raise Exception("Error fatal en la extraccion del perfil: "+trace)

							self.extractEnterpriseProfile(unidecode(p.nombre),p.perfil_url)			
						except (NoSuchElementException, TimeoutException, WebDriverException,ElementNotVisibleException):
							trace=traceback.format_exc()			
							self.mLogger.log("No se pudo finalmente extraer el perfil "+p.perfil_url+" :"+trace)
						
							if "WebDriverException" in trace and not "clickable" in trace:
								raise Exception("Error fatal en la extraccion del perfil: "+trace)

							per3 = Persistence()
							try:
								dt = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S');
								p = ProfileErrorDTO(nombre=unidecode(p.nombre),perfil_url=p.perfil_url,fecha=dt,error=trace,sesionfb_origen=self.session_user,categoria="Empresa")
								per3.merge(p)
							except:
								per3.close()
								trace=traceback.format_exc()			
								self.mLogger.log("Error al grabar el perfil con error "+p.perfil_url+" :"+trace)



				if extr_entre_tout != 0 and i % extr_entre_tout == 0:
					self.mLogger.log("Se va a hacer un timeout de "+str(timeout)+" segundos")
					time.sleep(timeout)

				i+=1
		

			strEnd = "Termino de realizar la extraccion de perfiles de empresa"

			try:
				self.mLogger.log(strEnd)

				from Mail import Mail
				m = Mail()

				fr="alertasrimbos@softdor.com"
				to=[self.notifMail]
				sub="Notificacion de extraccion de Facebook"
				body=strEnd

				m.sendMail(fr,to,sub,body)
			except:
				pass


			return [{"retcode":0,"data":strEnd}]


		except:

			trace=traceback.format_exc()	
			strEnd = "Hubo un error al realizar la extraccion de perfiles de empresa: "+trace+ "\n Retomar extraccion en el perfil '"+self.curProfile+"'"
			self.mLogger.log(strEnd)
			try:
				from ConfigModel import ConfigModel
				cmod = ConfigModel()
				cmod.setConfigs([{"config":{"retom_perf":self.curProfile}}])
			except:
				trace=traceback.format_exc()
				self.mLogger.log("Hubo un error al intentar grabar la configuracion para retomar la extraccion "+trace)

			return [{"retcode":1,"data":strEnd}]

		finally:

			per.close()

			if self.driver is not None:
				self.driver.quit()

			try:
				from Mail import Mail
				m = Mail()

				fr="alertasrimbos@softdor.com"
				to=[self.notifMail]
				sub="Notificacion de extraccion de Facebook"
				body=strEnd

				m.sendMail(fr,to,sub,body)
			except:
				pass





	def extractEnterpriseProfile(self,pNombre,pPerfilURL):

		from Persistence import Persistence
		from DTOS.ProfileDTO import ProfileDTO
		from DTOS.ProfileIniDTO import ProfileIniDTO
		from ConfigModel import ConfigModel
		import time
		from unidecode import unidecode
		from selenium.common.exceptions import NoSuchElementException
		from random import uniform
		from datetime import datetime
		from selenium.webdriver.common.action_chains import ActionChains
		from RandomAction import RandomAction
		from selenium.webdriver.support.ui import WebDriverWait
		from selenium.webdriver.common.by import By
		from selenium.webdriver.support import expected_conditions as EC


		self.mLogger.log("Se empieza a extraer el perfil de empresa de "+pNombre)

		self.curProfile = pNombre

		cmod = ConfigModel()

		idiom = "EN"

		try:
			idiom = cmod.getConfig("lang")[0].valor
		except IndexError:
			pass


		self.driver.get(pPerfilURL)

		time.sleep(uniform(5,6))


		xpathInfoLink = "//a[@class='_2yau' and contains(@href,'/about/')]"
		xpathPosts = "//a[@class='_2yau' and contains(@href,'/posts/')]"
		xpathNombre = "//h1[@id='seo_h1_tag']"
		xpathFotoURL = "//img[@class='_4jhq img']"
		xpathFotoCoverURLImg = "//img[@class='_4on7 _3mk2 img']"
		xpathFotoCoverURLVideo = "//video[@class='_ox1 _blh']"
		xpathDireccion = "//img[contains(@src,'BnWrwGV2-bt.png')]/../..//div[@class='_4bl9']"
		xpathAnioInicio = "//img[contains(@src,'Qz1rawS_hSy.png')]/../..//div[@class='_50f4']"
		xpathTelefono = "//img[contains(@src,'oOfSsM_zvYq.png')]/../..//div[@class='_4bl9']"
		xpathMessenger="//a[@class='_2wmb']"
		xpathEmails = "//img[contains(@src,'j6RRNSQTuuG.png')]/../../div[@class='_4bl9']/a/div"
		xpathWeb = "//img[contains(@src,'t7zX2ECfVwX.png')]/../../div[@class='_4bl9']/a/div"

		if idiom == "EN":
			xpathAcercaDe = "//div[@class='_50f4' and contains(text(),'About')]/../div[@class='_3-8w']"
		else:
			xpathAcercaDe = "//div[@class='_50f4' and contains(text(),'Descripc')]/../div[@class='_3-8w']"

		xpathTipoEmpresa = "//div[@class='_4bl9 _5m_o']/a" 
		xpathIntro = "//div[@class='_4wyf']" 
		xpathUbicacion = "//img[contains(@src,'BnWrwGV2-bt.png')]/../../div[@class='_4bl9']/div/span"     

		if idiom == "EN":
			xpathRangoPrecios = "//span[contains(text(),'Price Range')]/../../div[@class='_4bl9 _5k_']/span"						
		else:
			xpathRangoPrecios = "//span[contains(text(),'Rango de precios')]/../../div[@class='_4bl9 _5k_']/span"						

		xpathInfoGral = "//div[@class='_4-u2 _3-98 _4-u8']"

		Categoria = "Empresa"
		AcercaDe = ""
		Nombre = ""
		FotoURL = ""
		CoverPhotoURL = ""
		Direccion = ""
		AnioInicio = ""
		Telefonos = ""
		Messenger = ""
		Emails = ""
		Web = ""
		TipoEmpresa = ""
		Intro = ""
		Ciudad = ""
		Pais = ""
		RangoPrecios = ""
		InfoGral = ""

	
		wait = WebDriverWait(self.driver, 30)
		wait.until(EC.element_to_be_clickable((By.XPATH, xpathPosts)))

		self.mLogger.log("Se cargo la pagina y se encontro el link de posts, ahora se cargan todos los posts")

		linkPosts = self.driver.find_element_by_xpath(xpathPosts)
		hov = ActionChains(self.driver).move_to_element(linkPosts)
		hov.perform()

		linkPosts.click()
		time.sleep(uniform(5,6))

		rand = RandomAction(self.driver)
		rand.makeAction()	

		self.mLogger.log("Se carga la informacion del perfil")

		linkInfo = self.driver.find_element_by_xpath(xpathInfoLink)
		hov = ActionChains(self.driver).move_to_element(linkInfo)
		hov.perform()

		linkInfo.click()
		time.sleep(uniform(5,6))

		
		try:
			NombreElem = self.driver.find_element_by_xpath(xpathNombre)
			Nombre = NombreElem.text
		except NoSuchElementException as nse:
			pass

		try:
			FotoURLElem = self.driver.find_element_by_xpath(xpathFotoURL)
			FotoURL = FotoURLElem.get_attribute("src")
		except NoSuchElementException as nse:
			pass


		try:
			FotoCoverURLImgElem = self.driver.find_element_by_xpath(xpathFotoCoverURLImg)
			CoverPhotoURL = FotoCoverURLImgElem.get_attribute("src")
		except NoSuchElementException as nse:
			try:
				FotoCoverURLVideoElem = self.driver.find_element_by_xpath(xpathFotoCoverURLVideo)
				CoverPhotoURL = FotoCoverURLVideoElem.get_attribute("src")
			except NoSuchElementException as nse:
				pass

		
		try:
			DireccionElem = self.driver.find_element_by_xpath(xpathDireccion)
			Direccion = DireccionElem.text
		except NoSuchElementException as nse:
			pass

		try:
			AnioInicioElem = self.driver.find_element_by_xpath(xpathAnioInicio)
			AnioInicio = AnioInicioElem.text
		except NoSuchElementException as nse:
			pass

		try:
			TelefonoElem = self.driver.find_element_by_xpath(xpathTelefono)
			Telefonos = TelefonoElem.text
		except NoSuchElementException as nse:
			pass

		try:
			MessengerElem = self.driver.find_element_by_xpath(xpathMessenger)
			Messenger = MessengerElem.text
		except NoSuchElementException as nse:
			pass

		try:
			EmailsElem = self.driver.find_element_by_xpath(xpathEmails)
			Emails = EmailsElem.text
		except NoSuchElementException as nse:
			pass

		try:
			WebElem = self.driver.find_element_by_xpath(xpathWeb)
			Web = WebElem.text
		except NoSuchElementException as nse:
			pass

		try:
			AcercaDeElem = self.driver.find_element_by_xpath(xpathAcercaDe)
			AcercaDe = AcercaDeElem.text
		except NoSuchElementException as nse:
			pass

		try:
			TipoEmpresaElems = self.driver.find_elements_by_xpath(xpathTipoEmpresa)
			
			for TE in TipoEmpresaElems:
				TipoEmpresa += TE.text + " , "

		except NoSuchElementException as nse:
			pass


		try:
			IntroElem = self.driver.find_element_by_xpath(xpathIntro)
			Intro = IntroElem.text
		except NoSuchElementException as nse:
			pass


		try:
			RangoPreciosElem = self.driver.find_element_by_xpath(xpathRangoPrecios)
			RangoPrecios = RangoPreciosElem.text
		except NoSuchElementException as nse:
			pass


		try:
			InfoGralElem = self.driver.find_element_by_xpath(xpathInfoGral)
			InfoGral = InfoGralElem.text
		except NoSuchElementException as nse:
			pass

		self.mLogger.log("Se cargaron todos los campos de la empresa. Ahora se chequea el atributo de exclusion y carga la prioridad")

		dt = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S');

		per = Persistence()

		profq = per.select(ProfileIniDTO,None,ProfileIniDTO.perfil_url == pPerfilURL)

		v_prioridad = 3
		v_excluido = False
		v_excluido_por = None

		for pini in profq:
			v_prioridad = pini.prioridad


		p = ProfileDTO(coverphoto_url=unidecode(CoverPhotoURL),foto_url=unidecode(FotoURL),categoria=Categoria,perfil_url=pPerfilURL.split("?")[0],nombre=unidecode(Nombre),empresa=unidecode(Nombre),empresa_fan_page_url=pPerfilURL.split("?")[0],sitio_web=unidecode(Web),emails=unidecode(Emails),telefonos=unidecode(Telefonos),direccion_completa=unidecode(Direccion),ciudad=unidecode(Ciudad),pais=unidecode(Pais),tipo_empresa=unidecode(TipoEmpresa),ano_inicio=unidecode(AnioInicio),acerca_de=unidecode(AcercaDe),info_general=unidecode(InfoGral),intro=unidecode(Intro),fb_messenger=unidecode(Messenger),prioridad=v_prioridad,excluir_registro=v_excluido,motivo_exclusion=v_excluido_por,sesionfb_origen=self.session_user,extraido_fecha_hora=dt)

		try:
			per.merge(p)
		except:
			raise
		finally:
			per.close()

		self.mLogger.log("Se termino de extraer el perfil de empresa de "+pNombre)






	def getEncKey(self):
		return self.enckey




	def loadGroupPage(self):
	
		from selenium.common.exceptions import WebDriverException
		from selenium.common.exceptions import NoSuchElementException
		from selenium.webdriver.common.action_chains import ActionChains
		import time
		from random import uniform

		xpathMorePager = "//div[@class='clearfix pam uiMorePager stat_elem morePager _52jv']"
	
		count = 0
		descend = False
		retry_count = 7
		height = 0
		newHeight = 0

		self.mLogger.log("Se cargo la pagina de miembros del grupo y se van a cargar todos los perfiles de los miembros")

		while count < retry_count:

			try:
				descend = False
				height = self.driver.execute_script('return document.body.scrollHeight')
		
				self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')	

				time.sleep(uniform(3,5))

				morepage = self.driver.find_element_by_xpath(xpathMorePager)
				hov = ActionChains(self.driver).move_to_element(morepage)
				hov.perform()
				morepage.click()
	
				time.sleep(uniform(5,7))	

				newHeight = self.driver.execute_script('return document.body.scrollHeight')	

				if newHeight > height:
					count = 0
					descend = True

			except (NoSuchElementException,WebDriverException):
				self.mLogger.log("Se llego hasta el final de la pagina de miembros del grupo. Contador "+str(count))
			finally:
				if not descend:
					self.mLogger.log("Se suma un punto al contador. Valor "+str(count))
					count+=1




		
	def getProfileErrors(self):
		
		from DTOS.ProfileErrorDTO import ProfileErrorDTO
		from Persistence import Persistence
		per = Persistence()
		try:
			self.mLogger.log("Se van a cargar los perfiles con error desde la base de datos")

			profs = per.select(ProfileErrorDTO,None)
			self.mLogger.log("Se obtuvieron "+str(profs.count())+" perfiles con error desde la base de datos")
			
			json={"data": []}
	
			for p in profs:
				json["data"].append([p.nombre,p.perfil_url,p.fecha,p.error,p.sesionfb_origen,p.categoria])

			return json

		except:			
			trace=traceback.format_exc()
			raise Exception("Error no identificado en la obtencion de perfiles desde la base de datos: "+trace)
		finally:
			per.close()




	
	def reprocessErrors(self):

		from DTOS.ProfileErrorDTO import ProfileErrorDTO
		from Persistence import Persistence
		from ConfigModel import ConfigModel
		from selenium.common.exceptions import NoSuchElementException
		from selenium.common.exceptions import TimeoutException
		import time
		from random import uniform

		per = Persistence()
		try:

			cmod = ConfigModel()
			login = False
			origen = "Reprocesamiento de errores"

			self.mLogger.log("Se van a cargar los perfiles con error de personas desde la base de datos")

			perprofs = per.select(ProfileErrorDTO,None,ProfileErrorDTO.categoria == "Persona")
			self.mLogger.log("Se obtuvieron "+str(perprofs.count())+" perfiles con error de personas desde la base de datos")

			if perprofs.count() > 0:
				try:
					username = cmod.getConfig("username")[0].valor
					encpass = cmod.getConfig("password")[0].valor
					from AESCipher import AESCipher
					password = AESCipher(self.enckey).decrypt(encpass)
				
				except IndexError:
					raise Exception("No se encontraron las credenciales, por favor cerrar sesion y volverse a loguear")			
	
				self.login(username,password,True)

				login = True

				for p in perprofs:
					try:
						self.driver.get(p.perfil_url)
						time.sleep(uniform(5,7))
						self.extractPersonProfile(p.nombre,p.perfil_url,origen,True)
						per.delete(ProfileErrorDTO,ProfileErrorDTO.perfil_url == p.perfil_url)
					except NoSuchElementException, TimeoutException:
						trace=traceback.format_exc()
						self.mLogger.log("Error no identificado en el reprocesamiento de perfiles con error: "+trace)


				msgOK = "Se terminaron de reprocesar correctamente los errores de personas"

			else:
				msgOK = "No hay errores de personas para reprocesar"

			self.mLogger.log(msgOK)


			self.mLogger.log("Se van a cargar los perfiles con error de empresas desde la base de datos")
			per = Persistence()
			entprofs = per.select(ProfileErrorDTO,None,ProfileErrorDTO.categoria == "Empresa")
			self.mLogger.log("Se obtuvieron "+str(entprofs.count())+" perfiles con error de empresas desde la base de datos")


			if entprofs.count() > 0:

				if not login:
					try:
						username = cmod.getConfig("username")[0].valor
						encpass = cmod.getConfig("password")[0].valor
						from AESCipher import AESCipher
						password = AESCipher(self.enckey).decrypt(encpass)
				
					except IndexError:
						raise Exception("No se encontraron las credenciales, por favor cerrar sesion y volverse a loguear")			
	
					self.login(username,password,True)


				for p in entprofs:
					try:
						self.driver.get(p.perfil_url)
						time.sleep(uniform(5,7))
						self.extractPersonProfile(p.nombre,p.perfil_url,origen,True)
						per.delete(ProfileErrorDTO,ProfileErrorDTO.perfil_url == p.perfil_url)
					except NoSuchElementException, TimeoutException:
						trace=traceback.format_exc()
						self.mLogger.log("Error no identificado en el reprocesamiento de perfiles con error: "+trace)


				msgOK = "Se terminaron de reprocesar correctamente los errores de empresas"

			else:
				msgOK = "No hay errores de empresas para reprocesar"

			self.mLogger.log(msgOK)


			return [{"retcode":0,"data":"Se terminaron de reprocesar correctamente los errores de perfiles de empresas y personas"}]

		except Exception as ex:
			trace=traceback.format_exc()
			raise Exception("Error no identificado en el reprocesamiento de perfiles con error desde la base de datos: "+trace)

		finally:
			per.close()
			if self.driver is not None:
				self.driver.quit()

		



	def closeAndSwitchWindow(self,pWindowToSwitch):
			
		done1 = False
		f = 0
		while not done1 and f < 5:
			f+=1
			try:
				self.driver.close()
				done1 = True
				self.mLogger.log("Se cerro la ventana")
			except:
				trace=traceback.format_exc()
				self.mLogger.log("Error al cerrar de ventana: "+trace)


		done2 = False
		f = 0
		while not done2 and f < 5:
			f+=1
			try:
				self.driver.switch_to_window(pWindowToSwitch)
				done2 = True
				self.mLogger.log("Se cambio de ventana")
			except:
				trace=traceback.format_exc()
				self.mLogger.log("Error al cambiar de ventana: "+trace)

		if not (done1 and done2):
			raise Exception("Hubo un error fatal al intentar cerrar o cambiar de ventana. Se aborta proceso.")




	def pauseExtr(self):

		from ConfigModel import ConfigModel
		cmod = ConfigModel()
		cmod.setConfigs([{"config":{"pause_extr":"1"}}])
	
		return [{"retcode":0,"data":"Se indico para pausar en la proxima iteracion."}] 



	def seeIfDelPag(self):
		from DTOS.ProfileIniDTO import ProfileIniDTO
		from Persistence import Persistence
		from ConfigModel import ConfigModel
		del_pag = None

		cmod = ConfigModel()
		per = Persistence()

		try:
			del_pag_arr = cmod.getConfig("del_pag")
			del_pag = del_pag_arr[0].valor
		except IndexError:
			pass 			


		if del_pag is None or del_pag == "":
			del_pag = False			
		elif del_pag == "1" or del_pag.upper() == "TRUE":
			del_pag = True

		if del_pag:
			self.mLogger.log("Se van a eliminar todos los perfiles iniciales de empresa")

			per.delete(ProfileIniDTO,ProfileIniDTO.categoria == "Empresa")

			self.mLogger.log("Se eliminaron todos los perfiles iniciales de empresa")	




	def seeIfDelExcl(self):
		from DTOS.ExclusionDTO import ExclusionDTO
		from Persistence import Persistence
		from ConfigModel import ConfigModel
		del_excl = None

		cmod = ConfigModel()
		per = Persistence()

		try:
			del_excl_arr = cmod.getConfig("del_excl")
			del_excl = del_excl_arr[0].valor
		except IndexError:
			pass 			


		if del_excl is None or del_excl == "":
			del_excl = False			
		elif del_excl == "1" or del_excl.upper() == "TRUE":
			del_excl = True

		if del_excl:
			self.mLogger.log("Se van a eliminar todas las exclusiones")

			per.delete(ExclusionDTO)

			self.mLogger.log("Se eliminaron todas las exclusiones")	




	def seeIfDelPerfInd(self):
		from DTOS.ProfileIniDTO import ProfileIniDTO
		from Persistence import Persistence
		from ConfigModel import ConfigModel
		del_perf = None

		cmod = ConfigModel()
		per = Persistence()

		try:
			del_perf_arr = cmod.getConfig("del_perf_ind")
			del_perf = del_perf_arr[0].valor
		except IndexError:
			pass 			


		if del_perf is None or del_perf == "":
			del_perf = False			
		elif del_perf == "1" or del_perf.upper() == "TRUE":
			del_perf = True

		if del_perf:
			self.mLogger.log("Se van a eliminar todos los perfiles iniciales individuales")

			per.delete(ProfileIniDTO,ProfileIniDTO.categoria == "Persona")

			self.mLogger.log("Se eliminaron todos los perfiles iniciales individuales")	



	def snvl(self,pParam):
		if pParam is None:
			return ""
		else:
			ret = None
			try:
				ret = str(pParam) 
			except UnicodeEncodeError:
				from unidecode import unidecode
				ret = unidecode(pParam)

			return ret



	def nvl(self,pParam):
		if pParam is None:
			return ""
		else:
			return pParam


