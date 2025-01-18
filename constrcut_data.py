import openai
import json
import os

# 设置OpenAI API密钥
openai.api_key = 'YOUR_OPENAI_API_KEY'

def load_literature_sentences(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        sentences = json.load(f)
    return sentences


def translate_sentence(sentence, advice=None, target_language='chinese'):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional translator."},
            {"role": "user", "content": f"Translate the following sentence to {target_language}!!!: {sentence}. advice: {advice}"}
        ]
    )
    return response.choices[0].message.content


def get_advice(translation, original_sentence):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a translation advisor."},
            {"role": "user", "content": f"Provide feedback on the translation: {translation}. Original sentence: {original_sentence}"}
        ]
    )
    return response.choices[0].message.content


def evaluate_translation(translation, original_sentence, max_iterations=3):
    for i in range(max_iterations):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a translation evaluator."},
                    {"role": "user", "content": f"Evaluate the translation on a scale of 0 to 100: {translation}. Original sentence: {original_sentence}"}
                ]
            )
            score = int(response.choices[0].message.content)
            return score
        except Exception as e:
            print(response)
    
    return 0.0


def iterative_translation(sentence, max_iterations=3, score_threshold=97):
    translations_result = []
    print(f"sentence: {sentence}")
    for i in range(max_iterations):
        if i == 0:
            translation = translate_sentence(sentence)
        else:
            translation = translate_sentence(sentence, advice)
        print(f"{i}: translation: {translation}")
        advice = get_advice(translation, sentence)
        print(f"{i}: advice: {advice}")
        score = evaluate_translation(translation, sentence)
        print(f"{i}: score: {score}\n")
        
        translations_result.append({"translation": translation,
                                    "feedback": advice,
                                    "score": score})
        
        if score >= score_threshold:
            break
    
    return translations_result


def rewrite_long_thought(sentence, translations_result):
    long_thought = {
        "source_sentence": sentence,
        "translations": translations_result,
    }
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a content rewriter."},
            {"role": "user", "content": f"Rewrite the long thought process into a self-reflection description: {json.dumps(long_thought, ensure_ascii=False)}"}
        ]
    )
    return response.choices[0].message.content


def main():
    # # 加载文学句子
    # file_path = 'literature_sentences.json'
    # sentences = load_literature_sentences(file_path)

    
    # # 过滤出含有比喻或隐喻的句子
    # suitable_sentences = [sentence for sentence, has_metaphor in sentences.items() if has_metaphor]
    
    suitable_sentences = ["Women were weeping and children crying, and all were going as fast as seemingly lay in their power, looking behind now and then as if pursued by some deadly enemy."]
    # 保存长思考数据
    long_thought_data = []
    for sentence in suitable_sentences:
        translations_result = iterative_translation(sentence)
        long_thought = rewrite_long_thought(sentence, translations_result)
        long_thought_data.append({"sentence": sentence,
                                  "translations_result": translations_result,
                                  "long_thought":long_thought})
    
    # 保存长思考数据到文件
    with open('long_thought_data.json', 'w', encoding='utf-8') as f:
        json.dump(long_thought_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
