import os

import openai
from flask import Flask, json, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=generate_story_prompt(
                request.form["main-character"],
                request.form["second-character"],
                request.form["theme"],
                request.form["age"],
            ),
        )
        result = json.loads(response.choices[0].message.content)
        for (i, chapter) in enumerate(result):
            print("Generating image for: ", chapter)

            response = openai.Image.create(
                prompt=chapter["img_prompt"],
                n=1,
                size="1024x1024"
            )
            img_url = response['data'][0]['url']
            result[i]["img_url"] = img_url
        print("result: ", result)
        return redirect(url_for("story", chapter=1, data=json.dumps(result)))

    result = request.args.get("result")
    img_result = request.args.get("img_result")
    return render_template("index.html", result=result, img_result=img_result)


@ app.route("/story", methods=["GET"])
def story():
    data = json.jsonify(request.args.get("data"))
    chapter = request.args.get("chapter")
    return render_template("story.html", chapter=chapter, data=data)


@ app.route("/img", methods=["POST"])
def img():
    print("/img request json: ", request.json)
    if request.method == "POST":
        input = request.json["result"]
        response = openai.Image.create(
            prompt=input,
            n=1,
            size="1024x1024"
        )
        img_url = response['data'][0]['url']
        response = app.response_class(
            response=json.dumps({"img_url": img_url}),
            status=200,
            mimetype='application/json'
        )
        return response


def generate_story_prompt(main_character, second_character, theme, age):
    return [
        {"role": "system", "content": "You are a story teller,\
         that tells engaging bed time stories."},

        {"role": "user", "content":
         "Tell me a bed time story with " + main_character +
         " as the main character and " +
         second_character + " as the second character.\
            The story should be about " + theme +
            " and for someone who is " + age + " years old.\
            Split it into 5 chapters and give a very detailed prompt\
            for generating an image with DALLE for each chapter.\
            The prompts should be related to each other and the story.\
            The output should be a json in the following format:\
            [{\"chapter\": 1, \"text\": \"the text of the chapter\",\
            \"img_prompt\": \"The prompt for generating an image\" }, ...]"
         },
    ]
