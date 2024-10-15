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
from temp_dir import TempDir

class ChatHandler:
    def __init__(self):
        llm = OpenAI(model = "gpt-4o-mini")
        embed_model = OpenAIEmbedding(moedl = "text-embedding-3-small")
        Settings.embed_model = embed_model
        Settings.llm = llm

        self.vector_store = OpensearchVectorStore(self.default_opensearch())
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
        
    def add_documents(self, uploaded_files):
        file_dict = {file.name: file.getvalue() for file in uploaded_files}
        with TempDir(file_dict) as tempdir:
            reader = SimpleDirectoryReader(input_dir=tempdir)
            docs = reader.load_data()
            print(docs)
            self.index.refresh(docs)
        
    def default_opensearch(self):
        return OpensearchVectorClient(
            endpoint="http://localhost:9200",
            index="data-mining-embeddings",
            dim=1536,
        )
        
    def new_conversation(self):
        self.memory.reset()

    def handle_chat(self, chat):
        response = self.chat_engine.stream_chat(chat)
        for token in response.response_gen:
            yield token