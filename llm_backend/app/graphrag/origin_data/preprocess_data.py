import pandas as pd
import os
from datetime import datetime
import re

# 获取脚本所在目录的绝对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 导出数据目录
EXPORT_DIR = os.path.join(SCRIPT_DIR, 'exported_data')

# 简单的token计数函数
def count_tokens(text):
    """
    简单估算文本的token数量
    中文：每个字符算1个token
    英文：按空格分词，每个单词算1个token
    标点符号：每个标点算1个token
    """
    if not text:
        return 0
        
    # 中文字符
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    # 英文单词
    english_words = re.findall(r'[a-zA-Z]+', text)
    # 数字
    numbers = re.findall(r'[0-9]+', text)
    # 标点符号
    punctuations = re.findall(r'[^\w\s\u4e00-\u9fff]', text)
    
    # 总token数 = 中文字符数 + 英文单词数 + 数字数 + 标点符号数
    return len(chinese_chars) + len(english_words) + len(numbers) + len(punctuations)

def preprocess_reviews(reviews_file=None, 
                       products_file=None,
                       customers_file=None,
                       categories_file=None,
                       output_file=None):
    """
    预处理评论数据，将其与产品、客户和类别数据关联，生成结构化文本
    
    参数:
    reviews_file: 评论CSV文件路径
    products_file: 产品CSV文件路径
    customers_file: 客户CSV文件路径
    categories_file: 类别CSV文件路径
    output_file: 输出的CSV文件路径
    """
    # 设置默认文件路径
    if reviews_file is None:
        reviews_file = os.path.join(EXPORT_DIR, 'reviews.csv')
    if products_file is None:
        products_file = os.path.join(EXPORT_DIR, 'products.csv')
    if customers_file is None:
        customers_file = os.path.join(EXPORT_DIR, 'customers.csv')
    if categories_file is None:
        categories_file = os.path.join(EXPORT_DIR, 'categories.csv')
    if output_file is None:
        output_file = os.path.join(EXPORT_DIR, 'processed_reviews.csv')
    
    print(f"开始处理评论数据: {reviews_file}")
    print(f"导出目录: {EXPORT_DIR}")
    
    # 检查导出目录是否存在
    if not os.path.exists(EXPORT_DIR):
        print(f"错误: 导出目录 {EXPORT_DIR} 不存在")
        return
    
    # 检查输入文件是否存在
    for file_path, file_name in [(reviews_file, "评论"), (products_file, "产品"), 
                                 (customers_file, "客户"), (categories_file, "类别")]:
        if not os.path.exists(file_path):
            print(f"错误: {file_name}文件 {file_path} 不存在")
            return
    
    # 读取CSV文件
    try:
        reviews_df = pd.read_csv(reviews_file)
        products_df = pd.read_csv(products_file)
        customers_df = pd.read_csv(customers_file)
        categories_df = pd.read_csv(categories_file)
        
        print(f"成功读取 {len(reviews_df)} 条评论记录")
    except Exception as e:
        print(f"读取CSV文件时出错: {e}")
        return
    
    # 合并数据
    # 1. 将评论与产品数据合并
    if 'ProductID' in reviews_df.columns and 'ProductID' in products_df.columns:
        merged_df = pd.merge(reviews_df, products_df, on='ProductID', how='left', suffixes=('', '_product'))
    else:
        print("错误: 评论或产品数据缺少ProductID列")
        return
    
    # 2. 将合并后的数据与客户数据合并
    if 'CustomerID' in reviews_df.columns and 'CustomerID' in customers_df.columns:
        merged_df = pd.merge(merged_df, customers_df, on='CustomerID', how='left', suffixes=('', '_customer'))
    else:
        print("错误: 评论或客户数据缺少CustomerID列")
        return
    
    # 3. 将合并后的数据与类别数据合并
    if 'CategoryID' in merged_df.columns and 'CategoryID' in categories_df.columns:
        merged_df = pd.merge(merged_df, categories_df, on='CategoryID', how='left', suffixes=('', '_category'))
    else:
        print("警告: 无法与类别数据合并，可能缺少CategoryID列")
    
    # 创建结构化文本描述
    merged_df['text'] = merged_df.apply(
        lambda row: format_review_text(row), 
        axis=1
    )
    
    # 计算每条评论的token数量
    merged_df['token_count'] = merged_df['text'].apply(count_tokens)
    print(f"平均每条评论的token数量: {merged_df['token_count'].mean():.2f}")
    print(f"最大token数量: {merged_df['token_count'].max()}")
    print(f"最小token数量: {merged_df['token_count'].min()}")
    
    # 保存处理后的数据
    try:
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 选择需要输出的列
        output_columns = ['ReviewID', 'ProductID', 'CustomerID', 'Rating', 'ReviewDate', 'text', 'token_count']
        if 'CategoryName' in merged_df.columns:
            output_columns.append('CategoryName')
        if 'ProductName' in merged_df.columns:
            output_columns.append('ProductName')
        if 'CompanyName' in merged_df.columns:
            output_columns.append('CompanyName')
        
        # 保存到CSV
        merged_df[output_columns].to_csv(output_file, index=False, encoding='utf-8')
        print(f"处理后的数据已保存到: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"保存处理后的数据时出错: {e}")
        return None

def format_review_text(row):
    """
    根据行数据格式化评论文本，生成更丰富的描述
    """
    # 获取产品名称和详细信息
    product_name = row.get('ProductName', '未知产品')
    unit_price = row.get('UnitPrice', '未知价格')
    units_in_stock = row.get('UnitsInStock', '未知库存')
    
    # 获取供应商信息（如果有）
    supplier_name = row.get('SupplierName', '')
    
    # 获取客户信息
    customer_id = row.get('CustomerID', '未知客户ID')
    customer_company = row.get('CompanyName', '未知客户公司')
    customer_location = f"{row.get('City', '')}, {row.get('Country', '')}"
    customer_location = customer_location.strip(', ')
    
    # 获取类别名称
    category_name = row.get('CategoryName', '未知类别')
    
    # 获取评分和评论
    rating = row.get('Rating', 0)
    review_text = row.get('ReviewText', '')
    
    # 获取评论日期并格式化
    review_date = row.get('ReviewDate', '')
    try:
        if review_date:
            date_obj = pd.to_datetime(review_date)
            review_date = date_obj.strftime('%Y年%m月%d日')
    except:
        pass
    
    # 格式化文本 - 更丰富的版本
    parts = []
    parts.append(f"客户ID: {customer_id}")
    parts.append(f"客户公司: {customer_company}")
    if customer_location:
        parts.append(f"客户所在地: {customer_location}")
    
    parts.append(f"产品信息: {product_name} (类别: {category_name})")
    if supplier_name:
        parts.append(f"生产商: {supplier_name}")
    if unit_price != '未知价格':
        parts.append(f"产品价格: {unit_price}")
    
    # 完全移除类别描述部分
    
    parts.append(f"评分: {rating}星")
    parts.append(f"评价日期: {review_date}")
    parts.append(f"评价内容: \"{review_text}\"")
    
    formatted_text = "\n".join(parts)
    return formatted_text

def merge_csv_rows(input_file=None, output_file=None, group_size=5, separator="<ROW_SEP>\n\n", max_tokens=1000):
    """
    将CSV文件中的行按固定数量合并，保留所有字段，并确保不超过token阈值
    
    参数:
        input_file: 输入CSV文件路径
        output_file: 输出CSV文件路径
        group_size: 每组合并的行数，默认为5
        separator: 行之间的分隔符，默认为"<ROW_SEP>\n\n"
        max_tokens: 合并后文本的最大token数量，默认为1000
    """
    # 设置默认文件路径
    if input_file is None:
        input_file = os.path.join(EXPORT_DIR, 'processed_reviews.csv')
    if output_file is None:
        output_file = os.path.join(EXPORT_DIR, 'merged_reviews.csv')
    
    print(f"合并评论数据，使用分隔符: '{separator}'")
    print(f"最大token数: {max_tokens}, 每组最大行数: {group_size}")
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误：输入文件 {input_file} 不存在")
        return None
        
    # 读取CSV文件
    df = pd.read_csv(input_file)
    
    # 确保有text列
    if 'text' not in df.columns:
        print(f"错误：输入文件 {input_file} 中没有text列")
        return None
    
    # 获取所有列名
    all_columns = df.columns.tolist()
    text_column_idx = all_columns.index('text')
    other_columns = [col for col in all_columns if col != 'text']
    
    # 存储合并后的行
    merged_rows = []
    
    # 计算所有评论的token数量
    if 'token_count' not in df.columns:
        df['token_count'] = df['text'].apply(count_tokens)
    
    # 检查token阈值是否合理
    max_single_token = df['token_count'].max()
    if max_tokens < max_single_token:
        print(f"警告: max_tokens ({max_tokens}) 小于最大单条评论的token数 ({max_single_token})")
        print(f"将自动调整 max_tokens 为 {max(max_single_token, 500)}")
        max_tokens = max(max_single_token, 500)  # 确保至少为500或最大单条评论的token数
    
    # 按类别分组，如果有CategoryName列
    if 'CategoryName' in df.columns:
        grouped = df.groupby('CategoryName')
        
        for category, group in grouped:
            print(f"处理类别: {category}, 共 {len(group)} 条评论")
            
            # 当前批次的文本和token计数
            current_texts = []
            current_token_count = 0
            
            # 记录第一行用于保留元数据
            first_row_in_batch = None
            
            # 遍历组内的每一行
            for _, row in group.iterrows():
                # 如果这是批次中的第一行，记录它
                if not current_texts:
                    first_row_in_batch = row
                
                # 获取当前行的文本和token数量
                text = row['text']
                token_count = row.get('token_count', count_tokens(text))
                
                # 如果单条评论就超过了最大token数，单独处理这条评论
                if token_count > max_tokens:
                    print(f"警告: 单条评论token数 ({token_count}) 超过最大限制 ({max_tokens})")
                    
                    # 如果当前批次有内容，先保存当前批次
                    if current_texts:
                        merged_text = separator.join(current_texts)
                        merged_row = {'text': merged_text}
                        
                        # 添加其他列的值
                        for col in other_columns:
                            merged_row[col] = first_row_in_batch[col]
                        
                        # 添加token计数
                        merged_row['token_count'] = current_token_count
                        
                        # 添加到结果
                        merged_rows.append(merged_row)
                        
                        # 重置当前批次
                        current_texts = []
                        current_token_count = 0
                    
                    # 尝试截断文本
                    truncated_text = truncate_text(text, max_tokens)
                    truncated_token_count = count_tokens(truncated_text)
                    
                    # 创建单独的行
                    merged_row = {'text': truncated_text}
                    
                    # 添加其他列的值
                    for col in other_columns:
                        merged_row[col] = row[col]
                    
                    # 添加token计数
                    merged_row['token_count'] = truncated_token_count
                    
                    # 添加到结果
                    merged_rows.append(merged_row)
                    
                    # 继续处理下一条评论
                    continue
                
                # 计算添加分隔符的token数
                separator_tokens = count_tokens(separator) if current_texts else 0
                
                # 检查添加这条评论后是否会超过token限制
                if current_token_count + token_count + separator_tokens > max_tokens:
                    # 如果会超过，先保存当前批次
                    if current_texts:
                        merged_text = separator.join(current_texts)
                        merged_row = {'text': merged_text}
                        
                        # 添加其他列的值
                        for col in other_columns:
                            merged_row[col] = first_row_in_batch[col]
                        
                        # 添加token计数
                        merged_row['token_count'] = current_token_count
                        
                        # 添加到结果
                        merged_rows.append(merged_row)
                        
                        # 重置当前批次
                        current_texts = [text]
                        current_token_count = token_count
                        first_row_in_batch = row
                    else:
                        # 这种情况不应该发生，因为我们已经处理了单条评论的token数
                        print("警告: 意外情况，当前批次为空但token计数检查失败")
                else:
                    # 如果不会超过，添加到当前批次
                    current_texts.append(text)
                    current_token_count += token_count + separator_tokens
            
            # 处理最后一个批次
            if current_texts:
                merged_text = separator.join(current_texts)
                merged_row = {'text': merged_text}
                
                # 添加其他列的值
                for col in other_columns:
                    merged_row[col] = first_row_in_batch[col]
                
                # 添加token计数
                merged_row['token_count'] = current_token_count
                
                # 添加到结果
                merged_rows.append(merged_row)
    else:
        # 如果没有CategoryName列，直接按行处理
        print("未找到CategoryName列，将直接按行处理")
        
        # 当前批次的文本和token计数
        current_texts = []
        current_token_count = 0
        
        # 记录第一行用于保留元数据
        first_row_in_batch = None
        
        # 遍历每一行
        for _, row in df.iterrows():
            # 如果这是批次中的第一行，记录它
            if not current_texts:
                first_row_in_batch = row
            
            # 获取当前行的文本和token数量
            text = row['text']
            token_count = row.get('token_count', count_tokens(text))
            
            # 如果单条评论就超过了最大token数，单独处理这条评论
            if token_count > max_tokens:
                print(f"警告: 单条评论token数 ({token_count}) 超过最大限制 ({max_tokens})")
                
                # 如果当前批次有内容，先保存当前批次
                if current_texts:
                    merged_text = separator.join(current_texts)
                    merged_row = {'text': merged_text}
                    
                    # 添加其他列的值
                    for col in other_columns:
                        merged_row[col] = first_row_in_batch[col]
                    
                    # 添加token计数
                    merged_row['token_count'] = current_token_count
                    
                    # 添加到结果
                    merged_rows.append(merged_row)
                    
                    # 重置当前批次
                    current_texts = []
                    current_token_count = 0
                
                # 尝试截断文本
                truncated_text = truncate_text(text, max_tokens)
                truncated_token_count = count_tokens(truncated_text)
                
                # 创建单独的行
                merged_row = {'text': truncated_text}
                
                # 添加其他列的值
                for col in other_columns:
                    merged_row[col] = row[col]
                
                # 添加token计数
                merged_row['token_count'] = truncated_token_count
                
                # 添加到结果
                merged_rows.append(merged_row)
                
                # 继续处理下一条评论
                continue
            
            # 计算添加分隔符的token数
            separator_tokens = count_tokens(separator) if current_texts else 0
            
            # 检查添加这条评论后是否会超过token限制
            if current_token_count + token_count + separator_tokens > max_tokens:
                # 如果会超过，先保存当前批次
                if current_texts:
                    merged_text = separator.join(current_texts)
                    merged_row = {'text': merged_text}
                    
                    # 添加其他列的值
                    for col in other_columns:
                        merged_row[col] = first_row_in_batch[col]
                    
                    # 添加token计数
                    merged_row['token_count'] = current_token_count
                    
                    # 添加到结果
                    merged_rows.append(merged_row)
                    
                    # 重置当前批次
                    current_texts = [text]
                    current_token_count = token_count
                    first_row_in_batch = row
                else:
                    # 这种情况不应该发生，因为我们已经处理了单条评论的token数
                    print("警告: 意外情况，当前批次为空但token计数检查失败")
            else:
                # 如果不会超过，添加到当前批次
                current_texts.append(text)
                current_token_count += token_count + separator_tokens
                
                # 如果达到了group_size，保存当前批次
                if len(current_texts) >= group_size:
                    merged_text = separator.join(current_texts)
                    merged_row = {'text': merged_text}
                    
                    # 添加其他列的值
                    for col in other_columns:
                        merged_row[col] = first_row_in_batch[col]
                    
                    # 添加token计数
                    merged_row['token_count'] = current_token_count
                    
                    # 添加到结果
                    merged_rows.append(merged_row)
                    
                    # 重置当前批次
                    current_texts = []
                    current_token_count = 0
                    first_row_in_batch = None
        
        # 处理最后一个批次
        if current_texts:
            merged_text = separator.join(current_texts)
            merged_row = {'text': merged_text}
            
            # 添加其他列的值
            for col in other_columns:
                merged_row[col] = first_row_in_batch[col]
            
            # 添加token计数
            merged_row['token_count'] = current_token_count
            
            # 添加到结果
            merged_rows.append(merged_row)
    
    # 创建新的DataFrame
    merged_df = pd.DataFrame(merged_rows)
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 保存处理后的CSV文件
    merged_df.to_csv(output_file, index=False)
    print(f"处理完成，已保存到 {output_file}")
    print(f"原始行数: {len(df)}, 合并后行数: {len(merged_df)}")
    print(f"合并后的列: {merged_df.columns.tolist()}")
    
    # 打印token统计信息
    if 'token_count' in merged_df.columns:
        print(f"合并后平均token数量: {merged_df['token_count'].mean():.2f}")
        print(f"合并后最大token数量: {merged_df['token_count'].max()}")
        print(f"合并后最小token数量: {merged_df['token_count'].min()}")
    
    # 添加一个示例，展示如何使用<ROW_SEP>分隔符进行切分
    if not merged_df.empty:
        first_text = merged_df.iloc[0]['text']
        rows = first_text.split('<ROW_SEP>')
        print(f"\n示例：第一条合并记录包含 {len(rows)} 条原始评论")
        print(f"可以使用 text.split('<ROW_SEP>') 进行切分")
    
    return output_file

def truncate_text(text, max_tokens):
    """
    截断文本，使其token数不超过max_tokens
    
    参数:
        text: 要截断的文本
        max_tokens: 最大token数
    
    返回:
        截断后的文本
    """
    # 如果文本为空，直接返回
    if not text:
        return text
    
    # 如果文本token数已经小于max_tokens，直接返回
    if count_tokens(text) <= max_tokens:
        return text
    
    # 按行分割文本
    lines = text.split('\n')
    
    # 保留评论的基本信息部分（前几行）和评论内容的开头部分
    essential_info = lines[:5]  # 保留前5行基本信息
    
    # 找到评论内容所在的行
    review_content_line = None
    for i, line in enumerate(lines):
        if line.startswith("评价内容:"):
            review_content_line = i
            break
    
    # 如果找到了评论内容行
    if review_content_line is not None:
        review_content = lines[review_content_line]
        
        # 提取评论内容的引号内部分
        content_match = re.search(r'"(.*)"', review_content)
        if content_match:
            content = content_match.group(1)
            
            # 计算已有内容的token数
            info_tokens = count_tokens('\n'.join(essential_info))
            
            # 计算评论内容可用的token数
            available_tokens = max_tokens - info_tokens - 20  # 预留一些空间给引号和省略号
            
            # 如果可用token数小于等于0，只保留基本信息
            if available_tokens <= 0:
                truncated_content = "..."
            else:
                # 截断评论内容
                truncated_content = truncate_content(content, available_tokens)
            
            # 替换原评论内容
            lines[review_content_line] = f'评价内容: "{truncated_content}..."'
            
            # 只保留必要的行
            return '\n'.join(essential_info + [lines[review_content_line]])
    
    # 如果没有找到评论内容行或处理失败，简单截断
    result = '\n'.join(essential_info)
    if count_tokens(result) > max_tokens:
        # 如果基本信息都超过了max_tokens，进一步简化
        result = '\n'.join(lines[:3]) + "\n...(内容已截断)..."
    
    return result

def truncate_content(content, max_tokens):
    """
    截断评论内容，使其token数不超过max_tokens
    
    参数:
        content: 评论内容
        max_tokens: 最大token数
    
    返回:
        截断后的内容
    """
    # 如果内容为空，直接返回
    if not content:
        return content
    
    # 如果内容token数已经小于max_tokens，直接返回
    if count_tokens(content) <= max_tokens:
        return content
    
    # 对于中文，按字符截断
    if re.search(r'[\u4e00-\u9fff]', content):
        # 二分查找合适的截断位置
        left, right = 0, len(content)
        while left < right:
            mid = (left + right) // 2
            if count_tokens(content[:mid]) <= max_tokens:
                left = mid + 1
            else:
                right = mid
        
        # 找到最后一个完整的句子结束位置
        last_sentence_end = max(
            content[:left-1].rfind('。'),
            content[:left-1].rfind('！'),
            content[:left-1].rfind('？'),
            content[:left-1].rfind('；'),
            content[:left-1].rfind(','),
            content[:left-1].rfind('，')
        )
        
        if last_sentence_end > 0:
            return content[:last_sentence_end+1]
        else:
            return content[:left-1]
    
    # 对于英文，按单词截断
    words = content.split()
    result = []
    current_tokens = 0
    
    for word in words:
        word_tokens = count_tokens(word)
        if current_tokens + word_tokens <= max_tokens:
            result.append(word)
            current_tokens += word_tokens
        else:
            break
    
    return ' '.join(result)

def list_files_in_export_dir():
    """列出导出目录中的所有文件"""
    if not os.path.exists(EXPORT_DIR):
        print(f"导出目录 {EXPORT_DIR} 不存在")
        return
    
    print(f"导出目录 {EXPORT_DIR} 中的文件:")
    for file in os.listdir(EXPORT_DIR):
        file_path = os.path.join(EXPORT_DIR, file)
        if os.path.isfile(file_path):
            print(f"  - {file} ({os.path.getsize(file_path)} 字节)")

if __name__ == "__main__":
    # 列出导出目录中的文件
    list_files_in_export_dir()
    
    # 如果直接运行此脚本，处理默认路径的文件
    processed_file = preprocess_reviews()
    
    # 如果处理成功，则合并处理后的评论
    if processed_file:
        merge_csv_rows(
            input_file=processed_file,
            max_tokens=1000  # 设置最大token数为1000
        ) 