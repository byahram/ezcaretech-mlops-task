import torch
import time
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class ModelLoader:
    def __init__(self, model_name="snunlp/KR-FinBert-SC"):
        self.model_name = model_name
        # Acceleration: MPS for Apple Silicon, CUDA for NVIDIA, or CPU
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
        elif torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")
            
        self.tokenizer = None
        self.model = None

    def load_model(self):
        print(f"[*] Initializing model on device: {self.device}")
        start_time = time.time()
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name).to(self.device)
        
        print(f"[+] Model loaded in {time.time() - start_time:.2f}s")
        return self.tokenizer, self.model

    def benchmark(self, test_text="이 기업의 실적은 우수합니다.", iterations=50):
        if self.model is None:
            self.load_model()

        inputs = self.tokenizer(test_text, return_tensors="pt").to(self.device)
        
        # Warm-up run
        with torch.no_grad():
            _ = self.model(**inputs)

        start_time = time.time()
        for _ in range(iterations):
            with torch.no_grad():
                self.model(**inputs)
        
        avg_latency = ((time.time() - start_time) / iterations) * 1000
        tps = 1000 / avg_latency

        print(f"--- Benchmark Result: {self.device} ---")
        print(f"Latency: {avg_latency:.2f} ms | TPS: {tps:.2f}")
        return avg_latency, tps

if __name__ == "__main__":
    loader = ModelLoader()
    loader.benchmark()