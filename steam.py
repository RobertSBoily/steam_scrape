from openpyxl import Workbook
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import sys
import time

# URL Config
URL_1 = 'https://steamcommunity.com/id/'
URL_2 = '/followedgames'
USERNAME = 'gabelogannewell' # For example purposes only, replace with a public profile.

# Tf you update this, also update it at the end of the main for loop.
HEADER_ROW = ('URL', 'Title', 'Price', 'Discount %', 'Original Price', 'Early Access?')


class SteamScraper:
	def __init__(self, username):
		self.url = URL_1 + username + URL_2

		# Set up spreadshheet
		self.wb = Workbook()
		self.ws = self.wb.active
		self.ws.title = 'Steam Followed'
		self.ws.append(HEADER_ROW)

		# Set up webdriver
		self.driver = webdriver.Firefox()
		self.driver.maximize_window()


	def get_early_access(self):
		try:
			self.driver.find_element_by_class_name('early_access_header')
		except NoSuchElementException:
			return False
		else:
			return True


	def get_price(self):
		# Get price, handle errors for if the item is Coming Soon, or some such.
		# Uses driver to get info, not to navigate.
		# Return in format (price, discount_percent, original_price)
		try: 
			price = self.driver.find_element_by_css_selector('.game_purchase_price.price').text # String, not int, eg 'CDN$ 16.99'
			return (price, None, None)
		except NoSuchElementException:
			print('Handling nonstandard price entry...')
			# Try the procedure for "item on sale".
			try:
				# Remember, all of these are strings, not ints, eg 'CDN$ 16.99' or '-80%'
				price = self.driver.find_element_by_class_name('discount_final_price').text
				discount_percent = self.driver.find_element_by_class_name('discount_pct').text
				original_price = self.driver.find_element_by_class_name('discount_original_price').text
				print('Item is on discount.')
				print(price + discount_percent + original_price)
				return(price, discount_percent, original_price)
			except NoSuchElementException:
				print('Item is not on discount...')
				try:
					coming_soon = self.driver.find_element_by_css_selector('.game_area_comingsoon.game_area_bubble')
					price = coming_soon.find_element_by_tag_name('h1').text
					print('Item has no price set.')
					return (price, None, None)
				except:
					# Give up, send the exception to the terminal and the price field.
					# Expected cases: Game is no longer on sale, but still has a Store page.
					print('===Unexpected error!===')
					print(sys.exc_info()[0])
					price = "EXCEPTION:" + str((sys.exc_info()[0]))
					return (price, None, None)



	def handle_agecheck(self):
		# Assigns self.url_components - not best practice
		self.url_components = self.driver.current_url.split(sep='/') # Not sure if this should be a class variable

		if self.url_components[-1] == 'agecheck': # For format "http://store.steampowered.com/app/691690/agecheck"
			print("Bypassing agecheck type A...")
			# Move forward, then reset url_components for later steps.
			print()
			self.driver.find_element_by_link_text('View Page').click()
			time.sleep(5) # Needed to ensure url_components reset goes smoothly.
			self.url_components = self.driver.current_url.split(sep='/')

		elif self.url_components[3] == 'agecheck':
			print("Bypassing agecheck type B...")
			# Set birth date, move forward, then reset url_components for later steps.
			year_dropdown = Select(self.driver.find_element_by_id('ageYear'))
			year_dropdown.select_by_value("1987")
			self.driver.find_element_by_link_text('Enter').click()
			self.url_components = self.driver.current_url.split(sep='/')

		# Sufficient, but not necessary condition, for the presence of an agecheck that this code doesn't handle.
		elif 'agecheck' in self.url_components:
			print("Unhandled agecheck! Price will be missing for this entry.")


	def set_game_urls(self):
		"""Must be run before calling self.game_urls"""
		# Should this be in __init__()? I don't like the idea of running a webdriver in __init__()
		self.driver.get(self.url)
		self.games = self.driver.find_elements_by_link_text('Visit the Store Page')
		self.game_urls = [] # Should this be created in __init__() ?

		for game in self.games:
			self.game_urls.append(game.get_attribute('href'))


	def main(self):
		self.set_game_urls()

		for url in self.game_urls:
			# For loop cleanup - do NOT want these variables retained from the 
			# previous loop, since we might not set them to new values.
			# We DO want these values used on IF they exist for this game.
			# This also allows the diagnostics logic to work.
			discount_percent = None
			original_price = None

			self.driver.get(url)
			print(url)

			self.handle_agecheck()

			app_id = self.url_components[-3]
			title = self.url_components[-2]

			price, discount_percent, original_price = self.get_price()

			early_access = self.get_early_access()

			# Diagnostics
			print('url_components == ' + str(self.url_components)) # url_components is an array.
			print('app_id == ' + app_id)
			print('title == ' + title)
			print('price == ' + price)
			print('discount_percent == ' + str(discount_percent)) # discount_percent might be NoneType.
			print('original_price == ' + str(original_price)) # original_price might be NoneType.
			print('early_access == ' + str(early_access)) # early_access is a bool.

			# Header row above: followed_sheet.append('URL', 'Title', Price', 'Discount %', 'Original Price', 'Early Access?')
			export_info = (self.driver.current_url, title, price, discount_percent, original_price, str(early_access))
			self.ws.append(export_info)

		# Save data
		self.wb.save('steam.xlsx')
		self.driver.quit()
