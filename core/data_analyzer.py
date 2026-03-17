"""对数据文件进行描述性统计分析，生成文本摘要和图表"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Arial Unicode MS", "SimHei", "STHeiti"]
plt.rcParams["axes.unicode_minus"] = False

def analyze_dataframe(df: pd.DataFrame, name: str, output_dir: str = "output/charts") -> dict:
    os.makedirs(output_dir, exist_ok=True)
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    analysis = {
        "file_name": name,
        "shape": f"{df.shape[0]}行 x {df.shape[1]}列",
        "columns": list(df.columns),
        "missing": {c: int(df[c].isnull().sum()) for c in df.columns if df[c].isnull().sum() > 0},
        "numeric_describe": df[numeric_cols].describe().round(3).to_string() if numeric_cols else "无数值列",
        "charts": [],
    }

    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr().round(3)
        analysis["correlation"] = corr.to_string()
        fig, ax = plt.subplots(figsize=(8, 6))
        im = ax.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1)
        ax.set_xticks(range(len(corr.columns)))
        ax.set_yticks(range(len(corr.columns)))
        ax.set_xticklabels(corr.columns, rotation=45, ha="right", fontsize=8)
        ax.set_yticklabels(corr.columns, fontsize=8)
        plt.colorbar(im)
        ax.set_title("相关性矩阵")
        chart_path = os.path.join(output_dir, f"{name}_corr.png")
        fig.savefig(chart_path, bbox_inches="tight", dpi=150)
        plt.close()
        analysis["charts"].append(chart_path)

    for col in numeric_cols[:5]:
        fig, ax = plt.subplots(figsize=(6, 4))
        df[col].dropna().hist(ax=ax, bins=20, color="#2A7B88", edgecolor="white")
        ax.set_title(f"{col} 分布")
        ax.set_xlabel(col)
        ax.set_ylabel("频数")
        chart_path = os.path.join(output_dir, f"{name}_{col}_dist.png")
        fig.savefig(chart_path, bbox_inches="tight", dpi=150)
        plt.close()
        analysis["charts"].append(chart_path)

    return analysis

def analyze_all(data_frames: dict, output_dir: str = "output/charts") -> list:
    results = []
    for name, df in data_frames.items():
        results.append(analyze_dataframe(df, name.replace(".", "_"), output_dir))
    return results

def analysis_to_text(analyses: list) -> str:
    parts = []
    for a in analyses:
        parts.append(f"## 数据文件: {a['file_name']}")
        parts.append(f"规模: {a['shape']}")
        parts.append(f"变量: {', '.join(a['columns'])}")
        if a["missing"]:
            parts.append(f"缺失值: {a['missing']}")
        parts.append(f"\n描述性统计:\n{a['numeric_describe']}")
        if "correlation" in a:
            parts.append(f"\n相关性矩阵:\n{a['correlation']}")
        parts.append("")
    return "\n".join(parts)
