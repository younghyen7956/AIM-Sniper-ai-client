import os

import httpx
import openai
from openai import OpenAI
from dotenv import load_dotenv

from interview_preprocessing.repository.interview_preprocessing_openai_repository import \
    InterviewPreprocessingOpenAIRepository

load_dotenv()
openaiApiKey = os.getenv('OPENAI_API_KEY')
if not openaiApiKey:
    raise ValueError("API KEY가 준비되어 있지 않습니다!")

client = OpenAI(api_key=openaiApiKey)


class InterviewPreprocessingOpenAIRepositoryImpl(InterviewPreprocessingOpenAIRepository):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def generateIntent(self, question):
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistance for labeling intent of question."},
                {"role": "user",
                 "content": """
                    [Question] """+question+"""
                    
                    [Note]
                    1. Only one intent is extracted.
                    2. The intent is selected from ['협업 능력', '적응력', '대처 능력', '프로젝트 경험', '자기 개발', '기술적 역량'].
                    3. '협업 능력' refers to the intent of understanding the role a person has played within an organization.
                    4. '적응력' refers to the intent of assessing how well a person can adjust to new situations.
                    5. '대처 능력' refers to the intent of understanding how a person handles crises or conflicts.
                    6. '프로젝트 경험' refers to the intent of understanding the types of projects a person has worked on, but if the question is about what role they played in the project, the intent is '협업 능력'.
                    7. '자기 개발' refers to the intent of assessing the person’s study plans, future goals, and personal learning strategies.
                    8. '기술적 역량' refers to the intent of assessing the person's abilities in programming languages, analysis, development processes, and operating systems.
                    9. The output must be one of the words from the given intents, with no additional explanation—only the word written by korean.
                    10. If there is no matching intent, output null.
                """
                 }
            ]
        )
        return response.choices[0].message.content.strip()

    def getTechKeyword(self, role):
        question = f"{role}가 알아야 할 핵심 기술 50가지를 알려줘."
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"너는 {role}야."},
                {"role": "user",
                 "content": f'{question} output은 "키워드<s>키워드<s>키워드<s>...키워드" 형식으로만 작성해줘.'
                 }
            ]
        )
        return response.choices[0].message.content.strip()

    def getTechAnswer(self, question, score, job):
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"너는 {job} 엔지니어야."},
                {"role": "user",
                 "content":
                     """[Question] """ + question +
                     f"""[Note]
                     1. [Question]에 대해 답변을 작성해줘.
                     2. 100점을 기준으로 했을 때 [Question]에 대해 {score}점짜리 답변을 작성해줘.
                     3. 또한 네가 100점이라고 생각하는 Answer를 제공해줘.
                     4. 예시를 제시할게.
                     [Question] 회사 입장에서는 페어 프로그래밍이 필요합니다 장점이 무엇이고 또 본인이 할 수 있는 역량에 대해 설명해 보시죠.
                     answer:우선 어떤 피씨 한 대를 줄일 수 있는 그런 효과도 있는 것 같습니다. 페어 프레이밍을 할 때는 개발할 수 있는 컴퓨터 한 대에서 두 사람이 동시에 작업을 하니까 한 사람이 먼저 선행한 작업 또 뒤에 한 사람이 또 다른 작업 선행 이렇게 모아서 한 프로그램을 만들 수 있는 그런 좋은 것이라고 생각합니다. 페어 프레이밍의 장점은 한 피씨 안에서 개발할 수 있는 한 피씨 안에서 두 사람이 동시에 작업을 이어갈 수 있다는 것입니다. 그렇게 함으로써 어떤 손실이나 어떤 만들었을 때 오류 같은 것을 방지할 수도 있고 각자 또 하는 어떤 프로그램의 작업이 잘 이루어질 수 있다고 봅니다. 또 페어 프로그램을 통해서 개발하는 모든 프로그램들은 훨씬 더 견고하게 만들어질 수 있고 또 생 다른 사람의 생각과 어떤 것이 따로 잘 정립될 수 있는 그런 하나의 수단이기 때문에 저는 훨씬 더 좋은 프로그램을 만들 수 있다고 생각합니다. 그리고 그렇게 함으로써 동시에 많은 작업이 수 수행할 수 있는 그런 어떤 이점도 있다고 생각합니다. 그래서 페어 프로그램밍은 우리가 잘 사용하고 또 할 수 있는 그런 하나의 어떤 방법이 아닌가 그렇게 생각합니다. 그래서 이 방법을 잘 활용하고 잘 이용한다면 좋은 성과를 낼 수 있다고 생각합니다
                     <s>feedback:답변에서 페어 프로그래밍의 장점에 대한 설명이 있지만, 내용이 다소 중복되고 모호하게 표현되어 있습니다. 페어 프로그래밍이 어떻게 개발 과정에서 효과적으로 작용하는지에 대한 구체적인 예시나 개인의 역량에 대한 서술이 부족합니다. 좀 더 명확하고 구체적인 내용을 제시하는 것이 좋겠습니다.
                     <s>alternative_answer:페어 프로그래밍의 가장 큰 장점은 두 명의 개발자가 서로 협력하면서 코드 품질을 높일 수 있다는 것입니다. 한 사람의 코드가 다른 사람에 의해 즉시 검토되어 오류를 빠르게 발견할 수 있고, 다양한 관점을 반영한 설계가 가능합니다. 또한, 페어 프로그래밍은 업무의 공유와 지식 전이에도 큰 도움이 됩니다. 저는 팀 작업에서의 원활한 소통과 협업 능력을 통해 이러한 개발 환경을 잘 활용할 수 있습니다.
                     5. output은 "answer:~<s>feedback:~<s>example:~" 형식으로만 출력해줘.
                     """

                 }
            ]
        )
        return response.choices[0].message.content.strip()

    def scoreAnswer(self, question, intent, answer):
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 면접 대상자의 답변을 채점하는 유용한 채용 담당자야."},
                {"role": "user",
                 "content":
                f"""[Question]{question} 
                    [Intent]{intent} 
                    [Answer]{answer}
                    [Note]
                    1. [Answer]는 면접관이 면접 대상자의 [Intent]를 파악하기 위한 [Question]에 대한 면접 대상자의 답변이야.
                    2. 면접자가 면접관의 질문에 대해 얼마나 잘 대답했는지를 1~100점으로 채점하고, 답변에 대한 feedback을 제공해줘.
                    3. 답변에 아쉬운 점이 존재한다면 점수를 낮게 주었으면 해.
                    3. output은 "score:~점<s>feedback:답변에 대한 피드백"처럼 각각을 "<s>"로 분리하여 생성해줘.
                """
                 }
            ]
        )
        return response.choices[0].message.content.strip()

    def generateQAS(self, beforeQuestion, beforeAnswer, intent, percent): # 20 30 50
        if intent == '프로젝트 경험':
            context = '"프로젝트 경험"을 파악하기 위한 질문은 지원자가 프로젝트 경험을 설명하게 하기 위한 질문이야. 따라서, 프로젝트 진행 중에 발생한 문제나 어려움, 지원자의 역할 및 기여도가 아닌, 그 프로젝트가 어떤 내용이었는지를 중점적으로 설명하도록 유도하는 질문이어야 해.'
        else:
            context = ('질문 생성시 "프로젝트 경험"을 파악하기 위한 것이 아니기 때문에 프로젝트 관련 질문을 하면 안돼.\n'
                       '예상 답변 생성시에도 프로젝트에 대한 언급은 최대한 제외하고 생성해줘.')

        if percent == 20 :
            answerText = '답변에 대한 채점 점수가 50점 미만으로 나오도록 조금 잘못된 답변을 생성해봐.'
        elif percent == 30:
            answerText = ' 답변에 대한 채점 점수가 65점 정도로 나오도록 조금 애매한 답변을 생성해봐'
        else:
            answerText = ''

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"너는 1:1 면접을 진행하는 면접관이야."},
                {"role": "user",
                 "content":
                 f"""질문 의도: ['자기 분석', '대처 능력', '소통 능력', '프로젝트 경험', '자기 개발']
                     이전 질문: "{beforeQuestion}"
                     이전 답변: "{beforeAnswer}"
                     [Note]
                     1. 질문 의도는 면접관이 질문해야 할 질문 리스트들이야. 이중 너는 {intent}에 관한 질문을 생성할 거야.
                     2. 이전 답변은 면접자가 이전 질문에 답변한 내용이야.
                     3. 질문 생성시 면접자의 이전 답변을 참고하여 만들어줘.
                     4. 단, 이전 질문과 유사하지 않고, 면접자의 "{intent}"을 파악할 수 있도록 면접 질문을 생성하고, 그 질문에 대한 예상 답변까지도 생성하고 그 답변에 대해 0~100점으로 채점하고, 답변에 대한 피드백도 함께 알려줘.
                     5. {context}
                     6. {answerText}
                     7. 질문, 예상 답변, 피드백은 각각 3문장으로 생성해줘. 
                     8. output은 "question:너가 생성한 질문<s>answer:질문에 대한 예상 답변<s>score:~점<s>feedback:답변에 대한 피드백"처럼 각각을 "<s>"로 분리하여 생성해줘.
                  """
                 }
            ]
        )
        return response.choices[0].message.content.strip()
