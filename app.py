from flask import Flask, request, jsonify
from openai import OpenAI
import os

api_key = os.getenv("API_KEY", "your_default_api_key_if_not_set")

client = OpenAI(api_key=api_key)

app = Flask(__name__)

evaluation_criteria = {
    "Feasibility": {
        "description": "Feasibility (Score out of 3): Not feasible at all: The proposed idea cannot be implemented within the given 50 hour timeframe. (0 points) Feasibility is low: The idea could potentially be implemented, but it may require additional time (beyond the 50 hours) or different team members with specific expertise. (1 point) Feasible with some changes: The idea seems feasible, but it may require some modifications or adjustments to be implemented within the given timeframe. (2 points) Highly feasible: The idea is very likely to be successfully implemented within the 50 hour timeframe. (3 points)",
        "relevant_questions": [1, 2, 3, 4, 5]
    },
    "Impact": {
        "description": "Impact (Score out of 3): Very low impact: The proposed solution would only affect a very small number of people, and the impact would be minimal. (0 points) Low impact: The solution would have a significant impact on a small number of people, or a positive impact on a large number of people. (1 point) Moderate impact: The solution has a potential to make a significant impact on a substantial number of people. (2 points) High impact: The solution would have a substantial and positive impact on a large number of people. (3 points)",
        "relevant_questions": [1, 2, 3, 4, 5]
    },
    "Relevance to AI": {
        "description": "Relevance to AI (Score out of 3): Not related at all: The proposed idea has no connection or relevance to AI. (0 points) Partially related: The idea has some connection to AI, but it may not fully leverage the techniques and models used in AI. (1 point) Highly related: The idea is directly applicable to AI and leverages the techniques and models used in this field. (3 points)",
        "relevant_questions": [2, 9]
    },
    "Innovation": {
        "description": "Innovation (Score out of 3): Prominently available: The proposed solution is already widely available and implemented in various places. (0 points) Commonly existing but not available everywhere: The idea is based on an existing solution, but it is not widely available and may have limited availability. (1 point) Existing but for a specific niche: The solution already exists but caters to a specific niche or limited target audience. (2 points) I have never seen this before: The idea is unique and innovative, and the participant has not come across a similar solution before. (3 points)",
        "relevant_questions": [2, 3]
    }
}

@app.route('/evaluate', methods=['POST'])
def evaluate():
    input_data = request.json

    def evaluate_project(input_data, criteria):
        evaluation_results = {}

        for criterion, details in criteria.items():
            description = details["description"]
            relevant_questions = ", ".join(map(str, details["relevant_questions"]))

            prompt = f"Evaluate the following project based on the {criterion} criteria: {description}\n\n"
            prompt += f"Relevant Questions: {relevant_questions}\n\n"
            prompt += f"Project Data:\n"
            for key, value in input_data.items():
                prompt += f"{key}: {value}\n"
            prompt += f"\nProvide a numerical score out of 3 for the {criterion} based on the relevant questions."

            response = client.chat.completions.create(model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in evaluating hackathon projects."},
                {"role": "user", "content": prompt}
            ])

            score_text = response.choices[0].message.content.strip()
            score = int(next((s for s in score_text.split() if s.isdigit()), '0'))
            evaluation_results[criterion] = score

        return evaluation_results

    evaluation_results = evaluate_project(input_data, evaluation_criteria)
    return jsonify(evaluation_results)

if __name__ == '__main__':
    app.run(debug=True)
