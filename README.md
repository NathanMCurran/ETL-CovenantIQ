I used Claude for the initial design and architecture of the project, then tested a variety of scenarios to verify that it was working across different file formats and edge cases. I then reviewed the codebase to ensure the code quality, structure, and maintainability were up to standard.

Install:
```bash
python3 -m pip install -r requirements.txt
```

Run:
```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/
    
curl -X POST "http://127.0.0.1:8000/transforms" \
  -F "name={file_name}" \
  -F "transformer={Transform1|Transform2}" \
  -F "file={@path_to_excel_file}"  

How to run Transformer 1 with file in current directory
curl -X POST "http://127.0.0.1:8000/transforms" \
  -F "name=CIQ_Interview_Sheet_v1.xlsx" \
  -F "transformer=Transform1" \
  -F "file=@CIQ_Interview_Sheet_v1.xlsx"    

How to run Transformer 2 with file in current directory
curl -X POST "http://127.0.0.1:8000/transforms" \
  -F "name=CIQ_Interview_Sheet_v2.xlsx" \
  -F "transformer=Transform2" \
  -F "file=@CIQ_Interview_Sheet_v2.xlsx"                               
