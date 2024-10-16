from llama_index.core.llama_dataset import download_llama_dataset
from llama_index.core.llama_pack import download_llama_pack
from llama_index.core import VectorStoreIndex
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core import SimpleDirectoryReader, StorageContext
from llama_index.core.llama_dataset import LabelledRagDataset
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.opensearch import (
    OpensearchVectorStore,
    OpensearchVectorClient,
)
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from temp_dir import TempDir
from time import time

class ChatHandler:
    def __init__(self, index_name="data-mining-embeddings"):
        llm = OpenAI(model = "gpt-4o-mini")
        embed_model = OpenAIEmbedding(moedl = "text-embedding-3-small")
        Settings.embed_model = embed_model
        Settings.llm = llm

        self.vector_store = OpensearchVectorStore(self.default_opensearch(index_name))
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store
        )
        
        # creating chat memory buffer
        self.memory = ChatMemoryBuffer.from_defaults()
        # creating chat engine
        self.chat_engine = self.index.as_chat_engine(
            chat_mode="condense_plus_context",
            memory=self.memory,
            llm=llm,
        )
    
    def add_text(self, text):
        docs = [Document(text=text)]
        node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
        docs = node_parser.get_nodes_from_documents(docs)
        self.index.insert_nodes(docs)
        return len(docs)
        
    def add_documents(self, uploaded_files):
        start_time = time()
        file_dict = {file.name: file.getvalue() for file in uploaded_files}
        docs = []
        with TempDir(file_dict) as tempdir:
            reader = SimpleDirectoryReader(input_dir=tempdir)
            docs = reader.load_data()
            node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
            docs = node_parser.get_nodes_from_documents(docs)
            self.index.insert_nodes(docs)
        print(docs)
        print(len(docs))
        return len(docs), time() - start_time
        
    def default_opensearch(self, index_name):
        return OpensearchVectorClient(
            endpoint="http://localhost:9200",
            index=index_name,
            dim=1536,
        )
        
    def new_conversation(self):
        self.memory.reset()

    def handle_chat(self, chat):
        response = self.chat_engine.stream_chat(chat)
        for token in response.response_gen:
            yield token