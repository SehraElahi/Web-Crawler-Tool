from bs4 import BeautifulSoup
import requests
from collections import Counter
import re
from pprint import pprint
import time
import json
import collections
import os
import yaml

url = "http://example.webscraping.com"

elim_tup = ("http://example.webscraping.com/places/default/iso/", "http://example.webscraping.com/places/default/edit/")

elim_tup2 = ("http://example.webscraping.com/places/default/user/login?_", "http://example.webscraping.com/places/default/user/register?_", "http://example.webscraping.com/places/default/index/0")

global_links = ["http://example.webscraping.com/places/default/index"]
store_index = []


while True:
    input_string = input('\n\n*****************************************\nThe Following commands are available:\n- build\n- load\n- print word\n- find word(s)\n- exit\nPlease type your response: ')

    input_list = input_string.split()

####################################################################
#                              BUILD
####################################################################
    if input_list[0] == 'build':
        #creating a list of URLs by extracting them though web crawling
        print ("\n***** Crawling the Web for you *****\n          Please wait...\n")

        for link in global_links:
            link_source = requests.get(link).text
            link_soup = BeautifulSoup(link_source, 'html.parser')
            for tag in link_soup.find_all('a', href=True):
                url_path = tag['href']
                full_url =  url + url_path

                if url_path != "#" and full_url not in global_links and not full_url.startswith(elim_tup):
                    # print(full_url)
                    global_links.append(full_url)
            time.sleep(5)
        all_links_result = [elem for elem in global_links if not elem.startswith(elim_tup2)]
        with open ('find_URL_pages.txt', 'w') as ff:
            for item in all_links_result:
                ff.write("%s\n" % item)
#######################################################################
        # creating inverted index
        #
        print("***** Building the Index for you now *****\n         Please remain Patient.")
        for link in all_links_result:
            doc_number = all_links_result.index(link)

            source = requests.get(link).text
            soup = BeautifulSoup(source, 'html.parser')
            # print(soup.prettify())

            for script in soup.find_all('script', src=False):
                script.decompose()
            text_list = soup.get_text(" ").split()
            # print(text_list)

            reg = ([re.sub(r"[^a-zA-Z]", "", text) for text in text_list])
            c_dic= dict((Counter(reg)))

            ignore = ['', 'faAFpsuzAFtk', 'arBHenfaur', 'AZdAZAZdAZAZdAZAZdAZAZdAZdAZAZdAZdAZGIRAA']
            for word in ignore:
                if word in c_dic:
                    del c_dic[word]

            for i, j in c_dic.items():
                test = ({'Word':i, 'Frequency':j, 'Document':doc_number})
                store_index.append(test)
                # print(test)
            time.sleep(5)

        newlist = sorted(store_index, key=lambda k: k['Frequency'], reverse=True)
        # pprint(newlist)
        with open('inverted_index.json', 'w+') as fp:
            json.dump(newlist, fp, indent = 4)
        print("\n***** Index Successfully Created! *****")

####################################################################
#                              LOAD
####################################################################
    elif input_list[0] == 'load':
        if os.path.getsize("inverted_index.json") and os.path.getsize("find_URL_pages.txt"):
            with open("inverted_index.json") as f:
                loaded_index = json.load(f)
            with open ("find_URL_pages.txt") as of:
                lines = of.readlines()
            print("\n\n***** Index Successfully loaded *****\n")
        else:
            print("\n***** Error occured while loading the files! *****\n Please use the 'build' command first to generate the necessary files!\n")

####################################################################
#                              PRINT
####################################################################
    elif input_list[0] == 'print':
        if len(input_list) == 2:
            storage = []
            word = input_list[1]
            try:
                loaded_index
            except NameError:
                print("\nPlease use the 'load' command to load the Inverted Index first!\n")
            else:
                for i in loaded_index:
                    if i['Word'] == word:
                        test2 = ({'Word':i['Word'], 'Frequency':i['Frequency'], 'Document':i['Document']})
                        storage.append(test2)

                if not storage:
                    print("\n\n***** Word not in Index! *****\n")
                else:

                    print("\n***** Following index Found for '" + word +"' *****\n\n" + yaml.dump(storage))
        else:
            print('\nIncorrect command! Try "print word" for a single word instead.')

####################################################################
#                              FIND
####################################################################
    elif input_list[0] == 'find':
        if  1 < len(input_list) <= 4:
            docnums = []
            cntr = 0
            try:
                loaded_index
            except NameError:
                print("\nPlease use the 'load' command to load the Inverted Index first!\n")
            else:
                for word in range(1,len(input_list)):
                    for i in loaded_index:
                        if i['Word'] == input_list[word]:
                            # print(input_list[word])
                            n = i['Document']
                            docnums.append(n)
                # pprint(docnums)

                # pprint(dict(Counter(docnums)))
                print("\n***** Top Results Found *****\n\n")
                if dict(Counter(docnums)) == {}:
                    print("\n       No such page found!\n")
                else:
                    for i, j in dict(Counter(docnums)).items():
                        if len(input_list) == 2 and j==1:
                            cntr +=1
                            print(str(cntr) +": " + lines[i].rstrip('\n'))
                            # break
                        elif len(input_list) == 3 and j==2:
                            cntr +=1
                            print(str(cntr) +": " + lines[i].rstrip('\n'))
                        elif len(input_list) == 4 and j==3:
                            cntr +=1
                            print(str(cntr) +": " + lines[i].rstrip('\n'))

                print("\n")
        elif len(input_list) == 1:
            print ('\nTry "find word(s)" - up to three words allowed.')
        else:
            print('\nIncorrect command! Try "find word(s)" - up to three words allowed.')
####################################################################
#                              EXIT
####################################################################
    elif input_list[0] == 'exit':
        print('***** Goodbye *****')
        break
    else:
        print('\nInvalid syntax! Select from the Commands available!\n')
####################################################################
