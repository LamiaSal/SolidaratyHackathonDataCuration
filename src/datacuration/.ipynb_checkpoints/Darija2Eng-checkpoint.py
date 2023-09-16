"""
class to traduct text from darija to english
"""
class Darija2Eng :
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
        "facebook/nllb-200-distilled-600M", src_lang="ary_Arab",
        )
        self.model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")
        
    def prediction(self, article : str):
        inputs = self.tokenizer(article, return_tensors="pt")

        translated_tokens = self.model.generate(
            **inputs, forced_bos_token_id=tokenizer.lang_code_to_id["eng_Latn"], max_length=30
        )
        outputs = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]

        return outputs