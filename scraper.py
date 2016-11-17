
# We import the dependencies
import json

# This is needed to create a lxml element object that has a css selector
from lxml.etree import fromstring

# The requests librart
import requests

class WholeFoodsScraper:

    API_url = 'http://www.wholefoodsmarket.com/views/ajax'
    scraped_stores = []

    def get_stores_info(self, page):
        '''
        Sends a post request to the wholefoods undocumented
        API to return the stores located in a specific page
        '''
        
        # This is the only data required by the api 
        # To send back the stores info
        data = {
        'view_name': 'store_locations_by_state',
        'view_display_id': 'state',
        'page': page
        }
        # Making the post request
        response = requests.post(self.API_url, data=data)

        # The data that we are looking is in the second
        # Element of the response and has the key 'data', 
        # so that is what's returned
        return response.json()[1]['data']

    def parse_stores(self, data):
        '''
        Parse the html that contains info about wholefoods stores that's 
        inserted in their webpage using AJAX
        '''

        # Creating an lxml Element instance
        element = fromstring(data)

        for store in element.cssselect('.views-row'):
            store_info = {}
            
            # The lxml etree css selector always returns a list, so we get
            # just the first item
            store_name = store.cssselect('.views-field-title a')[0].text
            street_address = store.cssselect('.street-block div')[0].text
            address_locality = store.cssselect('.locality')[0].text
            address_state = store.cssselect('.state')[0].text
            address_postal_code = store.cssselect('.postal-code')[0].text
            phone_number = store.cssselect('.views-field-field-phone-number div')[0].text
            
            try:
                opening_hours = store.cssselect('.views-field-field-store-hours div')[0].text
            except IndexError:
                # Stores that doesn't have opening hours are closed and should not be saved
                # this is found while debugging, so don't worry if you get errors when you
                # run a scraper
                opening_hours = 'STORE CLOSED'
                continue
            
            full_address = "{}, {}, {} {}".format(street_address,
                                                  address_locality,
                                                  address_state,
                                                  address_postal_code)
            
            # now we add all the info to a dict
            store_info = {
                        'name': store_name,
                        'full_address': full_address,
                        'phone': phone_number,
                        'hours': opening_hours
                        }
            
            # We add the store to the scraped stores list
            self.scraped_stores.append(store_info)
            
    
    def run(self):
        for page in range(22):
            # Retrieving the data
            data = self.get_stores_info(page)
            # Parsing it
            self.parse_stores(data)
            print('scraped the page' + str(page))

        self.save_data()

    def save_data(self):
        with open('wholefoods_stores.json', 'w') as json_file:
            json.dump(self.scraped_stores, json_file, indent=4)

if __name__ == '__main__':
    scraper = WholeFoodsScraper()
    scraper.run()

        
            

            

        

        
         
