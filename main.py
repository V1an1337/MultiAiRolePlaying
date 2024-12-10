from zhipuai import ZhipuAI
import json
from datetime import datetime, timedelta
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename="server.log")

client = ZhipuAI(api_key="265cfaa4c09ba0b78b2b14c2c4e36eaa.XSKfczcMNsSJmwYG")
model = "GLM-4-PLUS"


def Update(name, character_info, other_character_info, memory,thought, field_perception, plan, time):
    Output_format = """
    你需要严格按照以下格式输出：
    {"Speak": <(extraAction(string, Optional)) + text(string,Optional）>,"Action": <action (string)>,"Facial expression": <Facial expression (string)>,"Thoughts": <Thoughts (string)>}
    以下是两个输出例子：
    {"Speak": "(无言)","Action": "向小明走去","Facial expression": "微笑","Thoughts": "小明在向我走来，我感到很高兴"}
    {"Speak": "(生气地附和小明)对啊小张，你不该胡乱扔垃圾的","Action": "抬起手指着小张，指责小张","Facial expression": "皱眉","Thoughts": "小张乱扔垃圾的行为我一定要制止！"}    
    """

    Other_field_perception = ""
    for characterName in Field_perception.keys():
        characterContent = Field_perception[characterName]
        characterTime = characterContent['Time']
        characterSpeak = characterContent['Speak']
        characterAction = characterContent['Action']
        characterFacialExpression = characterContent['Facial expression']

        Other_field_perception += f"""
        {characterName}在{characterTime}的时候：
        说了：{characterSpeak}
        动作：{characterAction}
        神态：{characterFacialExpression}
        """

    prompt = f"""
    你是一个角色扮演助手，你的任务是扮演角色'{name}'，你需要结合你的"记忆"，"感知"，"计划"三个板块并综合下做出一个决定，以下是详细要求：

    你需要严格按照以下格式输出(json)：
    · 言语（若不说话，则设置extraAction为"无言",并设置text为空）（你可以在extraAction中添加额外的动作，例如"附和某人","向某人说"）
    · 动作
    · 神态
    · 内心想法（详细）

    {Output_format}

    以下是你要扮演的人物的详细信息：
    {character_info}
    
    以下是其他角色的详细信息：
    {other_character_info}

    以下是你要扮演的人物的记忆：
    {memory}

    以下是你对场景的感知：
    {field_perception}

    以下是一些额外的场景感知：
    {Other_field_perception}
    
    以下是你之前的一些想法：
    {thought}

    以下是你预想的计划：
    {plan}

    现在的时间是:
    {time.strftime("%H:%M")}

    """

    logging.info(f"\nUser input:\n{prompt}")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "你是一个剧本分析助手，你将对用户提供的问题提出专业、准确、有见地的解答。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=1,
        top_p=1,
        max_tokens=4095,
        stream=True
    )

    contents = ""
    for trunk in response:
        content = trunk.choices[0].delta.content
        contents += content

    logging.info(f"\nUpdate-Response:\n{contents}")
    return contents


def Integrate_memory(Other_field_perception, thought, name, plan):
    Output_format = """
    {
        "Memory": [<memory1 (string)>, <memory2 (string), ...],
        "Thoughts": [<thought1 (string)>, <thought2 (string), ...],
        "Plan": <plan (string)>
    }
    """
    prompt = f"""
    你的任务是调整人物记忆并在有需要的时候调整计划，你需要以json格式输出：

    你需要严格按照以下格式输出(json)：
    ·人物记忆(<谁> 在 <什么时候> <以什么神态> <做什么动作> <说什么语言>)
    ·内心想法(在原来的基础上加上 我在 <什么时候> 的想法是： <想法>)
    ·未来计划

    你需要严格按照以下格式输出：
    {Output_format}
    以下是你原来的想法：
    {thought}
    以下是你原来的计划：
    {plan}

    以下是你当前感知到的东西(你可以选择其中重要的，总结后整合到记忆中)：
    {Other_field_perception}

    以下是你在{Thoughts[name]['Time']}产生的内心想法:
    {Thoughts[name]['Thought']}
    """

    logging.info(f"\nUser input:\n{prompt}")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "你是一个剧本分析助手，你将对用户提供的问题提出专业、准确、有见地的解答。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        top_p=0.3,
        max_tokens=4095,
        stream=True
    )

    contents = ""
    for trunk in response:
        content = trunk.choices[0].delta.content
        contents += content

    logging.info(f"\nIntegrate_memory-Response:\n{contents}")
    return contents


def Update_field_perception(Other_field_perception):
    Output_format = """
    {
        "Surroundings": <surrounding (string)>
        "People": <people (string)>
    }
    """
    prompt = f"""
    
    你是一个场景整理助手，你需要根据整合提供的场景，并输出一个详细的场景介绍。
    
    你需要严格按照以下格式输出：
    ·场景中存在的东西（客观事物，比如家具，食物，装饰，周围事物，风景等等）
    ·场景中存在的人物（名字+出现的地点或位置）

    你需要严格按照以下格式输出：
    {Output_format}
    
    以下是提供的场景：
    
    
    {Other_field_perception}
    """

    logging.info(f"\nUser input:\n{prompt}")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "你是一个剧本整理助手，你将对用户提供的问题提出专业、准确、有见地的解答。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        top_p=0.2,
        max_tokens=4095,
        stream=True
    )

    contents = ""
    for trunk in response:
        content = trunk.choices[0].delta.content
        contents += content

    logging.info(f"\nUpdate field perception-Response:\n{contents}")
    return contents


currentTime = datetime.strptime("18:00", "%H:%M")
Field_perception = {}
Thoughts = {}
Characters = ["黄自成", "林翊", "林远翔", "张肖麟", "张国宏"]

for character in Characters:
    with open(f"Characters/{character}.info", "r", encoding="utf-8") as f:
        data = json.load(f)
        name = data["Name"]
        character_info = data["Character_info"]
        other_character_info = data["Other_Character_info"]
        memory = data["Memory"]
        thought = data["Thoughts"]
        field_perception = data["Field_perception"]
        plan = data["Plan"]

    flag = False
    response = {}
    while not flag:
        try:
            response = Update(name, character_info, other_character_info, memory, thought, field_perception, plan, currentTime)
            response = response.replace("```json", "").replace("```", "")
            response = json.loads(response)
            logging.info(f"\nResponse:\n{response}")
            Field_perception[name] = {'Time': currentTime.strftime("%H:%M"), 'Speak': response['Speak'],
                                      'Action': response['Action'],
                                      'Facial expression': response['Facial expression']}
            Thoughts[name] = {'Time': currentTime.strftime("%H:%M"), "Thought": response['Thoughts']}
            flag = True
        except Exception as e:
            print(e)
    print(f"完成人物{character}的更新!")
    currentTime += timedelta(minutes=1)

logging.info(f"\nField_perception:\n{Field_perception}")

Other_field_perception = ""
Character_outputs = ""
for characterName in Field_perception.keys():
    characterContent = Field_perception[characterName]
    characterTime = characterContent['Time']
    characterSpeak = characterContent['Speak']
    characterAction = characterContent['Action']
    characterFacialExpression = characterContent['Facial expression']

    Other_field_perception += f"""
    {characterName}在{characterTime}的时候：
    说了：{characterSpeak}
    动作：{characterAction}
    神态：{characterFacialExpression}
    """

    Character_outputs += f"""
    {characterName}在{characterTime}的时候：
    说了：{characterSpeak}
    动作：{characterAction}
    神态：{characterFacialExpression}
    想法：{Thoughts[characterName]}
    """
print(Character_outputs)

with open("CharacterOutput.txt", "a", encoding="utf-8") as f:
    f.write(Character_outputs)

for character in Characters:
    with open(f"Characters/{character}.info", "r", encoding="utf-8") as f:
        data = json.load(f)
        name = data["Name"]
        character_info = data["Character_info"]
        memory = data["Memory"]
        thoughts = data["Thoughts"]
        field_perception = data["Field_perception"]
        plan = data["Plan"]

    flag = False
    response = {}
    while not flag:
        try:
            response = Integrate_memory(Other_field_perception, thoughts, name, plan)
            response = response.replace("```json", "").replace("```", "")
            response = json.loads(response)
            logging.info(f"\nResponse:\n{response}")
            newMemory = []
            for m in response["Memory"]:
                m = m.replace(name, "我")
                newMemory.append(m)
            data["Memory"] += newMemory
            data["Plan"] = response["Plan"]
            data["Thoughts"] = response["Thoughts"]
            flag = True
        except Exception as e:
            print(e)

    print(f"完成人物{character}的记忆整合!")
    with open(f"Characters/{character}.info", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
