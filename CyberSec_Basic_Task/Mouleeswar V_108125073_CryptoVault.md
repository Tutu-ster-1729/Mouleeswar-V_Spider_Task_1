STAGE 1 

OBJECTIVE: To implement a CLI Tool that can encrypt and decrypt text files using the Caesar Cipher. Can attempt to decrypt to plaintext with no prior shift amount given by using the user defined crack function

CAESAR CIPHER: substitutes each letter of the text to be encrypted with a fixed number of positions (shift) ahead (or behind)

IMPLEMENTATION:
    Individual user defined functions are being utilised to encrypt/decrypt strings or textfiles with or without shift given from input arguements. This improves modularity and Reusability.
    Encrypting reads through a string and gets their ordinal (ASCII) value which is then subtracted with "A" or "a" depending on the case and this gives the position of the alphabet. This avoids the looping problem in ASCII. The shift is then applied to position (%26 is implied) and then convered back to letters. In the case the character is not a alphabet, it is appended to the decrypt text as it is.
    Decrypting employes the above logic but shifting the characters backwards.
    To find the Top 3 Ciphers, each shift was given a score based on how common they occur in readable english, how many common english words occur and how many bigrams are present from the functions frequency_score(), common_word_score() and ngram_score() respectively. 
    common_word_score() compares each word in the decrypted text with a defined list of common words and assigns a score based on them 
    frequency_score() has a pre defined probability of each letters occuring in sentences. It utilises the Counter method from the collections module to make a list of occurrences and then their frequency is subtracted from them. This error is subtracted from the score (absolute). So the lesser score a string gets the closer it is to readable English
    ngram_score() implements the same logic as common_word_score() but with pre defined bigrams. It can also be extended with any length (trigrams, etc)
    Total score weightage is purely experimental and can be changed
    Argument parsing is done to read command line arguements using argparse library

RESULT:
Ciphertext:Wkh txlfn eurzq ira mxpsv ryhu wkh odcb grj.Fubswrjudskb lv wkh duw rizulwlqj dqg vroylqj frghv
Top Ranked Output:Top 3:
Shift 3 : Score = 41.353493670886074 : The quick brown fox jumps over the lazy dog. Cryptography is the art ofwriting and solving codes
Shift 16 : Score = -6.949797468354431 : Gur dhvpx oebja sbk whzcf bire gur ynml qbt. Pelcgbtencul vf gur neg bsjevgvat naq fbyivat pbqrf
Shift 14 : Score = -7.7634683544303815 : Iwt fjxrz qgdlc udm yjbeh dktg iwt apon sdv. Rgneidvgpewn xh iwt pgi dulgxixcv pcs hdakxcv rdsth

LIMITATIONS:
1. Limited Number of Keys (26) --> Easy to break / Bruteforce
2. Frequency Analysis can be applied to speed up the eliminations in actual Caesar cipher. But in this stage it is less reliable for uncommon vocabulary and can be easily misleading. Hence the scoring system exists
3. Scoring Accuracy increases as length of the ciphertexts increases, ie actual text can still be scored less for below top 3 if its shorter in length

-------------------
STAGE 2

OBJECTIVE: Extending the cryptovault with integrity feature which can be triggered with the optional added flag in the CLI
While Encrypting using Caesar cipher offers some confidentiality, it can still be decoded and be tampered with. Hence Hashing is implemented 

SHA256 HASHING: Secure Hash Algorithm - 256 bit - A cryptographic hash functions that generates a fixed string of 256 bits or 32 bytes or 64 hex characters for any input. It does not change as long as the input isnt change. When changed it causes huge difference in the hash making it easy to spot. It is also fixed in length for any amount of given input, hence it is technically impossible to recover original content from the hash

IMPLEMENTATION:
    standard library module hashlib function has been used for implementing this function.
    Optional parser flag --verify has been added
    A hash function has been defined with help of haslib module, which first converts the text input to bytes with the .encode() methode, then a hash is generated in the form of bytes which is then converted to hex characters using .hexdigest() method
    encrypt function has been changed so that, encrypting a file always produces a hash and stores it in the .txt.enc file
    decrypt function has been changed so that verify flag defaultly remains false but can be called if the flag has been called in the cli. without the flag, the function will not verify the hash. It will still generate a has for the encrypted output. when the flag is called, the hashes are compared and respective messages are shown to output

OBSERVATION: Improved detection of accidental corruption/file modification during transfer or basic tampering attempts

LIMITATIONS: While the current design can offer basic integrity check, an attacker can still modify both the has and content leaving it vulnerable, tampered with without any warnings 

-------------------
STAGE 3 

To prevent any confusion regarding Caesar cipher and AES encrypting, all Caesar functions were added a prefix "c" to their names 

OBJECTIVE: To replace Caesar cipher with a more modern encryption scheme AES-256-CBC while preserving integrity verification, as Caesar has only 26 possible shifts while AES-256 has a theoretical 2^256 keyspace.

AES: Advanced Encryption Standard: A symmetric encryption algorithm (encryption key = decryption key)
AES-256-CBC : uses 256 bits key and Cipher Block Chaining - enrcypts each plaintext block (block size of AES: 128 bits) using info prom previous encrypted blocks, reducing any visible patterns
PBKDF2 : Password Based Key Derivation Function 2: As such passwords cannot be used as keys, hence this module is used to convert them into fixed length cryptographic keys using repeated computation/iterations to slow down any brute-forcing
Salt : Randomly generated during encryption and combined with password for deriving keys
IV : Initialization Vector : CBC requires a random IV

IMPLEMENTATION:
ENCRYPTION:                         |        DECRYPTION:
Plaintext file ->                   |        Read SALT ->
Compute SHA256 hash ->              |        Derive AES key from password ->
Generate random salt ->             |        Read IV ->
Derive AES key using PBKDF2 ->      |        AES decrypt ciphertext ->
Generate random IV ->               |        Remove padding ->
Pad plaintext ->                    |        Recover plaintext ->
AES-256-CBC encryption->            |        Verify SHA256 integrity hash ->
Store:                              |        Restore file
    SALT                            |
    IV                              |
    HASH                            |
    DATA                            |

Only the correct password can be able to decrypt the file, an incorrect password would trigger a Padding/decrytion error
Same Integrity check from stage 2 has been implemented 
Even with same password, repeated encryption would trigger different ciphertext as salt and iv are random renerated 

LIMITATIONS: 
1. Incorrect password raises error rather than an explicit warning message
2. Not as Sophisticated as modern encryption modes and standards

-------------------
STAGE 4

OBJECTIVE: Extend Cryptovault beyond passwords by implementing a hybrid cryptographic system combining RSA and AES. The goal is to securely encrypt the files without requiring the users to exchange passwords

IMPLEMENTATION:
While password based AES encryption is secure, a sender will have to share the password to a receiver to make use of the encrypted files. Hybrid encryption follows assymetric encryption (ie different keys to encrypt and decrypt file) to solve the misuse of passwords
RSA uses Asymmetric encryption which can effectively encrypt small data such as other keys but is not suitable for large data. Hence AES is used to encrypt large data using symmetric encryption and AES key is encrypted using RSA. Hence use of RSA directly is not feasible for files, it can be rather implemented on keys
A separate function for key generation has been implemented that stores private and public keys in a .pem file for each. They are generated by computing using functions in rsa's module (cryptography.hazmat.primitives.asymmetric)
AES uses a different PKCS7 padding while RSA uses OAEP padding. Their methods might be different but they are used to serve the same purpose, ie to fill out redundant bytes until block size of the algorithm used is filled (AES - 16 bytes - 128 bits)

ENCRYPTION:                                     DECRYPTION:
Generate random AES-256 key ->                  Read RSAKEY ->
Generate random IV ->                           Load private.pem ->
Encrypt file using AES-CBC ->                   Decrypt RSAKEY ->
Load recipient public key ->                    Recover AES session key ->
Encrypt AES key using RSA-OAEP ->               AES decrypt ciphertext ->
Store:                                          Remove padding ->
    RSAKEY                                      Recover plaintext ->
    IV                                          Verify SHA256 hash
    HASH
    DATA

The structure used here is somewhat similar to modern HTTP/TLS (Transport layer security) protocol which encrypts HTTPS communication over the internet. During the TLS handshake or initiation, client obtains the server's public key and generates a temporary symmetric session key which is encrypted using the RSA public key and transmitted back to the server. This is decrypted by the server using its private key, after which both client and server switch to AES. This handshake encryption is exactly implemented in this stage.

LIMITATIONS:
There are possible improvements that can be done to this model such as using the much more modern AES-GCM algorithm, implementing digital signatures and validating certificates, encrypting the private keys, timely key expiry or rotation like authenticator apps

-------------------