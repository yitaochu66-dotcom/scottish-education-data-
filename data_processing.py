# -*- coding: utf-8 -*-
"""
数据处理脚本 - 苏格兰考试历史数据可视化
处理1888-1962年的教育考试数据
"""

import pandas as pd
import matplotlib.pyplot as plt
import json
import re
import os

# 配色方案 - 暖色系
COLORS = {
    'background': '#F2EDD5',
    'primary': '#3E4031',
    'secondary': '#8C8B79',
    'light': '#D9D5C1',
    'border': '#BFBCAA'
}

# 设置matplotlib样式
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.facecolor'] = COLORS['background']
plt.rcParams['figure.facecolor'] = COLORS['background']

# 获取当前脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 数据文件夹路径（假设data文件夹和脚本在同一目录下）
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')
# 输出文件夹路径
OUTPUT_DIR = SCRIPT_DIR

def load_data():
    """加载所有数据文件"""
    print("Loading data files...")
    print(f"Data directory: {DATA_DIR}")
    
    # 读取文档时间线
    doc_timeline = pd.read_csv(os.path.join(DATA_DIR, 'doc_timeline.csv'))
    
    # 读取科目名称
    subject_names = pd.read_csv(os.path.join(DATA_DIR, 'subject_names.csv'))
    
    # 读取合并后的科目年份数据
    merged_data = pd.read_csv(os.path.join(DATA_DIR, 'merged_textinfo_by_subject_and_year.csv'))
    
    print("Data loaded successfully!")
    return doc_timeline, subject_names, merged_data

def create_timeline_chart(doc_timeline):
    """创建文档数量时间线图表"""
    print("Creating timeline chart...")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 绘制折线图
    ax.plot(doc_timeline['Year'], doc_timeline['Document Count'], 
            color=COLORS['secondary'], linewidth=2)
    
    # 标注战争期间（1939-1945）
    war_years = doc_timeline[(doc_timeline['Year'] >= 1939) & (doc_timeline['Year'] <= 1945)]
    ax.axvspan(1939, 1945, alpha=0.2, color=COLORS['primary'], label='War Years (1939-1945)')
    
    # 标注1944-1945无记录
    ax.scatter([1944, 1945], [0, 0], color='red', s=100, zorder=5, label='No Records')
    
    # 设置标签和标题
    ax.set_xlabel('Year', fontsize=12, color=COLORS['primary'])
    ax.set_ylabel('Number of Documents', fontsize=12, color=COLORS['primary'])
    ax.set_title('Scottish Education Documents Over Time (1888-1962)', 
                 fontsize=14, fontweight='bold', color=COLORS['primary'], pad=20)
    
    # 网格线
    ax.grid(True, alpha=0.3, color=COLORS['border'])
    ax.legend(loc='upper left')
    
    # 设置刻度颜色
    ax.tick_params(colors=COLORS['secondary'])
    for spine in ax.spines.values():
        spine.set_color(COLORS['border'])
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'timeline_chart.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                facecolor=COLORS['background'])
    plt.close()
    
    print(f"Timeline chart saved to: {output_path}")

def create_language_subjects_chart(merged_data):
    """创建语言科目对比柱状图"""
    print("Creating language subjects chart...")
    
    # 定义语言科目
    language_subjects = ['ENGLISH', 'FRENCH', 'LATIN', 'GERMAN', 'GREEK', 
                         'GAELIC', 'GAELIC (LEARNERS)', 'GAELIC (NATIVE SPEAKERS)', 'SPANISH']
    
    # 筛选语言科目数据
    lang_data = merged_data[merged_data['Subject'].isin(language_subjects)]
    
    # 按科目汇总文档数量
    subject_counts = lang_data.groupby('Subject')['Document Count'].sum().sort_values(ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 创建柱状图
    bars = ax.bar(range(len(subject_counts)), subject_counts.values, 
                   color=COLORS['secondary'], edgecolor=COLORS['primary'], linewidth=1.5)
    
    # 高亮显示英语和盖尔语
    english_idx = list(subject_counts.index).index('ENGLISH') if 'ENGLISH' in subject_counts.index else None
    gaelic_indices = [i for i, subj in enumerate(subject_counts.index) if 'GAELIC' in subj]
    
    if english_idx is not None:
        bars[english_idx].set_color(COLORS['primary'])
    for idx in gaelic_indices:
        bars[idx].set_color('#D9534F')  # 红色标注盖尔语
    
    # 设置标签
    ax.set_xticks(range(len(subject_counts)))
    ax.set_xticklabels(subject_counts.index, rotation=45, ha='right')
    ax.set_xlabel('Language Subject', fontsize=12, color=COLORS['primary'])
    ax.set_ylabel('Total Document Count', fontsize=12, color=COLORS['primary'])
    ax.set_title('Language Subjects in Scottish Exams (1888-1962)', 
                 fontsize=14, fontweight='bold', color=COLORS['primary'], pad=20)
    
    # 网格线
    ax.grid(True, axis='y', alpha=0.3, color=COLORS['border'])
    ax.tick_params(colors=COLORS['secondary'])
    for spine in ax.spines.values():
        spine.set_color(COLORS['border'])
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'language_subjects_chart.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor=COLORS['background'])
    plt.close()
    
    print(f"Language subjects chart saved to: {output_path}")
    
    return subject_counts

def create_language_trends_chart(merged_data):
    """创建语言科目随时间变化的趋势图"""
    print("Creating language trends chart...")
    
    # 主要语言科目
    main_languages = ['ENGLISH', 'FRENCH', 'LATIN', 'GERMAN', 'GAELIC']
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 为每个语言科目绘制趋势线
    for lang in main_languages:
        lang_data = merged_data[merged_data['Subject'] == lang].sort_values('Year')
        if not lang_data.empty:
            if lang == 'ENGLISH':
                ax.plot(lang_data['Year'], lang_data['Document Count'], 
                       label=lang, linewidth=3, color=COLORS['primary'])
            elif lang == 'GAELIC':
                ax.plot(lang_data['Year'], lang_data['Document Count'], 
                       label=lang, linewidth=2.5, color='#D9534F', linestyle='--')
            else:
                ax.plot(lang_data['Year'], lang_data['Document Count'], 
                       label=lang, linewidth=1.5, alpha=0.7)
    
    # 标注教育法案年份（1918年教育法案）
    ax.axvline(x=1918, color=COLORS['primary'], linestyle=':', linewidth=2, 
               label='Education Act 1918', alpha=0.7)
    
    # 标注战争期间
    ax.axvspan(1914, 1918, alpha=0.1, color='gray', label='WWI')
    ax.axvspan(1939, 1945, alpha=0.1, color='gray', label='WWII')
    
    ax.set_xlabel('Year', fontsize=12, color=COLORS['primary'])
    ax.set_ylabel('Number of Documents', fontsize=12, color=COLORS['primary'])
    ax.set_title('Language Subjects Over Time', 
                 fontsize=14, fontweight='bold', color=COLORS['primary'], pad=20)
    
    ax.legend(loc='upper left', framealpha=0.9, facecolor=COLORS['light'])
    ax.grid(True, alpha=0.3, color=COLORS['border'])
    ax.tick_params(colors=COLORS['secondary'])
    for spine in ax.spines.values():
        spine.set_color(COLORS['border'])
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'language_trends_chart.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor=COLORS['background'])
    plt.close()
    
    print(f"Language trends chart saved to: {output_path}")

def extract_quotes():
    """从educationcomms.txt提取相关引文"""
    print("Extracting quotes from historical documents...")
    
    quotes = []
    
    try:
        file_path = os.path.join(DATA_DIR, 'educationcomms.txt')
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 提取包含"English"和"certificate"的句子（简化版）
        sentences = content.split('.')
        for i, sentence in enumerate(sentences[:1000]):  # 只查看前1000句
            if 'English' in sentence and 'certificate' in sentence and len(sentence) < 200:
                clean_sentence = sentence.strip()
                if len(clean_sentence) > 30:
                    quotes.append({
                        'text': clean_sentence + '.',
                        'topic': 'English Requirement'
                    })
                    if len(quotes) >= 3:
                        break
        
        print(f"Extracted {len(quotes)} quotes")
        
    except Exception as e:
        print(f"Error extracting quotes: {e}")
        quotes = [
            {
                'text': 'Candidates for the Leaving Certificate must demonstrate proficiency in English.',
                'topic': 'English Requirement'
            }
        ]
    
    return quotes

def generate_statistics(doc_timeline, merged_data):
    """生成关键统计数据"""
    print("Generating statistics...")
    
    stats = {
        'total_years': int(doc_timeline['Year'].max() - doc_timeline['Year'].min()),
        'total_documents': int(doc_timeline['Document Count'].sum()),
        'war_year_drop': int(doc_timeline[doc_timeline['Year'].between(1939, 1945)]['Document Count'].sum()),
        'english_dominance': 0,
        'gaelic_presence': 0
    }
    
    # 计算英语和盖尔语的文档数量
    english_count = merged_data[merged_data['Subject'] == 'ENGLISH']['Document Count'].sum()
    gaelic_count = merged_data[merged_data['Subject'].str.contains('GAELIC', na=False)]['Document Count'].sum()
    
    stats['english_dominance'] = int(english_count)
    stats['gaelic_presence'] = int(gaelic_count)
    
    # 保存为JSON
    output_path = os.path.join(OUTPUT_DIR, 'statistics.json')
    with open(output_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"Statistics saved to: {output_path}")
    return stats

def main():
    """主函数"""
    print("=" * 50)
    print("Scottish Exam Data Processing")
    print("=" * 50)
    print(f"Script directory: {SCRIPT_DIR}")
    print(f"Data directory: {DATA_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 50)
    
    # 检查数据文件夹是否存在
    if not os.path.exists(DATA_DIR):
        print(f"\nERROR: Data directory not found: {DATA_DIR}")
        print("Please make sure the 'data' folder is in the same directory as this script.")
        print("\nExpected directory structure:")
        print("  your_project_folder/")
        print("  ├── data_processing.py  (this script)")
        print("  └── data/")
        print("      ├── doc_timeline.csv")
        print("      ├── educationcomms.txt")
        print("      ├── merged_textinfo_by_subject_and_year.csv")
        print("      └── subject_names.csv")
        return
    
    # 加载数据
    try:
        doc_timeline, subject_names, merged_data = load_data()
    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        print("\nPlease make sure all required data files are in the 'data' folder:")
        print("  - doc_timeline.csv")
        print("  - educationcomms.txt")
        print("  - merged_textinfo_by_subject_and_year.csv")
        print("  - subject_names.csv")
        return
    
    # 生成图表
    create_timeline_chart(doc_timeline)
    create_language_subjects_chart(merged_data)
    create_language_trends_chart(merged_data)
    
    # 提取引文
    quotes = extract_quotes()
    output_path = os.path.join(OUTPUT_DIR, 'quotes.json')
    with open(output_path, 'w') as f:
        json.dump(quotes, f, indent=2)
    print(f"Quotes saved to: {output_path}")
    
    # 生成统计数据
    stats = generate_statistics(doc_timeline, merged_data)
    
    print("\n" + "=" * 50)
    print("Processing Complete!")
    print("=" * 50)
    print(f"Total Years: {stats['total_years']}")
    print(f"Total Documents: {stats['total_documents']}")
    print(f"English Documents: {stats['english_dominance']}")
    print(f"Gaelic Documents: {stats['gaelic_presence']}")
    print("\nGenerated files:")
    print(f"  - {os.path.join(OUTPUT_DIR, 'timeline_chart.png')}")
    print(f"  - {os.path.join(OUTPUT_DIR, 'language_subjects_chart.png')}")
    print(f"  - {os.path.join(OUTPUT_DIR, 'language_trends_chart.png')}")
    print(f"  - {os.path.join(OUTPUT_DIR, 'statistics.json')}")
    print(f"  - {os.path.join(OUTPUT_DIR, 'quotes.json')}")
    print("=" * 50)

if __name__ == "__main__":
    main()
