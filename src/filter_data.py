

import pandas as pd


def parse_gg_sheet(url):
    print("Parsing Google Sheet:", url)
    url = url.replace("edit#gid=", "export?format=csv&gid=")
    df = pd.read_csv(url, on_bad_lines="warn")
    return df

import nltk
from nltk.stem import WordNetLemmatizer

nltk.download('wordnet')
nltk.download('omw-1.4')
lemmatizer = WordNetLemmatizer()




VERIFIED_REQUESTS_URL = (
    "https://docs.google.com/spreadsheets/d/1PXcAtI5L95hHSXAiRl3Y4v5O4coG39S86OTfBEcvLTE/edit#gid=0"
)
REQUESTS_URL = "https://docs.google.com/spreadsheets/d/1gYoBBiBo1L18IVakHkf3t1fOGvHWb23loadyFZUeHJs/edit#gid=966953708"
INTERVENTIONS_URL = (
    "https://docs.google.com/spreadsheets/d/1eXOTqunOWWP8FRdENPs4cU9ulISm4XZWYJJNR1-SrwY/edit#gid=2089222765"
)


PHRASE_NO_PROBLEMS = ['got food',
                      'got food and clothes',
                     'got food and covers']

KEYS_HOUSE = [
    "shelters",
    "mattresses",
    "pillows",
    "blankets",
    "shelter",
    "tentes",
    "housing",
    "couvertures",
    "tents",
    "covers",
    "sdader",
    "housing_shelter",
]
KEYS_FOOD = [
    "groceries",
    "nouriture",
    "food",
    "water",
    "gaz",
    "dishes",
    "oil",
    "sugar",
    "tea",
    "hungry",
]
KEYS_CLOTHES = [
    "clothes",
    "clothing",
    "hygiene",
]
KEYS_MEDICAL = [
    "betadine",
    "medical",
    "diabetics",
    "medicaments",
    "diabetes",
    "doliprane",
    "vitamines",
    "drugs",
]

lemmatize_house = [lemmatizer.lemmatize(word) for word in KEYS_HOUSE]
lemmatize_food = [lemmatizer.lemmatize(word) for word in KEYS_FOOD]
lemmatize_clothes = [lemmatizer.lemmatize(word) for word in KEYS_CLOTHES]
lemmatize_medical = [lemmatizer.lemmatize(word) for word in KEYS_MEDICAL]







df= parse_gg_sheet(VERIFIED_REQUESTS_URL)
df

from typing import List
from enum import Enum


class HelpCategory(Enum):
    HOUSE = 'house'
    FOOD = 'food'
    CLOTHES = 'clothes'
    MEDICAL = 'medical'
    UNKNOW = 'unknow'


def to_category(text: str) -> List[HelpCategory]:
    if text in PHRASE_NO_PROBLEMS:
        return []

    words = text.split()
    categories = []
    for word in words:
        if word in KEYS_HOUSE:
            categories.append(HelpCategory.HOUSE)
        elif word in KEYS_FOOD:
            categories.append(HelpCategory.FOOD)
        if word in KEYS_CLOTHES:
            categories.append(HelpCategory.CLOTHES)
        if word in KEYS_MEDICAL:
            categories.append(HelpCategory.MEDICAL)
        if lemmatizer.lemmatize(word) in lemmatize_house:
            categories.append(HelpCategory.HOUSE)
        if lemmatizer.lemmatize(word) in lemmatize_food:
            categories.append(HelpCategory.FOOD)
        if lemmatizer.lemmatize(word) in lemmatize_clothes:
            categories.append(HelpCategory.CLOTHES)
        if lemmatizer.lemmatize(word) in lemmatize_medical:
            categories.append(HelpCategory.MEDICAL)
    if len(categories) == 0:
        categories = [HelpCategory.UNKNOW]
    return categories


def clean(text: str) -> str:
    text = text.replace('Housing/Shelter', 'housing_shelter')
    text = text.replace('/', ',')
    text = text.lower()
    text = text.strip()
    return text


def to_list(text: str) -> List[str]:
    helps = text.split(',')
    helps = [help_string.replace('.', ' ').strip() for help_string in helps]
    return helps


def help_text_to_help_category(helps: List[str]) -> List[str]:
    all_categories = set()
    for help_string in helps:
        categories = to_category(help_string)
        all_categories.update(categories)
    return list(all_categories)



flatten_list = lambda lst: [item for sublist in lst for item in sublist]
df['help_category'] = df['Help Details'].apply(clean).apply(to_list).apply(help_text_to_help_category)
need = df.groupby('Location Details')['help_category'].apply(list).apply(flatten_list).apply(lambda x: list(set(x)))
need[10:20]

degree_score = {'High': 9, 'Medium': 3, 'Low': 1}


def aggregate_degree(degrees):
    total_score = sum([degree_score[degree] for degree in degrees])
    if total_score >= 9:
        return 'High'
    if total_score >= 3:
        return 'Medium'
    else:
        return 'Low'


emergency_degree = df.groupby('Location Details')['Emergency Degree'].apply(list).apply(aggregate_degree)
emergency_degree[10:20]

def filter_category(category:HelpCategory, request:pd.DataFrame)-> pd.DataFrame:
    in_category = request['help_category'].apply(lambda x : category in x)
    return request[in_category]



import datetime
current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
request['Horodateur'].fillna(current_time, inplace=True)








def calculate_score(row):
    current_time = datetime.datetime.now()
    delta = current_time - row['Horodateur']
    base_score = delta.total_seconds() / 60

    text_score = get_text_score(row)

    temp_score = get_score_temp(row)

    return base_score + text_score + temp_score

def get_temp(lat, lon):
  url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}'

  response = requests.get(url)

  if response.status_code == 200:
      data = response.json()
      temp = sum([single_point['main']['temp_min'] for single_point in data['list']])/40
  else:
      print(f'Error: Unable to fetch weather data. Status code: {response.status_code}')
  return temp

NEED_COL =  'ما هي احتياجاتك؟ (أضفها إذا لم يتم ذكرها)'
COOR_COL = 'هل يمكنك تقديم الإحداثيات الدقيقة للموقع؟ (ادا كنت لا توجد بعين المكان) متلاً \n31.01837503440344, -6.781405948842175'

def get_text_score(row):
    score = 0

    need = row[NEED_COL]
    needs = need.split(' ')
    if 'وماء' in needs:#water
      score += 500
    if 'طعام' in needs:#food
      score += 500
    if 'إغاثة' in needs:#secours
      score+=500
    if 'لنقود' in needs: #secours
      score += 500
    if 'الخيام' in needs: #tent
      score += 500
    if 'ولملابس' in needs:#clothes
      score += 250
    if 'الأغطية' in needs: #covers
      score += 250
    if 'أفرشة' in needs: #matress
      score+=100

    return score

def get_score_temp(row):
    score = 0
    need = row[NEED_COL]
    needs = need.split(' ')
    # tent, clothes or cover
    if ('الخيام' not in needs) and ('ولملابس' not in needs) and ('الأغطية' not in needs):
      return score


    lat, lon = row[COOR_COL].split(',')
    lon = lon.strip()
    lat = lat.strip()

    average_temp = get_temp(lat, lon)
    if average_temp < 283:
        score += 1000
    if average_temp < 273:
        score += 1000
    return score

def sort_request(requests):

    scores = []
    for index, row in requests.iterrows():
        scores.append(calculate_score(row))

    requests['score'] = scores

    requests = requests.sort_values(by='score', ascending=False)

    return requests

request= parse_gg_sheet(REQUESTS_URL)
sort_request(request)






