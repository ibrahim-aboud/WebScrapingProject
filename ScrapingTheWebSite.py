from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
import time
import json

#______________________________________AUTOBIP SCRAPING PROJECT___________________________________________

#___________________________________________by Aboud Ibrahim_______________________________________________

#___________________________for imediate use, scroll down to the end of the code snippet_____________________________

#this function is equivalent to "previous page", not used in this code but might be useful elsewhere
def efficient_back(driver):
    max_iteration = 10
    counter =0
    current_url = driver.current_url
    driver.back()
    #making sure to back to the previous page because some might take more than one click
    while(driver.current_url==current_url and counter <max_iteration):
        driver.back()
        counter+=1    
# a separate function for clicking -safely- individual elements
def click_element(driver, xpath):
    try:
        element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    except StaleElementReferenceException as e1:
        element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    except WebDriverException as e2:
        element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    time.sleep(0.5)
    try:
        element.click()
    except StaleElementReferenceException as e1:
        print("stale")
    except WebDriverException as e2:
        print("stale")

def scan_car_page(driver,car_brand,car_sub_brand,car_link = ""):
    if(car_link!=""):
        driver.get(car_link)
        #waiting for the target elements to load (the car specs titles)
        wait = WebDriverWait(driver, 20)                        
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'mt-4')))
    #initialising the car as a dictionary, and adding the brand and sub-brand values to it
    car= {}
    car['brand'] = car_brand
    car['sub-brand']= car_sub_brand
    #finding the main specs of the car
    main_specs = driver.find_elements(By.CLASS_NAME,"mt-4")
    for main_spec in main_specs:
        #extracting both the name of the spec and it's value, then adding them to the car dictionary
        separated_texts = main_spec.find_elements(By.XPATH,'./div')
        main_spec_name = separated_texts[0].text
        main_spec_value = separated_texts[1].text
        car[main_spec_name]=main_spec_value

    # finding the specs headers (motor, comfort, security .. etc)
    spec_headers = driver.find_elements(By.CLASS_NAME,'my-1')

    #eleminating the first header since it is just the name of the car
    spec_headers.pop(0)

    #initialising the spec list (which by itself should contain the spec headers, that in turn contain the real data)
    full_spec_list = {}
    spec_header_index = 0
    # after each header "next to it" we have the list of specs - the real data - so we must relocate ourselves to that place
    for spec_header in spec_headers:
        spec_header_index +=1
        spec_header_name = spec_header.text
        spec_header_content_parent = spec_header.find_element(By.XPATH,'..')
        try:
            spec_header_content_holder = spec_header_content_parent.find_element(By.XPATH,'following-sibling::div')
            #here is the real data list - the specs that comes after each header - 
            spec_header_content=spec_header_content_holder.find_elements(By.CLASS_NAME,'mb-1')
            list_of_specs = {}
            # this loop will check the availability of all data (shown and not hidden)
            for spec in spec_header_content:
                # a work around to show hidden data (because when there is a long list of data, a "show more" button appears, we must click it first)
                if(len(spec.find_elements(By.XPATH,'./div/div'))==0):
                    # if the "show more" button indeed appears to exist, we locate it and click it
                    spec.find_element(By.XPATH,'./button').click()
                    break
            # just to make sure, we need to update the new list of specs after clicking the "show more" button
            spec_headers = driver.find_elements(By.CLASS_NAME,'my-1')      
            new_spec_header=spec_headers[spec_header_index]
            spec_header_content_parent = new_spec_header.find_element(By.XPATH,'..')
            spec_header_content_holder = spec_header_content_parent.find_element(By.XPATH,'following-sibling::div')
            spec_header_content=spec_header_content_holder.find_elements(By.CLASS_NAME,'mb-1')     
            # finally we loop over the data of each spec, extracting the name of the spec, and its value, with a little if else
            # so that we can convert the -green check mark- and the -red cross- to  -True- and -False- values
            for spec in spec_header_content:
                spec_details = spec.find_elements(By.XPATH,'./div/div')
                spec_name = spec_details[0].text
                spec_value = spec_details[1].text
                if (spec_value ==""):
                    if(len(spec.find_elements(By.CLASS_NAME,'green--text'))!=0):
                        spec_value = True
                    else:
                        if (len(spec.find_elements(By.CLASS_NAME,'red--text'))!=0):
                            spec_value=False
                #filling gradually the list of specs for a given spec header
                list_of_specs[spec_name]=spec_value
        except NoSuchElementException as e:
            spec_header_content_holder = spec_header_content_parent.find_element(By.XPATH,'following-sibling::span')
            list_of_specs = spec_header_content_holder.text

        # filling gradualy the full list header by header
        full_spec_list[spec_header_name]=list_of_specs

    # last but not least, giving the car the specs attribute
    car['specs list']=full_spec_list
    # converting the dictionary to a json formatted string, to use it later on
    return car
def number_of_car_brands():
    # setting up the driver by selecting the chrome web browser
    driver = webdriver.Chrome()
    # going to the url
    driver.get(website)
    #the xpath syntax is the following : '//tagName[@attribute="value"]' for example : '//button[@class="redButton"]'
    main_page_link = driver.current_url
    #reextracting the list of brands
    brands_list = driver.find_element(By.ID,"carbrands").find_element(By.XPATH,"following-sibling::div/following-sibling::div").find_elements(By.CLASS_NAME,'pa-2')
    brands_number = len(brands_list)
    driver.close()
    return brands_number

def scan_brand(brand_index,car_list_object,website ='https://www.autobip.com/fr/prix-du-neuf-voitures-algerie'):
    # setting up the driver by selecting the chrome web browser
    driver = webdriver.Chrome()
    # going to the url
    driver.get(website)
    #the xpath syntax is the following : '//tagName[@attribute="value"]' for example : '//button[@class="redButton"]'

    main_page_link = driver.current_url
    #reextracting the list of brands
    brands_list = driver.find_element(By.ID,"carbrands").find_element(By.XPATH,"following-sibling::div/following-sibling::div").find_elements(By.CLASS_NAME,'pa-2')
    brand_link = '//*[@id="app_main"]/main/div/div/div/div[13]/div/div'+'['+str(brand_index+1)+']'
    #click_element(driver,brand_link)
    time.sleep(0.5)
    #acessing each brand
    brand_name = brands_list[brand_index].text
    brands_list[brand_index].click()
    wait = WebDriverWait(driver, 20)                        
    wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="app_main"]/main/div/div/div/div[1]/div/div[1]')))
    #############################################################################
    time.sleep(0.5)
    #the actual full class name of each square is : "pa-2 col-sm-4 col-md-3 col-lg-3 col-6" but looks like there is a spacing problem
    #getting all the subbrands
    all_subbrands = driver.find_elements(By.CLASS_NAME,'pa-2')
    number_of_subbrands = len(all_subbrands)
    # saving the brand link to go back to it later
    brand_link = driver.current_url
    #iterating through each subbrand
    for subbrand_index in range(number_of_subbrands):
        all_subbrands = subbrand_index
        #verification print
        #print("  subbrand number : ",subbrand_index," of ",number_of_subbrands)
        try:
            wait = WebDriverWait(driver, 20)    
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'pa-2')))
            all_subbrands = driver.find_elements(By.CLASS_NAME,'pa-2')
            time.sleep(0.2)
            subbrand_name = all_subbrands[subbrand_index].find_element(By.CLASS_NAME,'h3').text
            all_subbrands[subbrand_index].click()
        except IndexError:
            print("  i counted wrong")
            break
        except StaleElementReferenceException as e:
            print("  stale")
            driver.switch_to.default_content()
            try:
                wait = WebDriverWait(driver, 20)    
                all_subbrands = driver.find_elements(By.CLASS_NAME,'pa-2')
                subbrand_name = all_subbrands[subbrand_index].text
                all_subbrands[subbrand_index].click()
            except:
                print("can't prevent more than that")
        ###########################################################################    
        time.sleep(0.5)
        wait = WebDriverWait(driver, 20)                        
        wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="app_main"]/main/div/div/div/div[1]/div/div[1]')))
        subbrand_link = driver.current_url
        wait = WebDriverWait(driver, 20)    
        all_models = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'pa-2')))
        number_of_models = len(all_models)
        #iterating through each model of the subbrand
        for model_index in range(number_of_models):
            all_models = model_index
            #print("    model number : ",model_index," of ",number_of_models)
            try:
                all_models = driver.find_elements(By.CLASS_NAME,'pa-2')
                #time.sleep(0.5)
                all_models[model_index].click()
                ###########################################################################
                time.sleep(0.5)
                #print("technically speaking i am at the car's page right now")
            except StaleElementReferenceException:
                print("  stale model element")
                try:
                    all_models = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'pa-2')))
                    #time.sleep(0.5)
                    all_models[model_index].click()
                    #we have finally arrived at the car's page
                except StaleElementReferenceException:
                    print("can't prevent more than that nope")
            except IndexError:
                print("   i counted wrong i think")
                break
            except:
                print("idk what other thing should i do ")
            finally:
                car = scan_car_page(driver, brand_name,subbrand_name)
                car_list_object.append(car)
                
            wait = WebDriverWait(driver, 20)                        
            wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="app_main"]/main/div/div/div/div[1]/div/div[1]')))
            #do some stuff with the data
            driver.get(subbrand_link)
        driver.get(brand_link)        
    driver.close()
    return car_list_object

#____________________________________THE JUICY PART OF THE CODE______________________________________________

# inorder to scrap the website follow the three steps

# step 1 : initialise your variable that contains a list of dictionaries, each dictionary is a full car brand
car_list = []

# step 2 : get the number of brands from the website
print(number_of_car_brands())

# step 3 : run the following method including the car_list and the specefic car index (from 0 to number_of_car_brands())
# the car_list will be updated "so appending the new brand selected by the index"
car_list = scan_brand(0,car_list)

# once run all the method as many times as the number of brands, convert the list into a json string, you can then save it as a json file
json_dictionary={}
json_dictionary['autoBip']=car_list
final_json_string = json.dumps(json_dictionary,indent=2)
print(final_json_string)

# NOTES : 
# inorder to prevent stale element refrence exception
# it is recommended to run the program as many times as the number
# of the brands, at each time changing the brand index
# however a "for loop" iterating through all the brands can do the trick
# the problem is that there is a higher probability of having the exeption which could eventually
# stop the program ... etc 
# "and it is not solvable with try and except, it is just because the program takes a very long time to execute"
