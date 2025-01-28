from semanticscholar import SemanticScholar
import pickle as pkl
import csv
import json
from difflib import SequenceMatcher as sm
from tqdm.notebook import tqdm
import pandas as pd
from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from os import path


def get_field(p):
    if 'fieldOfStudy' in p and p['fieldOfStudy']:
      return p['fieldsOfStudy'][0]
    if 's2FieldsOfStudy' in p and p['s2FieldsOfStudy']:
      return p['s2FieldsOfStudy'][0]['category']

with open('papers.json', 'r') as f:
    papers = json.load(f)

sns.set_theme(style="whitegrid")
f, ax = plt.subplots(figsize=(20, 6))

yearly = Counter()
for pid in papers:
    field = get_field(papers[pid])
    if 'year' in papers[pid] and papers[pid]['year'] and 2025 > int(papers[pid]['year']) > 2012:
        yearly[papers[pid]['year']] += 1

yearly_df = pd.DataFrame([{'year': key, 'count': yearly[key]} for key in yearly])

sns.barplot(data=yearly_df, x="year", y='count')
ax.set(xlabel='', ylabel='paper count', title='XAI growth')
plt.savefig('xai/figures/yearly-growth.png')

# Medicine only
sns.set_theme(style="whitegrid")
f, ax = plt.subplots(figsize=(20, 6))

yearly = Counter()
for pid in papers:
    field = get_field(papers[pid])
    if field != 'Medicine':
        continue
    if 'year' in papers[pid] and papers[pid]['year'] and 2025 > int(papers[pid]['year']) > 2012:
        yearly[papers[pid]['year']] += 1

yearly_df = pd.DataFrame([{'year': key, 'count': yearly[key]} for key in yearly])

sns.barplot(data=yearly_df, x="year", y='count')
ax.set(xlabel='', ylabel='paper count', title='XAI growth in Medicine')
plt.savefig('xai/figures/yearly-growth-medicine.png')

# Non-CS and non-Medicine

sns.set_theme(style="whitegrid")
f, ax = plt.subplots(figsize=(20, 6))

yearly = Counter()
for pid in papers:
    field = get_field(papers[pid])
    if field == 'Computer Science' or field == 'Medicine':
        continue
    if 'year' in papers[pid] and papers[pid]['year'] and 2025 > int(papers[pid]['year']) > 2012:
        yearly[papers[pid]['year']] += 1

yearly_df = pd.DataFrame([{'year': key, 'count': yearly[key]} for key in yearly])

sns.barplot(data=yearly_df, x="year", y='count')
ax.set(xlabel='', ylabel='paper count', title='XAI growth outside of CS/Medicine')
plt.savefig('xai/figures/yearly-growth-else.png')


sns.set_theme(style="whitegrid")
f, ax = plt.subplots(figsize=(26, 6))

clusters = Counter()
for pid in papers:
    cluster = get_field(papers[pid])
    if cluster:
        clusters[cluster] += 1

clusters_df = pd.DataFrame([{'field': key.replace(' ','\n'),
                          'count': clusters[key]} for key in clusters])


sns.barplot(data=clusters_df.sort_values(by='count', ascending=False), x="field", y='count')
ax.set(xlabel='', ylabel='paper count')
plt.savefig('xai/figures/field-counts.png')

f, ax = plt.subplots(figsize=(26, 6))
del clusters['Computer Science']
clusters_df = pd.DataFrame([{'field': key.replace(' ','\n'),
                          'count': clusters[key]} for key in clusters])

sns.barplot(data=clusters_df.sort_values(by='count', ascending=False), x="field", y='count')
ax.set(xlabel='', ylabel='paper count')
plt.savefig('xai/figures/field-counts-sans-cs.png')


with open('expanded_papers.json', 'r') as f:
    papers = json.load(f)

counts = {}
fields = set(get_field(papers[pid]) for pid in papers)

for field in fields:
    counts[field] = Counter()
# counts['Linguistics'] = Counter()

for pid in papers:
    cites = papers[pid]['citations'] if 'citations' in papers[pid] else []
    for citing_paper in cites:
        citing_pid = citing_paper['paperId']
        citing_field = get_field(citing_paper)
        cited_field = get_field(papers[pid])
        if citing_pid in papers and citing_field != cited_field and citing_field and cited_field:
            counts[citing_field][cited_field] += 1

field = 'Computer Science'
num_cites = sum(list(counts[field].values()))
sns.set_theme(style="whitegrid")
f, ax = plt.subplots(figsize=(8, 6))
counts_data = pd.DataFrame([{'field': key, f'% citations by {field}': counts[field][key]/num_cites*100} for key in counts[field] if counts[field][key]/num_cites*100 > 1])
sns.barplot(data=counts_data.sort_values(by=f'% citations by {field}', ascending=False), x="field", y=f'% citations by {field}')
ax.set(title=f'% of citations by XAI-{field} by field (top 5) out of all cross-field citations by XAI-CS', xlabel='')
plt.savefig(f'figures/percentage-cited-by-{field}.pdf')