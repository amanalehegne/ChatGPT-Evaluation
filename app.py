from flask import Flask, request, jsonify
import openai
import os

api_key = os.getenv("API_KEY", "your_default_api_key_if_not_set")
print(api_key)
openai.api_key = api_key

app = Flask(__name__)

provided_questions = [
    "What problem do you aim to solve?",
    "Outline your proposed solution.",
    "List alternatives that people currently use to solve the problem.",
    "Clearly state why customers should choose your solution over alternatives.",
    "List your target customer segments in order of priority.",
    "Who are your early adopters likely to be?",
    "List some of the methods you could use to monetize your product.",
    "What challenges do you expect to face throughout your project?",
    "Is there any additional information you would like to share about your project?"
]

evaluation_criteria = {
    "Problem and Solution Clarity": {
        "description": "Problem and Solution Clarity (Score out of 3): No problem identified and no solution provided: The problem is not clearly defined or relevant to the African context, and no clear solution is proposed. (0 points) Vague problem and insufficient solution detail: The problem is somewhat identified but lacks clarity or significance, and the proposed solution lacks sufficient detail or clarity. (1 point) Clear problem and vague solution: The problem is clearly defined and relevant, but the proposed solution lacks sufficient detail or clarity. (2 points) Highly relevant problem and well-constructed solution: The problem is clearly defined and highly relevant to the African context, and the solution is well-detailed, clear, and logically constructed. (3 points)",
        "relevant_questions": [0, 1]
    },
    "Relevance to AI": {
        "description": "Relevance to AI (Score out of 3): Not related at all: The proposed idea has no connection or relevance to AI. (0 points) Partially related: The idea has some connection to AI, but it may not fully leverage the techniques and models used in AI. (1 point) Moderately related: The idea is somewhat applicable to AI and makes use of basic AI techniques or models. (2 points) Highly related: The idea is directly applicable to AI and leverages the techniques and models used in this field. (3 points)",
        "relevant_questions": [1, 8]
    },
    "Impact": {
        "description": "Impact (Score out of 3): Very low impact: The proposed solution would only affect a very small number of people, and the impact would be minimal. (0 points) Low impact: The solution would have a significant impact on a small number of people, or a positive impact on a large number of people. (1 points) Moderate impact: The solution has a potential to make a significant impact on a substantial number of people. (2 points) High impact: The solution would have a substantial and positive impact on a large number of people. (3 points)",
        "relevant_questions": [1, 3, 4]
    },
    "Competitive Advantage": {
        "description": "Competitive Advantage (Score out of 3): No differentiation: The solution does not clearly differentiate itself from existing alternatives. (0 points) Minimal differentiation: The solution offers some differentiation but it is not compelling. (1 point) Moderate differentiation: The solution is moderately differentiated and presents a reasonable case for its advantages. (2 points) High differentiation: The solution is highly differentiated and presents a compelling reason for customers to choose it over alternatives. (3 points)",
        "relevant_questions": [2, 3]
    },
    "Market Potential and Customer Segmentation": {
        "description": "Market Potential and Customer Segmentation (Score out of 3): Prominently available with no identified customer segments: The solution addresses an already well-served market, and no specific customer segments are identified. (0 points) Commonly existing but not available everywhere with basic customer segment identification: The market exists with room for growth, and basic customer segments are identified but may lack depth. (1 point) Existing for a specific niche with detailed customer segment identification: The solution targets a niche market, and detailed customer segments are identified, showing understanding of the market. (2 points) Untapped potential with comprehensive customer segment identification: The solution addresses a market with significant untapped potential, and comprehensive customer segments are clearly identified, demonstrating a clear strategy for market penetration. (3 points)",
        "relevant_questions": [2, 3, 4, 5]
    },
    "Monetization Strategy": {
        "description": "Monetization Strategy (Score out of 3): No monetization methods: No methods to monetize the product are outlined. (0 points) Basic monetization methods: Basic monetization methods are outlined but may lack depth. (1 point) Detailed monetization methods but needs refinement: Detailed monetization methods are provided but may need further refinement. (2 points) Comprehensive and viable monetization methods: Comprehensive and viable monetization methods are clearly outlined. (3 points)",
        "relevant_questions": [6]
    },
    "Challenges and Risk Management": {
        "description": "Challenges and Risk Management (Score out of 3): No challenges identified: No potential challenges are identified. (0 points) Minimal challenges identified: Some challenges are identified but risk management strategies are unclear. (1 point) Moderate challenges with some risk management: Challenges are identified with some proposed risk management strategies. (2 points) Comprehensive challenges and risk management: Challenges are comprehensively identified with clear risk management strategies. (3 points)",
        "relevant_questions": [7, 8]
    }
}


@app.route('/evaluate', methods=['POST'])
def evaluate():    
    input_data = request.json
    evaluation_results = {}

    for criterion, details in evaluation_criteria.items():
        description = details["description"]
        relevant_questions = [provided_questions[idx] for idx in details["relevant_questions"]]

        prompt = (f"Evaluate the following project based on the {criterion} criteria: {description}\n\n"
                "Relevant Questions:\n" + "\n".join(relevant_questions) + "\n\nProject Data:\n")

        for key, value in input_data.items():
            if isinstance(value, list):
                prompt += f"{key}:\n" + "\n".join(f"{i+1}. {item}" for i, item in enumerate(value)) + "\n"
            else:
                prompt += f"{key}: {value}\n"

        prompt += f"\nProvide a numerical score \bOUT OF 3\b for the {criterion} based on the relevant questions."

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in evaluating hackathon projects."},
                {"role": "user", "content": prompt}
            ]
        )

        score_text = response.choices[0].message['content'].strip()
        score = int(next((s for s in score_text.split() if s.isdigit()), '0'))
        evaluation_results[criterion] = score

    return jsonify(evaluation_results)

if __name__ == '__main__':
    app.run(debug=True)
