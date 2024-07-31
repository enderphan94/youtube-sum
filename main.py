from flask import Flask, request, render_template
from youtube_transcript_api import YouTubeTranscriptApi
import openai
from dotenv import load_dotenv
import os
import re

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/', methods=['GET', 'POST'])
def index():
    corrected_text = None
    summary_text = None
    fixed_text = None
    summary_list = None

    if request.method == 'POST':
        video_id = request.form.get('video-id')
        language = request.form.get('language')

        # Determine the language for prompts
        if language == 'ENG':
            system_prompt = "You are a high-level assistant that helps to check spelling and correct English text. Do not provide titles."
            user_prompt_correct = "Correct the spelling and finalize the following text, do not provide titles:"
            user_prompt_summarize = "Provide 10 key points from the following text, do not provide titles:"
        else:
            system_prompt = "Bạn là trợ lý cấp cao giúp kiểm tra chính tả và sửa chữa văn bản tiếng Việt. Không cần đưa ra tiêu đề"
            user_prompt_correct = "Sửa lỗi chính tả và hoàn chỉnh đoạn văn bản sau, không cần đưa ra tiêu đề:"
            user_prompt_summarize = "Đưa ra 10 ý chính quan trọng trong văn bản giúp người đọc nắm được các thông tin chính, không cần đưa ra tiêu đề:"

        try:
            # List all available transcripts
            all_transcripts = YouTubeTranscriptApi.list_transcripts(video_id)

            manual_transcript = None
            auto_transcript = None

            # Identify manual and automatic transcripts
            for transcript in all_transcripts:
                if transcript.is_generated:
                    auto_transcript = transcript
                else:
                    manual_transcript = transcript

            # Prefer manual transcript, fall back to automatic if necessary
            selected_transcript = manual_transcript or auto_transcript

            if selected_transcript:
                # Fetching the transcript text
                transcript_text = selected_transcript.fetch()
                full_text = ' '.join([line['text'] for line in transcript_text])

                if selected_transcript == auto_transcript:
                    # Correct the transcript using OpenAI if it's an auto-transcript
                    fixed_response = openai.ChatCompletion.create(
                        model="gpt-4o-mini",  # Ensure this model is available for your API key
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"{user_prompt_correct} {full_text}"}
                        ],
                        max_tokens=4000  # Adjust based on your needs
                    )
                    fixed_text = fixed_response['choices'][0]['message']['content'].strip()

                    print("Fixed Text:", fixed_text)

                    sum_response = openai.ChatCompletion.create(
                        model="gpt-4o-mini",  # Ensure this model is available for your API key
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"{user_prompt_summarize} {fixed_text}"}
                        ],
                        max_tokens=4000  # Adjust based on your needs
                    )
                    summary_text = sum_response['choices'][0]['message']['content'].strip()

                    print("Summary Text:", summary_text)

                    # Split summary text based on numbers, excluding leading empty strings
                    summary_list = re.split(r'\d+\.\s', summary_text)
                    summary_list = [item.strip() for item in summary_list if item.strip()]

                    print("Summary List:", summary_list)

                else:
                
                    # Correct the transcript using OpenAI if it's an auto-transcript
                    fixed_response = openai.ChatCompletion.create(
                        model="gpt-4o-mini",  # Ensure this model is available for your API key
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"{user_prompt_correct} {full_text}"}
                        ],
                        max_tokens=4000  # Adjust based on your needs
                    )
                    fixed_text = fixed_response['choices'][0]['message']['content'].strip()

                    print("Fixed Text:", fixed_text)

                    sum_response = openai.ChatCompletion.create(
                        model="gpt-4o-mini",  # Ensure this model is available for your API key
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"{user_prompt_summarize} {fixed_text}"}
                        ],
                        max_tokens=4000  # Adjust based on your needs
                    )
                    summary_text = sum_response['choices'][0]['message']['content'].strip()

                    print("Summary Text:", summary_text)

                    # Split summary text based on numbers, excluding leading empty strings
                    summary_list = re.split(r'\d+\.\s', summary_text)
                    summary_list = [item.strip() for item in summary_list if item.strip()]

                    print("Summary List:", summary_list) 

            else:
                summary_text = "No transcript available"
                print(summary_text)

        except Exception as e:
            summary_text = f"An error occurred: {str(e)}"
            print(summary_text)

    return render_template('index.html', corrected_text=fixed_text, summary_list=summary_list)

if __name__ == '__main__':
    app.run(debug=True)