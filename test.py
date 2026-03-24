import project as db

database = db.Database("declarkt", "665182861")

testUserData = {"username": "Luis"}
testProofData = {"claim": "Pigs can fly", "result": "They Can! Source: trust me bro!", "creator": "Luis"}

if (database.addUser(testUserData)) == True:
    print("\033[32mAdd User Passed!\033[0m")
else:
    print("\033[31mAdd User Failed!\033[0m")
 
if (database.addProof(testProofData)) == True:
    print("\033[32mAdd Proof Passed!\033[0m")
else:
    print("\033[31mAdd Proof Failed!\033[0m")

result = database.retrieveProofs(testUserData)   
if (result) != None:
    print(result)
    print("\033[32mRetrieve Proofs Passed!\033[0m")
else:
    print("\033[31mRetrieve Proofs Failed!\033[0m")

testProofData = database.retrieveProof(testProofData)
if (testProofData) != None:
    print(testProofData)
    print("\033[32mRetrieve Proof Passed!\033[0m")
else:
    print("\033[31Retrieve Proof Failed!\033[0m")
  
if (database.deleteProof(testProofData[0])) == True:
    print("\033[32mDelete Proof Passed!\033[0m")
else:
    print("\033[31mDelete Proof Failed!\033[0m")
    
if (database.deleteUser(testUserData)) == True:
    print("\033[32mDelete User Passed!\033[0m")
else:
    print("\033[31mDelete User Failed!\033[0m")