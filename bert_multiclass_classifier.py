import numpy as np
import torch
from transformers import BertTokenizer

class BertMulticlassClassifier:
    def __init__(self):
        self.model = torch.load('/models/bert_multiclass.pt', map_location=torch.device('cpu'))
        self.tokenizer = BertTokenizer.from_pretrained('cointegrated/rubert-tiny')
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.max_len = 512
        self.model.to(self.device)

    def predict(self, text):
        self.model.eval()
        text = " ".join(text.split())

        inputs = self.tokenizer.encode_plus(
            text,
            None,
            add_special_tokens=True,
            max_length=self.max_len,
            pad_to_max_length=True,
            truncation=True,
            return_token_type_ids=True
        )
        ids_list = []
        ids = inputs['input_ids']
        ids_list.append(ids)

        mask_list = []
        mask = inputs['attention_mask']
        mask_list.append(mask)

        token_type_ids = inputs["token_type_ids"]

        token_data = {
            'ids': torch.tensor(ids_list, dtype=torch.long),
            'mask': torch.tensor(mask_list, dtype=torch.long),
            'token_type_ids': torch.tensor(token_type_ids, dtype=torch.long)
        }

        ids = token_data['ids'].to(self.device, dtype = torch.long)
        mask = token_data['mask'].to(self.device, dtype = torch.long)
        token_type_ids = token_data['token_type_ids'].to(self.device, dtype = torch.long)

        outputs = self.model(ids, mask, token_type_ids)

        predictions = torch.sigmoid(outputs).cpu().detach().numpy().tolist()

        return (np.array(predictions) >= 0.5)[0]