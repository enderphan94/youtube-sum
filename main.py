from flask import Flask, request, render_template
from youtube_transcript_api import YouTubeTranscriptApi
import openai
from dotenv import load_dotenv
import os

app = Flask(__name__)

openai.api_key = os.environ["OPENAI_API_KEY"]

@app.route('/', methods=['GET', 'POST'])
def index():
    corrected_text = None
    if request.method == 'POST':
        video_id = request.form.get('video-id')
        
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
                    response = openai.ChatCompletion.create(
                        model="gpt-4o-mini",  # You can choose another model if preferred
                        messages=[
                            {"role": "system", "content": "Bạn là trợ lý cấp cao giúp kiểm tra chính tả và sửa chữa văn bản tiếng Việt."},
                            {"role": "user", "content": f"Sửa lỗi chính tả và hoàn chỉnh đoạn văn bản sau, tóm tắt các ý chính đó ra thành 10 ý chính: {full_text}"}
                        ],
                        max_tokens=4000  # Adjust based on your needs
                    )
                    corrected_text = response.choices[0].message['content'].strip()
                else:
                    corrected_text = full_text
            else:
                corrected_text = "No transcript available"

        except Exception as e:
            corrected_text = f"An error occurred: {str(e)}"

    return render_template('index.html', corrected_text=corrected_text)

if __name__ == '__main__':
    app.run(debug=True)