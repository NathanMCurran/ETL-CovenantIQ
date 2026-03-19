# FastAPI Controller/Router/View Example

Install:
```bash
python3 -m pip install -r requirements.txt
```

Run:
```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/

                    E       
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
