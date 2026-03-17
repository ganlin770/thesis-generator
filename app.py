"""论文自动生成工具 — FastAPI 主入口"""
import os
import json
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from typing import List

import config
from core.file_parser import parse_folder
from core.data_analyzer import analyze_all, analysis_to_text
from core.thesis_generator import ThesisGenerator
from core.docx_builder import build_thesis

app = FastAPI(title="论文自动生成工具")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.post("/api/generate")
async def generate_thesis(
    files: List[UploadFile] = File(...),
    title: str = Form("毕业论文"),
    subject: str = Form(""),
    degree: str = Form("本科"),
    author: str = Form(""),
    school: str = Form(""),
):
    async def event_stream():
        upload_id = str(uuid.uuid4())[:8]
        upload_dir = os.path.join(config.UPLOAD_DIR, upload_id)
        os.makedirs(upload_dir, exist_ok=True)

        try:
            # 保存上传的文件
            for f in files:
                fpath = os.path.join(upload_dir, f.filename)
                with open(fpath, "wb") as out:
                    content = await f.read()
                    out.write(content)

            # 阶段1: 解析文件
            yield sse({"stage": "parsing", "status": "active"})
            parsed = parse_folder(upload_dir)
            yield sse({"stage": "parsing", "status": "done"})

            # 阶段2: 数据分析
            yield sse({"stage": "analyzing", "status": "active"})
            analyses = analyze_all(parsed.data_frames)
            data_text = analysis_to_text(analyses)
            charts = []
            for a in analyses:
                charts.extend(a.get("charts", []))
            yield sse({"stage": "analyzing", "status": "done"})

            # 初始化生成器
            gen = ThesisGenerator()

            # 阶段3: 生成大纲
            yield sse({"stage": "outline", "status": "active"})
            outline = gen.generate_outline(parsed.proposal_text, data_text)
            yield sse({"stage": "outline", "status": "done", "preview": outline[:500]})

            # 阶段4: 文献综述
            yield sse({"stage": "literature", "status": "active"})
            literature = gen.generate_literature()
            yield sse({"stage": "literature", "status": "done", "preview": literature[:500]})

            # 阶段5: 研究方法
            yield sse({"stage": "methodology", "status": "active"})
            methodology = gen.generate_methodology(data_text)
            yield sse({"stage": "methodology", "status": "done", "preview": methodology[:500]})

            # 阶段6: 数据分析与结果
            yield sse({"stage": "results", "status": "active"})
            results = gen.generate_results(data_text)
            yield sse({"stage": "results", "status": "done", "preview": results[:500]})

            # 阶段7: 结论与摘要
            yield sse({"stage": "conclusion", "status": "active"})
            conclusion = gen.generate_conclusion()
            abstract = gen.generate_abstract()
            yield sse({"stage": "conclusion", "status": "done", "preview": conclusion[:500]})

            # 阶段8: 组装 Word
            yield sse({"stage": "docx", "status": "active"})
            sections = {
                "abstract": abstract,
                "literature": literature,
                "methodology": methodology,
                "results": results,
                "conclusion": conclusion,
            }
            metadata = {"title": title, "author": author, "school": school}
            output_path = build_thesis(sections, metadata, charts)
            yield sse({"stage": "docx", "status": "done", "download_url": f"/download/{os.path.basename(output_path)}"})

        except Exception as e:
            yield sse({"stage": "error", "status": "error", "message": str(e)})
        finally:
            shutil.rmtree(upload_dir, ignore_errors=True)

    return StreamingResponse(event_stream(), media_type="text/event-stream")

def sse(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

@app.get("/download/{filename}")
async def download_file(filename: str):
    filepath = os.path.join(config.OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        return FileResponse(filepath, filename=filename, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    return {"error": "文件不存在"}

os.makedirs(config.UPLOAD_DIR, exist_ok=True)
os.makedirs(config.OUTPUT_DIR, exist_ok=True)
os.makedirs("output/charts", exist_ok=True)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"论文自动生成工具启动中... http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
