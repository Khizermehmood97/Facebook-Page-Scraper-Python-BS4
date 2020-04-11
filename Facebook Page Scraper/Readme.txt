Facebook Page Post Scraper:
A tool for gathering all the posts and comments of a page and related data including post comments, shares, reacts, their counts and comment replies.
All this data is exported as datagram into EXCEL document.

Requirements:
1) Python.3.6	
2) BeautifulSoup4
3) openpyxl
4) pandas
5) selenium
6) chromedriver 

List of files:
1) FacebookRenderEngine.py: This files takes care of rendering a page and return html_source of that particular page.
2) FacebookScraper.py: This files takes care of scraping the html_source from render engine.
3) Controller: This is the main files which takes care of excel sheet generation.
		
How to Run:
	1. In line-17 of FacebookRenderEngine.py file, add the path of chromedriver.
	2. Run the program using : python3 Controller.py
	
Note
This tool is for research purposes only. Hence, the developers of this tool won't be responsible for any misuse of data collected using this tool.
