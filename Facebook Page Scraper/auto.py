from selenium import webdriver
#driver = webdriver.Firefox()
#driver.get("http:google.com")
chromedriver = "/home/khizer/Downloads/chromedriver"
driver = webdriver.Chrome(chromedriver)
driver.get("http:gsmarena.com")