import argparse
from collections import Counter
import hashlib
import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import (hashes, serialization)
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives.ciphers import (Cipher, algorithms, modes)
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding

parser = argparse.ArgumentParser()
parser.add_argument("mode")
parser.add_argument("file", nargs="?", default=None)
parser.add_argument("--shift", type=int)
parser.add_argument("--password")
parser.add_argument("--verify", action="store_true")
parser.add_argument("--pub")
parser.add_argument("--priv")
args = parser.parse_args()

###
def cencrypt_text(text, shift):
    encrypted = ''
    for char in text:
        if not char.isalpha():
            encrypted+=char
            continue
        if char.isupper():            
            position = ord(char) - ord('A')
            position = (position + shift) % 26
            encrypted += chr(position + ord('A'))
        elif char.islower():
            position = ord(char) - ord('a')
            position = (position + shift) % 26
            encrypted += chr(position + ord('a'))
    return encrypted

def cdecrypt_text(text, shift):
    return cencrypt_text(text, -shift)

def cencrypt(file, shift):
    with open(file, "r") as f1:
        content = f1.read()
    enc_cont = cencrypt_text(content, shift)
    file_hash = hashit(content)
    with open(file+'.enc', "w") as f2:
        f2.write(f"HASH: {file_hash}\n")
        f2.write(f"DATA: {enc_cont}")

def cdecrypt(file, shift, verify=False):
    with open(file, "r") as f1:
        content = f1.readlines()
    stored = content[0].replace("HASH:","").strip()
    de_cont = cdecrypt_text(content[1].replace("DATA",""), shift)
    new = hashit(de_cont)
    if verify:
        if stored == new:
            print("Integrity OK") 
            with open(file.removesuffix('.enc'), "w") as f2:
                f2.write(de_cont)
        else:
            print("WARNING: file tampered")

def crack(text):
    rated = []
    for shift in range(26):
        dec = cdecrypt_text(text, shift)
        score = total_score(dec)
        rated.append((score,shift,dec))
        print(f"Shift {shift}: ", dec)
    rated.sort(reverse=True)
    print("\nTop 3:")
    for score,shift,dec in rated[:3]:
        print(f"Shift {shift} : Score = {score} : {dec}")

def common_word_score(text):
    common = ['the', 'and', 'is', 'of', 'to', 'in', 'that', 'for', 'on', 'with']
    text = text.lower()
    score = 0
    for word in common:
        score += text.count(word)
    return score

def frequency_score(text):
    letters = [c.upper() for c in text if c.isalpha()]
    if len(letters) == 0:
        return -999
    counts = Counter(letters)
    score = 0
    total = len(letters)
    ENGLISH_FREQ = {'E':12.7,'T':9.1,'A':8.2,'O':7.5,'I':7.0,'N':6.7,'S':6.3,'H':6.1,'R':6.0,'D':4.3,'L':4.0,'C':2.8,'U':2.8,'M':2.4,'W':2.4,'F':2.2,'G':2.0,'Y':2.0,'P':1.9,'B':1.5,'V':1.0,'K':0.8,'J':0.15,'X':0.15,'Q':0.1,'Z':0.07}
    for letter, freq in ENGLISH_FREQ.items():
        observed = (counts.get(letter, 0)/total)*100
        score -= abs(observed-freq)                     # observed - expected error being subtracted from 0
    return score                                        # less negative more alike with readable english     

def ngram_score(text):
    COMMON_BIGRAMS = ["th","he","in","er","an","re","on","at","en","nd"]
    text = text.lower()
    score = 0
    for gram in COMMON_BIGRAMS:
        score += text.count(gram)
    return score

def total_score(text):
    return (3*common_word_score(text) + 0.2*frequency_score(text) + 2*ngram_score(text))

def hashit(text):
    return hashlib.sha256(text.encode()).hexdigest()
###

def derive_key(password, salt):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
    return kdf.derive(password.encode())

def encrypt_pass(file, password):
    with open(file, "r") as f1:
        content = f1.read()
    fhash = hashit(content)
    salt = os.urandom(16)                                       # AES block size = 16 bytes, IV prevents identical ciphertext
    key = derive_key(password, salt)
    iv = os.urandom(16)                                         # For AES enc key = size 32 bytes 
    plaintext = content.encode()
    padder = sym_padding.PKCS7(128).padder()                        # AES - 16 bytes - adds redundant bytes if less
    padded = (padder.update(plaintext) + padder.finalize())
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = (encryptor.update(padded) + encryptor.finalize())
    with open(file+".enc", "w") as f2:
        f2.write("SALT: " + base64.b64encode(salt).decode() + "\n")
        f2.write("IV: " + base64.b64encode(iv).decode() + "\n")
        f2.write("HASH: " + fhash + "\n")
        f2.write("DATA: " + base64.b64encode(ciphertext).decode())

def decrypt_pass(file, password, verify=False):
    with open(file, "r") as f1:
        lines = f1.readlines()
    salt = base64.b64decode(lines[0].replace("SALT: ", "").strip())
    iv = base64.b64decode(lines[1].replace("IV: ", "").strip())
    stored_hash = lines[2].replace("HASH: ", "").strip()
    ciphertext = base64.b64decode(lines[3].replace("DATA: ", ""))
    key = derive_key(password, salt)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted = (decryptor.update(ciphertext) + decryptor.finalize())
    unpadder = sym_padding.PKCS7(128).unpadder()                        # reverse - removes unwanted bytes
    plaintext = (unpadder.update(decrypted) + unpadder.finalize())
    content = plaintext.decode()
    new_hash = hashit(content)
    if verify:
        if (new_hash == stored_hash):
            print("Integrity OK")
        else:
            print("WARNING: File tampered")
            return
    with open(file.removesuffix(".enc"), "w") as f2:
        f2.write(content)

def keygen():
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = private.public_key()
    with open("private.pem", "wb") as f:
        f.write(private.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()))
    with open("public.pem", "wb") as f:
        f.write(public.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo))
    print("RSA keys generated")

def rsa_encrypt(file, pubpem):
    with open(file, "r") as f:
        content = f.read()
    fhash = hashit(content)
    key = os.urandom(32)
    iv = os.urandom(16)
    plaintext = content.encode()
    padder = sym_padding.PKCS7(128).padder()                        # AES - 16 bytes - adds redundant bytes if less
    padded = (padder.update(plaintext) + padder.finalize())
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = (encryptor.update(padded) + encryptor.finalize())
    with open(pubpem, "rb") as f:
        public = (serialization.load_pem_public_key(f.read()))
    encrypted_key = (public.encrypt(key, asym_padding.OAEP(mgf = asym_padding.MGF1(algorithm=hashes.SHA256()), algorithm= hashes.SHA256(), label=None)))
    with open(file+".enc", "w") as f2:
        f2.write("RSAKEY: " + base64.b64encode(encrypted_key).decode() + "\n")
        f2.write("IV: " + base64.b64encode(iv).decode() + "\n")
        f2.write("HASH: " + fhash + "\n")
        f2.write("DATA: " + base64.b64encode(ciphertext).decode())

def rsa_decrypt(file, privpem, verify=False):
    with open(file, "r") as f:
        lines = f.readlines()
    encrypted_key = base64.b64decode(lines[0].replace("RSAKEY: ", "").strip())
    iv = base64.b64decode(lines[1].replace("IV: ", "").strip())
    stored_hash = lines[2].replace("HASH: ", "").strip()
    ciphertext = base64.b64decode(lines[3].replace("DATA: ", ""))
    with open(privpem, "rb") as f:
        private = (serialization.load_pem_private_key(f.read(), password=None))
    recovered_key = (private.decrypt(encrypted_key, asym_padding.OAEP(mgf=asym_padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)))
    cipher = Cipher(algorithms.AES(recovered_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted = (decryptor.update(ciphertext) + decryptor.finalize())
    unpadder = sym_padding.PKCS7(128).unpadder()                        # reverse - removes unwanted bytes
    plaintext = (unpadder.update(decrypted) + unpadder.finalize())
    content = plaintext.decode()
    new_hash = hashit(content)
    if verify:
        if (new_hash == stored_hash):
            print("Integrity OK")
        else:
            print("WARNING: File tampered")
            return
    with open(file.removesuffix(".enc"), "w") as f2:
        f2.write(content)

if args.mode == "crack":
    with open(args.file, "r") as f:
        text = f.read()
    crack(text)
elif args.mode == "encrypt":
    if args.password:
        encrypt_pass(args.file, args.password)
    elif args.shift is not None:
        cencrypt(args.file, args.shift)
    elif args.pub:
        rsa_encrypt(args.file, args.pub)
    else:
        print("Needs password or shift or key")
elif args.mode == "decrypt":
    if args.password:
        decrypt_pass(args.file, args.password, args.verify)
    elif args.shift is not None:
        cdecrypt(args.file, args.shift, args.verify)
    elif args.priv:
        rsa_decrypt(args.file, args.priv, args.verify)
    else:
        print("Needs password or shift or key")
elif args.mode == "keygen":
    keygen()