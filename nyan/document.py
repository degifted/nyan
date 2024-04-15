import json
import os
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass, field

from tqdm import tqdm

from nyan.mongo import get_documents_collection, get_annotated_documents_collection
from nyan.util import Serializable


CURRENT_VERSION = 6


@dataclass
class Document(Serializable):
    url: str
    channel_id: str
    post_id: int
    views: int
    pub_time: int
    text: str = None
    fetch_time: int = None
    images: List[str] = tuple()
    links: List[str] = tuple()
    videos: List[str] = tuple()
    reply_to: str = None
    forward_from: str = None

    channel_title: str = ""
    has_obscene: bool = False
    patched_text: str = None
    groups: Dict[str, str] = field(default_factory=dict)
    issue: str = None
    language: str = None
    category: str = None
    category_scores: Dict[str, float] = field(default_factory=dict)
    tokens: str = None
    embedding: List[float] = None
    embedding_key: str = "multilingual_e5_base"
    embedded_images: List[Dict[str, Any]] = tuple()

    version: int = CURRENT_VERSION

    def is_reannotation_needed(self, new_doc):
        assert new_doc.url == self.url
        if self.version != CURRENT_VERSION:
            return True
        return new_doc.text != self.text

    def is_discarded(self):
        if self.issue is None:
            return True
        if self.groups is None:
            return True
        if not self.patched_text or len(self.patched_text) < 12:
            return True
        return self.category == "not_news"

    def update_meta(self, new_doc):
        self.fetch_time = new_doc.fetch_time
        self.views = new_doc.views

    def asdict(self, is_short: bool = False):
        record = super().asdict()
        if is_short:
            record.pop("text")
            record.pop("embedding")
            record.pop("embedded_images")
        return record

    @property
    def cropped_text(self, max_words_count: int = 50):
        words = self.patched_text.split()
        if len(words) < max_words_count:
            return " ".join(words)
        return " ".join(words[:max_words_count]) + "..."


def read_documents_file(file_path, current_ts=None, offset=None):
    assert os.path.exists(file_path)
    with open(file_path) as r:
        docs = [Document.deserialize(line) for line in r]
        if current_ts and offset:
            docs = [doc for doc in docs if doc.pub_time >= current_ts - offset]
    return docs


def read_documents_mongo(mongo_config_path, current_ts, offset):
    collection = get_documents_collection(mongo_config_path)
    docs = list(collection.find({"pub_time": {"$gte": current_ts - offset}}))
    return [Document.fromdict(doc) for doc in docs]


def read_annotated_documents_mongo(mongo_config_path, docs):
    collection = get_annotated_documents_collection(mongo_config_path)
    annotated_docs = []
    remaining_docs = []
    for doc in tqdm(docs, desc="Reading annotated docs from Mongo"):
        annotated_doc = collection.find_one({"url": doc.url})
        if not annotated_doc:
            remaining_docs.append(doc)
            continue

        annotated_doc = Document.fromdict(annotated_doc)
        if annotated_doc.is_reannotation_needed(doc):
            remaining_docs.append(doc)
            continue

        annotated_doc.update_meta(doc)
        assert annotated_doc.embedding is not None
        assert annotated_doc.patched_text is not None
        annotated_docs.append(annotated_doc)
    return annotated_docs, remaining_docs


def write_annotated_documents_mongo(mongo_config_path, docs):
    collection = get_annotated_documents_collection(mongo_config_path)

    indices = collection.index_information()
    if "url_1" not in indices:
        collection.create_index([("url", 1)], name="url_1")

    for doc in docs:
        assert doc.embedding is not None
        assert doc.patched_text is not None
        collection.replace_one({"url": doc.url}, doc.asdict(), upsert=True)
