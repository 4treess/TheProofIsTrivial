from fastapi import FastAPI
from pydantic import BaseModel
import project
import proof as tc

from fastapi.middleware.cors import CORSMiddleware

db = project.Database("declarkt", "665182861")
app = FastAPI()

# Website: http://192.168.18.191/~declarkt/index.html
# Alternate Link: http://dolphin.csci.viu.ca/~declarkt/index.html
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials = True, allow_methods = ["*"], allow_headers = ["*"])

class User(BaseModel):
    username: str

class Proof(BaseModel):
    proposition: str
    result: str
    creator: str
    

@app.get("/Proof/{proposition}")
async def get_proof(proposition: str):
    return db.retrieveProof({"proposition": proposition})

@app.get("/Proofs/{username}")
async def get_proof_by_creator(username: str):
    return db.retrieveProofs({"username": username})

@app.get("/Login/{username}")
async def login_to_website(username: str):
    return db.getUser({"username": username})

@app.post("/AddUser")
async def add_user(user: User):
    return db.addUser(user.dict())

@app.post("/Proof")
async def add_proof(proof: Proof):
    prop1 = proof.proposition
    try:
        p1 = tc.Proof(prop1)
    except tc.PropositionError as e:
        print(e)
        return False

    proof.result = p1.getProof()
    # lists = proof.result.split("\n")
    # proof.result = ""
    # for i in lists:
    #     proof.result += i + "<br/>"
            
    return db.addProof(proof.dict())

@app.post("/DelUser")
async def del_user(user: User):
    return db.deleteUser(user.dict())

@app.post("/DelProof")
async def del_proof(proof: Proof):
    return db.deleteProof(proof.dict())