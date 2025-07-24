from typing import Dict, List, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import json
from pathlib import Path
import os
import hashlib
import time
import PyPDF2

class EmbeddingService:
    def __init__(self):
        # 使用多语言模型以支持中文
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.index_dir = Path("indexes")
        self.index_dir.mkdir(exist_ok=True)
        
        # 初始化空索引和文档存储
        self.dimension = 384  # 修改为与模型输出维度一致
        self.current_index = None
        self.current_documents = {}
    
    def _generate_safe_id(self, metadata: dict) -> str:
        """生成安全的文件ID"""
        # 使用时间戳和文件信息生成唯一ID
        timestamp = str(int(time.time()))
        file_info = f"{metadata.get('filename', '')}_{timestamp}"
        # 使用MD5生成安全的文件名
        return hashlib.md5(file_info.encode()).hexdigest()
        
    def _create_index(self) -> faiss.IndexFlatL2:
        """创建新的 FAISS 索引"""
        return faiss.IndexFlatL2(self.dimension)
    
    def _get_index_path(self, file_path: str) -> str:
        """生成索引文件路径"""
        # 使用文件路径的哈希作为索引文件名
        file_hash = hashlib.md5(file_path.encode()).hexdigest()
        return f"indexes/index_{file_hash}.bin"
    
    async def create_embeddings(self, file_path: str, index_dir: str) -> Dict:
        """从文件创建向量索引"""
        try:
            # 读取 PDF 文件内容
            text_chunks = []
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text_chunks.append(page.extract_text())
            
            # 创建索引
            index = self._create_index()
            
            # 使用 SentenceTransformer 生成向量
            vectors = self.model.encode(text_chunks)
            vectors = vectors.astype('float32')  # 确保类型正确
            
            # 添加向量到索引
            index.add(vectors)
            
            # 生成文件 ID
            file_hash = hashlib.md5(file_path.encode()).hexdigest()
            index_id = f"index_{file_hash}"
            
            # 创建文档数据
            documents = {}
            for i, text in enumerate(text_chunks):
                documents[str(i)] = {
                    "text": text,
                    "metadata": {
                        "page": i + 1,
                        "source": file_path
                    }
                }
            
            # 保存索引和文档数据
            self._save_index(file_hash, index, documents)
            
            return {
                "status": "success",
                "index_id": index_id,
                "chunks": len(text_chunks)
            }
            
        except Exception as e:
            raise Exception(f"创建向量失败: {str(e)}")
    
    def _save_index(self, file_id: str, index: faiss.Index, documents: dict):
        """保存索引和文档数据"""
        try:
            # 使用安全的文件名
            index_path = self.index_dir / f"index_{file_id}.bin"  # 这里添加了 "index_" 前缀
            docs_path = self.index_dir / f"docs_{file_id}.json"
            
            
            # 保存 FAISS 索引
            faiss.write_index(index, str(index_path))
            
            # 保存文档数据
            with open(docs_path, 'w', encoding='utf-8') as f:
                json.dump(documents, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            raise Exception(f"保存索引失败: {str(e)}")
    
    def _load_index(self, index_id: str):
        """加载索引和文档数据"""
        try:
            # 保持与保存时相同的文件名格式
            index_path = self.index_dir / f"{index_id}.bin"  # 这里没有添加 "index_" 前缀，因为 index_id 已经包含了
            docs_path = self.index_dir / f"docs_{index_id.replace('index_', '')}.json"
            
            
            if not index_path.exists() or not docs_path.exists():
                # 尝试旧的文件名格式
                old_index_path = self.index_dir / f"index_{index_id}.bin"
                old_docs_path = self.index_dir / f"docs_{index_id}.json"
                
                if old_index_path.exists() and old_docs_path.exists():
                    index_path = old_index_path
                    docs_path = old_docs_path
                else:
                    raise FileNotFoundError(f"找不到索引文件: {index_id}")
            
            # 加载索引
            self.current_index = faiss.read_index(str(index_path))
            
            # 验证索引维度
            if self.current_index.d != self.dimension:
                raise ValueError(f"索引维度不匹配: 期望 {self.dimension}, 实际 {self.current_index.d}")
            
            # 加载文档数据
            with open(docs_path, 'r', encoding='utf-8') as f:
                self.current_documents = json.load(f)
            
            # 验证是否有数据
            if not self.current_documents:
                raise ValueError("文档数据为空")
            
            print(f"成功加载索引 {index_id}: {self.current_index.ntotal} 个向量, {len(self.current_documents)} 个文档")
            
        except Exception as e:
            self.current_index = None
            self.current_documents = {}
            raise Exception(f"加载索引失败: {str(e)}")
    
    async def search(self, query: str, top_k: int = 3) -> List[dict]:
        """搜索最相关的文档片段"""
        try:
            if not self.current_index:
                raise Exception("未加载索引")
            
            # 生成查询向量
            query_vector = self.model.encode([query], convert_to_tensor=False)
            query_vector = query_vector.astype('float32')
            
            # 搜索最相似的向量
            distances, indices = self.current_index.search(query_vector, top_k)
            
            # 返回结果
            results = []
            for i in range(len(indices[0])):
                idx_str = str(int(indices[0][i]))
                if idx_str in self.current_documents:
                    results.append({
                        "score": float(distances[0][i]),
                        "content": self.current_documents[idx_str]["text"],
                        "metadata": self.current_documents[idx_str]["metadata"]
                    })
            
            return results
                
        except Exception as e:
            raise Exception(f"搜索失败: {str(e)}") 