from bs4 import BeautifulSoup
import requests
from datetime import date
from datetime import datetime
import json
import pathlib





class PeopleFinder:

    def __init__(self):
        pass
    # Creating soup object
    def get_soup(self, url):
        response = requests.get(url)
        return  BeautifulSoup(response.text, "lxml")

   # Calculating Age
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


    #--------------------------------------
    #Takes in first Namr, Last Name, Date of Birth(mm-dd-YYYY), City, Satea nd Zip
    #--------------------------------------
    def query(self, fst_name , mdl_name , lst_name, dob , city , state, zip):

        #Searching for a person
        #URL fromation
        url = "https://www.truepeoplesearch.com"
        search_name = fst_name.strip()+" "+mdl_name.strip()+" "+lst_name.strip()
        search_name = search_name.strip()
        if(search_name is None) | (search_name == ''):
            print("Last name is required")
            return
        url = url +"/results?name="+ search_name
        search_citystatezip = city.strip() +" "+ state.strip() +" "+ zip.strip()
        search_citystatezip = search_citystatezip.strip()

        if(search_citystatezip is not None) & (search_citystatezip != ""):
            url = url + "&citystatezip=" + search_citystatezip

        if (dob is not None) & (dob != ""): # should apply regex
          age = self.calculateAge(dob.strip())
          url = url + "&agerange=" + str(age) + "-" + str(age)


        # url = url + search_name + "&citystatezip=" + search_citystatezip + "&agerange=" + str(age) + "-" + str(age)
        url = url.replace(" ", "%20")
        print(url)


        #creating soup object for search page
        soup_searchpage = self.get_soup(url)
        first_match = soup_searchpage.find_all("a", {'aria-label' : "View All Details"})

        #checking if  null records or errors have been returned
        if len(first_match) == 0:
            countdiv = soup_searchpage.find("div", {'class': "row pl-1 record-count"})
            errorduv = soup_searchpage.find("span", {'class': "alert alert-danger error-message"})
            if  (countdiv is not None):
                if len(countdiv)!=0:
                    alertspan = countdiv.find("div", {"class": "col"})
                    print(alertspan.get_text())
                    return None
            elif errorduv is not None :
                if(len(errorduv) != 0 ):
                    alertspan = soup_searchpage.find("span", {'class': "alert alert-danger error-message"})
                    print(alertspan.get_text())
                    exit()
            else:
                print("Please Check the website manually once. There could be a bot withholding progress!")
                exit()


        elif first_match is None:
            print("Please Check the website manually once, There could be a bot withholding progress!")

        print(soup_searchpage)


        first_match = first_match[0]
        details_url = first_match['href']
        details_url = "https://www.truepeoplesearch.com" + details_url

        print(url)
        print(details_url)

        #creating soup objects for details page
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
        temp1 = soup_detailspage.find_all('div', {'class': 'row pl-md-3'})
        # temp2 = temp1.find_all('div', {'class': 'row pl-sm-2'})
        if len(temp1) >= 4:
            temp2 = temp1[3].find_all('div', {'class': 'row pl-sm-2'})
            if len(temp2) != 0:
                for lvl1 in temp2 :
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
        print(len(phone_numbers))
        if ((phone_numbers is not None) & (len(phone_numbers) != 0)):
            for phone_number in phone_numbers:
                phone_num_list.append(phone_number.get_text())
                print(phone_number.get_text())
        person['phone_num_list']=phone_num_list
        print('-------------------------')

        #Associated Names
        print("Associated Names:")
        associated_Names_lst= []
        associated_Names = soup_detailspage.find_all('a', {'data-link-to-more': 'aka'})
        if ((associated_Names is not None) & (len(associated_Names) != 0)):
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
        if (len(addresses) >= 2 ):
            for address in addresses[1:]:
                print(address.get_text())
                dt = address.find_next('span')
                print(dt.get_text())
                past_add_dict[str(address)] = dt.get_text()
        person['past_add_dict']= past_add_dict
        print('-------------------------')

        #Possible Relatives
        print("Possible Relatives:")
        relative_lst =[]
        relatives = soup_detailspage.find_all('a', {'data-link-to-more': 'relative'})
        if ((relatives is not None) & (len(relatives) != 0)):
            for relative in relatives:
                relative_lst.append(relative.get_text())
                print(relative.get_text())
        person['relatives_lst']=relative_lst
        print('-------------------------')

        #Possible Associates
        print("Possible Associates:")
        associates_lst=[]
        associates = soup_detailspage.find_all('a', {'data-link-to-more': 'associate'})
        if((associates is not None) & (len(associates) != 0)):
            for associate in associates:
                associates_lst.append(associate.get_text())
                print(associate.get_text())

        person['associates_lst'] = associates_lst
        print('-------------------------')

        # Possible Businesses
        print("Possible Businesses")
        div_poss_bs = soup_detailspage.find_all('div', {'class': 'row pl-md-3'})
        possible_bussines_lst =[]
        if len(div_poss_bs) >= 9:
            for lvl1 in soup_detailspage.find_all('div', {'class': 'row pl-md-3'})[8].find_all('div', {'class': 'row pl-sm-2'}):
                for lvl2 in lvl1.find_all('div', {'class': 'col'}):
                    for business in lvl2.find_all('div', {'class': 'content-value'}):
                      possible_bussines_lst.append(business.get_text())
                      print(business.get_text())
        person['poss_bussines_lst'] = possible_bussines_lst


        data_lst = [] #storing data as a list of json objects
        path = pathlib.Path('Data/Data.json')
        # if file is not present create a file else extract the data and append the new data
        try:
            if (not path.exists()) & (not path.is_file()):
                with open("Data/Data.json", "a+") as f:
                    data_lst.append(person)
                    f.write(json.dumps(data_lst))
            else:
                with open("Data/Data.json", "r+") as f:
                    data_lst = json.load(f)
                    data_lst.append(person)
                    f.seek(0)
                    f.write(json.dumps(data_lst))
                    f.truncate()

        except IOError:
          print('An error occurred trying to read the file.')







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
    # print(person_details)




if __name__ == '__main__':
    main()
