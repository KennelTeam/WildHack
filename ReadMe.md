# WildHack

This project was created during the [WildHack hackathon](https://wildhack.croc.ru/)

The task this project solving is processing and classifing news about Kamchatka.

As input data we receivedseveral thousands of news and as output we were required to structurize this news in a way that future newswriters could access the desired news easier.

We checked these news sites:
- kam-kray.ru
- kamtoday.ru
- kamchatinfo.com
- kam24.ru
- kronoki.ru

And decided to use kamtoday.ru

## How to use

1. Clone this repo
2. Run the website/website.py using Flask
3. Go to the address you will receive in the terminal and use program!

### Ther are 2 modes

1. _Groups_ - classified news. You can see keywords for each news group in the square colored picture. Click on news card to see detailed description. Also you can search and filter news by desired keywords
2. _Cards_ - news are grouped by the year of publish. You can apply filters and click on news cards to see detailed description. _Search_ on this page doesn't work because it requires _ElasticSearch_ to be set up on your server.

## Programmactic part

Server is made on Flask framework

There are several interesting scripts like `kamtoday.py` which grab data from news site and prepare it.

Classification is made with `tf-idf` filter and then `KMeans` classifier.

Have a look at [colab notebook](https://colab.research.google.com/drive/18Kakud9rQpDo_VgJIbyFFCPMSnvaNEg-?usp=sharing) with classification code and the [presentaion](https://docs.google.com/presentation/d/1PqP1uVA8vBgd9AlNu2eSRM5doshSacsFs_yB_8JtCgY/edit#slide=id.g1063036f9c7_2_77) of the project (in russian).
