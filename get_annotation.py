import requests
from tqdm import tqdm
import json
import re
import argparse
import pandas as pd
from bs4 import BeautifulSoup
import os

    
def preprocess_texts(folder_name):
    with open("C:/Users/danie/Downloads/tagtog_AI_Tech_Car_data (1)/AI_Tech_Car_data/annotations-legend.json", 'r', encoding="UTF-8") as f:
        entity_map = json.load(f)
    folder_dir=os.path.join("C:/Users/danie/AI Tech/데이터제작/tagtog_AI_Tech_Car_data/AI_Tech_Car_data/ann.json/master/pool",folder_name)

    """
    tagtog documents 에 txt 파일들을 id로 가져옴
    가져온 data에 entity가 2개보다 적거나 많을 시(정상 데이터는 2개) 경고 알림 후 패스
    """
    txt_folder_dir = folder_dir.replace("ann.json/master","plain.html")
    matched_ids = os.listdir(txt_folder_dir)
    relation_map = {
        "r_42" : "org:top_members/employees",
        "r_53" : "org:product",
        "r_17" : "org:founded",
        "r_52" : "idv:component",
        "r_41" : "no_relation",
        "r_39" : "no_relation",
        "r_18" : "org:top_members/employees",
        "r_37" : "no_relation",
        "r_50" : "idv:feature",
        "r_22" : "idv:alternate_name",
        "r_36" : "no_relation",
        "r_40" : "no_relation",
        "r_51" : "org:feature",
        "r_38" : "no_relation",
        "r_38" : "no_relation",
        "r_32" : "idv:type",
        "r_16" : "org:city_of_headquarters"
    }
    sentences = []
    subject_entities = []
    object_entities = []
    labels = []
    untagged_ids=[]
    over_tagged_ids = []
    for id in tqdm(matched_ids):
        if not os.path.exists(os.path.join(folder_dir,id.replace("plain.html","ann.json"))):
            print(f"Error no id found in ann folder {id}")
            untagged_ids.append(id)
            continue
        with open(os.path.join(folder_dir,id.replace("plain.html","ann.json")), encoding="UTF-8") as f:
            ann_json = json.load(f)
        entity_types = ann_json["entities"]
        if len(entity_types) < 2:
            print(f"{id} entities may be miss tagged please check")
            untagged_ids.append(id)
            continue
        elif len(entity_types) > 2:
            print(f"{id} entities may be over tagged please check")
            over_tagged_ids.append(id)
            continue
        for i in range(2):
            type_info = entity_map[entity_types[i]["classId"]]
            type_info = re.split("_", type_info)
            word_info = entity_types[i]["offsets"][0]
            if type_info[0] == "SUB":
                sub_word = word_info["text"]
                sub_start_idx = int(word_info["start"])
                sub_end_idx = sub_start_idx + len(sub_word) - 1
                sub_type = type_info[1]
                if ann_json['relations']:
                    if ann_json['relations'][0]['classId'] != 'r_35' and ann_json['relations'][0]['classId'] != 'r_33':
                        relation = ann_json['relations'][0]['classId']
            else:
                obj_word = word_info["text"]
                obj_start_idx = int(word_info["start"])
                obj_end_idx = obj_start_idx + len(obj_word) - 1
                obj_type = type_info[1]
        subject_entity = f"{{'word':'{sub_word}','start_idx':{sub_start_idx},'end_idx':{sub_end_idx},'type':'{sub_type}'}}"
        subject_entities.append(subject_entity)
        object_entity = f"{{'word':'{obj_word}','start_idx':{obj_start_idx},'end_idx':{obj_end_idx},'type':'{obj_type}'}}"
        object_entities.append(object_entity)
        text_soup = BeautifulSoup(open(os.path.join(txt_folder_dir, id), encoding="utf8"), "html.parser")
        text_info = text_soup.select('pre')[0].text
        if not relation:
            print(f"{id} relation may be miss tagged please check")
        labels.append(relation_map[relation])
        sentences.append(text_info.strip())
    return {
        "sentence":sentences,
        "subject_entity":subject_entities,
        "object_entity":object_entities,
        "label":labels
    }#, sorted([re.search(r"[0-9]+.txt", uid).group(0) for uid in untagged_ids]),sorted([re.search(r"[0-9]+.txt", oid).group(0) for oid in over_tagged_ids])

def save_dataframe(folder_name):
    if folder_name == "all":
        for name in ["YC", "GU", "DI", "SH", "JD"]:
            save_dataframe(name)
        return
    dict_for_df = preprocess_texts(folder_name)
    df = pd.DataFrame(dict_for_df)
    df.to_csv(f"annotation_csvs_split_by_person_{folder_name}.csv", encoding="utf-8-sig")
    # with open(f"../untagged_texts/{folder_name}_untagged.txt","w",encoding="utf-8-sig") as f:
    #     f.write(str(untagged_ids))
    # with open(f"../over_tagged_texts/{folder_name}_over_tagged.txt","w",encoding="utf-8-sig") as f:
    #     f.write(str(over_tagged))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder_name", type=str, default="all", help="다운로드할 폴더(사람)의 이름 all 이면 모든 폴더 변환 default: all")
    args = parser.parse_args()
    save_dataframe(args.folder_name)
    print('OK!')