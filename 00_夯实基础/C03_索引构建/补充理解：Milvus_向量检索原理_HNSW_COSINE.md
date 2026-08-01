# Milvus 向量检索原理（HNSW + COSINE）

> 面向 RAG、LangChain、Milvus 初学者与培训课程的学习笔记。

---

## 目录

- [官方文档](#官方文档)
- [第一章 Milvus 核心概念](#第一章-milvus-核心概念)
- [第二章 向量检索整体架构](#第二章-向量检索整体架构)
- [第三章 Metric（相似度计算）](#第三章-metric相似度计算)
- [第四章 HNSW 是什么](#第四章-hnsw-是什么)
- [第五章 HNSW 建图](#第五章-hnsw-建图)
- [第六章 HNSW 查询](#第六章-hnsw-查询)
- [第七章 HNSW 与 Metric 如何协同](#第七章-hnsw-与-metric-如何协同)
- [第八章 HNSW 参数](#第八章-hnsw-参数)
- [第九章 LangChain 与 Milvus](#第九章-langchain-与-milvus)
- [第十章 推荐配置](#第十章-推荐配置)
- [第十一章 常见误区与排错](#第十一章-常见误区与排错)
- [一句话总结](#一句话总结)

---

## 官方文档

- Milvus 中文文档首页：https://milvus.io/docs/zh
- 什么是 Milvus（Overview）：https://milvus.io/docs/zh/overview.md
- 索引（Index Explained）：https://milvus.io/docs/zh/index-explained.md
- 相似度量（Metric）：https://milvus.io/docs/zh/metric.md
- HNSW 索引：https://milvus.io/docs/zh/hnsw.md

---

## 第一章 Milvus 核心概念

### 1.1 什么是 Milvus

Milvus 是一款开源向量数据库（Vector Database），专门用于存储、索引和检索高维向量数据。

**传统数据库擅长：**

- 精确查询（Exact Match）
- SQL
- 事务处理

**Milvus 擅长：**

- 相似性搜索（Similarity Search）
- AI 检索
- RAG
- 推荐系统
- 图像检索

> 一句话：Milvus = 专门用于向量检索的数据库。

---

### 1.2 Embedding

Embedding 是利用深度学习模型，将文本、图片、音频等数据转换为高维向量。

```
文本
 ↓
Embedding Model
 ↓
Vector
```

Embedding 保存的是**语义信息**，而不是关键字——这是它和传统关键词检索（如 Elasticsearch 全文检索）最本质的区别。

---

### 1.3 Vector

Embedding 输出的数据就是向量，例如：

```text
[0.21, 0.75, -0.31, ...]
```

Milvus 中通常保存：

- ID
- Metadata
- Vector

真正参与检索的是 **Vector**。

---

### 1.4 Collection

Collection 相当于关系数据库中的 Table。

例如：

```
rag_docs
```

里面保存：

- Document（原文/分片文本）
- Metadata（来源、时间、标签等）
- Vector（Embedding 结果）

---

### 1.5 Index

Index 决定：

> 如何快速找到相似向量。

常见类型：

| Index | 特点 |
|---|---|
| FLAT | 暴力全量比对，100% 精确，速度最慢，小数据集或需要精确结果时用 |
| IVF_FLAT | 先聚类分桶，再桶内比对，速度与精度折中 |
| HNSW | 基于图的近似搜索，速度快、精度高，内存占用较大 |
| DiskANN | 面向磁盘存储优化，适合超大规模、内存受限场景 |

> 注意：**Index 决定"怎么找"，不是"什么叫相似"。**

---

### 1.6 Metric

Metric 决定：

> 什么叫相似。

Milvus 常见的三种度量方式：

| Metric | 全称 | 中文 |
|---|---|---|
| COSINE | Cosine Similarity | 余弦相似度 |
| IP | Inner Product | 内积 |
| L2 | Euclidean Distance | 欧氏距离 |

---

### 1.7 ANN

**ANN = Approximate Nearest Neighbor（近似最近邻搜索）**

作用：不用遍历所有向量，而是快速找到 TopK 近似结果。

常见 ANN 算法：

- HNSW
- IVF
- DiskANN

---

### 1.8 Reranker

向量数据库返回 TopK 后，可以继续对结果重新排序，进一步提升相关性。

常见方式：

- **MMR**（Maximal Marginal Relevance）：兼顾相关性与多样性，避免结果过于同质化
- **RRF**（Reciprocal Rank Fusion）：融合多路召回（如向量检索 + 关键词检索）的排序结果
- **CrossEncoder**：用更精细的模型对 query-doc 对重新打分，精度高但速度慢，一般只用于对 TopK 做二次排序

> Reranker 不属于 Milvus 索引范畴，通常在应用层（LangChain/业务代码）实现。

---

### 1.9 整体关系

```text
Documents
    │
Embedding
    │
Vectors
    │
Collection
    │
Index (HNSW)
    │
Metric (COSINE)
    │
TopK
    │
Reranker (可选)
    │
LLM
```

---

## 第二章 向量检索整体架构

```
Query
 │
Embedding
 │
Query Vector
 │
HNSW（ANN）
 │
COSINE / IP / L2
 │
TopK
 │
LLM
```

三个层次：

| 层次 | 内容 | 示例 |
|---|---|---|
| 相似度计算 | Metric | COSINE、IP、L2 |
| ANN 索引 | Index | HNSW、IVF、DiskANN |
| 重排序 | Reranker | MMR、RRF、CrossEncoder |

---

## 第三章 Metric（相似度计算）

### COSINE（余弦相似度）

- 只比较**方向**，不比较长度（模长）
- 值域 `[-1, 1]`，越接近 1 越相似
- **最适合文本 Embedding**：文本语义的关键在于方向，而非向量的绝对大小

### IP（内积）

同时比较：

- 方向
- 长度

> 如果 Embedding 已归一化（单位向量），则 **IP ≈ COSINE**。

这也是为什么很多向量数据库（包括 Milvus）在归一化数据上会优先用 IP 做底层计算——数学等价，但省去了除以模长的开销，速度更快。

### L2（欧氏距离）

计算两点之间的直线距离。

> 距离越小越相似（与 COSINE/IP "越大越相似"方向相反，配置时容易搞混，需注意）。

### 三种 Metric 对比速查

| Metric | 是否比较长度 | 值域 | 相似方向 | 典型场景 |
|---|---|---|---|---|
| COSINE | 否 | [-1, 1] | 值越大越相似 | 文本语义检索（RAG 首选） |
| IP | 是 | 不固定 | 值越大越相似 | 已归一化向量、追求极致性能 |
| L2 | 是 | [0, +∞) | 值越小越相似 | 图像/坐标类特征，绝对尺度有意义的场景 |

---

## 第四章 HNSW 是什么

全称：

**Hierarchical Navigable Small World（分层可导航小世界图）**

作用：

> 快速找到近似最近邻。

关键认知：

> HNSW **不计算相似度**，它只负责**组织索引结构**——具体"谁离谁近"仍然由 Metric（如 COSINE）来判断。

可以理解为：HNSW 是"地图和导航系统"，Metric 是"判断两地距离远近的尺子"。

---

## 第五章 HNSW 建图

### 建图流程

```
Document
 ↓
Embedding
 ↓
Vector
 ↓
随机决定最高层
 ↓
利用已有 HNSW 导航
 ↓
COSINE 寻找邻居
 ↓
efConstruction 搜索候选
 ↓
选择 M 个邻居
 ↓
建立连接
```

### 说明

- 每个新插入的节点，会按**指数衰减概率**随机生成它所在的最高层——大多数节点只存在于底层，越往上节点越稀疏。
- **所有节点都存在于 Level 0**（最底层），这是保证全图连通、任何查询最终都能找到结果的基础。
- 高层节点越来越少，形成金字塔结构，高层负责"粗定位"，底层负责"精细搜索"。
- 建边依据完全由 Metric（例如 COSINE）决定：距离越近，越可能被选为邻居。

### 直观类比

高层就像高速公路（节点少、跨度大，快速拉近距离），底层就像小区内部道路（节点密集，精确定位到具体楼栋）。查询时"从高速公路下到小路"，正是 HNSW 分层的核心思想。

---

## 第六章 HNSW 查询

### 查询流程

```
Query
 ↓
Embedding
 ↓
Query Vector
 ↓
最高层入口
 ↓
HNSW 导航
 ↓
每一步计算 COSINE
 ↓
下降到底层
 ↓
TopK
```

### 关键点

COSINE **不是最后算一次**，而是在整个导航过程中**每一步都在计算**：每到一个节点，就要比较它的邻居谁离 Query 更近，从而决定下一步往哪走。这正是 HNSW 之所以快的原因——不断用局部比较代替全局遍历。

---

## 第七章 HNSW 与 Metric 如何协同

### 建图阶段

```
Vector
 ↓
COSINE 计算距离
 ↓
寻找邻居
 ↓
HNSW 建立边
```

- **COSINE**：负责判断谁近（提供"近"的定义）
- **HNSW**：负责建立导航图（提供"怎么快速找到近的路径"）

### 查询阶段

```
Query
 ↓
HNSW 导航
 ↓
COSINE 判断下一步
 ↓
继续导航
 ↓
TopK
```

> 一句话：**COSINE 定义"什么叫近"，HNSW 定义"如何最快找到近的向量"。**

---

## 第八章 HNSW 参数

### M（Maximum Connections）

控制：每个节点最多连接多少邻居。

- M 越大：图的连接更密集，召回率更高，但内存占用和建图时间也更高
- M 越小：图更稀疏，速度快、省内存，但精度可能下降

推荐：

```
M = 16
```

（大多数场景够用；对召回率要求极高时可尝试 32~64）

---

### efConstruction（Expansion Factor during Construction）

建图时：搜索多少候选节点来挑选邻居。

- 值越大，建图质量越高（图的连接更合理），但建图速度更慢
- 只影响**建图阶段**，不影响查询速度

推荐：

```
200
```

---

### ef / efSearch（Expansion Factor during Search）

查询时：探索多少候选节点。

- 值越大，召回率越高，但查询延迟也越高
- 是**查询阶段**最主要的"精度 vs 速度"调节旋钮，可以随时调整，无需重建索引

推荐：

```
64 ~ 200
```

> 实践建议：以上数值是常见经验值，实际最优参数需结合数据规模、维度和业务对召回率/延迟的要求，通过实测（如召回率-QPS 曲线）确定。

---

### 参数职责一览

| 参数 | 作用阶段 | 作用 |
|---|---|---|
| COSINE (Metric) | 建图 + 查询 | 判断谁最近 |
| M | 建图 | 最终每个节点连接多少邻居 |
| efConstruction | 建图 | 建图时搜索多少候选 |
| ef | 查询 | 查询时探索多少候选 |

---

## 第九章 LangChain 与 Milvus

### 首次创建

```python
Milvus.from_documents(...)
```

会自动完成：

- 创建 Collection
- 创建 Schema
- 创建 HNSW Index
- 导入数据

### 后续追加数据

```python
add_documents(...)
```

只负责插入数据，**不会重新建索引**（Milvus 内部增量维护索引结构）。

### 连接已存在的 Collection

如果 Collection 已经创建过，不需要每次都走 `from_documents`（否则可能重复建索引或报错），而是直接实例化并 attach：

```python
from langchain_milvus import Milvus

vectorstore = Milvus(
    embedding_function=embeddings,
    collection_name="rag_docs",
    connection_args={"uri": "http://localhost:19530"},
)
```

这样可以直接对已有 Collection 做 `similarity_search` 或 `add_documents`，无需重建索引。

---

## 第十章 推荐配置

```python
index_params = {
    "index_type": "HNSW",
    "metric_type": "COSINE",
    "params": {
        "M": 16,
        "efConstruction": 200,
    }
}

search_params = {
    "params": {
        "ef": 100
    }
}
```

适用于：

- LangChain
- LlamaIndex
- Dify
- OpenWebUI
- 企业 RAG 知识库

---

## 第十一章 常见误区与排错

| 误区 | 正确理解 |
|---|---|
| "HNSW 是一种相似度算法" | 错，HNSW 是索引结构，相似度由 Metric 决定 |
| "M 越大越好" | 错，M 增大会显著增加内存占用，需权衡 |
| "ef 需要重建索引才能改" | 错，ef 是查询参数，可随时调整，无需重建 |
| "COSINE 和 IP 效果一样" | 只有向量**归一化后**才近似相等，未归一化会有差异 |
| "index_type 和 metric_type 建索引后能随便改" | 错，一旦建索引，metric_type 通常需要重建 Collection/Index 才能更改 |

---

## 一句话总结

- **Embedding**：把文本变成向量。
- **Metric**：定义什么叫相似。
- **HNSW**：快速找到相似向量。
- **Reranker**：进一步优化排序。

> COSINE 决定"谁最近"，HNSW 决定"如何最快找到最近的人"。
