from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('distilbert-base-nli-mean-tokens')

department_name = "Department of Computer Science"
department_name_encoding = model.encode(department_name)
sentences = [
    'Computer Science',
    'Electrical and Computer Engineering',
    'Architecture'
    ]

sentence_embeddings = model.encode(sentences)
for i in range(0, len(sentences)):
  result = util.pytorch_cos_sim(department_name_encoding, sentence_embeddings[i])
  if(result.item()>=0.90):
    print(sentences[i]+" is similar to "+ department_name)
