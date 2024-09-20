import glob
import json
import os
import random

import torch
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from mecab import MeCab
from preprocessing.repository.interview_preprocessing_repository import InterviewPreprocessingRepository

class InterviewPreprocessingRepositoryImpl(InterviewPreprocessingRepository):
    __instance = None

    torch.manual_seed(42)
    np.random.seed(42)
    random.seed(42)
    sentenceTransformer = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def readJsonFile(self, filePath='assets/raw_json_data/'):
        os.makedirs(filePath, exist_ok=True)
        jsonFiles = glob.glob(os.path.join(filePath, '**', '*.json'), recursive=True)
        dataList = []
        for file_path in jsonFiles:
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    dataList.append(data)
                except json.JSONDecodeError as e:
                    print(f"Error reading {file_path}: {e}")
        return dataList

    def extractColumns(self, rawDataList):
        extractedData = {}

        for data in rawDataList:
            info = data['dataSet']['info']
            infoKey = '_'.join(list(info.values()))

            if infoKey not in extractedData:
                extractedData[infoKey] = []

            extractedData[infoKey].append({
                'question': data['dataSet']['question']['raw']['text'],
                'answer': data['dataSet']['answer']['raw']['text'],
                'occupation': data['dataSet']['info']['occupation'],
                'gender': data['dataSet']['info']['gender'],
                'ageRange': data['dataSet']['info']['ageRange'],
                'experience': data['dataSet']['info']['experience'],
            })
        return extractedData

    def separateFileByInfo(self, extractedData):
        os.makedirs('assets/interview', exist_ok=True)

        for info_key, data in extractedData.items():
            filename = f'assets/interview/{info_key}.json'
            with open(filename, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
        print('Saved at assets/interview/*')

        return True

    def loadMecab(self):
        mecab = MeCab()
        return mecab

    def posTagging(self, mecab, text):
        posTagging = mecab.pos(text)
        # print(posTagging)
        # 일반 명사,
        return posTagging

    def filterWord(self, posTagging):
        # targetTags = ['NNG']
        targetTags = ['NNG', 'NNP', 'VV', 'VA']

        # 특정 태그에 포함된 단어들만 리스트에 저장
        filteredWords = [word for word, tag in posTagging if any(t in tag for t in targetTags)]
        # print(list(set(filtered_words)))
        return list(set(filteredWords))

    def calculateCosineSimilarity(self, filteredAnswer, filteredQuestion):
        # sentenceTransformer = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

        filteredAnswerString = ' '.join(filteredAnswer)
        filteredQuestionString = ' '.join(filteredQuestion)

        embeddingAnswer = self.sentenceTransformer.encode(filteredAnswerString)
        embeddingQuestion = self.sentenceTransformer.encode(filteredQuestionString)

        cosineSimilarity = cosine_similarity([embeddingAnswer], [embeddingQuestion])

        return cosineSimilarity