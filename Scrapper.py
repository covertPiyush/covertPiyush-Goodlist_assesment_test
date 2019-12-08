from bs4 import BeautifulSoup
import requests
from datetime import date
from datetime import datetime
import urllib.parse
import json




# url = ""
class PeopleFinder:

    def __init__(self):
        pass

    def get_soup(self, url):
        response = requests.get(url)
        return  BeautifulSoup(response.text, "lxml")


    def calculateAge(self, born):
        today = date.today()
        born = datetime.strptime(born, '%m-%d-%Y').date()
        try:
            birthday = born.replace(year=today.year)

            # raised when birth date is February 29
        # and the current year is not a leap year
        except ValueError:
            birthday = born.replace(year=today.year,
                                    month=born.month + 1, day=1)

        if birthday > today:
            return today.year - born.year - 1
        else:
            return today.year - born.year


   #mm-dd-yyyy age
    def query(self, fst_name , mdl_name , lst_name, dob , city , state, zip):

        #Searching for a person
        search_url = "https://www.truepeoplesearch.com/results?name="
        search_name = fst_name+" "+mdl_name+" "+lst_name
        search_name = search_name.strip()
        serach_citystatezip = city +" "+ state +" "+ zip
        serach_citystatezip = serach_citystatezip.strip()
        age = self.calculateAge(dob)
        search_url = search_url + search_name + "&citystatezip=" + serach_citystatezip + "&agerange=" +str(age)+"-"+str(age)
        search_url = search_url.replace(" ","%20")
        print(search_url)

        #creating soup object for search page
        soup_searchpage = self.get_soup(search_url)
        first_match = soup_searchpage.find_all("a", {'aria-label' : "View All Details"})
        first_match = first_match[0]
        details_url = first_match['href']
        details_url = "https://www.truepeoplesearch.com" + details_url

        print(search_url)
        print(details_url)

        #creating soup objects for details page
        # response_details = requests.get(details_url)
        soup_detailspage = self.get_soup(details_url)#BeautifulSoup(response_details.text, "lxml")


        person =dict()

        #name
        span1 = soup_detailspage.find("span", {'class' : 'h2'})
        # lines = [span.get_text() for span in spans]
        name = span1.get_text()
        print("Name :" + name)
        person['Name'] = name
        print('-------------------------')


        #age
        span2 = soup_detailspage.find("span", {'class' : 'content-value'})
        age = span2.get_text().split()[-1]
        print("Age "+ age)
        person['Age'] = age
        print('-------------------------')


        #email_addresses
        print("Email Addresses:")
        email_add_lst =[]
        for lvl1 in soup_detailspage.find_all('div', {'class': 'row pl-md-3'})[3].find_all('div', {'class': 'row pl-sm-2'}):
            for lvl2 in lvl1.find_all('div', {'class': 'col'}):
                for email in lvl2.find_all('div', {'class': 'content-value'}):
                  email_add_lst.append(email.get_text())
                  print(email.get_text())
        person['email_add_lst'] = email_add_lst
        print('-------------------------')

        #phone numbers
        print("Phone Numbers:")
        phone_num_list =[]
        phone_numbers = soup_detailspage.find_all('a', {'data-link-to-more': 'phone'})
        for phone_number in phone_numbers:
            phone_num_list.append(phone_number.get_text())
            print(phone_number.get_text())
        person['phone_num_list']=phone_num_list
        print('-------------------------')


        #Associated Names
        print("Associated Names:")
        associated_Names_lst= []
        associated_Names = soup_detailspage.find_all('a', {'data-link-to-more': 'aka'})
        for associated_Name in associated_Names:
            associated_Names_lst.append(associated_Name.get_text())
            print(associated_Name.get_text())

        person['associated_Names_lst']= associated_Names_lst
        print('-------------------------')

        # Addresses
        addresses = soup_detailspage.find_all("a", {'data-link-to-more' : 'address'})
        curr_address = addresses[0].get_text()
        person['curr_address'] = curr_address
        print("Current Address is:" + curr_address )
        print("\nPast  Addresses:")
        past_add_dict ={}
        for address in addresses[1:]:
            print(address.get_text())
            test = address.find_next('span')
            print(test.get_text())
            past_add_dict[str(address)] = test.get_text()
        person['past_add_dict']= past_add_dict
        print('-------------------------')

        #Possible Relatives
        print("Possible Relatives:")
        relative_lst =[]
        relatives = soup_detailspage.find_all('a', {'data-link-to-more': 'relative'})
        for relative in relatives:
            relative_lst.append(relative.get_text())
            print(relative.get_text())
        person['relative_lst']=relative_lst
        print('-------------------------')

        #Possible Associates
        print("Possible Associates:")
        associates_lst=[]
        associates = soup_detailspage.find_all('a', {'data-link-to-more': 'associate'})
        for associate in associates:
            associates_lst.append(associate.get_text())
            print(associate.get_text())

        person['associates_lst'] = associates_lst
        print('-------------------------')

        # Possible Businesses
        print("Possible Businesses")
        div_poss_bs = soup_detailspage.find_all('div', {'class': 'row pl-md-3'})
        possible_bussines_lst =[]
        if len(div_poss_bs) >= 8:
            for lvl1 in soup_detailspage.find_all('div', {'class': 'row pl-md-3'})[8].find_all('div', {'class': 'row pl-sm-2'}):
                for lvl2 in lvl1.find_all('div', {'class': 'col'}):
                    for business in lvl2.find_all('div', {'class': 'content-value'}):
                      possible_bussines_lst.append(business.get_text())
                      print(business.get_text())
        person['poss_bussines_lst'] = possible_bussines_lst

        app_json = json.dumps(person)
        print(app_json)





def main():
    # c = PeopleFinder()
    first_name=input("Enter First Name - ")
    middle_name = input("Enter Middle Name - ")
    last_name=input("Enter Last Name - ")

    dob=input("Enter Date of Birth(mm-dd-yy) - ")
    city=input("Enter City - ")
    state = input("Enter State -")
    zip = input("Enter zip code -")

    print(first_name)
    print(middle_name)
    print(last_name)
    print(dob)
    print(city)
    print(state)
    print(zip)

    c = PeopleFinder()
    person_details = c.query(first_name , middle_name , last_name, dob , city , state, zip)
    print(person_details)




if __name__ == '__main__':
    main()