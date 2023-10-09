import numpy as np
import pandas as pd
import json
import math, pywikibot
from arywikibotlib import interlink_page_with_qid, has_wikipedia_article

SAVE_MESSAGE = "مقال تصاوب"


excel_file_path = 'Batch 1 final - Al Haouz Province.xlsx'
df = pd.read_excel(excel_file_path)

json_file_path = 'column_mapping.json' 
with open(json_file_path, 'r') as json_file:
    data = json.load(json_file)
    
letter_to_index = {chr(65 + i): i for i in range(26)}

def key_dicc(x):
    return letter_to_index[data[x]]

def village_count(x):
    s=0
    for i in range(0,df.shape[0]):
        if df.iloc[i, key_dicc('{fraction}')] == df.iloc[x, key_dicc('{fraction}')]:
            s=s+1
            
    return s


def calculate_max_value(*values):
    magnitude = max(values)
    power_of_10 = 10 ** int(math.log10(magnitude))
    max_value = math.ceil(magnitude / power_of_10) * power_of_10
    return max_value


def create_article_2004(x):

    return create_article(x,"template_x.txt")
    
def create_article_2014(x):

    return create_article(x,"template.txt")

def create_article(x,template_file):

    with open(template_file, "r", encoding="utf8") as f:
        text_code_source = str(f.read())
        
    
    for old_value, index_value in data.items():
        text_code_source = text_code_source.replace(old_value, str(df.iloc[x, letter_to_index[index_value]]))

    
    # {pop_change}
    if not str(df.iloc[i, key_dicc('{population}')]).lower()=='x':
        if df.iloc[x, key_dicc('{population}')] > df.iloc[x, key_dicc('{population_2004}')]:
            text_code_source = text_code_source.replace("{pop_change}", "تزاد")
        elif df.iloc[x, key_dicc('{population}')] < df.iloc[x, key_dicc('{population_2004}')]:
            text_code_source = text_code_source.replace("{pop_change}", "نقص")
        else:
            text_code_source = text_code_source.replace("{pop_change}", "ماتبدلش")
        
        # {population_increase_perc}
        population_increase_perc = 100 * abs(df.iloc[x, key_dicc('{population}')] - df.iloc[x, key_dicc('{population_2004}')]) / df.iloc[x, key_dicc('{population_2004}')]
        text_code_source = text_code_source.replace("{population_increase_perc}", "{:.1f}".format(population_increase_perc))
    
        # {fam_change}
        if df.iloc[x, key_dicc('{families}')] > df.iloc[x, key_dicc('{families_2004}')]:
            text_code_source = text_code_source.replace("{fam_change}", "تزاد")
        elif df.iloc[x, key_dicc('{families}')] < df.iloc[x, key_dicc('{families_2004}')]:
            text_code_source = text_code_source.replace("{fam_change}", "نقص")
        else:
            text_code_source = text_code_source.replace("{fam_change}", "ماتبدلش")
        
        # {families_increase_perc}
        families_increase_perc = 100 * abs(df.iloc[x, key_dicc('{families}')] - df.iloc[x, key_dicc('{families_2004}')]) / df.iloc[x, key_dicc('{families_2004}')]
        text_code_source = text_code_source.replace("{families_increase_perc}", "{:.1f}".format(families_increase_perc))
    
        # {marriage_perc}
        marriage_perc = 100 * (df.iloc[x, letter_to_index["Q"]] / df.iloc[x, key_dicc('{population}')])
        text_code_source = text_code_source.replace("{marriage_perc}", "{:.1f}".format(marriage_perc))
    
        # {families_max_value}
        families_max_value = calculate_max_value(df.iloc[x, key_dicc('{families}')], df.iloc[x, key_dicc('{families_2004}')])
        text_code_source = text_code_source.replace("{families_max_value}", str(families_max_value))
    
        # {population_max_value}
        population_max_value = calculate_max_value(df.iloc[x, key_dicc('{population}')], df.iloc[x, key_dicc('{population_2004}')])
        text_code_source = text_code_source.replace("{population_max_value}", str(population_max_value))

    
    # {village_count} 
    text_code_source = text_code_source.replace("{village_count}", str(village_count(x)))
    
    # {prov_type}
    text_code_source = text_code_source.replace("{prov_type}", "إقليم")
    #print("text_code_source",text_code_source)
    return text_code_source

if __name__ == '__main__':
    for i in range(0,df.shape[0]):
        name_final=df.iloc[i, key_dicc('{village_name}')]+' ('+df.iloc[i, key_dicc('{fraction}')]+')'
        print(f'*********{str(i+1)}/{str(df.shape[0])}************* : {str(name_final)}')
        site = pywikibot.Site()
        site.login()
        page = pywikibot.Page(site,name_final)
        temp_text = page.text

        qid = df.iloc[i, key_dicc('{qid}')]

        if not has_wikipedia_article(qid, site.lang):
            if temp_text.strip()=='':
                #print(df.iloc[i, key_dicc('{population}')])
                if str(df.iloc[i, key_dicc('{population}')]).lower()=='x':
                    text_adwwar=create_article_2004(i)

                    temp_text=text_adwwar

                else:
                    text_adwwar=create_article_2014(i)

                    temp_text=text_adwwar

                if temp_text != page.text:
                    page.text = temp_text
                    page.save(SAVE_MESSAGE)

                    interlink_page_with_qid(page, site.lang, qid, namespace="article")
        else:
            print(f"article for {name_final} already exists with qid {qid}")
