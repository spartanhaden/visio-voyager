import torch
import open_clip
import time
import random
import glob
import sqlite3
import tqdm
import pprint
import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image
from IPython import embed
import numpy as np


class ImageDB:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # key is the filename and the value is the embedding
        self.data_dict = {}

        self.load_model()
        self.init_db()

    def load_model(self):
        start_time = time.time()
        print("loading model...")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms('ViT-bigG-14', pretrained='laion2b_s39b_b160k', device=self.device)
        print("model loaded in %0.2f seconds" % (time.time() - start_time))
        self.tokenizer = open_clip.get_tokenizer('ViT-bigG-14')

    def embed_string(self, query=''):
        start_time = time.time()
        text = self.tokenizer([query]).to(self.device)
        text_embedding = None
        with torch.no_grad(), torch.cuda.amp.autocast():
            text_embedding = self.model.encode_text(text).float()
            text_embedding /= text_embedding.norm(dim=-1, keepdim=True)
        print(f"encoded text in {time.time() - start_time} seconds")

        return text_embedding.cpu().numpy()[0]

    def embed_image(self, filepath):
        start_time = time.time()
        # print(f'loading image {filepath}')
        try:
            image = Image.open(filepath)
            converted_image = self.preprocess(image.convert("RGB"))
        except Exception as e:
            print(f'error opening {filepath}: {e}')
            return None

        # print(f'image loaded in {time.time() - start_time} seconds')

        start_time = time.time()
        # print('creating embedding...')
        with torch.no_grad(), torch.cuda.amp.autocast():
            tensor_image = torch.stack([converted_image.to(self.device)])
            embedding = self.model.encode_image(tensor_image).float()
            # normalize
            embedding /= embedding.norm(dim=-1, keepdim=True)

        # print(f'embedding created in {time.time() - start_time} seconds')
        self.data_dict[filepath] = embedding.cpu().numpy()[0]

        # return embedding

    def search_files(self, term, show_top=20):
        print(f"Searching for {term}")

        text_embedding = self.embed_string(term)

        # Pre-calculate the norm of the text embedding
        norm_a = np.linalg.norm(text_embedding)

        similarities = {}

        for filepath, image_embedding in self.data_dict.items():
            dot_product = np.dot(text_embedding, image_embedding)
            norm_b = np.linalg.norm(image_embedding)
            cosine_similarity = dot_product / (norm_a * norm_b)

            similarities[filepath] = cosine_similarity

        # Sort the files based on cosine similarity in descending order
        sorted_similarities = sorted(similarities.items(), key=lambda x: x[1], reverse=True)

        # Get the top 10 closest files
        top_files = [filepath for filepath, similarity in sorted_similarities[:show_top]]

        for i, file in enumerate(top_files):
            print(f"{i + 1}\t{sorted_similarities[i][1]:.3f}\t{file}")

        return top_files

        # Get a list of the the keys in the data_dict
        file_paths = list(self.data_dict.keys())
        print(f"Number of files: {len(file_paths)}")

        # Randomly get 10 of the file paths
        random.shuffle(file_paths)
        file_paths = file_paths[:show_top]

        text_embedding = self.embed_string(term)

        start_time = time.time()
        distances, indices = self.nbrs.kneighbors(text_embedding.cpu().numpy())
        print(f"searched in {time.time() - start_time} seconds")

        print("Indices of nearest neighbors:", indices)
        print("Distances to nearest neighbors:", distances)

        # print the filenames of the most similar images. the indices are from the embeddings dict
        for i in range(len(distances[0])):
            print(f"{distances[0][i]*100.0:.2f}%\t{self.filenames[indices[0][i]]}")

        return distances, indices[0]

    def validate_image(self, filepath):
        # TODO return if the filepath is in the db
        return True

    def index_directory(self, directory):
        # recursively get all the files
        glob_files = glob.glob(f'{directory}/**', recursive=True)
        # glob_files = glob.glob('test_images/*')

        print(f'number of files: {len(glob_files)}')

        # remove any folders that are empty
        glob_files = [filepath for filepath in glob_files if os.path.isfile(filepath)]

        extension_set = set([filepath.split('.')[-1] for filepath in glob_files])
        print(f'initial extensions: {extension_set}')

        # remove 'mov', 'avi', 'txt', 'wmv', 'mp4', 'webm'
        glob_files = [filepath for filepath in glob_files if filepath.split('.')[-1] not in ('mov', 'avi', 'txt', 'wmv', 'mp4', 'webm')]

        # only add images
        glob_files = [filepath for filepath in glob_files if filepath.endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG', '.gif', '.GIF'))]

        extension_set = set([filepath.split('.')[-1] for filepath in glob_files])
        print(f'extensions remaining: {extension_set}')

        pprint.pprint(glob_files)

        print(f'embedding {len(glob_files)} images')

        for filepath in tqdm.tqdm(glob_files):
            self.embed_image(filepath)

        data_to_insert = [(filepath, data.tobytes()) for filepath, data in self.data_dict.items()]

        conn = sqlite3.connect('embeddings.db')
        c = conn.cursor()

        # remove all the entries in the files table
        c.execute('DELETE FROM files')

        c.executemany('INSERT INTO files VALUES (?, ?)', data_to_insert)

        conn.commit()
        conn.close()

    def init_db(self):
        conn = sqlite3.connect('embeddings.db')
        c = conn.cursor()
        # check if any tables exist and if not, create one
        c.execute('CREATE TABLE IF NOT EXISTS files (filepath TEXT PRIMARY KEY, raw_data BLOB)')

        c.execute('SELECT * FROM files')
        rows = c.fetchall()

        conn.commit()
        conn.close()

        if len(rows) == 0:
            print('No data found')
            directory = self.get_directory()
            print(f"Selected folder: {directory}")
            self.index_directory(directory)
        else:
            # TODO check if the files exist
            print(f'Loading {len(rows)} files')
            for row in tqdm.tqdm(rows):
                embedding = np.frombuffer(row[1], dtype=np.float32)
                self.data_dict[row[0]] = embedding

    def get_directory(self):
        root = tk.Tk()

        # Hide thne main window
        root.withdraw()

        # Open the dialog and get the folder selected
        folder_selected = filedialog.askdirectory()

        # Destroy the main window
        root.destroy()

        return folder_selected
