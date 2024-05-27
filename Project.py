#!/usr/bin/env python
# coding: utf-8

# In[96]:


import os
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


# In[97]:


folder_path = 'output/'
files = os.listdir(folder_path)


# In[98]:


csv_files = []


# In[99]:


csv_files = [file for file in files if file.endswith('.csv')]


# In[100]:


len(csv_files)


# In[101]:


columns = ['Transaction ID', 'User ID', 'Name', 'Timestamp', 'Amount', 'Card Number', 'Merchant ID', 'Merchant', 'Merchant Category', 'Latitude', 'Longitude', 'Transaction Type', 'Transaction Device']


# In[102]:


dfs = pd.DataFrame(columns=columns)


# In[103]:


def is_file_empty(file_path):
    return os.path.getsize(file_path) == 0


# In[104]:


for csv_file in csv_files:
    file_path = os.path.join(folder_path, csv_file)
    if is_file_empty(file_path):
        print("File is empty")
    else:
        dataframe = pd.read_csv(file_path,header=None)
        dataframe.columns = columns
        dfs = dfs.append(dataframe,ignore_index=True)


# In[105]:


dfs.head()


# # Tokenization

# In[106]:


import pandas as pd
import hashlib
import secrets


# In[ ]:





# In[107]:


def tokenize(value):
    return secrets.token_hex(16)


# In[108]:


def tokenize_dataframe(df, columns_to_tokenize):
    tokenized_df = df.copy()
    for column in columns_to_tokenize:
        tokenized_df[column] = tokenized_df[column].apply(tokenize)
    return tokenized_df


# In[109]:


columns_to_tokenize = ['Card Number', 'Transaction ID','Name', 'User ID']


# In[110]:


tokenized_df = tokenize_dataframe(dfs, columns_to_tokenize)


# In[111]:


tokenized_df.head()


# In[ ]:





# In[ ]:





# # Data Privacy 

# In[112]:


import pandas as pd
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


# In[113]:


data = dfs


# In[114]:


k_values = range(2, 101)
silhouette_scores = []


# In[115]:


X = data[['Latitude', 'Longitude']]


# In[116]:


for k in k_values:
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(X)
    if len(set(kmeans.labels_)) < 2:
        silhouette_scores.append(float('-inf'))  # Assign a very low score
        continue
    
    silhouette_scores.append(silhouette_score(X, kmeans.labels_))


# In[117]:


# Find the index of the maximum silhouette score
best_k_index = silhouette_scores.index(max(silhouette_scores))


# In[118]:


# Get the best k value
best_k = k_values[best_k_index]


# In[119]:


# Plot the silhouette scores
#Silhouette value is a measure of how similar an object is to its own cluster (cohesion) compared to other clusters (separation)
plt.figure(figsize=(10, 6))
plt.plot(k_values, silhouette_scores, marker='o', linestyle='-')
plt.title('Silhouette Score vs. Value of K')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Silhouette Score')
plt.xticks(range(2, 101, 5))
plt.grid(True)
plt.tight_layout()
plt.show()


# In[120]:


print(f"The best k value is: {best_k}")


# In[121]:


k = best_k


# In[122]:


# Anonymize sensitive attributes
dfs['Name'] = dfs['Name'].apply(lambda x: str(x)[0] + '*'*(len(str(x))-1))
dfs['Card Number'] = dfs['Card Number'].apply(lambda x: '*'*(len(str(x))-4) + str(x)[-4:])
dfs['Merchant'] = dfs['Merchant'].apply(lambda x: str(x)[0] + '*'*(len(str(x))-1))


# In[ ]:





# In[ ]:





# # LSH

# In[199]:


import pandas as pd
from datasketch import MinHashLSH, MinHash
import hashlib
import networkx as nx
import matplotlib.pyplot as plt


# In[200]:


# Load your data into a DataFrame (replace 'data.csv' with your actual data file)
data = dfs


# In[201]:


selected_columns = ['Transaction ID', 'User ID', 'Name']  # Add more columns as needed
selected_data = data[selected_columns]


# In[202]:


# Convert each row to a set of shingles
def row_to_shingles(row):
    shingles = []
    for value in row:
        if isinstance(value, str):
            shingles.append(value)
        else:
            shingles.append(str(value))
    return set(shingles)

shingles = selected_data.apply(row_to_shingles, axis=1)


# In[203]:


# Initialize MinHash objects for each row
minhashes = []
for shingle_set in shingles:
    m = MinHash(num_perm=128)  # Adjust num_perm as needed
    for shingle in shingle_set:
        m.update(hashlib.md5(shingle.encode('utf-8')).digest())
    minhashes.append(m)


# In[205]:


# Create the LSH index
lsh = MinHashLSH(threshold=0.5, num_perm=128)


# In[206]:


# Index each MinHash object
for i, minhash in enumerate(minhashes):
    lsh.insert(str(i), minhash)


# In[207]:


# Create a graph to represent the mappings
G = nx.Graph()


# In[208]:


# Add nodes for each item
for i in range(len(minhashes)):
    G.add_node(i, label=str(selected_data.iloc[i]))


# In[209]:


# Add edges for mappings between similar items
for i, minhash in enumerate(minhashes):
    result = lsh.query(minhash)
    for idx in result:
        if int(idx) != i:
            G.add_edge(i, int(idx))


# In[210]:


# Draw the graph with zooming enabled
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G)  # Position nodes using the spring layout algorithm
nx.draw(G, pos, with_labels=True, node_size=3000, node_color='skyblue', font_size=10, font_weight='bold')
plt.title('Mapping between Items')
plt.show()


# In[ ]:





# In[ ]:




