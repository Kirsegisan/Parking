from roboflow import Roboflow

rf = Roboflow(api_key="kmdwHagZQlYas7gzGfw9")
project = rf.workspace().project("parking-utku6")
model = project.version("4").model

job_id, signed_url, expire_time = model.predict_video(
    "images/record/01.mp4",
    fps=5,
    prediction_type="batch-video",
    #visualize=True
)

results = model.poll_until_video_results(job_id)

print(results)
